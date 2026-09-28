# R3 tables reproduced by ubpgen

| Design | U | K | Base DRC | Base setup / hold (ns) | Base ODB = historical | A×T | vs strongest (14.25e6) | All programs pass |
|---|---|---|---|---|---|---|---|---|
| golden_r3_ubp3_u60 | 60 | 4 | 0 | +1.022 / +0.293 | True | 8.5660e+06 | 1.663× | True |
| golden_r3_ubp3_u52 | 52 | 4 | 0 | +0.976 / +0.268 | True | 9.2625e+06 | 1.538× | True |
| golden_r3_pc2_u67 | 67 | 4 | 0 | -0.846 / +0.024 | True | 1.7885e+07 | — (competitor) | True |
| r3_g1_u75 | 75 | 4 | 0 | +0.775 / +0.065 | None | 1.4804e+07 | — (competitor) | True |

| Design | W | DRT final (it.) | met4 / met5 WL (µm) | via4 | setup / prog-path WS (ns) | post-PnR = numpy, mutation | invariants | historical (it., met4 WL, prog WS) |
|---|---|---|---|---|---|---|---|---|
| golden_r3_ubp3_u60 | w1 | 0 (13) | 57,018 / 3,340 | 685 | +0.840 / +0.840 | True, True | True | 13, 57,018, +0.840 |
| golden_r3_ubp3_u60 | w2 | 0 (13) | 58,847 / 4,190 | 789 | +0.939 / +0.998 | True, True | True | 13, 58,847, +0.998 |
| golden_r3_ubp3_u60 | w3 | 0 (7) | 30,419 / 1,356 | 253 | +0.939 / +0.971 | True, True | True | 7, 30,419, +0.971 |
| golden_r3_ubp3_u60 | w4 | 0 (13) | 57,409 / 4,148 | 879 | +0.825 / +0.825 | True, True | True | 13, 57,409, +0.825 |
| golden_r3_ubp3_u60 | w5 | 0 (1) | 11,649 / 0 | 0 | +0.788 / +0.788 | True, True | True | 1, 11,649, +0.788 |
| golden_r3_ubp3_u52 | w1 | 0 (14) | 60,063 / 4,236 | 772 | +0.888 / +1.094 | True, True | True | 14, 60,063, +1.094 |
| golden_r3_ubp3_u52 | w2 | 0 (13) | 62,396 / 4,464 | 823 | +0.888 / +1.082 | True, True | True | 13, 62,396, +1.082 |
| golden_r3_ubp3_u52 | w3 | 0 (7) | 32,097 / 1,905 | 361 | +0.888 / +1.071 | True, True | True | 7, 32,097, +1.071 |
| golden_r3_ubp3_u52 | w4 | 0 (14) | 60,641 / 5,174 | 937 | +0.888 / +1.073 | True, True | True | 14, 60,641, +1.073 |
| golden_r3_ubp3_u52 | w5 | 0 (1) | 12,533 / 23 | 4 | +0.888 / +0.996 | True, True | True | 1, 12,533, +0.996 |
| golden_r3_pc2_u67 | w1 | 0 (14) | 62,326 / 393 | 132 | -2.453 / -2.453 | True, True | True | — |
| golden_r3_pc2_u67 | w4 | 0 (14) | 72,921 / 665 | 234 | -2.803 / -2.803 | True, True | True | 14, 72,921, -2.803 |
| r3_g1_u75 | w1 | 0 (8) | 66,608 / 388 | 138 | +0.715 / +0.963 | True, True | True | — |
| r3_g1_u75 | w2 | 0 (8) | 66,463 / 309 | 118 | +0.715 / +0.987 | True, True | True | — |
| r3_g1_u75 | w3 | 0 (5) | 34,876 / 79 | 28 | +0.715 / +1.036 | True, True | True | — |
| r3_g1_u75 | w4 | 0 (10) | 78,412 / 553 | 196 | +0.715 / +0.963 | True, True | True | — |
| r3_g1_u75 | w5 | 0 (1) | 28,983 / 0 | 0 | +0.715 / +0.930 | True, True | True | — |

**B advantage over the competitors measured in this suite** (competitor A×T / B A×T, established rule):

| B design | golden_r3_pc2_u67 | r3_g1_u75 |
|---|---|---|
| golden_r3_ubp3_u60 | 2.088× | 1.728× |
| golden_r3_ubp3_u52 | 1.931× | 1.598× |

**Differences vs the historical records:** 0
