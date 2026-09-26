#!/usr/bin/env bash
# Stage-wise decomposition test: (a) &cec between pre-ABC and post-ABC netlists derived from the SAME pre netlist;
# (b) algebraic backward rewriting (&polyn) on the pre-ABC netlist vs the post-ABC netlist.
S=/mnt/c/Users/meetb/Documents/Codex/2026-09-20/muxwise-experiment-1-zero-commitment-eda/outputs/muxwise-experiment-02/work/oss-cad-suite
ABC="$S/bin/yosys-abc"; Y="$S/bin/yosys"
WK=/mnt/c/Users/meetb/AppData/Local/Temp/claude/C--Users-meetb-Desktop-CLAUDE-OPUS-5-5-RESEARCH-CONTEXT/03476a4d-4e8a-44cd-9bcd-493130f6d087/scratchpad/s1/work
T=$WK/stage; mkdir -p $T; cd $T
TMO=${TMO:-120}
sigstr() { local n=$1 s="(" i; for ((i=0;i<n;i++)); do s+="$i*o$i"; [ $i -lt $((n-1)) ] && s+="+"; done; echo "$s)"; }
echo "design,W,arch,step,status,seconds,detail"
for W in ${W_LIST:-8 16 32}; do
 for d in mul_u mac_u dot2_u; do
  rtl=$WK/rtl/${d}_w$W.v
  [ -s $rtl ] || continue
  case $d in mul_u) nout=$((2*W)); exp=$((W*W));; mac_u) nout=$((2*W+1)); exp=$((W*W+2*W));; dot2_u) nout=$((2*W+1)); exp=$((2*W*W));; esac
  SIG=$(sigstr $nout)
  for arch in norm booth tree; do
   flag=""; [ $arch = booth ] && flag=-booth; [ $arch = tree ] && flag=-arith_tree
   b=${d}_w${W}_$arch
   "$Y" -q -p "read_verilog $rtl; synth -top top $flag -noabc; opt_clean; write_rtlil $b.pre.il" >/dev/null 2>&1 || { echo "$d,$W,$arch,synth,ERROR,,"; continue; }
   "$Y" -q -p "read_rtlil $b.pre.il; aigmap; opt_clean; write_aiger -symbols $b.pre.aig" >/dev/null 2>&1
   "$Y" -q -p "read_rtlil $b.pre.il; abc; opt -fast; aigmap; opt_clean; write_aiger -symbols $b.post.aig" >/dev/null 2>&1
   # (a) ABC step validation by generic CEC
   t0=$(date +%s.%N); timeout $((TMO+30)) "$ABC" -c "&r $b.pre.aig; &cec -T $TMO $b.post.aig" > $b.cec.log 2>&1; rc=$?; t1=$(date +%s.%N)
   v=ERROR; [ $rc -eq 124 ] && v=TIMEOUT; grep -q "Networks are equivalent" $b.cec.log && v=PASS; grep -q "NOT EQUIVALENT" $b.cec.log && v=FAIL
   printf '%s,%d,%s,cec_pre_vs_post,%s,%.1f,\n' $d $W $arch $v "$(echo "$t1-$t0"|bc)"
   # (b) algebraic rewriting on pre and post
   for st in pre post; do
     t0=$(date +%s.%N); timeout $TMO "$ABC" -c "&r $b.$st.aig; &polyn -S $SIG" > $b.$st.polyn.log 2>&1; rc=$?; t1=$(date +%s.%N)
     lf=$(grep -o "Left = [0-9]*" $b.$st.polyn.log | awk '{print $3}'); tt=$(grep -o "Total = [0-9]*" $b.$st.polyn.log | awk '{print $3}')
     v=OK; [ $rc -eq 124 ] && v=TIMEOUT; [ -z "$lf" ] && [ $v = OK ] && v=NO_RESULT
     printf '%s,%d,%s,polyn_%s,%s,%.1f,left=%s expected=%d total=%s\n' $d $W $arch $st $v "$(echo "$t1-$t0"|bc)" "${lf:--}" $exp "${tt:--}"
   done
  done
 done
done
