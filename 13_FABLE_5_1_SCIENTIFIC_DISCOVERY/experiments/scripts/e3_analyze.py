"""Summarize E3 (regime-V gate level) against K3/ADV3. python3 e3_analyze.py ../results/E3/E3_results.json"""
from __future__ import annotations

import json
import sys


def main(path):
    d = json.load(open(path))
    comps = d['components']
    ok = all(v['aig_check'] and v['map_delay']['cec'] for v in comps.values())
    iso_ok = all(vv['cec'] for v in comps.values() for k, vv in v.items() if k.startswith('iso_'))
    print('# E3 summary: regime-(V) fabrics from weight-independent components (generated; do not edit)\n')
    print(f'Components: {len(comps)}; all independent AIG checks and ABC cec passed: {ok}; all iso-delay cec passed: {iso_ok}\n')
    print('SKY130 HD tt_025C_1v80; cell area only (via-select wiring excluded, see wire_model.txt).')
    print('Fabric area = m x TREE + generators + shared negators; iso-delay: every fabric\'s critical path <= D*.\n')
    ratios = {}
    for f in d['fabrics']:
        n = f['n']
        g1 = f['designs']['g1']['fabric_area_um2']
        print(f'## n = m = {n}; D* = {f["D_star"]:.0f} ps\n')
        print('| fabric | leaves/row | leaf bits | area mm^2 | g1_V / this | trees | generators | negators |')
        print('|---|---|---|---|---|---|---|---|')
        for k, v in f['designs'].items():
            p = v['parts']
            print(f"| {k} | {v['L']} | {v['w']} | {v['fabric_area_um2']/1e6:.3f} | {g1/v['fabric_area_um2']:.3f} | "
                  f"{p['trees']/1e6:.3f} | {p.get('gen', 0)/1e6:.3f} | {p['neg']/1e6:.3f} |")
        best = max(g1 / v['fabric_area_um2'] for k, v in f['designs'].items() if k != 'g1')
        ratios[n] = best
        print(f'\nbest g1_V/UBP_V at n={n}: **{best:.3f}**\n')
    print('## Pre-registered conditions\n')
    print(f"- K3 (best ratio < 1.3 at both n): {'KILL' if all(r < 1.3 for r in ratios.values()) else 'not triggered'}")
    print(f"- ADV3 (>= 1.5 at n = 1024): {'MET' if ratios.get(1024, 0) >= 1.5 else 'NOT MET'}")


if __name__ == '__main__':
    main(sys.argv[1])
