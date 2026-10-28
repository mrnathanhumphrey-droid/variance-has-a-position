# PRE-REGISTRATION — Giannis trade 26-27 forward win-total test

**frozen_as_of: 2026-06-25** (trade agreed 2026-06-22, executes 2026-07-06; 26-27 season unplayed)
**Status: LOCKED.** No artifact below may change after this date; validation is strictly against 26-27 actuals.

---

## 1. What this pre-registers

A **forward (preseason) prediction** of the win-total impact of the Antetokounmpo trade
(MIL ↔ MIA), produced by the roster-aware **Tier 1A** method *before* a single 26-27 game
is played. This is the cleanest possible forward test: the team-historical methods
(Tier 1B / SRS / lineup-def) **cannot see this trade** until 26-27 games accumulate, so the
preseason number is driven entirely by the player-aggregation layer + a 25-26 anchor.

## 2. The trade (frozen facts)

- **To MIA:** Giannis Antetokounmpo, Bobby Portis.
- **To MIL:** Tyler Herro, Kel'el Ware, Jaime Jaquez Jr., Kasparas Jakučionis,
  No. 13 pick (→ Nate Ament), 2031 + 2033 unprotected 1sts, 2030 swap, 2033 2nd.
- MIL also drafted Brayden Burries (No. 10).

## 3. Method (frozen)

`scripts/phase3_trade_win_swing_final.py` — anchored-delta on the existing Tier 1A pipeline:

- **Offense:** Σ_rotation( ship per-min PTS × allocated minutes(240) ) × 1.0591
  [`phase2_possession_aggregator_v1` Tier 1A; ship CSV = v6.1 LOCKED 25-26].
- **Defense:** `def_pts_impact = pct_plusminus × d_fga × 2.5 / gp` (25-26), minutes-weighted.
- **Anchor:** each team's ACTUAL 25-26 point differential; trade applied as a DELTA
  (cancels the ~+3 pt absolute-offense bias). `wins = 82·logistic(margin/12)`.
- 26-27 player rates: vets = ship per-min; rookies = rookie fit (`draft_2026_projections`).

## 4. Frozen predictions

| Team | 25-26 actual | Projected 26-27 (this trade only) | Win swing |
|---|---|---|---|
| **MIA** | +2.3 pg, ~43 W | margin +13.0 → **61 W** | **+18 W** |
| **MIL** | −6.2 pg, ~32 W | margin −14.0 → **20 W** | **−12 W** |

Baseline validates: model reproduces MIL at 32 W = their real 32-50 record.

**Honest precision statement:** the offense delta swaps per-minute scoring rates and therefore
**over-credits the incoming star** (usage redistribution not modeled), so the magnitudes are a
**soft ceiling**. Committed estimates:

- **Direction (high confidence):** MIA improves; MIL declines.
- **Magnitude (point estimate / defensible range):** MIA **+18 W [+10, +18]**; MIL **−12 W [−8, −12]**.
- **Absolute totals:** MIA **61 W [52, 61]**; MIL **20 W [20, 28]**.

## 5. Falsification triggers (pre-committed)

- **F1 (direction):** FAILS if MIA's 26-27 win% ≤ 25-26, or MIL's ≥ 25-26.
- **F2 (magnitude/MIA):** FLAGS over-statement if MIA finishes < 52 W (healthy-season, ≥70 GP availability).
- **F3 (magnitude/MIL):** FLAGS over-statement if MIL finishes > 30 W.
- **F4 (vs market):** record sign + magnitude error vs the 26-27 Vegas preseason line for both teams
  (historical anchor: MIA 44-48, MIL 51-54). Beating the line's directional move is the bar.
- Confounds logged, NOT excuses: major injuries (Giannis/Bam/Herro < 60 GP), further offseason
  moves to either roster, mid-season trades. If a confound fires, the test is annotated, not voided.

## 6. Blend forward-test (the method's OOS credential, locked 2026-06-25)

Walk-forward on 25-26 (true game dates), blending Tier 1A (roster) with Tier 1B (team-eff):

| Scheme | best single | **blend t1a+t1b** | lift |
|---|---|---|---|
| Static 60/40 (test n=471) | t1b 70.9% / RMSE 15.60 | **72.6% / 15.32** | +1.7 pp |
| Expanding-window WF (n=976) | t1b 65.9% / 15.28 | **66.4% / 15.12** | +0.5 pp |

Fitted weight on the roster layer is small but consistently positive (t1a ≈ 0.075). The roster
layer's value is **maximal preseason** (the only trade-aware input), which is exactly the regime
this pre-registration tests.

## 7. Validation procedure

After 26-27 (or at the All-Star break for an interim read): pull MIA/MIL actual records,
score F1-F4, compare projected vs actual margin, and compare to the 26-27 Vegas preseason line.
Publish with equal prominence whether confirmed or falsified.
