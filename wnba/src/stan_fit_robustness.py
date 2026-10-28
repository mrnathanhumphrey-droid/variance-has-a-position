"""WNBA Stan robustness fit for Test 1 cross-league replication.

Fits the hierarchical NB2 single-stat skill model on prior-season WNBA data
and projects the test season per-player rate. Runs for stat in {PTS, REB, BLK}
and test season in {2023, 2024, 2025}, then computes per-player residuals
and re-runs the 4-cell coupling test under the three position classifiers.

The output answers the robustness question for paper Section 5.6:
'does the BLK x Center coupling result hold under a Stan posterior projection
instead of career-mean?'

Output: audit_runs/stan_robustness/wnba_stan_4_cell.csv
"""
from __future__ import annotations
import os
import sys
sys.stdout.reconfigure(encoding="utf-8")

RTOOLS = r"C:\Users\Nate\.cmdstan\RTools40"
os.environ["PATH"] = (
    f"{RTOOLS}\\usr\\bin;{RTOOLS}\\mingw64\\bin;" + os.environ.get("PATH", "")
)

import time
from pathlib import Path

import numpy as np
import pandas as pd
from cmdstanpy import CmdStanModel
from scipy import stats

ROOT = Path(r"D:/WNBA Projections")
DATA = ROOT / "data" / "processed"
MODEL = ROOT / "models" / "stan" / "hierarchical_one_stat_wnba.stan"
OUT_DIR = ROOT / "audit_runs" / "stan_robustness"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TEST_SEASONS = [2023, 2024, 2025]
STATS = ["PTS", "REB", "BLK"]
STAT_TO_COL = {"PTS": "pts", "REB": "trb", "BLK": "blk"}
PRIOR_MU = {"PTS": (-0.9, 0.7), "REB": (-1.9, 0.7), "BLK": (-3.9, 1.0)}
MIN_GAMES_TEST = 15
MIN_GAMES_TRAIN = 5
VET_YEARS = 10
N_CHAINS = 4
N_WARMUP = 300
N_SAMPLING = 300


def position_inclusive(p):
    if pd.isna(p) or not p or str(p).strip() == "": return "Forward"
    s = str(p).lower()
    if "center" in s: return "Center"
    if "guard" in s: return "Guard"
    return "Forward"


def position_strict(p):
    if pd.isna(p) or not p or str(p).strip() == "": return "Forward"
    s = str(p).strip().lower()
    if s == "center": return "Center"
    if s == "guard": return "Guard"
    return "Forward"


def position_primary(p):
    if pd.isna(p) or not p or str(p).strip() == "": return "Forward"
    primary = str(p).split("-")[0].strip().lower()
    if primary == "center": return "Center"
    if primary == "guard": return "Guard"
    return "Forward"


CLASSIFIERS = {
    "inclusive": position_inclusive,
    "strict": position_strict,
    "primary": position_primary,
}


def f_test_two_sided(arr_in, arr_out):
    a = np.asarray(arr_in, dtype=float)
    b = np.asarray(arr_out, dtype=float)
    if len(a) < 2 or len(b) < 2: return np.nan
    var_a, var_b = a.var(ddof=1), b.var(ddof=1)
    if var_a == 0 or var_b == 0: return np.nan
    F = var_a / var_b
    cdf = stats.f.cdf(F, len(a) - 1, len(b) - 1)
    return 2 * min(cdf, 1 - cdf)


def run_cell(r_in, r_out, season, stat, class_label, classifier):
    n_in, n_out = len(r_in), len(r_out)
    base = {"classifier": classifier, "season": season, "stat": stat,
            "class": class_label, "n_in": n_in, "n_out": n_out}
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


def build_train_test(games, meta, test_season, stat_col):
    train_games = games[games["season"] < test_season].copy()
    test_games = games[games["season"] == test_season].copy()

    train_gp = train_games.groupby("player_slug")["game_id"].count()
    eligible_train = train_gp[train_gp >= MIN_GAMES_TRAIN].index
    train_games = train_games[train_games["player_slug"].isin(eligible_train)].copy()

    test_gp = test_games.groupby("player_slug")["game_id"].count()
    eligible_test = test_gp[test_gp >= MIN_GAMES_TEST].index
    test_games = test_games[test_games["player_slug"].isin(eligible_test)].copy()

    cohort_slugs = sorted(set(train_games["player_slug"]) | set(test_games["player_slug"]))
    slug_to_idx = {s: i + 1 for i, s in enumerate(cohort_slugs)}
    train_games["player_idx"] = train_games["player_slug"].map(slug_to_idx)
    test_games["player_idx"] = test_games["player_slug"].map(slug_to_idx)

    pos_inclusive = dict(zip(meta["player_slug"],
                              meta["position"].apply(position_inclusive)))
    pos_class_per_player = {s: pos_inclusive.get(s, "Forward") for s in cohort_slugs}
    pos_to_idx = {"Guard": 1, "Forward": 2, "Center": 3}
    player_position = np.array([pos_to_idx[pos_class_per_player[s]]
                                  for s in cohort_slugs], dtype=int)

    train_games["counts"] = pd.to_numeric(train_games[stat_col], errors="coerce")
    train_games = train_games[train_games["counts"].notna()].copy()
    train_games["counts"] = train_games["counts"].astype(int)
    train_games = train_games[train_games["minutes"] > 0].copy()

    return train_games, test_games, slug_to_idx, player_position, cohort_slugs


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
        data=data,
        chains=N_CHAINS,
        parallel_chains=N_CHAINS,
        iter_warmup=N_WARMUP,
        iter_sampling=N_SAMPLING,
        seed=12345,
        show_progress=False,
        show_console=False,
    )
    return fit


