#!/usr/bin/env bash
# &polyn (algebraic backward rewriting) scaling on Yosys architectures for unsigned multiplier y=a*b.
S=/mnt/c/Users/meetb/Documents/Codex/2026-09-20/muxwise-experiment-1-zero-commitment-eda/outputs/muxwise-experiment-02/work/oss-cad-suite
ABC="$S/bin/yosys-abc"; Y="$S/bin/yosys"
WK=/mnt/c/Users/meetb/AppData/Local/Temp/claude/C--Users-meetb-Desktop-CLAUDE-OPUS-5-5-RESEARCH-CONTEXT/03476a4d-4e8a-44cd-9bcd-493130f6d087/scratchpad/s1/work
P=$WK/polyn; mkdir -p $P; cd $P
echo "W,arch,status,seconds,HashM,Total,Left,expected_left"
for W in 6 8 10 12 16 24 32; do
  printf 'module top(input [%d:0] a, input [%d:0] b, output [%d:0] y);\n  assign y = a * b;\nendmodule\n' $((W-1)) $((W-1)) $((2*W-1)) > m$W.v
  SIG="("; for ((i=0;i<2*W;i++)); do SIG+="$i*o$i"; [ $i -lt $((2*W-1)) ] && SIG+="+"; done; SIG+=")"
  for arch in norm booth; do
    flag=""; [ $arch = booth ] && flag=-booth
    [ -s m${W}_$arch.aig ] || "$Y" -q -p "read_verilog m$W.v; synth -top top $flag; aigmap; opt_clean; write_aiger -symbols m${W}_$arch.aig" >/dev/null 2>&1
    t0=$(date +%s.%N)
    timeout 120 "$ABC" -c "&r m${W}_$arch.aig; &polyn -S $SIG" > pl_${W}_$arch.log 2>&1; rc=$?
    t1=$(date +%s.%N)
    st=OK; [ $rc -eq 124 ] && st=TIMEOUT; grep -q "Left = " pl_${W}_$arch.log || { [ $st = OK ] && st=NO_RESULT; }
    hm=$(grep -o "HashM = [0-9]*" pl_${W}_$arch.log | awk '{print $3}'); tt=$(grep -o "Total = [0-9]*" pl_${W}_$arch.log | awk '{print $3}'); lf=$(grep -o "Left = [0-9]*" pl_${W}_$arch.log | awk '{print $3}')
    printf '%d,%s,%s,%.1f,%s,%s,%s,%d\n' $W $arch $st "$(echo "$t1 - $t0" | bc)" "${hm:--}" "${tt:--}" "${lf:--}" $((W*W))
  done
done
