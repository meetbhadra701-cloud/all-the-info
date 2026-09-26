#!/usr/bin/env bash
# Runs INSIDE a local Yosys image (muxwise-yosys-*:exp6) with /work = experiment root, --network none.
# Usage: synth_in_container.sh <jobs file relative to /work> <parallelism>
set -u
cd /work
JOBS="$1"; PAR="${2:-4}"
run_one() {
  base="$1"
  t0=$(date +%s.%N)
  timeout 3600 /build/yosys -q -l "$base.log" -s "$base.ys" > /dev/null 2>&1
  rc=$?
  t1=$(date +%s.%N)
  ok=0; [ -s "$base.aig" ] && ok=1
  printf '%s,%d,%d,%.2f\n' "$base" "$rc" "$ok" "$(echo "$t1 - $t0" | bc 2>/dev/null || python3 -c "print($t1-$t0)")"
}
export -f run_one
echo "base,rc,aig_written,seconds"
xargs -P "$PAR" -I{} bash -c 'run_one {}' < "$JOBS"
