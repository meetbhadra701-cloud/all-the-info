#!/usr/bin/env bash
# E1 negative control, M1 re-done: the first attempt used OR2x2, which is not in asap7.genlib (the evaluator failed
# closed without a verdict line). M1b uses the library's OR2x4 (same pins A, B, Y), a real cell with a different function.
W=/r/13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION; S=$W/experiments/outputs/e1/cpsat_test/ctrl_D0_full.v; O=$W/experiments/outputs/e1/negctrl
awk 'BEGIN{d=0} /AND2x2_ASAP7_75t_R/ && !d {sub(/AND2x2_ASAP7_75t_R/,"OR2x4_ASAP7_75t_R"); d=1} {print}' $S > $O/m1b_and2_to_or2x4.v
diff $O/orig.v $O/m1b_and2_to_or2x4.v
bash $W/experiments/scripts/e1_eval_netlist.sh ctrl $O/m1b_and2_to_or2x4.v
python3 $W/experiments/scripts/c1_eval_w11.py /r/12_WAVE_10_EXPERIMENTAL_DISCOVERY/third_party/MappingEvolve/third-party/mockturtle/experiments/cell_libraries/asap7.genlib /r/12_WAVE_10_EXPERIMENTAL_DISCOVERY/third_party/MappingEvolve/third-party/mockturtle/experiments/benchmarks/ctrl.aig $O/m1_and2_to_or2.v $O/m1_tmp.blif 2>&1 | tail -2; rm -f $O/m1_tmp.blif
