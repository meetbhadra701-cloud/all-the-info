#!/usr/bin/env bash
D=/mnt/c/Users/meetb/AppData/Local/Temp/claude/C--Users-meetb-Desktop-CLAUDE-OPUS-5-5-RESEARCH-CONTEXT/03476a4d-4e8a-44cd-9bcd-493130f6d087/scratchpad/s1
command -v bc >/dev/null || { echo "bc missing"; exit 2; }
bash "$D/scale.sh" > "$D/scale_results.csv" 2> "$D/scale_stderr.txt"
echo "DONE $(date)" >> "$D/scale_results.csv"
