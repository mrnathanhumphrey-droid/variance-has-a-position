"""NCAA D1 Stan robustness fit for Test 1 cross-league replication.

Adapts the WNBA hierarchical NB2 model to NCAA D1 scale. Fits PTS/REB/BLK
on prior-season data and projects per-player rates for the test season,
then computes per-game residuals and re-runs the 3-cell coupling test.

Tests whether the surgical NCAA REB x Center coupling reflects residual
variance asymmetry or position-mean structure (parallel to the WNBA
Section 5.6.1 procedure). BLK is expected to survive Stan attenuation
based on the WNBA precedent; REB is the test that disambiguates.

Output: audit_runs/stan_robustness/ncaa_<div>_stan_3_cell.csv
"""
from __future__ import annotations
import os
import sys
sys.stdout.reconfigure(encoding="utf-8")

RTOOLS = r"C:\Users\Nate\.cmdstan\RTools40"
os.environ["PATH"] = (
    f"{RTOOLS}\\usr\\bin;{RTOOLS}\\mingw64\\bin;" + os.environ.get("PATH", "")
)

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd
from cmdstanpy import CmdStanModel
from scipy import stats

p = argparse.ArgumentParser()
p.add_argument("--division", choices=["mens", "womens"], required=True)
args = p.parse_args()

DIV = args.division.upper().replace("MENS", "Mens").replace("WOMENS", "Womens")
ROOT = Path(rf"D:/NCAA D1 {DIV}")
RAW = ROOT / "data" / "raw" / "sportsdataverse"
MODEL = Path(r"D:/WNBA Projections/models/stan/hierarchical_one_stat_wnba.stan")
OUT_DIR = ROOT / "audit_runs" / "stan_robustness"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TEST_SEASONS = [2024, 2025]
STATS = ["PTS", "REB", "BLK"]
STAT_TO_COL = {"PTS": "points", "REB": "rebounds", "BLK": "blocks"}
PRIOR_MU = {"PTS": (-0.9, 1.0), "REB": (-1.9, 1.0), "BLK": (-3.9, 1.5)}
MIN_GAMES_TEST = 10
MIN_GAMES_TRAIN = 3
N_CHAINS = 4
N_WARMUP = 200
N_SAMPLING = 200


def position_inclusive(p):
    if pd.isna(p) or not p or str(p).strip() == "": return "Forward"
    s = str(p).lower()
    if "center" in s: return "Center"
    if "guard" in s: return "Guard"
    return "Forward"


def f_test_two_sided(arr_in, arr_out):
    a = np.asarray(arr_in, dtype=float); b = np.asarray(arr_out, dtype=float)
    if len(a) < 2 or len(b) < 2: return np.nan
    var_a, var_b = a.var(ddof=1), b.var(ddof=1)
    if var_a == 0 or var_b == 0: return np.nan
    F = var_a / var_b
    cdf = stats.f.cdf(F, len(a) - 1, len(b) - 1)
    return 2 * min(cdf, 1 - cdf)


def run_cell(r_in, r_out, season, stat):
    n_in, n_out = len(r_in), len(r_out)
    base = {"division": DIV.upper(), "season": season, "stat": stat,
            "class": "Center", "n_in": n_in, "n_out": n_out}
    if n_in < 5 or n_out < 5:
        base.update({"sd_in": np.nan, "sd_out": np.nan, "ratio": np.nan,
                     "p_levene": np.nan, "p_bartlett": np.nan, "p_F": np.nan})
        return base
    sd_in, sd_out = float(r_in.std(ddof=1)), float(r_out.std(ddof=1))
    ratio = sd_in / sd_out if sd_out > 0 else np.nan
    try: _, p_lev = stats.levene(r_in, r_out, center="median")
    except Exception: p_lev = np.nan
    try: _, p_bart = stats.bartlett(r_in, r_out)
    except Exception: p_bart = np.nan
    base.update({
        "sd_in": sd_in, "sd_out": sd_out, "ratio": float(ratio),
        "p_levene": float(p_lev), "p_bartlett": float(p_bart),
        "p_F": float(f_test_two_sided(r_in, r_out)),
    })
    return base


