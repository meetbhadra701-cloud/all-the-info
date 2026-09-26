#!/usr/bin/env bash
# ABC-step isolation: apply ONE ABC optimisation step directly to a pre-ABC netlist and write AIGER (PI/PO order preserved).
# Uses the local OSS CAD Suite ABC (same binary as cec_pre_post.sh). Output: netlists/ABCSTEP/<name>__<step>.aig
HERE="$(cd "$(dirname "$0")/.." && pwd)"
ABC=/mnt/c/Users/meetb/Documents/Codex/2026-09-20/muxwise-experiment-1-zero-commitment-eda/outputs/muxwise-experiment-02/work/oss-cad-suite/bin/yosys-abc
OUT="$HERE/netlists/ABCSTEP"; mkdir -p "$OUT"
declare -A STEP=(
  [strash]="strash"
  [balance]="strash; balance"
  [rewrite]="strash; rewrite"
  [refactor]="strash; refactor"
  [dc2]="strash; dc2"
  [resyn2]="strash; balance; rewrite; refactor; balance; rewrite; rewrite -z; balance; refactor -z; rewrite -z; balance"
  [fraig]="strash; fraig"
  [dch]="strash; &get -n; &dch -f; &put; strash"
  [yosysnomap]="strash; &get -n; &fraig -x; &put; scorr; dc2; dretime; strash; &get -n; &dch -f; &put; strash"
)
for src in "$@"; do
  name=$(basename "$src" .aig)
  for s in "${!STEP[@]}"; do
    "$ABC" -c "read_aiger $HERE/$src; ${STEP[$s]}; write_aiger -s $OUT/${name}__${s}.aig" > "$OUT/${name}__${s}.log" 2>&1
    echo "$name $s rc=$? $(grep -c . "$OUT/${name}__${s}.log") $(ls -la "$OUT/${name}__${s}.aig" 2>/dev/null | awk '{print $5}')"
  done
done
