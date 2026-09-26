#!/usr/bin/env bash
D="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
"$D" run --rm --network none --entrypoint /bin/bash openroad/orfs:latest -c '
cd /OpenROAD-flow-scripts/flow && source ../env.sh >/dev/null 2>&1
make DESIGN_CONFIG=./designs/asap7/aes/config.mk print-LIB_FILES print-DONT_USE_CELLS print-SC_LEF 2>/dev/null | tail -4
command -v eqy sby yosys-smtbmc 2>/dev/null; yosys -V
'
