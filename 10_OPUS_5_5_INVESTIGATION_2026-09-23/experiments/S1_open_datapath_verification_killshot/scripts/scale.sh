#!/usr/bin/env bash
# S1 kill-shot, part 2: scaling of open CEC engines on Yosys datapath architectures + &acec soundness mutants.
# Fail-closed verdicts: PASS / FAIL / UNDECIDED / TIMEOUT / ERROR, parsed from ABC's verdict text (never exit code).
set -u
S=/mnt/c/Users/meetb/Documents/Codex/2026-09-20/muxwise-experiment-1-zero-commitment-eda/outputs/muxwise-experiment-02/work/oss-cad-suite
ABC="$S/bin/yosys-abc"; Y="$S/bin/yosys"
WK=/mnt/c/Users/meetb/AppData/Local/Temp/claude/C--Users-meetb-Desktop-CLAUDE-OPUS-5-5-RESEARCH-CONTEXT/03476a4d-4e8a-44cd-9bcd-493130f6d087/scratchpad/s1/work
A=$WK/aig; L=$WK/cec_logs; mkdir -p "$L"
TMO=${TMO:-300}

# --- mutants (inequivalent by construction) for false-PASS test of &acec ---
for W in 8 16; do
  printf 'module top(input [%d:0] a, input [%d:0] b, input [%d:0] c, output [%d:0] y);\n  assign y = (a * b + c) ^ ({%d{1'"'"'b0}} | ((a[0] & b[%d]) << 5));\nendmodule\n' $((W-1)) $((W-1)) $((2*W-1)) $((2*W)) $((2*W+1)) $((W-1)) > $WK/rtl/macbug_u_w$W.v
  printf 'module top(input [%d:0] a0, input [%d:0] b0, input [%d:0] a1, input [%d:0] b1, output [%d:0] y);\n  assign y = (a0 * b0 + a1 * b1) ^ ({%d{1'"'"'b0}} | ((a0[0] & b1[%d]) << 3));\nendmodule\n' $((W-1)) $((W-1)) $((W-1)) $((W-1)) $((2*W)) $((2*W+1)) $((W-1)) > $WK/rtl/dot2bug_u_w$W.v
  for d in macbug_u dot2bug_u; do
    "$Y" -q -p "read_verilog $WK/rtl/${d}_w$W.v; synth -top top -arith_tree; aigmap; opt_clean; write_aiger -symbols -map $A/${d}_w${W}_tree.map $A/${d}_w${W}_tree.aig" >/dev/null 2>&1 || echo "SYNTH_ERROR $d w$W"
  done
done

check() { # id engine fileA fileB
  local id=$1 eng=$2 fa=$3 fb=$4 cmd
  case $eng in
    gcec)  cmd="&r $fa; &cec -T $TMO $fb";;
    acec)  cmd="&acec -T $TMO $fa $fb";;
    acecb) cmd="&acec -b -T $TMO $fa $fb";;
    cec)   cmd="cec -T $TMO $fa $fb";;
  esac
  local log="$L/${id}__${eng}.log" t0 t1 rc v mode
  t0=$(date +%s.%N)
  timeout $((TMO+60)) "$ABC" -c "$cmd" > "$log" 2>&1; rc=$?
  t1=$(date +%s.%N)
  if [ $rc -eq 124 ]; then v=TIMEOUT
  elif grep -q "Networks are NOT EQUIVALENT" "$log"; then v=FAIL
  elif grep -q "Networks are equivalent" "$log"; then v=PASS
  elif grep -qi "UNDECIDED\|undecided\|timed out\|time limit\|resource limit" "$log"; then v=UNDECIDED
  else v=ERROR; fi
  mode=-
  grep -q "Trying regular CEC" "$log" && mode=fallback_regular
  grep -q "Matching of adder trees in LHS and RHS succeeded" "$log" && mode=adder_tree_matched
  printf '%s,%s,%s,%.1f,%s,%d\n' "$id" "$eng" "$v" "$(echo "$t1 - $t0" | bc)" "$mode" "$rc"
}
export -f check; export ABC L TMO

jobs=()
for W in 16 24 32; do
  jobs+=("mul_u_w${W}_norm~booth gcec $A/mul_u_w${W}_norm.aig $A/mul_u_w${W}_booth.aig")
  jobs+=("mul_u_w${W}_norm~booth acecb $A/mul_u_w${W}_norm.aig $A/mul_u_w${W}_booth.aig")
  jobs+=("mul_s_w${W}_norm~booth gcec $A/mul_s_w${W}_norm.aig $A/mul_s_w${W}_booth.aig")
  jobs+=("mul_s_w${W}_norm~booth acecb $A/mul_s_w${W}_norm.aig $A/mul_s_w${W}_booth.aig")
  jobs+=("mac_u_w${W}_norm~tree gcec $A/mac_u_w${W}_norm.aig $A/mac_u_w${W}_tree.aig")
  jobs+=("mac_u_w${W}_norm~tree acec $A/mac_u_w${W}_norm.aig $A/mac_u_w${W}_tree.aig")
  jobs+=("dot2_u_w${W}_norm~tree gcec $A/dot2_u_w${W}_norm.aig $A/dot2_u_w${W}_tree.aig")
  jobs+=("dot2_u_w${W}_norm~tree acec $A/dot2_u_w${W}_norm.aig $A/dot2_u_w${W}_tree.aig")
done
for W in 8 16; do
  jobs+=("dot2_u_w${W}_norm~tree acec $A/dot2_u_w${W}_norm.aig $A/dot2_u_w${W}_tree.aig")
  jobs+=("MUT_macbug_u_w${W}_tree_vs_mac_norm acec $A/mac_u_w${W}_norm.aig $A/macbug_u_w${W}_tree.aig")
  jobs+=("MUT_macbug_u_w${W}_tree_vs_mac_norm gcec $A/mac_u_w${W}_norm.aig $A/macbug_u_w${W}_tree.aig")
  jobs+=("MUT_dot2bug_u_w${W}_tree_vs_dot2_norm acec $A/dot2_u_w${W}_norm.aig $A/dot2bug_u_w${W}_tree.aig")
  jobs+=("MUT_dot2bug_u_w${W}_tree_vs_dot2_norm gcec $A/dot2_u_w${W}_norm.aig $A/dot2bug_u_w${W}_tree.aig")
done
jobs+=("mac_u_w8_norm~tree acec $A/mac_u_w8_norm.aig $A/mac_u_w8_tree.aig")
echo "id,engine,verdict,seconds,acec_mode,rc"
printf '%s\n' "${jobs[@]}" | xargs -P 4 -L 1 bash -c 'check "$@"' _
