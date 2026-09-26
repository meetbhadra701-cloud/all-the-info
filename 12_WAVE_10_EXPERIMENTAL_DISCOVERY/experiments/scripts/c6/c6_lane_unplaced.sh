#!/usr/bin/env bash
# R6 (Amendment 1): unplaced reproduction lane, run sequentially.
R=/mnt/c/Users/meetb/Desktop/CLAUDE_OPUS_5_5_RESEARCH_CONTEXT/12_WAVE_10_EXPERIMENTAL_DISCOVERY/experiments/scripts/c6/c6_run.sh
for ms in none:1 repair_timing:1 annealing:1 annealing:2 annealing:3; do m=${ms%%:*}; s=${ms##*:}; t0=$(date +%s); r=$(STAGE=unplaced TMO=5400 bash $R asap7 aes $m $s 2>&1 | tail -1); echo "unplaced $m s$s wall=$(( $(date +%s)-t0 ))s :: $r"; done
