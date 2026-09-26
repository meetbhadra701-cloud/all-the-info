#!/usr/bin/env bash
# Onset of the 64-bit pre-ABC difficulty: unsigned MAC (default lowering and arith_tree) and dot2 tree at W = 40/48/56 (MAIN image).
HERE="$(cd "$(dirname "$0")/.." && pwd)"; WIN="$(wslpath -w "$HERE")"
DOCKER="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
"$DOCKER" run --rm --network none --pull never -v "$WIN:/work" -w /work muxwise-yosys-current:exp6 bash /work/scripts/synth_in_container.sh "netlists/jobs_ONSET_MAIN.txt" 4 > "$HERE/logs/synth_ONSET_MAIN.csv" 2>&1
cat "$HERE/logs/synth_ONSET_MAIN.csv"
