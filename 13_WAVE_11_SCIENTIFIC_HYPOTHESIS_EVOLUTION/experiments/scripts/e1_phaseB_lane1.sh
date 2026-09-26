#!/usr/bin/env bash
# E1 phase B, lane 1 (budgets fixed in the deviation log before launch: eps models 300 s, 4 CP-SAT workers; eps 0.05 first)
export T_EPS=300 WORKERS=4 EPS_LIST="0.05 0 0.2"
bash /r/13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION/experiments/scripts/e1_lane.sh B ctrl int2float c432 dec c1355 i2c