def scenario_label(p_levene):
    if pd.isna(p_levene): return "n/a"
    if p_levene < 0.001: return "couples (p<0.001)"
    if p_levene < 0.05: return "couples (p<0.05)"
    if p_levene < 0.10: return "directional (p<0.10)"
    return "null"


def load_box(stat_col):
    frames = []
    for season in [2023, 2024, 2025]:
        df = pd.read_parquet(RAW / f"player_box_{season}.parquet",
            columns=["game_id", "season", "athlete_id",
                     "athlete_position_name", "minutes",
                     "points", "rebounds", "blocks", "did_not_play"])
        frames.append(df)
    games = pd.concat(frames, ignore_index=True)
    games = games[games["did_not_play"] == False].copy()
    games = games[games["minutes"].fillna(0) > 0].copy()
    games["athlete_id"] = games["athlete_id"].astype("Int64")
    return games


def build_train_test(games, test_season, stat_col):
    train_games = games[games["season"] < test_season].copy()
    test_games = games[games["season"] == test_season].copy()

    train_gp = train_games.groupby("athlete_id")["game_id"].count()
    eligible_train = train_gp[train_gp >= MIN_GAMES_TRAIN].index
    train_games = train_games[train_games["athlete_id"].isin(eligible_train)].copy()

    test_gp = test_games.groupby("athlete_id")["game_id"].count()
    eligible_test = test_gp[test_gp >= MIN_GAMES_TEST].index
    test_games = test_games[test_games["athlete_id"].isin(eligible_test)].copy()

    cohort_ids = sorted(set(train_games["athlete_id"].dropna()) |
                        set(test_games["athlete_id"].dropna()))
    id_to_idx = {a: i + 1 for i, a in enumerate(cohort_ids)}
    train_games["player_idx"] = train_games["athlete_id"].map(id_to_idx)
    test_games["player_idx"] = test_games["athlete_id"].map(id_to_idx)

    pos_map = (games.groupby("athlete_id")["athlete_position_name"]
               .agg(lambda s: s.dropna().mode().iloc[0]
                    if len(s.dropna()) and len(s.dropna().mode()) else None)
               .to_dict())
    pos_class = {a: position_inclusive(pos_map.get(a)) for a in cohort_ids}
    pos_to_idx = {"Guard": 1, "Forward": 2, "Center": 3}
    player_position = np.array([pos_to_idx[pos_class[a]] for a in cohort_ids],
                                 dtype=int)

    train_games["counts"] = pd.to_numeric(train_games[stat_col], errors="coerce")
    train_games = train_games[train_games["counts"].notna()].copy()
    train_games["counts"] = train_games["counts"].astype(int)
    train_games = train_games[train_games["minutes"] > 0].copy()

    return train_games, test_games, id_to_idx, player_position, cohort_ids, pos_class


def fit_one(model, train_games, player_position, n_players, prior_mu_pair):
    mu_loc, mu_sd = prior_mu_pair
    data = {
        "N": len(train_games),
        "N_players": n_players,
        "N_positions": 3,
        "player_idx": train_games["player_idx"].astype(int).values,
        "player_position": player_position.astype(int),
        "counts": train_games["counts"].astype(int).values,
        "minutes": train_games["minutes"].astype(float).values,
        "weights": np.ones(len(train_games), dtype=float),
        "prior_mu_league": float(mu_loc),
        "prior_mu_league_sd": float(mu_sd),
    }
    fit = model.sample(
        data=data, chains=N_CHAINS, parallel_chains=N_CHAINS,
        iter_warmup=N_WARMUP, iter_sampling=N_SAMPLING,
        seed=12345, show_progress=False, show_console=False,
    )
    return fit


