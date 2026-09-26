#!/usr/bin/env bash
# Run TRACE with progress steps (SP-size trajectory) for diagnosis. Usage: diag_steps.sh <tag> <rel netlist> <timeout> <args...>
HERE="$(cd "$(dirname "$0")/.." && pwd)"
TAG="$1"; shift
bash "$HERE/scripts/trace_run.sh" "$@" > "$HERE/logs/diag/$TAG.log" 2>&1
python3 "$HERE/scripts/sp_trajectory.py" "$HERE/logs/diag/$TAG.log" "$HERE/logs/diag/$TAG.traj.csv" 2>/dev/null || true
