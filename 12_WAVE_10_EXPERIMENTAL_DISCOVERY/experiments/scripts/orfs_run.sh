#!/usr/bin/env bash
# Run one ORFS flow (openroad/orfs:latest, 2026-09-19 image) in a sandboxed container.
# Usage: orfs_run.sh <platform> <design> <variant> <target: finish|synth|place|cts|route> [MAKEVAR=val ...]
# Outputs persist under experiments/outputs/orfs/<platform>/<design>/<variant>/ (WORK_HOME), plus a run log.
set -u
H="$(cd "$(dirname "$0")/../.." && pwd)"; HW="$(wslpath -w "$H")"
D="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
P=$1; DES=$2; V=$3; T=$4; shift 4
OUT="experiments/outputs/orfs/$P/$DES/$V"; mkdir -p "$H/$OUT"
EXTRA="$*"
t0=$(date +%s)
"$D" run --rm --network none --cpus ${CPUS:-2} --memory ${MEM:-6g} -v "$HW:/w" --entrypoint /bin/bash openroad/orfs:latest -c "
  cd /OpenROAD-flow-scripts/flow && source ../env.sh >/dev/null 2>&1
  export WORK_HOME=/w/$OUT
  timeout ${TMO:-7200} make DESIGN_CONFIG=./designs/$P/$DES/config.mk FLOW_VARIANT=$V $EXTRA $T > /w/$OUT/make.log 2>&1
  echo \"make_exit=\$?\" >> /w/$OUT/make.log
  make DESIGN_CONFIG=./designs/$P/$DES/config.mk FLOW_VARIANT=$V $EXTRA metadata >> /w/$OUT/make.log 2>&1 || true
" 
echo "$P,$DES,$V,$T,\"$EXTRA\",$(( $(date +%s)-t0 )),$(grep -o 'make_exit=[0-9]*' $H/$OUT/make.log | tail -1)" >> "$H/experiments/results/orfs_runs.csv"
tail -3 "$H/$OUT/make.log"
