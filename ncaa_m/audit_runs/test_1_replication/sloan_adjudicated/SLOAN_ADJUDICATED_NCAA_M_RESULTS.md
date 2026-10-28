# Sloan Adjudicated Test 1 — NCAA_M Results (surgical arm)

Pre-reg SHA: 28e3dc7
Adjudication artifact: ncaa_m_position_adjudication_v10.json

## Per-cell variance ratios

|   sd_in |   sd_out |   ratio |   ci95_lo |   ci95_hi |   p_levene |   p_bartlett |   p_F |   n_in |   n_out |   season | observable   | arm         | method   | disposition          |
|--------:|---------:|--------:|----------:|----------:|-----------:|-------------:|------:|-------:|--------:|---------:|:-------------|:------------|:---------|:---------------------|
|  1.1536 |   0.6602 |  1.7475 |    1.5605 |    1.9327 |          0 |            0 |     0 |     54 |    1376 |     2024 | BLK          | metadata    | surgical | (control)            |
|  1.1445 |   0.6401 |  1.7878 |    1.6601 |    1.9264 |          0 |            0 |     0 |     94 |    1336 |     2024 | BLK          | adjudicated | surgical | PERSISTS             |
|  4.4583 |   5.2321 |  0.8521 |    0.7775 |    0.9214 |          0 |            0 |     0 |     54 |    1376 |     2024 | PTS          | metadata    | surgical | (control)            |
|  4.5376 |   5.2492 |  0.8644 |    0.8216 |    0.9115 |          0 |            0 |     0 |     94 |    1336 |     2024 | PTS          | adjudicated | surgical | DIRECTIONAL-PERSISTS |
|  2.7607 |   2.2762 |  1.2129 |    1.1299 |    1.2928 |          0 |            0 |     0 |     54 |    1376 |     2024 | REB          | metadata    | surgical | (control)            |
|  2.8527 |   2.2514 |  1.2671 |    1.2078 |    1.3314 |          0 |            0 |     0 |     94 |    1336 |     2024 | REB          | adjudicated | surgical | WALK-BACK FALSIFIED  |
|  1.0746 |   0.6453 |  1.6652 |    1.4889 |    1.8523 |          0 |            0 |     0 |     52 |    1365 |     2025 | BLK          | metadata    | surgical | (control)            |
|  1.1255 |   0.6271 |  1.7947 |    1.6671 |    1.9181 |          0 |            0 |     0 |     81 |    1336 |     2025 | BLK          | adjudicated | surgical | PERSISTS             |
|  4.447  |   5.3444 |  0.8321 |    0.7712 |    0.8885 |          0 |            0 |     0 |     52 |    1365 |     2025 | PTS          | metadata    | surgical | (control)            |
|  4.4783 |   5.3608 |  0.8354 |    0.7847 |    0.8831 |          0 |            0 |     0 |     81 |    1336 |     2025 | PTS          | adjudicated | surgical | DIRECTIONAL-PERSISTS |
|  2.8183 |   2.2705 |  1.2413 |    1.1457 |    1.3287 |          0 |            0 |     0 |     52 |    1365 |     2025 | REB          | metadata    | surgical | (control)            |
|  2.8355 |   2.2556 |  1.2571 |    1.1897 |    1.3168 |          0 |            0 |     0 |     81 |    1336 |     2025 | REB          | adjudicated | surgical | WALK-BACK FALSIFIED  |

## n_in lift table

|   season | observable   |   n_in_meta_players |   n_in_adj_players |   lift_player | power_gate_pass   |
|---------:|:-------------|--------------------:|-------------------:|--------------:|:------------------|
|     2024 | BLK          |                 271 |                405 |        1.4945 | True              |
|     2024 | PTS          |                 271 |                405 |        1.4945 | True              |
|     2024 | REB          |                 271 |                405 |        1.4945 | True              |
|     2025 | BLK          |                 259 |                368 |        1.4208 | True              |
|     2025 | PTS          |                 259 |                368 |        1.4208 | True              |
|     2025 | REB          |                 259 |                368 |        1.4208 | True              |

## Aggregate dispositions (adjudicated, surgical)

- **BLK**: ['PERSISTS', 'PERSISTS']
- **PTS**: ['DIRECTIONAL-PERSISTS', 'DIRECTIONAL-PERSISTS']
- **REB**: ['WALK-BACK FALSIFIED', 'WALK-BACK FALSIFIED']

*Stan arm analysis pending Stan posterior file integration.*
