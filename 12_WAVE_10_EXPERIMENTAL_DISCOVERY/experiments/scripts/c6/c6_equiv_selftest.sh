#!/usr/bin/env bash
# C6 checker self-test: before==before must PASS; before vs a mutated copy (one NAND2 -> NOR2) must NOT pass.
T=/w/experiments/outputs/c6/asap7/aes/none_s1
awk 'BEGIN{d=0} /NAND2x1_ASAP7_75t_R/ && d==0 {sub("NAND2x1_ASAP7_75t_R","NOR2x1_ASAP7_75t_R"); d=1} {print}' $T/before.v > /tmp/mut.v
diff $T/before.v /tmp/mut.v | head -3
echo "self:    $(bash /w/experiments/scripts/c6/c6_equiv.sh $T/before.v $T/after.v aes_cipher_top /w/experiments/outputs/c6/equiv_selftest_self.log)"
echo "mutated: $(bash /w/experiments/scripts/c6/c6_equiv.sh $T/before.v /tmp/mut.v aes_cipher_top /w/experiments/outputs/c6/equiv_selftest_mut.log)"
