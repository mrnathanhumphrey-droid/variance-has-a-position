"""WNBA Test 1 cross-season replication — 4-cell mean-variance coupling test.

Replicates the NBA 4-cell argument (PTS/REB/BLK x Center; AST x deep-vet)
on WNBA 2023/2024/2025 using basketball-reference data. No Stan, no levers —
surgical projection (career-mean over prior seasons) to keep the test focused
on whether the position-vs-career-stage asymmetry replicates cross-league.

Output: audit_runs/test_1_replication/wnba_4_cell_replication.csv
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(r"D:/WNBA Projections")
DATA = ROOT / "data" / "processed"
OUT_DIR = ROOT / "audit_runs" / "test_1_replication"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TEST_SEASONS = [2023, 2024, 2025]
MIN_GAMES = 15
VET_YEARS = 10


def position_class(p):
    if pd.isna(p) or not p or str(p).strip() == "":
        return "Forward"
    s = str(p).lower()
    if "center" in s:
        return "Center"
    if "guard" in s:
        return "Guard"
    return "Forward"


def f_test_two_sided(arr_in, arr_out):
    a = np.asarray(arr_in, dtype=float)
    b = np.asarray(arr_out, dtype=float)
    if len(a) < 2 or len(b) < 2:
        return np.nan
    var_a = a.var(ddof=1)
    var_b = b.var(ddof=1)
    if var_a == 0 or var_b == 0:
        return np.nan
    F = var_a / var_b
    cdf = stats.f.cdf(F, len(a) - 1, len(b) - 1)
    return 2 * min(cdf, 1 - cdf)


def run_cell(r_in, r_out, season, stat, class_label):
    n_in, n_out = len(r_in), len(r_out)
    base = {"season": season, "stat": stat, "class": class_label,
            "n_in": n_in, "n_out": n_out}
    if n_in < 5 or n_out < 5:
        base.update({"mean_in": np.nan, "mean_out": np.nan,
                     "sd_in": np.nan, "sd_out": np.nan, "ratio": np.nan,
                     "p_levene": np.nan, "p_bartlett": np.nan, "p_F": np.nan})
        return base
    sd_in = float(r_in.std(ddof=1))
    sd_out = float(r_out.std(ddof=1))
    ratio = sd_in / sd_out if sd_out > 0 else np.nan
    try:
        _, p_lev = stats.levene(r_in, r_out, center="median")
    except Exception:
        p_lev = np.nan
    try:
        _, p_bart = stats.bartlett(r_in, r_out)
    except Exception:
        p_bart = np.nan
    base.update({
        "mean_in": float(r_in.mean()), "mean_out": float(r_out.mean()),
        "sd_in": sd_in, "sd_out": sd_out, "ratio": float(ratio),
        "p_levene": float(p_lev), "p_bartlett": float(p_bart),
        "p_F": float(f_test_two_sided(r_in, r_out)),
    })
    return base


def scenario_label(p_levene):
    if pd.isna(p_levene):
        return "n/a"
    if p_levene < 0.001:
        return "couples (p<0.001)"
    if p_levene < 0.05:
        return "couples (p<0.05)"
    if p_levene < 0.10:
        return "directional (p<0.10)"
    return "null"


def main():
    print("[load] WNBA player_game_logs + player_metadata")
    games = pd.read_csv(DATA / "player_game_logs.csv")
    meta = pd.read_csv(DATA / "player_metadata.csv")

    if "season_type" in games.columns:
        games = games[games["season_type"] == "regular"].copy()

    for c in ["pts", "trb", "ast", "blk"]:
        games[c] = pd.to_numeric(games[c], errors="coerce")

    season_agg = games.groupby(["player_slug", "season"], as_index=False).agg(
        gp=("game_id", "count"),
        PTS=("pts", "mean"),
        REB=("trb", "mean"),
        AST=("ast", "mean"),
        BLK=("blk", "mean"),
    )
    season_agg = season_agg[season_agg["gp"] >= MIN_GAMES].copy()

    meta["pos_class"] = meta["position"].apply(position_class)
    pos_lookup = dict(zip(meta["player_slug"], meta["pos_class"]))

    first_season = games.groupby("player_slug")["season"].min().to_dict()

    print(f"[load] {len(games)} regular-season game rows, "
          f"{season_agg['player_slug'].nunique()} unique players with >={MIN_GAMES} GP seasons")
    print(f"[load] position breakdown across all seasons: "
          f"{pd.Series(list(pos_lookup.values())).value_counts().to_dict()}")
    print()

    rows = []
    for N in TEST_SEASONS:
        prior = season_agg[season_agg["season"] < N].copy()
        cur = season_agg[season_agg["season"] == N].copy()

        proj = prior.groupby("player_slug")[["PTS", "REB", "AST", "BLK"]].mean().reset_index()
        proj = proj.rename(columns={c: f"{c}_proj" for c in ["PTS", "REB", "AST", "BLK"]})

        cohort = prior[["PTS", "REB", "AST", "BLK"]].mean().to_dict()

        df = cur.merge(proj, on="player_slug", how="left", indicator="_prior_match")
        n_newcomers = (df["_prior_match"] == "left_only").sum()
        df = df.drop(columns="_prior_match")
        for stat in ["PTS", "REB", "AST", "BLK"]:
            df[f"{stat}_proj"] = df[f"{stat}_proj"].fillna(cohort[stat])
            df[f"{stat}_resid"] = df[stat] - df[f"{stat}_proj"]

        df["pos_class"] = df["player_slug"].map(pos_lookup).fillna("Forward")
        df["first_season"] = df["player_slug"].map(first_season)
        df["years_pro"] = N - df["first_season"] + 1

        n_center = (df["pos_class"] == "Center").sum()
        n_vet = (df["years_pro"] >= VET_YEARS).sum()
        print(f"[season {N}] n_players={len(df)}, n_Center={n_center}, "
              f"n_vet({VET_YEARS}+)={n_vet}, n_newcomers={n_newcomers}")

        for stat in ["PTS", "REB", "BLK"]:
            in_mask = df["pos_class"] == "Center"
            r_in = df.loc[in_mask, f"{stat}_resid"].dropna().values
            r_out = df.loc[~in_mask, f"{stat}_resid"].dropna().values
            rows.append(run_cell(r_in, r_out, N, stat, "Center"))

        in_mask = df["years_pro"] >= VET_YEARS
        r_in = df.loc[in_mask, "AST_resid"].dropna().values
        r_out = df.loc[~in_mask, "AST_resid"].dropna().values
        rows.append(run_cell(r_in, r_out, N, "AST", f"vet_{VET_YEARS}+"))

    out = pd.DataFrame(rows)
    out["scenario"] = out["p_levene"].apply(scenario_label)
    out = out[["season", "stat", "class", "n_in", "n_out",
               "mean_in", "mean_out", "sd_in", "sd_out", "ratio",
               "p_levene", "p_bartlett", "p_F", "scenario"]]

    print()
    print("=" * 110)
    print("WNBA TEST 1 — 4-cell cross-season replication (2023/2024/2025)")
    print("=" * 110)
    print(out.to_string(index=False))

    out.to_csv(OUT_DIR / "wnba_4_cell_replication.csv", index=False)
    print(f"\n[save] {OUT_DIR / 'wnba_4_cell_replication.csv'}")

    print()
    print("=" * 110)
    print("CROSS-SEASON SUMMARY — replication scenario per cell")
    print("=" * 110)
    for (stat, cls), sub in out.groupby(["stat", "class"], sort=False):
        verdicts = sub["scenario"].tolist()
        n_couple = sum(1 for v in verdicts if "couples" in v)
        tag = "POSITION" if cls == "Center" else "CAREER-STAGE"
        print(f"  {stat:>4} x {cls:<10} [{tag}]: {n_couple}/3 seasons couple -> {verdicts}")

    print()
    print("Pre-registered NBA pattern (for comparison):")
    print("  PTS x Center      [POSITION]:     C  (directional, not significant)")
    print("  REB x Center      [POSITION]:     B  (2 of 3 seasons couple)")
    print("  BLK x Center      [POSITION]:     B  (2 of 3 seasons couple)")
    print("  AST x vet_13+     [CAREER-STAGE]: A  (clean null all 3 seasons)")
    print("Asymmetry hypothesis: position cells couple, career-stage cells do not.")


if __name__ == "__main__":
    main()
