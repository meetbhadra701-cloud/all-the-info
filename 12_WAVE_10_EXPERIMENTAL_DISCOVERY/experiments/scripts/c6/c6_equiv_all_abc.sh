#!/usr/bin/env bash
# Runs checker v3 (ABC) on every completed C6 treatment (after.v vs before.v). Writes <dir>/equiv.txt. Re-runs the mutated control first.
B=/w/experiments/outputs/c6/asap7/aes; O=/w/experiments/outputs/c6/equiv_v3_selftest
echo "control mutated: $(bash /w/experiments/scripts/c6/c6_equiv_abc.sh $B/none_s1/before.v $O/mut.v aes_cipher_top $O/mut2 | cut -c1-120)"
for d in $B/*/; do t=$(basename $d)
  [ -f $d/metrics.json ] && [ -f $d/after.v ] || continue
  [ -f $d/equiv.txt ] && { cat $d/equiv.txt; continue; }
  s=$(date +%s); v=$(bash /w/experiments/scripts/c6/c6_equiv_abc.sh $d/before.v $d/after.v aes_cipher_top $d/equiv_abc)
  echo "$t :: $v :: $(( $(date +%s)-s ))s" | tee $d/equiv.txt
done
