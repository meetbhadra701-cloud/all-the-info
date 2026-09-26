#!/usr/bin/env bash
# Runs a list of C6 treatments sequentially: c6_lane.sh "mode:seed mode:seed ..."
R=/mnt/c/Users/meetb/Desktop/CLAUDE_OPUS_5_5_RESEARCH_CONTEXT/12_WAVE_10_EXPERIMENTAL_DISCOVERY/experiments/scripts/c6/c6_run.sh
for ms in $1; do m=${ms%%:*}; s=${ms##*:}; t0=$(date +%s); r=$(TMO=${TMO:-5400} bash $R asap7 aes $m $s 2>&1 | tail -1); echo "$m s$s wall=$(( $(date +%s)-t0 ))s :: $r"; done
