# Sloan Adjudicated Test 1 — NCAA_W Results (surgical arm)

Pre-reg SHA: 28e3dc7
Adjudication artifact: ncaa_w_position_adjudication_v10.json

## Per-cell variance ratios

|   sd_in |   sd_out |   ratio |   ci95_lo |   ci95_hi |   p_levene |   p_bartlett |    p_F |   n_in |   n_out |   season | observable   | arm         | method   | disposition          |
|--------:|---------:|--------:|----------:|----------:|-----------:|-------------:|-------:|-------:|--------:|---------:|:-------------|:------------|:---------|:---------------------|
|  1.1381 |   0.6207 |  1.8336 |    1.6279 |    2.0454 |     0      |       0      | 0      |     62 |    1470 |     2024 | BLK          | metadata    | surgical | (control)            |
|  1.2093 |   0.6039 |  2.0024 |    1.8292 |    2.1702 |     0      |       0      | 0      |     79 |    1453 |     2024 | BLK          | adjudicated | surgical | PERSISTS             |
|  4.6327 |   4.9519 |  0.9355 |    0.8767 |    0.9951 |     0      |       0.0001 | 0.0001 |     62 |    1470 |     2024 | PTS          | metadata    | surgical | (control)            |
|  4.6732 |   4.9536 |  0.9434 |    0.8923 |    0.9994 |     0.0001 |       0.0001 | 0.0001 |     79 |    1453 |     2024 | PTS          | adjudicated | surgical | DIRECTIONAL-PERSISTS |
|  3.009  |   2.3059 |  1.3049 |    1.2227 |    1.388  |     0      |       0      | 0      |     62 |    1470 |     2024 | REB          | metadata    | surgical | (control)            |
|  3.0545 |   2.2925 |  1.3324 |    1.2602 |    1.4053 |     0      |       0      | 0      |     79 |    1453 |     2024 | REB          | adjudicated | surgical | WALK-BACK FALSIFIED  |
|  1.0827 |   0.6314 |  1.7147 |    1.5127 |    1.945  |     0      |       0      | 0      |     57 |    1520 |     2025 | BLK          | metadata    | surgical | (control)            |
|  1.1468 |   0.6167 |  1.8597 |    1.6897 |    2.0389 |     0      |       0      | 0      |     77 |    1500 |     2025 | BLK          | adjudicated | surgical | PERSISTS             |
|  4.7286 |   4.9981 |  0.9461 |    0.8768 |    1.0098 |     0.0085 |       0.0018 | 0.0019 |     57 |    1520 |     2025 | PTS          | metadata    | surgical | (control)            |
|  4.7903 |   4.9988 |  0.9583 |    0.9025 |    1.0158 |     0.0094 |       0.0049 | 0.0051 |     77 |    1500 |     2025 | PTS          | adjudicated | surgical | DIRECTIONAL-PERSISTS |
|  2.8943 |   2.2845 |  1.2669 |    1.1969 |    1.3491 |     0      |       0      | 0      |     57 |    1520 |     2025 | REB          | metadata    | surgical | (control)            |
|  3.0012 |   2.2674 |  1.3236 |    1.2494 |    1.4023 |     0      |       0      | 0      |     77 |    1500 |     2025 | REB          | adjudicated | surgical | WALK-BACK FALSIFIED  |

## n_in lift table

|   season | observable   |   n_in_meta_players |   n_in_adj_players |   lift_player | power_gate_pass   |
|---------:|:-------------|--------------------:|-------------------:|--------------:|:------------------|
|     2024 | BLK          |                 250 |                312 |        1.248  | True              |
|     2024 | PTS          |                 250 |                312 |        1.248  | True              |
|     2024 | REB          |                 250 |                312 |        1.248  | True              |
|     2025 | BLK          |                 265 |                315 |        1.1887 | True              |
|     2025 | PTS          |                 265 |                315 |        1.1887 | True              |
|     2025 | REB          |                 265 |                315 |        1.1887 | True              |

## Aggregate dispositions (adjudicated, surgical)

- **BLK**: ['PERSISTS', 'PERSISTS']
- **PTS**: ['DIRECTIONAL-PERSISTS', 'DIRECTIONAL-PERSISTS']
- **REB**: ['WALK-BACK FALSIFIED', 'WALK-BACK FALSIFIED']

*Stan arm analysis pending Stan posterior file integration.*
