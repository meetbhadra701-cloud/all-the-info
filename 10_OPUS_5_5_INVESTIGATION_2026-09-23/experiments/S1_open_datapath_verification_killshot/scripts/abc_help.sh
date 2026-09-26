#!/usr/bin/env bash
S=/mnt/c/Users/meetb/Documents/Codex/2026-09-20/muxwise-experiment-1-zero-commitment-eda/outputs/muxwise-experiment-02/work/oss-cad-suite
ABC="$S/bin/yosys-abc"
for c in "&cec -h" "cec -h" "&polyn -h" "dcec -h" "&fraig -h" "&acec -h" "acec -h"; do
  echo "================ $c"
  "$ABC" -c "$c" 2>&1 | head -40
done
