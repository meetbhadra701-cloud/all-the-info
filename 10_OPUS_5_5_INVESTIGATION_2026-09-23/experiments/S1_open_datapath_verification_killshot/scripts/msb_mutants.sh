#!/usr/bin/env bash
# Prediction test: &acec ignores the two most-significant outputs when adder-tree matching succeeds.
# Mutants flip exactly one output bit k of y = a*b + c (unsigned, W=8, 17-bit y) on inputs with a[0]&b[7].
# Each mutant is synthesized with -arith_tree and compared against the CORRECT normal-synthesis netlist.
S=/mnt/c/Users/meetb/Documents/Codex/2026-09-20/muxwise-experiment-1-zero-commitment-eda/outputs/muxwise-experiment-02/work/oss-cad-suite
ABC="$S/bin/yosys-abc"; Y="$S/bin/yosys"
WK=/mnt/c/Users/meetb/AppData/Local/Temp/claude/C--Users-meetb-Desktop-CLAUDE-OPUS-5-5-RESEARCH-CONTEXT/03476a4d-4e8a-44cd-9bcd-493130f6d087/scratchpad/s1/work
M=$WK/msb; mkdir -p $M
REF=$WK/aig/mac_u_w8_norm.aig
verdict() { if grep -q "Networks are NOT EQUIVALENT" "$1"; then echo FAIL; elif grep -q "Networks are equivalent" "$1"; then echo PASS; else echo OTHER; fi; }
echo "bit,expected,acec_verdict,acec_mode,gcec_verdict"
for k in 16 15 14 13 0; do
  cat > $M/mut_k$k.v <<EOF
module top(input [7:0] a, input [7:0] b, input [15:0] c, output [16:0] y);
  wire [16:0] good = a * b + c;
  assign y = good ^ ((a[0] & b[7]) ? (17'd1 << $k) : 17'd0);
endmodule
EOF
  "$Y" -q -p "read_verilog $M/mut_k$k.v; synth -top top -arith_tree; aigmap; opt_clean; write_aiger -symbols -map $M/mut_k$k.map $M/mut_k$k.aig" >/dev/null 2>&1 || { echo "$k,SYNTH_ERROR"; continue; }
  diff -q <(grep -E '^(input|output)' $WK/aig/mac_u_w8_norm.map) <(grep -E '^(input|output)' $M/mut_k$k.map) >/dev/null || echo "WARN map mismatch k=$k"
  timeout 300 "$ABC" -c "&acec -T 240 $REF $M/mut_k$k.aig" > $M/acec_k$k.log 2>&1
  mode=-; grep -q "Trying regular CEC" $M/acec_k$k.log && mode=fallback_regular; grep -q "Matching of adder trees in LHS and RHS succeeded" $M/acec_k$k.log && mode=adder_tree_matched
  timeout 300 "$ABC" -c "&r $REF; &cec -T 240 $M/mut_k$k.aig" > $M/gcec_k$k.log 2>&1
  echo "$k,NOT_EQUIVALENT,$(verdict $M/acec_k$k.log),$mode,$(verdict $M/gcec_k$k.log)"
done
