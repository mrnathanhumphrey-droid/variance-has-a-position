# Variance Has a Position
### A League-Wide Signal in Box-Score Projection Error

**Author:** Nathan Humphrey (Independent Researcher; Annapolis, MD) · ORCID [0009-0004-8512-4105](https://orcid.org/0009-0004-8512-4105)

Reproducibility bundle for the paper / abstract submission.

## Abstract

Every projection system is evaluated on how close its forecasts land — the mean error. We show that the *variance* of that error carries a structured, position-specific signal that the mean does not, and that the signal replicates across leagues and methods in a way that rules out the usual artifact explanations. After conditioning on prior-season production, position, age, and team context, the projection-error variance of blocks for centers is elevated by a factor of 1.26 to 2.03 relative to the rest of the league, and it couples in all 11 testable cells across four leagues (NBA, WNBA, NCAA Division I men's and women's) under two projection methods that share no machinery. The signal is selective: center scoring runs the opposite way (centers are more predictable scorers), veteran assists show no structure, and a center-rebounding effect that appeared under the simple method dissolves under the hierarchical one — a retraction reported at equal prominence. We pre-register a forward test on the 2026-27 season.

## Contents

| File | Description |
|---|---|
| `main.tex` | Full paper source (LaTeX) |
| `references.bib` | Bibliography (author-date / apalike) |
| `figures/fig1_cross_league_forest.png` | Cross-league forest plot |
| `figures/fig2_four_verdicts.png` | Four stat-and-position cells, four verdicts |

## Build

```bash
pdflatex main
bibtex   main
pdflatex main
pdflatex main
```

Produces `main.pdf`. Requires a standard TeX distribution (TeX Live / MiKTeX) with `natbib`, `authblk`, `booktabs`, `rotating`, and `placeins`.

## Reproducing the results

Every number in the paper comes from the scripts and artifacts below. Each league folder mirrors its original
project layout, so relative paths in the scripts resolve from that folder's root (`nba/` = the NBA project, `wnba/`,
`ncaa_m/`, `ncaa_w/` likewise). A few scripts carry absolute `D:/...` paths from the original machine: map
`D:/NBA Projections` -> `nba/`, `D:/WNBA Projections` -> `wnba/`, `D:/NCAA D1 Mens` -> `ncaa_m/`,
`D:/NCAA D1 Womens` -> `ncaa_w/`.

| Paper result | Script | Artifacts (outputs) |
|---|---|---|
| NBA BLK x Center, hierarchical (Stan) cells, 2023-24 / 2024-25 / 2025-26 (Table 2) | `nba/scripts/test_1_blk_center_cross_season.py` | `nba/audit_runs/test_1_blk_center/blk_center_cross_season.csv` |
| NBA career-mean cells; BLK / PTS / REB x Center, metadata + adjudicated arms | `nba/RMD_SRC_PIPELINE/src/sloan_adjudicated_test_1.py` | `nba/RMD_SRC_PIPELINE/results/sloan_adjudicated/` |
| WNBA career-mean | `wnba/src/test_1_replication.py` | `wnba/audit_runs/test_1_replication/wnba_4_cell_replication.csv` |
| WNBA / NCAA M / NCAA W hierarchical (Stan) | `*/src/stan_fit_robustness.py` (model: `wnba/models/stan/hierarchical_one_stat_wnba.stan`) | `*/audit_runs/stan_robustness/*_cell.csv` |
| NCAA M + W career-mean | `ncaa_m/src/test_1_sensitivity.py` | `ncaa_*/audit_runs/test_1_replication/ncaa_*_3way_sensitivity.csv` |
| Cross-league adjudicated analysis (WNBA, NCAA M, NCAA W) | `nba/RMD_SRC_PIPELINE/src/sloan_cross_league_analysis.py {WNBA\|NCAA_M\|NCAA_W}` | `*/audit_runs/test_1_replication/sloan_adjudicated/` |
| Veteran AST null, multi-season replication, Probe B, garbage/clutch nulls | `nba/paper_draft/test_scripts/` | `nba/paper_draft/cross_league_validation/` |
| Pre-registrations (incl. the 2026-27 forward test) | — | `nba/paper_draft/pre_registrations/` |

**Residual tables.** The per-player projections and residuals behind every cell are included:
`nba/audit_runs/**/per_player_projections*.csv` (NBA, both methods) and
`*/audit_runs/stan_robustness/*_per_player_projections.csv` (WNBA, NCAA M, NCAA W, hierarchical).

**Raw data is not redistributed.** Box scores and game logs (NBA, WNBA, NCAA D1) are public; the scripts read them
from `data/` paths in each league folder (`historical_box_scores.parquet`, `player_game_logs.csv`,
`player_box_{season}.parquet`). Pull them from the public league sources to re-run from scratch; the residual tables
above let you check every statistic without them.

Figures were drawn separately in matplotlib; figure scripts will be added with the final version of the paper.
