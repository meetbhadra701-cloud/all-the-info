# E3 summary: regime-(V) fabrics from weight-independent components (generated; do not edit)

Components: 14; all independent AIG checks and ABC cec passed: True; all iso-delay cec passed: True

SKY130 HD tt_025C_1v80; cell area only (via-select wiring excluded, see wire_model.txt).
Fabric area = m x TREE + generators + shared negators; iso-delay: every fabric's critical path <= D*.

## n = m = 128; D* = 5049 ps

| fabric | leaves/row | leaf bits | area mm^2 | g1_V / this | trees | generators | negators |
|---|---|---|---|---|---|---|---|
| g1 | 128 | 8 | 4.653 | 1.000 | 4.635 | 0.000 | 0.018 |
| g2 | 64 | 9 | 3.002 | 1.550 | 2.926 | 0.034 | 0.043 |
| g3 | 43 | 10 | 2.572 | 1.809 | 2.352 | 0.118 | 0.102 |
| g4 | 32 | 10 | 2.384 | 1.952 | 1.847 | 0.303 | 0.234 |

best g1_V/UBP_V at n=128: **1.952**

## n = m = 1024; D* = 6507 ps

| fabric | leaves/row | leaf bits | area mm^2 | g1_V / this | trees | generators | negators |
|---|---|---|---|---|---|---|---|
| g1 | 1024 | 8 | 303.943 | 1.000 | 303.801 | 0.000 | 0.142 |
| g2 | 512 | 9 | 184.753 | 1.645 | 184.141 | 0.272 | 0.341 |
| g3 | 342 | 10 | 147.341 | 2.063 | 145.592 | 0.937 | 0.812 |
| g4 | 256 | 10 | 121.879 | 2.494 | 117.584 | 2.425 | 1.870 |

best g1_V/UBP_V at n=1024: **2.494**

## Pre-registered conditions

- K3 (best ratio < 1.3 at both n): not triggered
- ADV3 (>= 1.5 at n = 1024): MET

## MODEL-ADJUSTED estimate (measured E3 cell area per leaf + modelled select wiring; NOT a measurement)

Per (row, leaf) site area = max(measured tree area per leaf, lines x bits x pitch x row height); generators/negators added as measured.
Lines per site: g=1 -> 1 (8-bit x_j; polarity via shared negated line), g -> (3^g-1)/2 canonical patterns. Bit-parallel buses.

| n | pitch um | g | logic/leaf um2 | wiring/site um2 | bound | fabric mm2 | g1_V / this |
|---|---|---|---|---|---|---|---|
| 128 | 0.46 | 1 | 283 | 10 | logic | 4.65 | 1.00 |
| 128 | 0.46 | 2 | 357 | 45 | logic | 3.00 | 1.55 |
| 128 | 0.46 | 3 | 427 | 163 | logic | 2.57 | 1.81 |
| 128 | 0.46 | 4 | 451 | 500 | wire | 2.59 | 1.80 |
| 128 | 0.92 | 1 | 283 | 20 | logic | 4.65 | 1.00 |
| 128 | 0.92 | 2 | 357 | 90 | logic | 3.00 | 1.55 |
| 128 | 0.92 | 3 | 427 | 325 | logic | 2.57 | 1.81 |
| 128 | 0.92 | 4 | 451 | 1001 | wire | 4.64 | 1.00 |
| 1024 | 0.46 | 1 | 290 | 10 | logic | 303.94 | 1.00 |
| 1024 | 0.46 | 2 | 351 | 45 | logic | 184.75 | 1.65 |
| 1024 | 0.46 | 3 | 416 | 163 | logic | 147.34 | 2.06 |
| 1024 | 0.46 | 4 | 449 | 500 | wire | 135.49 | 2.24 |
| 1024 | 0.92 | 1 | 290 | 20 | logic | 303.94 | 1.00 |
| 1024 | 0.92 | 2 | 351 | 90 | logic | 184.75 | 1.65 |
| 1024 | 0.92 | 3 | 416 | 325 | logic | 147.34 | 2.06 |
| 1024 | 0.92 | 4 | 449 | 1001 | wire | 266.69 | 1.14 |
