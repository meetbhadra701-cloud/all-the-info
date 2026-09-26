#!/usr/bin/env bash
# usage: e1_lane.sh PHASE BENCH... (inside the container). Budgets via T_FULL, T_EPS, T_LB, WORKERS, EPS_LIST, E1_SET.
echo "lane start $(date +%T) phase=$1 benches=${*:2} T_FULL=${T_FULL:-600} T_EPS=${T_EPS:-300} T_LB=${T_LB:-300} WORKERS=${WORKERS:-4} SET=${E1_SET:-}"
python3 /r/13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION/experiments/scripts/e1_run.py "$@"
echo "lane end $(date +%T)"
