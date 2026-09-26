#!/usr/bin/env bash
# Verify the pre-existing OSS CAD Suite (from MUXWISE Experiment 2) runs. No downloads.
S=/mnt/c/Users/meetb/Documents/Codex/2026-09-20/muxwise-experiment-1-zero-commitment-eda/outputs/muxwise-experiment-02/work/oss-cad-suite
echo "SUITE=$S"
cat "$S/VERSION"
"$S/bin/yosys" -V
"$S/bin/yosys-abc" -q "version" 2>&1 | head -3
for t in eqy sby bitwuzla z3 iverilog verilator yosys-smtbmc; do
  if [ -x "$S/bin/$t" ]; then echo "have $t"; else echo "MISSING $t"; fi
done
