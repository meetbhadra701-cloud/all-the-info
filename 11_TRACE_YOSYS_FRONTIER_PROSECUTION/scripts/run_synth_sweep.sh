#!/usr/bin/env bash
# Width sweep W = 4..16 of y = a*b (u/s) with booth / norm (and booth_lp for signed) on the MAIN image, for the
# onset analysis of post-ABC Booth difficulty. Same container settings as run_synth.sh.
HERE="$(cd "$(dirname "$0")/.." && pwd)"; WIN="$(wslpath -w "$HERE")"
DOCKER="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
"$DOCKER" run --rm --network none --pull never -v "$WIN:/work" -w /work muxwise-yosys-current:exp6 bash /work/scripts/synth_in_container.sh "netlists/jobs_SWEEP_MAIN.txt" 2 > "$HERE/logs/synth_SWEEP_MAIN.csv" 2>&1
cat "$HERE/logs/synth_SWEEP_MAIN.csv" | awk -F, 'NR>1 && ($2!=0 || $3!=1)' ; echo "done $(wc -l < "$HERE/logs/synth_SWEEP_MAIN.csv")"
