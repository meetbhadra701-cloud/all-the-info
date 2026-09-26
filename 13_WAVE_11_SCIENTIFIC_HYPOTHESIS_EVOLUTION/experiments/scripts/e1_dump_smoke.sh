#!/usr/bin/env bash
# E1 smoke test: dump the map search space for c17 and ctrl at required=0; compare the mapper's reported numbers with Wave 10's E:initial.
W=/r/13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION; G=/r/12_WAVE_10_EXPERIMENTAL_DISCOVERY/third_party/MappingEvolve/third-party/mockturtle/experiments/cell_libraries/asap7.genlib
C2=/r/12_WAVE_10_EXPERIMENTAL_DISCOVERY/experiments/inputs/c1/c2; O=$W/experiments/outputs/e1/smoke; mkdir -p $O
for b in c17 ctrl; do
  C1_DUMP=$O/$b.dump.json $W/experiments/bin/drv_dump $G $C2/$b.aig $O/${b}_map map 0
  python3 -c "import json; d=json.load(open('$O/$b.dump.json')); print('$b', 'nodes', len(d['nodes']), 'cands', sum(len(n['cands']) for n in d['nodes']), 'gates', len(d['gates']), 'delay', d['delay'], 'area', d['area'], 'pis', len(d['pis']), 'pos', len(d['pos']))"
done
/oss/bin/z3 --version
