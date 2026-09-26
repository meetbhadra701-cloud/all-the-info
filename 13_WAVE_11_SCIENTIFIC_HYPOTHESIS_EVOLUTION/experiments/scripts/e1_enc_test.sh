#!/usr/bin/env bash
# E1 encoding test on ctrl at D0: pb + difference constraints, with default and difference-logic arithmetic solvers (300 s each)
W=/r/13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION; G=/r/12_WAVE_10_EXPERIMENTAL_DISCOVERY/third_party/MappingEvolve/third-party/mockturtle/experiments/cell_libraries/asap7.genlib
O=$W/experiments/outputs/e1/smoke; b=ctrl
D=$(python3 -c "import json; print(json.load(open('$O/$b.dump.json'))['delay'] + 0.001)")
for ar in default 1; do
  if [ $ar = default ]; then unset E1_ARITH; else export E1_ARITH=$ar; fi
  E1_ENC=pb python3 $W/experiments/scripts/e1_exact.py $O/$b.dump.json $G $D -1 300 $O/${b}_exact_pb_ar$ar
done
E1_ENC=pb python3 $W/experiments/scripts/e1_exact.py $O/$b.dump.json $G $D 0.05 300 $O/${b}_exact_pb_eps005
