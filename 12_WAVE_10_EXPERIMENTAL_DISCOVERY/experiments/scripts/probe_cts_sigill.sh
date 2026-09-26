#!/usr/bin/env bash
D="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
"$D" run --rm --network none --entrypoint /bin/bash openroad/orfs:latest -c '
sed -n 70,95p /OpenROAD-flow-scripts/flow/scripts/cts.tcl
grep -n "exec\|python\|klayout" /OpenROAD-flow-scripts/flow/scripts/cts.tcl | head
grep -o "avx512[a-z]*\|avx2\|bmi2\|sha_ni\|vaes" /proc/cpuinfo | sort | uniq -c
'
grep -o "avx512[a-z]*\|avx2\|bmi2\|sha_ni\|vaes" /proc/cpuinfo | sort | uniq -c | head; grep -m1 "model name" /proc/cpuinfo
