#!/usr/bin/env bash
W=/r/13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION; G=/r/12_WAVE_10_EXPERIMENTAL_DISCOVERY/third_party/MappingEvolve/third-party/mockturtle/experiments/cell_libraries/asap7.genlib
O=$W/experiments/outputs/e1/cpsat_test
for b in c17 ctrl; do
  python3 $W/experiments/scripts/e1_heur_control.py $W/experiments/outputs/e1/smoke/$b.dump.json $G $O/${b}_heurcover.v
  bash $W/experiments/scripts/e1_eval_netlist.sh $b $O/${b}_heurcover.v
done
