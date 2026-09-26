#!/usr/bin/env bash
# Screening probe: does the local ORFS image's OpenROAD include the resynth/emap commands? (read-only, no network)
D="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
"$D" run --rm --network none --entrypoint /bin/bash openroad/orfs:latest -c '
source /OpenROAD-flow-scripts/env.sh >/dev/null 2>&1
openroad -version 2>/dev/null | head -2
cat > /tmp/p.tcl <<TCL
foreach c {resynth resynth_emap emap rmp::resynth_emap repair_timing restructure} { puts "\$c: [llength [info commands \$c]]" }
puts [join [lsort [info commands *resynth*]] " "]
puts [join [lsort [info commands *emap*]] " "]
TCL
openroad -no_init -exit /tmp/p.tcl 2>&1 | tail -8
ls /OpenROAD-flow-scripts/tools/OpenROAD/src/rmp 2>/dev/null | head -30 | tr "\n" " "; echo
grep -rl "emap" /OpenROAD-flow-scripts/tools/OpenROAD/src/rmp 2>/dev/null | head -10
grep -rn "resynth_emap\|RESYNTH\|EMAP" /OpenROAD-flow-scripts/flow/scripts/*.tcl /OpenROAD-flow-scripts/flow/scripts/variables.yaml 2>/dev/null | head -10
cd /OpenROAD-flow-scripts && git log -1 --format="ORFS %H %cd" 2>/dev/null; git -C tools/OpenROAD log -1 --format="OpenROAD %H %cd" 2>/dev/null
'
