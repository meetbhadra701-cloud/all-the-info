#!/usr/bin/env bash
# R1: unmodified MappingEvolve main.cpp in its default ISCAS85 mode, one run per operator variant.
# Its output is a sum over the 11 ISCAS85 circuits of relative deltas against main.cpp's hard-coded baselines.
set -u
B=/w/experiments/outputs/c1/bin; G=/w/third_party/MappingEvolve/third-party/mockturtle/experiments/cell_libraries/asap7.genlib
O=/w/experiments/results/c1_r1_iscas_orig.jsonl; : > $O
for v in initial gpt5_it29 deepseek_it24 qwen_it20; do
  for rep in 1 2; do
    out=$($B/orig_$v $G 2>/w/experiments/logs/c1/r1_${v}_$rep.stderr | tail -1)
    echo "{\"variant\": \"$v\", \"rep\": $rep, \"result\": $out}" >> $O
  done
done
cat $O
