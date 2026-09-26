#!/usr/bin/env bash
# E1 phase A, lane 1 (budgets fixed in the deviation log before launch: full model 600 s, no-timing bound 300 s, 4 CP-SAT workers)
export T_FULL=600 T_LB=300 WORKERS=4
bash /r/13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION/experiments/scripts/e1_lane.sh A ctrl int2float c432 dec c1355 i2c
