#!/usr/bin/env bash
# T0 smoke test: ABC help texts, and the driver + ABC netlist formats on c17 and adder.
set -u
B=/w/experiments/outputs/c1/bin; G=/w/third_party/MappingEvolve/third-party/mockturtle/experiments/cell_libraries/asap7.genlib
M=/w/third_party/MappingEvolve/third-party/mockturtle/experiments/benchmarks; C=/w/experiments/inputs/c1/c2
T=/w/experiments/outputs/c1/t0; mkdir -p $T



for b in c17 adder; do
  $B/drv_initial $G $C/$b.aig $T/${b}_init map 0
  yosys-abc -q "read_genlib $G; read_aiger $C/$b.aig; &get -n; &nf; &put; print_stats; write_verilog $T/${b}_nf.v" 2>&1 | tail -3
done
cat $T/c17_init.v; echo ----; cat $T/c17_nf.v
for b in c17 adder; do
  for k in init nf; do
    python3 /w/experiments/scripts/c1/c1_eval.py $G $M/$b.aig $T/${b}_$k.v $T/${b}_$k.blif
    yosys-abc -q "read_blif $T/${b}_$k.blif; strash; write_aiger $T/${b}_${k}_mine.aig" 2>&1 | tail -2
    yosys-abc -q "&r $M/$b.aig; &cec $T/${b}_${k}_mine.aig" 2>&1 | tail -2
    yosys-abc -q "cec -n $M/$b.aig $T/${b}_${k}_mine.aig" 2>&1 | tail -2
  done
done
