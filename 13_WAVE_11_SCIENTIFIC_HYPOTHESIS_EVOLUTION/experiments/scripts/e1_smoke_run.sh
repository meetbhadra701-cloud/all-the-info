#!/usr/bin/env bash
export T_FULL=20 T_LB=15 T_EPS=10 WORKERS=4 E1_SET=smoke_run EPS_LIST="0.05"
bash /r/13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION/experiments/scripts/e1_lane.sh A ctrl
bash /r/13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION/experiments/scripts/e1_lane.sh B ctrl
