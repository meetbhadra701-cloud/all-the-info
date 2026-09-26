#!/usr/bin/env bash
# E1 negative control (pre-registered, run once): the validation path must reject functionally mutated solver netlists.
# Source netlist: the validated ctrl D0 CP-SAT solution from the infrastructure test (outputs/e1/cpsat_test/ctrl_D0_full.v).
W=/r/13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION; S=$W/experiments/outputs/e1/cpsat_test/ctrl_D0_full.v; O=$W/experiments/outputs/e1/negctrl; mkdir -p $O
cp $S $O/orig.v
# M1: first AND2x2 instance becomes OR2x2 (same pins A, B, Y), a different function
awk 'BEGIN{d=0} /AND2x2_ASAP7_75t_R/ && !d {sub(/AND2x2_ASAP7_75t_R/,"OR2x2_ASAP7_75t_R"); d=1} {print}' $S > $O/m1_and2_to_or2.v
# M2: first AO21x1 instance gets its A1 and B connections swapped (AO21 = A1&A2 | B, not symmetric in A1/B)
python3 - "$S" "$O/m2_ao21_pinswap.v" <<'PY'
import re, sys
src = open(sys.argv[1]).read().splitlines()
out, done = [], False
for l in src:
    if not done and "AO21x1_ASAP7_75t_R" in l:
        a1 = re.search(r"\.A1 \(([^)]*)\)", l).group(1); b = re.search(r"\.B \(([^)]*)\)", l).group(1)
        l = l.replace(".A1 (%s)" % a1, ".A1 (__TMP__)").replace(".B (%s)" % b, ".B (%s)" % a1).replace(".A1 (__TMP__)", ".A1 (%s)" % b)
        done = True
    out.append(l)
open(sys.argv[2], "w").write("\n".join(out) + "\n")
PY
diff $O/orig.v $O/m1_and2_to_or2.v | head -4; diff $O/orig.v $O/m2_ao21_pinswap.v | head -4
for v in orig m1_and2_to_or2 m2_ao21_pinswap; do bash $W/experiments/scripts/e1_eval_netlist.sh ctrl $O/$v.v; done