def project_test(fit, test_games, n_players):
    rate_per_36 = fit.stan_variable("rate_per_36").mean(axis=0)
    rate_per_min = rate_per_36 / 36.0
    test_games["rate_per_min"] = test_games["player_idx"].astype(int).map(
        lambda i: rate_per_min[i - 1] if 1 <= i <= n_players else np.nan)
    test_games["proj_count"] = test_games["rate_per_min"] * test_games["minutes"]

    proj = (test_games.groupby("athlete_id")
            .agg(proj_total=("proj_count", "sum"),
                  actual_total=("counts", "sum"),
                  gp=("game_id", "count"))
            .reset_index())
    proj["proj_per_game"] = proj["proj_total"] / proj["gp"]
    proj["actual_per_game"] = proj["actual_total"] / proj["gp"]
    proj["resid"] = proj["actual_per_game"] - proj["proj_per_game"]
    return proj


def main():
    print(f"[load] NCAA {DIV} player_box")
    games = load_box(None)
    print(f"  {len(games)} game-rows after DNP/0-min filter, "
          f"{games['athlete_id'].nunique()} unique athletes")

    print(f"[compile] {MODEL}")
    t0 = time.time()
    model = CmdStanModel(stan_file=str(MODEL))
    print(f"[compile] {time.time() - t0:.1f}s")

    rows = []
    all_proj = []
    for stat in STATS:
        stat_col = STAT_TO_COL[stat]
        for N in TEST_SEASONS:
            print(f"\n=== fit {stat} test_season {N} ===")
            train_games, test_games, id_to_idx, player_position, cohort_ids, pos_class = \
                build_train_test(games, N, stat_col)
            test_games["counts"] = pd.to_numeric(test_games[stat_col], errors="coerce").fillna(0).astype(int)

            print(f"  train: {len(train_games)} rows, "
                  f"{len(cohort_ids)} unique athletes (G/F/C: "
                  f"{int((player_position == 1).sum())}/"
                  f"{int((player_position == 2).sum())}/"
                  f"{int((player_position == 3).sum())})")
            print(f"  test:  {test_games['athlete_id'].nunique()} test athletes "
                  f">= {MIN_GAMES_TEST} GP")

            t0 = time.time()
            fit = fit_one(model, train_games, player_position,
                           n_players=len(cohort_ids),
                           prior_mu_pair=PRIOR_MU[stat])
            print(f"  fit: {time.time() - t0:.1f}s")

            proj = project_test(fit, test_games, len(cohort_ids))
            proj["season"] = N
            proj["stat"] = stat
            proj["pos_class"] = proj["athlete_id"].map(
                lambda x: pos_class.get(int(x) if pd.notna(x) else None,
                                          "Forward"))
            all_proj.append(proj)

            in_mask = proj["pos_class"] == "Center"
            r_in = proj.loc[in_mask, "resid"].dropna().values
            r_out = proj.loc[~in_mask, "resid"].dropna().values
            rows.append(run_cell(r_in, r_out, N, stat))

    out = pd.DataFrame(rows)
    out["scenario"] = out["p_levene"].apply(scenario_label)
    out_csv = out[["division", "season", "stat", "class", "n_in", "n_out",
                   "sd_in", "sd_out", "ratio", "p_levene", "p_bartlett",
                   "p_F", "scenario"]]
    out_csv.to_csv(OUT_DIR / f"ncaa_{DIV.lower()}_stan_3_cell.csv", index=False)

    proj_df = pd.concat(all_proj, ignore_index=True)
    proj_df.to_csv(OUT_DIR / f"ncaa_{DIV.lower()}_stan_per_player_projections.csv",
                    index=False)

    print()
    print("=" * 100)
    print(f"NCAA {DIV.upper()} STAN ROBUSTNESS — coupling matrix (PTS/REB/BLK x Center)")
    print("=" * 100)
    cols = ["season", "stat", "n_in", "n_out", "ratio",
            "p_levene", "p_bartlett", "p_F", "scenario"]
    print(out[cols].to_string(index=False))

    print(f"\n[save] {OUT_DIR / f'ncaa_{DIV.lower()}_stan_3_cell.csv'}")


if __name__ == "__main__":
    main()
