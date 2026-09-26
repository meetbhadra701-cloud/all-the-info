#!/usr/bin/env bash
HERE="$(cd "$(dirname "$0")/.." && pwd)"; WIN="$(wslpath -w "$HERE")"
DOCKER="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
declare -A IMG=([MAIN]=muxwise-yosys-current:exp6 [PATCH]=muxwise-yosys-patched:exp6)
for b in MAIN PATCH; do [ -s "$HERE/netlists/jobs_${b}_w64pre.txt" ] || continue
  "$DOCKER" run --rm --network none --pull never -v "$WIN:/work" -w /work "${IMG[$b]}" bash /work/scripts/synth_in_container.sh "netlists/jobs_${b}_w64pre.txt" 4 > "$HERE/logs/synth_${b}_w64pre.csv" 2>&1
  cat "$HERE/logs/synth_${b}_w64pre.csv"; done
