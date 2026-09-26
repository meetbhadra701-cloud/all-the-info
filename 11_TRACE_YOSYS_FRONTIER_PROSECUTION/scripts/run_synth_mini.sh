#!/usr/bin/env bash
# Small signed MACs (W = 2..6) for minimising the phase-optimisation defect; same images and container settings as run_synth.sh
HERE="$(cd "$(dirname "$0")/.." && pwd)"; WIN="$(wslpath -w "$HERE")"
DOCKER="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
declare -A IMG=([MINI_MAIN]=muxwise-yosys-current:exp6 [MINI_PATCH]=muxwise-yosys-patched:exp6)
for b in MINI_MAIN MINI_PATCH; do
  "$DOCKER" run --rm --network none --pull never -v "$WIN:/work" -w /work "${IMG[$b]}" bash /work/scripts/synth_in_container.sh "netlists/jobs_${b}.txt" 4 > "$HERE/logs/synth_${b}.csv" 2>&1
  cat "$HERE/logs/synth_${b}.csv"; done
