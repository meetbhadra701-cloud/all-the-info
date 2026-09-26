#!/usr/bin/env bash
# WSL driver: runs all synthesis jobs inside the user's local Yosys images (no network, no pulls).
set -u
HERE="$(cd "$(dirname "$0")/.." && pwd)"
WIN="$(wslpath -w "$HERE")"
DOCKER="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
declare -A IMG=([MAIN]=muxwise-yosys-current:exp6 [PATCH]=muxwise-yosys-patched:exp6)
for b in ${BUILDS:-MAIN PATCH}; do
  "$DOCKER" run --rm --network none --pull never -v "$WIN:/work" -w /work "${IMG[$b]}" \
     bash /work/scripts/synth_in_container.sh "netlists/jobs_$b.txt" "${PAR:-6}" > "$HERE/logs/synth_$b.csv" 2> "$HERE/logs/synth_$b.stderr"
  echo "$b done: $(grep -c ',0,1,' "$HERE/logs/synth_$b.csv") ok of $(($(wc -l < "$HERE/logs/synth_$b.csv")-1))"
done
