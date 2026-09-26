#!/usr/bin/env bash
# Follow-up lane (Amendment 3): waits for the pre-fix annealing_repair_s1 to end, archives it if it failed, then reruns s1 and s2 with the fixed script.
H=/mnt/c/Users/meetb/Desktop/CLAUDE_OPUS_5_5_RESEARCH_CONTEXT/12_WAVE_10_EXPERIMENTAL_DISCOVERY
R=$H/experiments/scripts/c6/c6_run.sh; D=$H/experiments/outputs/c6/asap7/aes
until grep -q "make_exit=" $D/annealing_repair_s1/run.log 2>/dev/null; do sleep 20; done
sleep 5
if [ ! -f $D/annealing_repair_s1/metrics.json ]; then mv $D/annealing_repair_s1 $H/experiments/outputs/c6/failed_runs/annealing_repair_s1_EST-0104; echo "archived pre-fix annealing_repair_s1"; fi
for s in 1 2; do t0=$(date +%s); r=$(TMO=5400 bash $R asap7 aes annealing_repair $s 2>&1 | tail -1); echo "annealing_repair s$s (fixed) wall=$(( $(date +%s)-t0 ))s :: $r"; done
