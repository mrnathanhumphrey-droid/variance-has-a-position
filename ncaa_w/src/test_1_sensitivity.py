"""NCAA D1 Women's Test 1 — 3-cell x 3-classifier sensitivity matrix.

Surgical replication of the cross-league asymmetry test on NCAA D1 women's,
sportsdataverse player_box parquets. Mirrors NCAA MBB script with division
constant flipped.

Output: audit_runs/test_1_replication/ncaa_wbb_3way_sensitivity.csv
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(r"D:/NCAA D1 Womens")
RAW = ROOT / "data" / "raw" / "sportsdataverse"
OUT_DIR = ROOT / "audit_runs" / "test_1_replication"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TEST_SEASONS = [2023, 2024, 2025]
MIN_GAMES = 10
DIVISION = "WBB"


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
    primary = str(p).split("/")[0].split("-")[0].strip().lower()
    if primary == "center": return "Center"
    if primary in {"guard", "point guard", "shooting guard"}: return "Guard"
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


def run_cell(r_in, r_out, season, stat, classifier):
    n_in, n_out = len(r_in), len(r_out)
    base = {"division": DIVISION, "classifier": classifier, "season": season,
            "stat": stat, "class": "Center", "n_in": n_in, "n_out": n_out}
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


def load_box():
    frames = []
    for season in [2023, 2024, 2025]:
        path = RAW / f"player_box_{season}.parquet"
        df = pd.read_parquet(path,
            columns=["game_id", "season", "season_type", "athlete_id",
                     "athlete_display_name", "athlete_position_name",
                     "minutes", "points", "rebounds", "assists", "blocks",
                     "did_not_play"])
        frames.append(df)
    games = pd.concat(frames, ignore_index=True)
    games = games[games["did_not_play"] == False].copy()
    games = games[games["minutes"].fillna(0) > 0].copy()
    games["athlete_id"] = games["athlete_id"].astype("Int64")
    return games


def main():
    print(f"[load] NCAA {DIVISION} player_box 2023-2025")
    games = load_box()
    print(f"  {len(games)} game-rows after DNP/0-min filter, "
          f"{games['athlete_id'].nunique()} unique athletes")

    pos_lookup = (games.groupby("athlete_id")["athlete_position_name"]
                  .agg(lambda s: s.dropna().mode().iloc[0]
                       if len(s.dropna()) and len(s.dropna().mode()) else None)
                  .to_dict())

    season_agg = games.groupby(["athlete_id", "season"], as_index=False).agg(
        gp=("game_id", "count"),
        PTS=("points", "mean"),
        REB=("rebounds", "mean"),
        AST=("assists", "mean"),
        BLK=("blocks", "mean"),
    )
    season_agg = season_agg[season_agg["gp"] >= MIN_GAMES].copy()

    cur_all = season_agg[season_agg["season"].isin(TEST_SEASONS)].copy()
    for clf_name, fn in CLASSIFIERS.items():
        cur_all[f"pos_{clf_name}"] = cur_all["athlete_id"].map(
            lambda x: fn(pos_lookup.get(x)))
    summary = (cur_all.groupby("season")
               .agg(n_total=("athlete_id", "count"),
                    n_inclusive=("pos_inclusive", lambda s: (s == "Center").sum()),
                    n_strict=("pos_strict", lambda s: (s == "Center").sum()),
                    n_primary=("pos_primary", lambda s: (s == "Center").sum())))
    print("\nCenter cohort sizes per classifier × season:")
    print(summary.to_string())

    rows = []
    for clf_name, fn in CLASSIFIERS.items():
        for N in TEST_SEASONS:
            prior = season_agg[season_agg["season"] < N].copy()
            cur = season_agg[season_agg["season"] == N].copy()
            proj = (prior.groupby("athlete_id")[["PTS", "REB", "BLK"]]
                    .mean().reset_index())
            proj = proj.rename(columns={c: f"{c}_proj" for c in ["PTS", "REB", "BLK"]})
            cohort = prior[["PTS", "REB", "BLK"]].mean().to_dict()
            df = cur.merge(proj, on="athlete_id", how="left")
            for stat in ["PTS", "REB", "BLK"]:
                df[f"{stat}_proj"] = df[f"{stat}_proj"].fillna(cohort[stat])
                df[f"{stat}_resid"] = df[stat] - df[f"{stat}_proj"]
            df["pos_class"] = df["athlete_id"].map(lambda x: fn(pos_lookup.get(x)))
            for stat in ["PTS", "REB", "BLK"]:
                in_mask = df["pos_class"] == "Center"
                r_in = df.loc[in_mask, f"{stat}_resid"].dropna().values
                r_out = df.loc[~in_mask, f"{stat}_resid"].dropna().values
                rows.append(run_cell(r_in, r_out, N, stat, clf_name))

    out = pd.DataFrame(rows)
    out["scenario"] = out["p_levene"].apply(scenario_label)
    out_csv = out[["division", "classifier", "season", "stat", "class",
                   "n_in", "n_out", "sd_in", "sd_out", "ratio",
                   "p_levene", "p_bartlett", "p_F", "scenario"]]
    out_csv.to_csv(OUT_DIR / f"ncaa_{DIVISION.lower()}_3way_sensitivity.csv", index=False)

    print()
    print("=" * 110)
    print(f"NCAA {DIVISION} TEST 1 — 3-cell x 3-classifier sensitivity matrix")
    print("=" * 110)
    for clf_name in CLASSIFIERS:
        print(f"\n--- classifier: {clf_name.upper()} ---")
        sub = out[out["classifier"] == clf_name]
        cols = ["season", "stat", "n_in", "n_out", "ratio",
                "p_levene", "p_bartlett", "p_F", "scenario"]
        print(sub[cols].to_string(index=False))

    print()
    print("=" * 110)
    print("CROSS-CLASSIFIER SUMMARY")
    print("=" * 110)
    for clf_name in CLASSIFIERS:
        print(f"\n[{clf_name}]")
        sub = out[out["classifier"] == clf_name]
        for stat, cell in sub.groupby("stat", sort=False):
            verdicts = cell["scenario"].tolist()
            n_couple = sum(1 for v in verdicts if "couples" in v)
            print(f"  {stat:>4} x Center: {n_couple}/3 couple -> {verdicts}")

    print(f"\n[save] {OUT_DIR / f'ncaa_{DIVISION.lower()}_3way_sensitivity.csv'}")


if __name__ == "__main__":
    main()
