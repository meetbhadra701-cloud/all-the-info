#!/usr/bin/env bash
# Screening probe: OpenROAD rmp resynthesis command help, read from the installed binary (read-only, no network)
D="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
"$D" run --rm --network none --entrypoint /bin/bash openroad/orfs:latest -c '
source /OpenROAD-flow-scripts/env.sh >/dev/null 2>&1
cat > /tmp/h.tcl <<TCL
help resynth
help resynth_annealing
help resynth_genetic
help restructure
TCL
openroad -no_init -exit /tmp/h.tcl 2>&1 | head -60
ls /OpenROAD-flow-scripts/tools 2>/dev/null
grep -rln "resynth" /OpenROAD-flow-scripts/flow/scripts 2>/dev/null | head
'
