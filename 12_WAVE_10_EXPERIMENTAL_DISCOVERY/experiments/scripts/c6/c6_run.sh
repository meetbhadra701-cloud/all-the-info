#!/usr/bin/env bash
# Wave 10 / C6: runs one treatment on a copy of the placed design (network off). The original stage outputs are never modified.
# usage: c6_run.sh <platform> <design> <mode> <seed> [iters]
set -u
H="$(cd "$(dirname "$0")/../../.." && pwd)"; HW="$(wslpath -w "$H")"
D="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
P=$1; DES=$2; M=$3; S=$4; IT=${5:-}
SRC="experiments/outputs/orfs/$P/$DES/base"; T="experiments/outputs/c6/$P/$DES/${STAGE:+${STAGE}_}${M}_s$S${IT:+_i$IT}"
mkdir -p "$H/$T"
"$D" run --rm --network none --cpus ${CPUS:-1} --memory ${MEM:-4g} -v "$HW:/w" --entrypoint /bin/bash openroad/orfs:latest -c "
  cd /OpenROAD-flow-scripts/flow && source ../env.sh >/dev/null 2>&1
  W=/tmp/wh; mkdir -p \$W && cp -r /w/$SRC/results /w/$SRC/logs /w/$SRC/reports \$W/ 2>/dev/null
  export C6_MODE=$M C6_SEED=$S C6_OUT=/w/$T ${IT:+C6_ITERS=$IT} ${STAGE:+C6_STAGE=$STAGE}
  timeout ${TMO:-7200} make DESIGN_CONFIG=./designs/$P/$DES/config.mk FLOW_VARIANT=base WORK_HOME=\$W run RUN_SCRIPT=/w/experiments/scripts/c6/c6_treat.tcl RUN_LOG_NAME_STEM=c6 > /w/$T/run.log 2>&1
  echo \"make_exit=\$?\" >> /w/$T/run.log
"
cat "$H/$T/metrics.json" 2>/dev/null || { echo "NO_METRICS"; tail -20 "$H/$T/run.log"; }
