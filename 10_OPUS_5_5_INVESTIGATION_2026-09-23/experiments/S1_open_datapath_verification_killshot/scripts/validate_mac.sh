#!/usr/bin/env bash
# Independent validation of the &acec NOT-EQUIVALENT report for unsigned MAC y = a*b + c (W=8), norm vs -arith_tree.
S=/mnt/c/Users/meetb/Documents/Codex/2026-09-20/muxwise-experiment-1-zero-commitment-eda/outputs/muxwise-experiment-02/work/oss-cad-suite
ABC="$S/bin/yosys-abc"; Y="$S/bin/yosys"; IV="$S/bin/iverilog"; VVP="$S/bin/vvp"
W=/mnt/c/Users/meetb/AppData/Local/Temp/claude/C--Users-meetb-Desktop-CLAUDE-OPUS-5-5-RESEARCH-CONTEXT/03476a4d-4e8a-44cd-9bcd-493130f6d087/scratchpad/s1/work
V=$W/validate; mkdir -p "$V"; cd "$V"
echo "=== 1. ABC &cec (regular) norm vs tree"
timeout 300 "$ABC" -c "&r $W/aig/mac_u_w8_norm.aig; &cec $W/aig/mac_u_w8_tree.aig" 2>&1 | tail -4
echo "=== 2. ABC cec (FRAIG+SAT, name-matched) norm vs tree"
timeout 300 "$ABC" -c "cec -T 120 $W/aig/mac_u_w8_norm.aig $W/aig/mac_u_w8_tree.aig" 2>&1 | tail -6
echo "=== 3. Yosys: gold RTL vs gate (arith_tree netlist exported to Verilog, re-imported under distinct name)"
"$Y" -q -p "read_verilog $W/rtl/mac_u_w8.v; synth -top top -arith_tree; rename top gate; write_verilog -noattr $V/mac_u_w8_tree_gate.v" >/dev/null 2>&1; echo "export rc=$?"
"$Y" -q -p "read_verilog $W/rtl/mac_u_w8.v; synth -top top; rename top gatenorm; write_verilog -noattr $V/mac_u_w8_norm_gate.v" >/dev/null 2>&1; echo "export rc=$?"
cat > $V/miter.ys <<EOF
read_verilog $W/rtl/mac_u_w8.v
rename top gold
read_verilog $V/mac_u_w8_tree_gate.v
proc; opt_clean
miter -equiv -flatten -make_outputs -ignore_gold_x gold gate miter
hierarchy -top miter
sat -verify -prove trigger 0 -set-def-inputs -show-inputs -show-outputs miter
EOF
timeout 300 "$Y" -q -l $V/miter_tree.log $V/miter.ys >/dev/null 2>&1; echo "yosys sat rc=$? (nonzero expected on FAIL because of -verify)"
grep -E "SAT proof finished|model found|QED|FAIL|SUCCESS" $V/miter_tree.log | head -5
grep -E "\\\\in_a|\\\\in_b|\\\\in_c|gold_y|gate_y" $V/miter_tree.log | head -12
sed "s/mac_u_w8_tree_gate.v/mac_u_w8_norm_gate.v/; s/ gold gate miter/ gold gatenorm miter/" $V/miter.ys > $V/miter_norm.ys
timeout 300 "$Y" -q -l $V/miter_norm.log $V/miter_norm.ys >/dev/null 2>&1; echo "yosys sat (norm control) rc=$?"
grep -E "SAT proof finished|model found|QED|FAIL|SUCCESS" $V/miter_norm.log | head -5
