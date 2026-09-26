#!/usr/bin/env bash
# E1: lower bound = minimum area with NO delay constraint over map's space (pure MaxSAT), ctrl, 600 s
W=/r/13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION; G=/r/12_WAVE_10_EXPERIMENTAL_DISCOVERY/third_party/MappingEvolve/third-party/mockturtle/experiments/cell_libraries/asap7.genlib
O=$W/experiments/outputs/e1/smoke; b=ctrl
E1_NOTIMING=1 E1_ENC=pb python3 $W/experiments/scripts/e1_exact.py $O/$b.dump.json $G 1e9 -1 600 $O/${b}_lb_notiming
[ -f $O/${b}_lb_notiming.v ] && bash $W/experiments/scripts/e1_eval_netlist.sh $b $O/${b}_lb_notiming.v
