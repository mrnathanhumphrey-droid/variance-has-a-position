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
