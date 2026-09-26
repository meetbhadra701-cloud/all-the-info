#!/usr/bin/env bash
# R2: unmodified MappingEvolve main.cpp in single-file mode on the 20 EPFL circuits (the paper's Table 2 setting).
# Each run does compress2, then map, then MappingEvolve's own `cec -n` against the original AIG,
# and writes the cell netlist.
# usage: r2_epfl_orig.sh <variant>
set -u
v=$1
B=/w/experiments/outputs/c1/bin; M=/w/third_party/MappingEvolve/third-party/mockturtle/experiments
G=$M/cell_libraries/asap7.genlib
OD=/w/experiments/outputs/c1/r2/$v; mkdir -p $OD
O=/w/experiments/results/c1_r2_epfl_orig_$v.jsonl; : > $O
for b in adder bar div hyp log2 max multiplier sin sqrt square arbiter cavlc ctrl dec i2c int2float mem_ctrl priority router voter; do
  t0=$(date +%s.%N)
  out=$(set -o pipefail; timeout 3600 $B/orig_$v $G $M/benchmarks/$b.aig $OD/$b.v 2>$OD/$b.stderr | tail -1)
  rc=$?
  t1=$(date +%s.%N)
  [ -z "$out" ] && out='null'
  echo "{\"variant\": \"$v\", \"bench\": \"$b\", \"wall\": $(python3 -c "print(round($t1 - $t0, 3))"), \"rc\": $rc, \"result\": $out}" >> $O
done
echo done $v
