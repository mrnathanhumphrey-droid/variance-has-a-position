# Sloan Adjudicated Test 1 — WNBA Results (surgical arm)

Pre-reg SHA: 28e3dc7
Adjudication artifact: wnba_position_adjudication_v10.json

## Per-cell variance ratios

|   sd_in |   sd_out |   ratio |   ci95_lo |   ci95_hi |   p_levene |   p_bartlett |    p_F |   n_in |   n_out |   season | observable   | arm         | method   | disposition          |
|--------:|---------:|--------:|----------:|----------:|-----------:|-------------:|-------:|-------:|--------:|---------:|:-------------|:------------|:---------|:---------------------|
|  0.9625 |   0.5775 |  1.6668 |    1.3707 |    1.981  |     0      |       0      | 0      |     26 |     115 |     2023 | BLK          | metadata    | surgical | (control)            |
|  1.0041 |   0.5844 |  1.7184 |    1.4152 |    2.0422 |     0      |       0      | 0      |     20 |     121 |     2023 | BLK          | adjudicated | surgical | PERSISTS             |
|  4.7005 |   5.2379 |  0.8974 |    0.7428 |    1.0468 |     0.0006 |       0.0001 | 0.0001 |     26 |     115 |     2023 | PTS          | metadata    | surgical | (control)            |
|  4.9332 |   5.1805 |  0.9523 |    0.786  |    1.1104 |     0.1201 |       0.09   | 0.0925 |     20 |     121 |     2023 | PTS          | adjudicated | surgical | DIRECTIONAL-PERSISTS |
|  2.8447 |   2.1096 |  1.3484 |    1.1975 |    1.5265 |     0      |       0      | 0      |     26 |     115 |     2023 | REB          | metadata    | surgical | (control)            |
|  2.8723 |   2.1355 |  1.345  |    1.1675 |    1.5184 |     0      |       0      | 0      |     20 |     121 |     2023 | REB          | adjudicated | surgical | WALK-BACK FALSIFIED  |
|  0.9973 |   0.6134 |  1.626  |    1.3127 |    1.9625 |     0      |       0      | 0      |     25 |     117 |     2024 | BLK          | metadata    | surgical | (control)            |
|  1.0302 |   0.6127 |  1.6814 |    1.3513 |    2.0082 |     0      |       0      | 0      |     22 |     120 |     2024 | BLK          | adjudicated | surgical | PERSISTS             |
|  4.5986 |   5.1652 |  0.8903 |    0.7732 |    1.0062 |     0      |       0      | 0      |     25 |     117 |     2024 | PTS          | metadata    | surgical | (control)            |
|  4.7552 |   5.1273 |  0.9274 |    0.8082 |    1.049  |     0.01   |       0.0074 | 0.0076 |     22 |     120 |     2024 | PTS          | adjudicated | surgical | DIRECTIONAL-PERSISTS |
|  2.8476 |   2.107  |  1.3514 |    1.1899 |    1.5223 |     0      |       0      | 0      |     25 |     117 |     2024 | REB          | metadata    | surgical | (control)            |
|  2.932  |   2.1017 |  1.3951 |    1.225  |    1.5788 |     0      |       0      | 0      |     22 |     120 |     2024 | REB          | adjudicated | surgical | WALK-BACK FALSIFIED  |
|  0.9302 |   0.5972 |  1.5576 |    1.3296 |    1.793  |     0      |       0      | 0      |     31 |     130 |     2025 | BLK          | metadata    | surgical | (control)            |
|  0.9759 |   0.5943 |  1.642  |    1.4147 |    1.8755 |     0      |       0      | 0      |     27 |     134 |     2025 | BLK          | adjudicated | surgical | PERSISTS             |
|  4.8358 |   5.2028 |  0.9295 |    0.7967 |    1.0665 |     0.0013 |       0.0028 | 0.0029 |     31 |     130 |     2025 | PTS          | metadata    | surgical | (control)            |
|  5.0387 |   5.1562 |  0.9772 |    0.8229 |    1.1208 |     0.2773 |       0.3656 | 0.3717 |     27 |     134 |     2025 | PTS          | adjudicated | surgical | DIRECTIONAL-PERSISTS |
|  2.7908 |   2.1273 |  1.3118 |    1.1655 |    1.4659 |     0      |       0      | 0      |     31 |     130 |     2025 | REB          | metadata    | surgical | (control)            |
|  2.8937 |   2.121  |  1.3643 |    1.2112 |    1.5073 |     0      |       0      | 0      |     27 |     134 |     2025 | REB          | adjudicated | surgical | WALK-BACK FALSIFIED  |

## n_in lift table

|   season | observable   |   n_in_meta_players |   n_in_adj_players |   lift_player | power_gate_pass   |
|---------:|:-------------|--------------------:|-------------------:|--------------:|:------------------|
|     2023 | BLK          |                  26 |                 20 |        0.7692 | False             |
|     2023 | PTS          |                  26 |                 20 |        0.7692 | False             |
|     2023 | REB          |                  26 |                 20 |        0.7692 | False             |
|     2024 | BLK          |                  25 |                 22 |        0.88   | False             |
|     2024 | PTS          |                  25 |                 22 |        0.88   | False             |
|     2024 | REB          |                  25 |                 22 |        0.88   | False             |
|     2025 | BLK          |                  31 |                 27 |        0.871  | False             |
|     2025 | PTS          |                  31 |                 27 |        0.871  | False             |
|     2025 | REB          |                  31 |                 27 |        0.871  | False             |

## Aggregate dispositions (adjudicated, surgical)

- **BLK**: ['PERSISTS', 'PERSISTS', 'PERSISTS']
- **PTS**: ['DIRECTIONAL-PERSISTS', 'DIRECTIONAL-PERSISTS', 'DIRECTIONAL-PERSISTS']
- **REB**: ['WALK-BACK FALSIFIED', 'WALK-BACK FALSIFIED', 'WALK-BACK FALSIFIED']

*Stan arm analysis pending Stan posterior file integration.*
