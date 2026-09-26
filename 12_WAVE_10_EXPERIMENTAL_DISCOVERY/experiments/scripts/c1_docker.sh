#!/usr/bin/env bash
# Wave 10 / C1: runs an inner script inside openroad/orfs:latest with --network none.
# usage: c1_docker.sh <inner_script_relative_to_study_root> [args...]
set -u
H="$(cd "$(dirname "$0")/../.." && pwd)"; HW="$(wslpath -w "$H")"
D="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
S=$1; shift
"$D" run --rm --network none --cpus ${CPUS:-2} --memory ${MEM:-6g} -v "$HW:/w" --entrypoint /bin/bash openroad/orfs:latest -c "
  source /OpenROAD-flow-scripts/env.sh >/dev/null 2>&1
  mkdir -p /tmp/c1src/third-party && ln -sfn /w/third_party/MappingEvolve/third-party/mockturtle /tmp/c1src/third-party/mockturtle
  cd /w && bash /w/$S $*"
