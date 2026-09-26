#!/usr/bin/env bash
HERE="$(cd "$(dirname "$0")/.." && pwd)"
bash "$HERE/scripts/trace_run.sh" third_party/trace_d57aa9a7/README.md 30 --help
echo; echo "=== README example (as documented): 16x16 unsigned array multiplier, ripple-carry final adder"
bash "$HERE/scripts/trace_run.sh" third_party/trace_d57aa9a7/example_circuits/multipliers/16_16_U_SP_AR_RC.aig 300 -mul -p -c
