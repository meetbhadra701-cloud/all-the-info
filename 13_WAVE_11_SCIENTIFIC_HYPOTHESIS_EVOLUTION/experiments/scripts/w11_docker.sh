#!/usr/bin/env bash
# Wave 11: run an inner script in openroad/orfs:latest, network off.
# The research root is mounted at /r; the OSS CAD Suite (for the z3 binary) is mounted read-only at /oss.
# usage: w11_docker.sh <inner script path relative to the research root> [args]
set -u
H="$(cd "$(dirname "$0")/../.." && pwd)"; R="$(cd "$H/.." && pwd)"; RW="$(wslpath -w "$R")"
OSS=/mnt/c/Users/meetb/Documents/Codex/2026-09-20/muxwise-experiment-1-zero-commitment-eda/outputs/muxwise-experiment-02/work/oss-cad-suite
D="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
S=$1; shift
"$D" run --rm --network none --cpus ${CPUS:-2} --memory ${MEM:-6g} -v "$RW:/r" -v "$(wslpath -w $OSS):/oss:ro" --entrypoint /bin/bash openroad/orfs:latest -c "
  source /OpenROAD-flow-scripts/env.sh >/dev/null 2>&1
  cd /r && bash /r/$S $*"
