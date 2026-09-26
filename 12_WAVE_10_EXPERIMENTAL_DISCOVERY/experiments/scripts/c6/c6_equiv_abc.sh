#!/usr/bin/env bash
# Wave 10 / C6 checker v3: combinational equivalence with register correspondence, done by ABC.
# Yosys lowers each netlist (ASAP7 liberty functional models, flattened) to BLIF, with flops as .latch named by their Q net.
# ABC `cec` (FRAIG + SAT) then treats latches as cut points matched BY NAME and compares all primary outputs and latch inputs.
# The verdict fails closed: PASS only on the literal "Networks are equivalent".
# usage (inside the container): c6_equiv_abc.sh <gold.v> <gate.v> <top> <workdir>
set -u
G=$1; T=$2; TOP=$3; W=$4; mkdir -p $W
L=/tmp/asap7lib; mkdir -p $L
for f in /OpenROAD-flow-scripts/flow/platforms/asap7/lib/NLDM/asap7sc7p5t_{AO_RVT_FF_nldm_211120,INVBUF_RVT_FF_nldm_220122,OA_RVT_FF_nldm_211120,SIMPLE_RVT_FF_nldm_211120}.lib.gz; do
  [ -f $L/$(basename $f .gz) ] || zcat $f > $L/$(basename $f .gz); done
cp -n /OpenROAD-flow-scripts/flow/platforms/asap7/lib/NLDM/asap7sc7p5t_SEQ_RVT_FF_nldm_220123.lib $L/ 2>/dev/null
LIBS=""; for f in $L/*.lib; do LIBS="$LIBS read_liberty -ignore_miss_func -ignore_miss_dir $f;"; done
for x in gold:$G gate:$T; do n=${x%%:*}; v=${x#*:}
  yosys -q -l $W/yosys_$n.log -p "$LIBS read_verilog $v; hierarchy -top $TOP; flatten; opt_clean; techmap; opt -fast; dffunmap; clean; write_blif $W/$n.blif" > /dev/null 2>&1 || { echo "EQUIV_ABC_LOWERING_FAILED ($n)"; exit 0; }
done
out=$(timeout 3600 yosys-abc -q "cec -T 3000 -C 1000000 $W/gold.blif $W/gate.blif" 2>&1 | tail -3 | tr '\n' ' ')
echo "$out" > $W/abc_cec.txt
if echo "$out" | grep -q "Networks are equivalent"; then echo "EQUIV_ABC_PASS | $out"; elif echo "$out" | grep -qE "NOT EQUIVALENT|Verification failed|Value in Network1"; then echo "EQUIV_ABC_NEQ | $out"; else echo "EQUIV_ABC_UNDECIDED | $out"; fi
