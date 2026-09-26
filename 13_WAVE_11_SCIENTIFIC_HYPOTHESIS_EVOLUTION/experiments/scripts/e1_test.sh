#!/usr/bin/env bash
W=/r/13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION; G=/r/12_WAVE_10_EXPERIMENTAL_DISCOVERY/third_party/MappingEvolve/third-party/mockturtle/experiments/cell_libraries/asap7.genlib
O=$W/experiments/outputs/e1/smoke
for b in c17 ctrl; do
  D=$(python3 -c "import json; print(json.load(open('$O/$b.dump.json'))['delay'] + 0.001)")
  python3 $W/experiments/scripts/e1_exact.py $O/$b.dump.json $G $D -1 600 $O/${b}_exact_full
  bash $W/experiments/scripts/e1_eval_netlist.sh $b $O/${b}_map.v
  [ -f $O/${b}_exact_full.v ] && bash $W/experiments/scripts/e1_eval_netlist.sh $b $O/${b}_exact_full.v
done
