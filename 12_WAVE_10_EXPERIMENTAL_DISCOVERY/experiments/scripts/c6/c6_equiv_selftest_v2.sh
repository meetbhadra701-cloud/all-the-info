#!/usr/bin/env bash
# v2 checker self-test: identical must PASS; mutated must NOT pass; the repair_timing netlist is the case v1 failed on
T=/w/experiments/outputs/c6/asap7/aes/none_s1; O=/w/experiments/outputs/c6
awk 'BEGIN{d=0} /NAND2x1_ASAP7_75t_R/ && d==0 {sub("NAND2x1_ASAP7_75t_R","NOR2x1_ASAP7_75t_R"); d=1} {print}' $T/before.v > /tmp/mut.v
s=$(date +%s); echo "self:     $(bash /w/experiments/scripts/c6/c6_equiv.sh $T/before.v $T/after.v aes_cipher_top $O/equiv_v2_selftest_self.log) :: $(( $(date +%s)-s ))s"
s=$(date +%s); echo "mutated:  $(bash /w/experiments/scripts/c6/c6_equiv.sh $T/before.v /tmp/mut.v aes_cipher_top $O/equiv_v2_selftest_mut.log) :: $(( $(date +%s)-s ))s"
