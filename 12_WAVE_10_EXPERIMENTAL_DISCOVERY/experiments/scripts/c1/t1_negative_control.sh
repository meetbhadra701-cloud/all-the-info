#!/usr/bin/env bash
# T1 negative control: the validation pipeline must reject a mutated netlist.
# Takes the E:initial adder netlist, turns its first NAND2x1 into a NOR2x1, and checks that
# c1_eval reports SIM_MISMATCH and that ABC &cec reports NOT EQUIVALENT.
set -u
G=/w/third_party/MappingEvolve/third-party/mockturtle/experiments/cell_libraries/asap7.genlib
O=/w/third_party/MappingEvolve/third-party/mockturtle/experiments/benchmarks
T=/w/experiments/outputs/c1/t1; mkdir -p $T
for b in ctrl i2c; do
  zcat /w/experiments/outputs/c1/d1/$b/E:initial.v.gz > $T/${b}_good.v
  awk 'BEGIN{d=0} /NAND2x1_ASAP7_75t_R/ && d==0 {sub("NAND2x1_ASAP7_75t_R","NOR2x1_ASAP7_75t_R"); d=1} {print}' $T/${b}_good.v > $T/${b}_mut.v
  diff $T/${b}_good.v $T/${b}_mut.v | head -4
  for k in good mut; do
    python3 /w/experiments/scripts/c1/c1_eval.py $G $O/$b.aig $T/${b}_$k.v $T/${b}_$k.blif | python3 -c "import json,sys; d=json.load(sys.stdin); print('$b $k', d['area'], d['delay'], d['sim_verdict'], d['cex'])"
    yosys-abc -q "read_blif $T/${b}_$k.blif; strash; write_aiger $T/${b}_${k}_mine.aig" > /dev/null 2>&1
    yosys-abc -q "&r $O/$b.aig; &cec $T/${b}_${k}_mine.aig" 2>&1 | grep "Networks are"
  done
done
