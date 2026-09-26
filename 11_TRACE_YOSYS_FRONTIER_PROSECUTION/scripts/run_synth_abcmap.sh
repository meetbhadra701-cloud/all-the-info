#!/usr/bin/env bash
# ABC gate-library isolation: pre-ABC flow + Yosys 'abc' with different target gate sets (MAIN image).
HERE="$(cd "$(dirname "$0")/.." && pwd)"; WIN="$(wslpath -w "$HERE")"
DOCKER="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
"$DOCKER" run --rm --network none --pull never -v "$WIN:/work" -w /work muxwise-yosys-current:exp6 bash /work/scripts/synth_in_container.sh "netlists/jobs_ABCMAP.txt" 3 > "$HERE/logs/synth_ABCMAP.csv" 2>&1
cat "$HERE/logs/synth_ABCMAP.csv"
