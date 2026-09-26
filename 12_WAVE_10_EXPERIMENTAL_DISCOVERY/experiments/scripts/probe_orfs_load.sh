#!/usr/bin/env bash
# Probe: how ORFS loads a design into OpenROAD (load.tcl), which make targets open a stage, and the aes/asap7 config (read-only)
D="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
"$D" run --rm --network none --entrypoint /bin/bash openroad/orfs:latest -c '
cd /OpenROAD-flow-scripts/flow
sed -n 1,80p scripts/load.tcl
echo ===== aes config; cat designs/asap7/aes/config.mk; cat designs/asap7/aes/constraint.sdc
echo ===== targets; grep -n "^open_%\|^gui_%\|open_\$\|^run:\|^print-%" Makefile scripts/*.mk 2>/dev/null | head -20
grep -rn "resynth\|restructure" scripts/*.tcl | head -10
'
