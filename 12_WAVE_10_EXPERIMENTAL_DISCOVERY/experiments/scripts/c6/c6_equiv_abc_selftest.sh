#!/usr/bin/env bash
# v3 (ABC) checker controls: identical must PASS; mutated must be NEQ; then the repair_timing netlist
T=/w/experiments/outputs/c6/asap7/aes/none_s1; O=/w/experiments/outputs/c6/equiv_v3_selftest; mkdir -p $O
awk 'BEGIN{d=0} /NAND2x1_ASAP7_75t_R/ && d==0 {sub("NAND2x1_ASAP7_75t_R","NOR2x1_ASAP7_75t_R"); d=1} {print}' $T/before.v > $O/mut.v
s=$(date +%s); echo "self:     $(bash /w/experiments/scripts/c6/c6_equiv_abc.sh $T/before.v $T/after.v aes_cipher_top $O/self) :: $(( $(date +%s)-s ))s"
s=$(date +%s); echo "mutated:  $(bash /w/experiments/scripts/c6/c6_equiv_abc.sh $T/before.v $O/mut.v aes_cipher_top $O/mut) :: $(( $(date +%s)-s ))s"
R=/w/experiments/outputs/c6/asap7/aes/repair_timing_s1
s=$(date +%s); echo "repair_timing_s1: $(bash /w/experiments/scripts/c6/c6_equiv_abc.sh $R/before.v $R/after.v aes_cipher_top $O/repair) :: $(( $(date +%s)-s ))s"
grep -c "^.latch" $O/self/gold.blif $O/repair/gate.blif 2>/dev/null
