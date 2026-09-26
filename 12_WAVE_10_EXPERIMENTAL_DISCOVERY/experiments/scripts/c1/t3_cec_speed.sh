#!/usr/bin/env bash
# T3: compares CEC engines on the log2 E:initial netlist (own BLIF translation vs original AIG).
O=/w/third_party/MappingEvolve/third-party/mockturtle/experiments/benchmarks/log2.aig
T=/w/experiments/outputs/c1/t3; mkdir -p $T
cp "/w/experiments/outputs/c1/d1/log2/E:initial.blif" $T/log2_init.blif
yosys-abc -q "read_blif $T/log2_init.blif; print_stats; strash; print_stats; write_aiger $T/log2_mine.aig" 2>&1 | tail -2
yosys-abc -q "read_aiger $O; print_stats" 2>&1 | tail -1
s=$(date +%s); timeout 300 yosys-abc -q "cec -n -T 280 $O $T/log2_mine.aig" 2>&1 | tail -2; echo "cec -n: $(( $(date +%s)-s ))s"
s=$(date +%s); timeout 300 yosys-abc -q "read_blif $T/log2_init.blif; strash; dc2; write_aiger $T/log2_mine_dc2.aig" 2>&1|tail -1; yosys-abc -q "read_aiger $T/log2_mine_dc2.aig; print_stats" 2>&1 | tail -1; echo "dc2: $(( $(date +%s)-s ))s"
s=$(date +%s); timeout 300 yosys-abc -q "&r $O; &cec -T 280 $T/log2_mine_dc2.aig" 2>&1 | tail -2; echo "&cec dc2: $(( $(date +%s)-s ))s"
s=$(date +%s); timeout 300 yosys-abc -q "cec -n -T 280 $O $T/log2_mine_dc2.aig" 2>&1 | tail -2; echo "cec -n dc2: $(( $(date +%s)-s ))s"
C2=/w/experiments/inputs/c1/c2/log2.aig
s=$(date +%s); timeout 300 yosys-abc -q "&r $C2; &cec -T 280 $T/log2_mine.aig" 2>&1 | tail -2; echo "&cec vs compress2 AIG: $(( $(date +%s)-s ))s"
