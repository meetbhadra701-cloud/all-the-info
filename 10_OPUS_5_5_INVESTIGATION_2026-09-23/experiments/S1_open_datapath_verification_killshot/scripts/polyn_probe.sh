#!/usr/bin/env bash
S=/mnt/c/Users/meetb/Documents/Codex/2026-09-20/muxwise-experiment-1-zero-commitment-eda/outputs/muxwise-experiment-02/work/oss-cad-suite
ABC="$S/bin/yosys-abc"; Y="$S/bin/yosys"
WK=/mnt/c/Users/meetb/AppData/Local/Temp/claude/C--Users-meetb-Desktop-CLAUDE-OPUS-5-5-RESEARCH-CONTEXT/03476a4d-4e8a-44cd-9bcd-493130f6d087/scratchpad/s1/work
P=$WK/polyn; mkdir -p $P; cd $P
printf 'module top(input [3:0] a, input [3:0] b, output [7:0] y);\n  assign y = a * b;\nendmodule\n' > m4.v
for arch in norm booth; do
  flag=""; [ $arch = booth ] && flag=-booth
  "$Y" -q -p "read_verilog m4.v; synth -top top $flag; aigmap; opt_clean; write_aiger -symbols m4_$arch.aig" >/dev/null 2>&1
done
SIG="(0*o0+1*o1+2*o2+3*o3+4*o4+5*o5+6*o6+7*o7)"
echo "=== &polyn -v -S on 4x4 norm"; timeout 60 "$ABC" -c "&r m4_norm.aig; &polyn -v -S $SIG" 2>&1 | tail -25
echo "=== &polyn -S on 4x4 booth"; timeout 60 "$ABC" -c "&r m4_booth.aig; &polyn -S $SIG" 2>&1 | tail -25
echo "=== &polyn default on 4x4 norm"; timeout 60 "$ABC" -c "&r m4_norm.aig; &polyn -v" 2>&1 | tail -25
