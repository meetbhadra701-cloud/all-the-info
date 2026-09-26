#!/usr/bin/env bash
D="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
"$D" run --rm --network none --entrypoint /bin/bash openroad/orfs:latest -c '
sed -n 40,72p /OpenROAD-flow-scripts/flow/scripts/cts.tcl
grep -rn "proc run_lec_test" -A25 /OpenROAD-flow-scripts/flow/scripts/*.tcl | head -40
grep -rn "LEC_CHECK\|RUN_LEC\|lec" /OpenROAD-flow-scripts/flow/scripts/variables.yaml 2>/dev/null | head -10
'
