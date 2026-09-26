#!/usr/bin/env bash
# Checks one C6 treatment directory: equivalence of after.v against before.v; writes equiv.txt (skips if it already exists).
d=/w/experiments/outputs/c6/asap7/aes/$1
[ -f $d/equiv.txt ] && { cat $d/equiv.txt; exit 0; }
[ -f $d/after.v ] || { echo "NO_AFTER_NETLIST" > $d/equiv.txt; cat $d/equiv.txt; exit 0; }
t0=$(date +%s)
v=$(bash /w/experiments/scripts/c6/c6_equiv.sh $d/before.v $d/after.v aes_cipher_top $d/equiv_yosys.log)
echo "$1 :: $v :: $(( $(date +%s)-t0 ))s" > $d/equiv.txt; cat $d/equiv.txt