def project_test(fit, test_games, slug_to_idx, n_players):
    rate_per_36 = fit.stan_variable("rate_per_36").mean(axis=0)
    rate_per_min = rate_per_36 / 36.0
    test_games["rate_per_min"] = test_games["player_idx"].astype(int).map(
        lambda i: rate_per_min[i - 1] if 1 <= i <= n_players else np.nan)
    test_games["proj_count"] = test_games["rate_per_min"] * test_games["minutes"]

    proj = (test_games.groupby("player_slug")
            .agg(proj_total=("proj_count", "sum"),
                  actual_total=("counts", "sum"),
                  gp=("game_id", "count"))
            .reset_index())
    proj["proj_per_game"] = proj["proj_total"] / proj["gp"]
    proj["actual_per_game"] = proj["actual_total"] / proj["gp"]
    proj["resid"] = proj["actual_per_game"] - proj["proj_per_game"]
    return proj


def main():
    print("[load] WNBA player_game_logs + player_metadata")
    games = pd.read_csv(DATA / "player_game_logs.csv")
    meta = pd.read_csv(DATA / "player_metadata.csv")

    if "season_type" in games.columns:
        games = games[games["season_type"] == "regular"].copy()
    games["minutes"] = pd.to_numeric(games["mp_minutes"], errors="coerce")
    games = games[games["minutes"] > 0].copy()
    for c in ["pts", "trb", "blk"]:
        games[c] = pd.to_numeric(games[c], errors="coerce").fillna(0)

    first_season = games.groupby("player_slug")["season"].min().to_dict()

    print(f"[compile] Stan model: {MODEL}")
    t0 = time.time()
    model = CmdStanModel(stan_file=str(MODEL))
    print(f"[compile] {time.time() - t0:.1f}s")

    rows = []
    all_proj = []
    for stat in STATS:
        stat_col = STAT_TO_COL[stat]
        for N in TEST_SEASONS:
            print(f"\n=== fit {stat} test_season {N} ===")
            train_games, test_games, slug_to_idx, player_position, cohort_slugs = \
                build_train_test(games, meta, N, stat_col)
            test_games["counts"] = pd.to_numeric(test_games[stat_col], errors="coerce").fillna(0).astype(int)

            print(f"  train: {len(train_games)} game-rows, "
                  f"{len(cohort_slugs)} unique players")
            print(f"  test:  {test_games['player_slug'].nunique()} test players "
                  f">= {MIN_GAMES_TEST} GP")

            t0 = time.time()
            fit = fit_one(model, train_games, player_position,
                           n_players=len(cohort_slugs),
                           prior_mu_pair=PRIOR_MU[stat])
            print(f"  fit: {time.time() - t0:.1f}s")

            proj = project_test(fit, test_games, slug_to_idx, len(cohort_slugs))
            proj["season"] = N
            proj["stat"] = stat
            all_proj.append(proj)

            pos = meta.set_index("player_slug")["position"].to_dict()
            for clf_name, fn in CLASSIFIERS.items():
                proj["pos_class"] = proj["player_slug"].map(
                    lambda s: fn(pos.get(s)))
                in_mask = proj["pos_class"] == "Center"
                r_in = proj.loc[in_mask, "resid"].dropna().values
                r_out = proj.loc[~in_mask, "resid"].dropna().values
                rows.append(run_cell(r_in, r_out, N, stat, "Center", clf_name))

    out = pd.DataFrame(rows)
    out["scenario"] = out["p_levene"].apply(scenario_label)
    out_csv = out[["classifier", "season", "stat", "class", "n_in", "n_out",
                   "sd_in", "sd_out", "ratio", "p_levene", "p_bartlett",
                   "p_F", "scenario"]]
    out_csv.to_csv(OUT_DIR / "wnba_stan_4_cell.csv", index=False)

    proj_df = pd.concat(all_proj, ignore_index=True)
    proj_df.to_csv(OUT_DIR / "wnba_stan_per_player_projections.csv", index=False)

    print()
    print("=" * 100)
    print("WNBA STAN ROBUSTNESS — coupling matrix (PTS/REB/BLK only; AST not fit)")
    print("=" * 100)
    for clf_name in CLASSIFIERS:
        print(f"\n[{clf_name}]")
        sub = out[out["classifier"] == clf_name]
        for (stat, cls), cell in sub.groupby(["stat", "class"], sort=False):
            verdicts = cell["scenario"].tolist()
            n_couple = sum(1 for v in verdicts if "couples" in v)
            print(f"  {stat:>4} x {cls:<10}: {n_couple}/3 couple -> {verdicts}")

    print(f"\n[save] {OUT_DIR / 'wnba_stan_4_cell.csv'}")
    print(f"[save] {OUT_DIR / 'wnba_stan_per_player_projections.csv'}")


if __name__ == "__main__":
    main()
