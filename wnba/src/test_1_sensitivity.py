"""WNBA Test 1 — three-way Center-cohort sensitivity matrix.

Reruns the 4-cell coupling test under three position-classifier rules to
neutralize the 'your bbref position labels were sloppy' reviewer objection:

  1. INCLUSIVE — any 'center' substring in bbref position -> Center
                  (matches NBA Test 1 protocol exactly)
  2. STRICT    — bbref position string is exactly 'Center'
                  (drops all hyphenated boundary cases)
  3. PRIMARY   — first hyphen-token is 'Center'
                  (Center-Forward -> Center; Forward-Center -> Forward)

All three rules are PRE-residual: classifier set without looking at the
residuals being tested. No cherry-picking risk.

Output: audit_runs/test_1_replication/wnba_sensitivity_3way.csv
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


def position_inclusive(p):
    if pd.isna(p) or not p or str(p).strip() == "":
        return "Forward"
    s = str(p).lower()
    if "center" in s: return "Center"
    if "guard" in s: return "Guard"
    return "Forward"


def position_strict(p):
    if pd.isna(p) or not p or str(p).strip() == "":
        return "Forward"
    s = str(p).strip().lower()
    if s == "center": return "Center"
    if s == "guard": return "Guard"
    return "Forward"


def position_primary(p):
    if pd.isna(p) or not p or str(p).strip() == "":
        return "Forward"
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
    try:
        _, p_lev = stats.levene(r_in, r_out, center="median")
    except Exception:
        p_lev = np.nan
    try:
        _, p_bart = stats.bartlett(r_in, r_out)
    except Exception:
        p_bart = np.nan
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


def main():
    games = pd.read_csv(DATA / "player_game_logs.csv")
    meta = pd.read_csv(DATA / "player_metadata.csv")

    if "season_type" in games.columns:
        games = games[games["season_type"] == "regular"].copy()
    for c in ["pts", "trb", "ast", "blk"]:
        games[c] = pd.to_numeric(games[c], errors="coerce")

    season_agg = games.groupby(["player_slug", "season"], as_index=False).agg(
        gp=("game_id", "count"),
        PTS=("pts", "mean"), REB=("trb", "mean"),
        AST=("ast", "mean"), BLK=("blk", "mean"),
    )
    season_agg = season_agg[season_agg["gp"] >= MIN_GAMES].copy()

    first_season = games.groupby("player_slug")["season"].min().to_dict()

    # Pre-compute pos_class per classifier
    for name, fn in CLASSIFIERS.items():
        meta[f"pos_{name}"] = meta["position"].apply(fn)
    pos_lookups = {
        name: dict(zip(meta["player_slug"], meta[f"pos_{name}"]))
        for name in CLASSIFIERS
    }

    # Cohort sizes per classifier
    print("=" * 100)
    print("CENTER COHORT SIZES per classifier × season")
    print("=" * 100)
    cur_all = season_agg[season_agg["season"].isin(TEST_SEASONS)].copy()
    for name, lookup in pos_lookups.items():
        cur_all[f"pos_{name}"] = cur_all["player_slug"].map(lookup).fillna("Forward")
    summary = (cur_all.groupby("season")
               .agg(n_total=("player_slug", "count"),
                    n_inclusive=("pos_inclusive", lambda s: (s == "Center").sum()),
                    n_strict=("pos_strict", lambda s: (s == "Center").sum()),
                    n_primary=("pos_primary", lambda s: (s == "Center").sum())))
    print(summary.to_string())
    print()

    rows = []
    for clf_name, lookup in pos_lookups.items():
        for N in TEST_SEASONS:
            prior = season_agg[season_agg["season"] < N].copy()
            cur = season_agg[season_agg["season"] == N].copy()

            proj = (prior.groupby("player_slug")[["PTS", "REB", "AST", "BLK"]]
                    .mean().reset_index())
            proj = proj.rename(columns={c: f"{c}_proj" for c in ["PTS", "REB", "AST", "BLK"]})
            cohort = prior[["PTS", "REB", "AST", "BLK"]].mean().to_dict()

            df = cur.merge(proj, on="player_slug", how="left")
            for stat in ["PTS", "REB", "AST", "BLK"]:
                df[f"{stat}_proj"] = df[f"{stat}_proj"].fillna(cohort[stat])
                df[f"{stat}_resid"] = df[stat] - df[f"{stat}_proj"]

            df["pos_class"] = df["player_slug"].map(lookup).fillna("Forward")
            df["first_season"] = df["player_slug"].map(first_season)
            df["years_pro"] = N - df["first_season"] + 1

            for stat in ["PTS", "REB", "BLK"]:
                in_mask = df["pos_class"] == "Center"
                r_in = df.loc[in_mask, f"{stat}_resid"].dropna().values
                r_out = df.loc[~in_mask, f"{stat}_resid"].dropna().values
                rows.append(run_cell(r_in, r_out, N, stat, "Center", clf_name))

            in_mask = df["years_pro"] >= VET_YEARS
            r_in = df.loc[in_mask, "AST_resid"].dropna().values
            r_out = df.loc[~in_mask, "AST_resid"].dropna().values
            rows.append(run_cell(r_in, r_out, N, "AST",
                                 f"vet_{VET_YEARS}+", clf_name))

    out = pd.DataFrame(rows)
    out["scenario"] = out["p_levene"].apply(scenario_label)

    out_csv = out[["classifier", "season", "stat", "class", "n_in", "n_out",
                   "sd_in", "sd_out", "ratio", "p_levene", "p_bartlett",
                   "p_F", "scenario"]]
    out_csv.to_csv(OUT_DIR / "wnba_sensitivity_3way.csv", index=False)

    print("=" * 100)
    print("WNBA TEST 1 — 4-cell × 3-classifier sensitivity matrix")
    print("=" * 100)
    for clf_name in CLASSIFIERS:
        print(f"\n--- classifier: {clf_name.upper()} ---")
        sub = out[out["classifier"] == clf_name]
        cols = ["season", "stat", "class", "n_in", "n_out",
                "ratio", "p_levene", "p_bartlett", "p_F", "scenario"]
        print(sub[cols].to_string(index=False))

    print()
    print("=" * 100)
    print("CROSS-CLASSIFIER SUMMARY — replication scenario verdict per cell")
    print("=" * 100)
    for clf_name in CLASSIFIERS:
        print(f"\n[{clf_name}]")
        sub = out[out["classifier"] == clf_name]
        for (stat, cls), cell in sub.groupby(["stat", "class"], sort=False):
            verdicts = cell["scenario"].tolist()
            n_couple = sum(1 for v in verdicts if "couples" in v)
            tag = "POSITION" if cls == "Center" else "CAREER-STAGE"
            print(f"  {stat:>4} x {cls:<10} [{tag}]: "
                  f"{n_couple}/3 couple -> {verdicts}")

    print(f"\n[save] {OUT_DIR / 'wnba_sensitivity_3way.csv'}")


if __name__ == "__main__":
    main()
