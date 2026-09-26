#!/usr/bin/env bash
# Wave 10 / C6: functional equivalence of a treated netlist (after.v) against the placed netlist (before.v).
# Yosys with ASAP7 liberty functional models; equiv_make / equiv_struct / equiv_simple / equiv_induct, registers matched by name.
# equiv_struct merges structurally identical logic, which is soundness-preserving, so only the changed cones reach SAT.
# v2: after flattening, the '<instance>.<pin>' wires of the liberty cells are hidden (rename -hide w:*.*), so matching uses only
# top-level net and port names. v1 matched those pin wires, which pin swapping in repair_timing legitimately changes (false NOT_PROVEN).
# Still sound: every matched point, including all primary outputs and register nets, must be proven.
# The verdict fails closed: PASS only if equiv_status -assert succeeds AND reports "Found N $equiv cells ... Of those cells N are proven".
# usage (inside the container): c6_equiv.sh <gold.v> <gate.v> <top> <logfile>
set -u
G=$1; T=$2; TOP=$3; LOG=$4
L=/tmp/asap7lib; mkdir -p $L
for f in /OpenROAD-flow-scripts/flow/platforms/asap7/lib/NLDM/asap7sc7p5t_{AO_RVT_FF_nldm_211120,INVBUF_RVT_FF_nldm_220122,OA_RVT_FF_nldm_211120,SIMPLE_RVT_FF_nldm_211120}.lib.gz; do
  [ -f $L/$(basename $f .gz) ] || zcat $f > $L/$(basename $f .gz); done
cp -n /OpenROAD-flow-scripts/flow/platforms/asap7/lib/NLDM/asap7sc7p5t_SEQ_RVT_FF_nldm_220123.lib $L/ 2>/dev/null
LIBS=""; for f in $L/*.lib; do LIBS="$LIBS read_liberty -ignore_miss_func -ignore_miss_dir $f;"; done
yosys -l $LOG -p "
  $LIBS
  read_verilog $G; hierarchy -top $TOP; flatten; opt_clean; rename -hide w:*.*; rename $TOP gold; design -stash gold;
  $LIBS
  read_verilog $T; hierarchy -top $TOP; flatten; opt_clean; rename -hide w:*.*; rename $TOP gate; design -stash gate;
  design -copy-from gold -as gold gold; design -copy-from gate -as gate gate;
  equiv_make gold gate equiv; hierarchy -top equiv;
  equiv_struct; equiv_simple -undef; equiv_induct -undef; equiv_status -assert" > /dev/null 2>&1
rc=$?
st=$(grep -E 'Of those cells|Unproven [$]equiv' $LOG | tail -3 | tr '\n' ' ')
if [ $rc -eq 0 ] && grep -q "Equivalence successfully proven" $LOG; then echo "EQUIV_PASS | $st"; else echo "EQUIV_NOT_PROVEN (yosys_rc=$rc) | $st"; fi
