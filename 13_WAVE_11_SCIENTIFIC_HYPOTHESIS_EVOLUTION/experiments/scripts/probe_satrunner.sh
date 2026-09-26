#!/usr/bin/env bash
export LD_LIBRARY_PATH=/opt/or-tools/lib:${LD_LIBRARY_PATH:-}
S=/opt/or-tools/bin/sat_runner
ls -la $S; md5sum $S
$S --helpfull 2>&1 | grep -iE "^\s+--(input|output|params|wcnf|opb|use_|fingerprint|solution|hint|lower|upper|max_time|num_|interleave|log|proto|cp_model|reduce|presolve)" | head -60
echo "== usage head"; $S --help 2>&1 | head -30
echo "== version"; ls /opt/or-tools/lib | head -50
