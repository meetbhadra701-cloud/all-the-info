#!/usr/bin/env bash
D="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
"$D" run --rm --network none --entrypoint /bin/bash openroad/orfs:latest -c '
cd /OpenROAD-flow-scripts/flow
sed -n 900,935p Makefile
grep -n "RUN_SCRIPT\|RUN_LOG_NAME_STEM" Makefile scripts/*.mk scripts/variables.yaml | head -20
sed -n 1,40p scripts/global_place.tcl
'
