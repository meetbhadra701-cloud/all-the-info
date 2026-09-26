#!/usr/bin/env bash
# ABC step validation: &cec between pre-ABC (synth -noabc) and post-ABC (synth) netlists of the same design/arch.
# Uses the local OSS CAD Suite ABC 1.01 (no network). Verdict parsed from text.
HERE="$(cd "$(dirname "$0")/.." && pwd)"
ABC=/mnt/c/Users/meetb/Documents/Codex/2026-09-20/muxwise-experiment-1-zero-commitment-eda/outputs/muxwise-experiment-02/work/oss-cad-suite/bin/yosys-abc
OUT="$HERE/evidence/cec_pre_post.csv"
# Rows are written to one file per job on the Linux filesystem and assembled at the end: concurrent '>>' appends to
# a /mnt/c (drvfs) file are not atomic and lost one row in the first run (MAIN A_mul_u_w16 booth).
ROWS=$(mktemp -d)
ONLY="${1:-}"   # optional "BUILD DESIGN ARCH" to run a single row (appended to the existing CSV)
run() { b=$1; d=$2; a=$3; pre="$HERE/netlists/$b/${d}__${a}_pre.aig"; post="$HERE/netlists/$b/${d}__${a}.aig"
  [ -s "$pre" ] && [ -s "$post" ] || { echo "$b,$d,$a,MISSING," > "$ROWS/$b.$d.$a"; return; }
  t0=$(date +%s.%N); log=$(timeout 1800 "$ABC" -c "&r $pre; &cec -T 1700 $post" 2>&1); rc=$?; t1=$(date +%s.%N)
  v=ERROR; [ $rc -eq 124 ] && v=TIMEOUT; echo "$log" | grep -q "Networks are equivalent" && v=PASS; echo "$log" | grep -q "NOT EQUIVALENT" && v=FAIL
  echo "$b,$d,$a,$v,$(awk -v a=$t0 -v b=$t1 'BEGIN{printf "%.1f",b-a}')" > "$ROWS/$b.$d.$a"; }
export -f run; export HERE ABC OUT ROWS
if [ -n "$ONLY" ]; then run $ONLY; cat "$ROWS"/* >> "$OUT"; cat "$ROWS"/*; exit 0; fi
{
for W in 16 32 64; do for s in u s; do echo "MAIN A_mul_${s}_w$W norm"; echo "MAIN A_mul_${s}_w$W booth"; done; done
for W in 16 32 64; do for k in mac dot2; do echo "MAIN B_${k}_u_w$W tree"; echo "MAIN B_${k}_u_w$W norm"; done; echo "PATCH B_mac_s_w$W tree"; done
} | xargs -P 2 -L 1 bash -c 'run "$@"' _
{ echo "build,design,arch,verdict,seconds"; cat "$ROWS"/*; } > "$OUT"
cat "$OUT"
