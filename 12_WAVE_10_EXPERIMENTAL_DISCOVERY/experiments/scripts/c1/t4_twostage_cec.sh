#!/usr/bin/env bash
# T4: times two-stage CEC on hyp (original == compress2 AIG, then compress2 AIG == mapped netlist) against direct CEC.
G=/w/third_party/MappingEvolve/third-party/mockturtle/experiments/cell_libraries/asap7.genlib
O=/w/third_party/MappingEvolve/third-party/mockturtle/experiments/benchmarks/hyp.aig; C=/w/experiments/inputs/c1/c2/hyp.aig
T=/w/experiments/outputs/c1/t4; mkdir -p $T
zcat "/w/experiments/outputs/c1/d1/hyp/E:initial.v.gz" > $T/hyp_init.v
s=$(date +%s); python3 /w/experiments/scripts/c1/c1_eval.py $G $O $T/hyp_init.v $T/hyp_init.blif | cut -c1-160; echo "eval(isop) $(( $(date +%s)-s ))s"
yosys-abc -q "read_blif $T/hyp_init.blif; strash; print_stats; write_aiger $T/hyp_init_mine.aig" 2>&1 | tail -1
s=$(date +%s); timeout 1200 yosys-abc -q "cec -n -T 600 -C 100000 $C $T/hyp_init_mine.aig" 2>&1 | tail -1; echo "stageB c2==mine: $(( $(date +%s)-s ))s"
s=$(date +%s); timeout 1200 yosys-abc -q "cec -n -T 600 -C 100000 $O $C" 2>&1 | tail -1; echo "stageA orig==c2 (cec): $(( $(date +%s)-s ))s"
s=$(date +%s); timeout 1200 yosys-abc -q "&r $O; &cec $C" 2>&1 | tail -1; echo "stageA orig==c2 (&cec): $(( $(date +%s)-s ))s"
