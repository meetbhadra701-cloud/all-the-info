#!/usr/bin/env bash
# Pre-ABC signed low-power Booth (replica flow with booth -lowpower, no abc) at W = 8/16/32 on the MAIN image.
HERE="$(cd "$(dirname "$0")/.." && pwd)"; WIN="$(wslpath -w "$HERE")"
DOCKER="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
"$DOCKER" run --rm --network none --pull never -v "$WIN:/work" -w /work muxwise-yosys-current:exp6 bash /work/scripts/synth_in_container.sh "netlists/jobs_MAIN_lppre.txt" 3 > "$HERE/logs/synth_MAIN_lppre.csv" 2>&1
cat "$HERE/logs/synth_MAIN_lppre.csv"
