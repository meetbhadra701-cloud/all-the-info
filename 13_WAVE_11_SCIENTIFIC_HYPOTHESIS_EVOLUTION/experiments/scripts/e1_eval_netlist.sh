#!/usr/bin/env bash
# Independent validation of one netlist (Wave 10 evaluator): prints area, delay, sim verdict, CEC verdict (fail-closed).
# usage: e1_eval_netlist.sh <bench> <netlist.v>
B=$1; V=$2; P=${V%.v}
G=/r/12_WAVE_10_EXPERIMENTAL_DISCOVERY/third_party/MappingEvolve/third-party/mockturtle/experiments/cell_libraries/asap7.genlib
O=/r/12_WAVE_10_EXPERIMENTAL_DISCOVERY/third_party/MappingEvolve/third-party/mockturtle/experiments/benchmarks/$B.aig
E=$(python3 /r/13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION/experiments/scripts/c1_eval_w11.py $G $O $V $P.blif 2>&1 | tail -1)
yosys-abc -q "read_blif $P.blif; strash; write_aiger ${P}_mine.aig" >/dev/null 2>&1
C=$(yosys-abc -q "cec -n -T 600 -C 100000 $O ${P}_mine.aig" 2>&1 | grep -m1 "Networks are\|NOT EQUIV\|UNDECIDED" )
case "$C" in "Networks are equivalent"*) CV=PASS;; *"NOT EQUIVALENT"*) CV=NEQ;; *) CV=UNDECIDED;; esac
python3 -c "import json,sys; e=json.loads(sys.argv[1]); print(json.dumps({'bench':'$B','netlist':'$(basename $V)','area':e.get('area'),'delay':e.get('delay'),'instances':e.get('instances'),'sim':e.get('sim_verdict'),'cex':e.get('cex'),'cec':'$CV'}))" "$E"
rm -f $P.blif ${P}_mine.aig
