#!/usr/bin/env bash
# E1: first CP-SAT test on ctrl at D0 (full space, 120 s), with the heuristic-cover fidelity control.
W=/r/13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION; G=/r/12_WAVE_10_EXPERIMENTAL_DISCOVERY/third_party/MappingEvolve/third-party/mockturtle/experiments/cell_libraries/asap7.genlib
O=$W/experiments/outputs/e1/cpsat_test; mkdir -p $O; b=ctrl
D0=$(python3 -c "import json; print(json.load(open('$W/experiments/outputs/e1/smoke/$b.dump.json'))['delay'] + 0.001)")
echo "D0=$D0 start $(date +%T)"
python3 $W/experiments/scripts/e1_cpsat.py $W/experiments/outputs/e1/smoke/$b.dump.json $G $D0 -1 ${T:-120} ${WK:-6} $O/${b}_D0_full
echo "solve done $(date +%T)"
for v in $O/${b}_D0_full_heur.v $O/${b}_D0_full.v $W/experiments/outputs/e1/smoke/${b}_map.v; do [ -f $v ] && bash $W/experiments/scripts/e1_eval_netlist.sh $b $v; done
grep -E "^#Bound|^#[0-9]+|^#Done|^#Model|^CpSolverResponse|best_bound|^status|^objective" $O/${b}_D0_full.solver.log | tail -25
