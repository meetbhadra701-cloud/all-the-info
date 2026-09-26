#!/usr/bin/env bash
# Same-architecture false-PASS test for &acec. Reference = correct netlist of the SAME architecture as the mutant.
S=/mnt/c/Users/meetb/Documents/Codex/2026-09-20/muxwise-experiment-1-zero-commitment-eda/outputs/muxwise-experiment-02/work/oss-cad-suite
ABC="$S/bin/yosys-abc"; Y="$S/bin/yosys"
WK=/mnt/c/Users/meetb/AppData/Local/Temp/claude/C--Users-meetb-Desktop-CLAUDE-OPUS-5-5-RESEARCH-CONTEXT/03476a4d-4e8a-44cd-9bcd-493130f6d087/scratchpad/s1/work
M=$WK/msb
verdict() { if grep -q "Networks are NOT EQUIVALENT" "$1"; then echo FAIL; elif grep -q "Networks are equivalent" "$1"; then echo PASS; else echo OTHER; fi; }
mode() { local m=-; grep -q "Trying regular CEC" "$1" && m=fallback_regular; grep -q "Matching of adder trees in LHS and RHS succeeded" "$1" && m=adder_tree_matched; echo $m; }
dout() { grep -ho 'zero-based number [0-9]*' "$1" | head -1 | awk '{print $3}'; }
echo "arch,bit,expected,acec_verdict,acec_mode,acec_disproved_out,gcec_verdict,gcec_disproved_out"
for arch in tree norm; do
  flag=""; [ $arch = tree ] && flag="-arith_tree"
  REF=$WK/aig/mac_u_w8_${arch}.aig
  # identity control: reference vs itself
  timeout 300 "$ABC" -c "&acec -T 240 $REF $REF" > $M/id_${arch}.log 2>&1
  echo "$arch,none,EQUIVALENT,$(verdict $M/id_${arch}.log),$(mode $M/id_${arch}.log),$(dout $M/id_${arch}.log),-,-"
  for k in 16 15 14 13 8 0; do
    "$Y" -q -p "read_verilog $M/mut_k$k.v; synth -top top $flag; aigmap; opt_clean; write_aiger -symbols -map $M/m_${arch}_k$k.map $M/m_${arch}_k$k.aig" >/dev/null 2>&1 || { echo "$arch,$k,SYNTH_ERROR"; continue; }
    timeout 300 "$ABC" -c "&acec -T 240 $REF $M/m_${arch}_k$k.aig" > $M/a_${arch}_k$k.log 2>&1
    timeout 300 "$ABC" -c "&r $REF; &cec -T 240 $M/m_${arch}_k$k.aig" > $M/g_${arch}_k$k.log 2>&1
    echo "$arch,$k,NOT_EQUIVALENT,$(verdict $M/a_${arch}_k$k.log),$(mode $M/a_${arch}_k$k.log),$(dout $M/a_${arch}_k$k.log),$(verdict $M/g_${arch}_k$k.log),$(dout $M/g_${arch}_k$k.log)"
  done
done
