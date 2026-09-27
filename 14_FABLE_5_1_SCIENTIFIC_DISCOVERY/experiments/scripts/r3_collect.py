"""R3 collector: evaluates every pre-registered R3 criterion (09_PREREGISTRATION.md, R3) for one utilization.

python3 r3_collect.py U   -> results/G2/r3/r3_summary_uU.json and a markdown summary on stdout
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

G2 = Path('results/G2')
CELL_AREA_B = 169952.0          # R3 base cell area (identical to R2; checked in 2_1_floorplan.log)
TAP_CREDIT = 128 * (10.0096 - 2.5024)
# established baselines (16_GATE2_FIXED_BASE.md, R2 §4.4): (cell area, U, cycles, T)
A75 = (356417.0, 0.75, 14, 3.0 - 0.853041)
P2_67 = (274662.0, 0.67, 8, 3.0 - (-1.568512431))


def axt(area, u, cyc, t):
    return area / u * cyc * t


def main(u: int):
    recs = [json.loads(line) for line in (G2 / 'r3' / 'r3_results.jsonl').read_text().splitlines() if line.strip()]
    recs = {r['tag']: r for r in recs if r['design'] == 'ubp3r3' and r['U'] == u}
    rep = json.loads((G2 / 'orfs' / 'logs' / 'sky130hd' / f'g2r3_ubp3r3_u{u}' / 'base' / '6_report.json').read_text())
    base_drc = None
    for line in (G2 / 'orfs' / 'logs' / 'sky130hd' / f'g2r3_ubp3r3_u{u}' / 'base' / '5_2_route.log').read_text().splitlines():
        if 'Number of violations =' in line:
            base_drc = int(line.split('=')[-1].strip().rstrip('.'))
    base_ws, base_hold = rep['finish__timing__setup__ws'], rep['finish__timing__hold__ws']
    tags = ['w1', 'w2', 'w3', 'w4', 'w5']
    have = [t for t in tags if t in recs]
    t_est = 3.0 - min(base_ws, recs['w1']['prog_setup_ws_ns']) if 'w1' in recs else None
    t_rob = 3.0 - min([base_ws] + [recs[t]['prog_setup_ws_ns'] for t in have]) if have else None
    a_credit = axt(A75[0] - TAP_CREDIT, *A75[1:])
    p_credit = axt(P2_67[0] - TAP_CREDIT, *P2_67[1:])
    strongest = min(a_credit, p_credit)
    b_est = axt(CELL_AREA_B, u / 100, 14, t_est) if t_est else None
    b_rob = axt(CELL_AREA_B, u / 100, 14, t_rob) if t_rob else None
    crit = {
        'all_five_programs_present': have == tags,
        'routability_all_zero_violations': all(recs[t]['drt_final'] == 0 for t in have) and have == tags,
        'invariance_all': all(recs[t]['invariance']['all_invariants_hold'] for t in have) and have == tags,
        'correctness_all': all(recs[t]['matches_numpy'] and recs[t]['mutation_detected'] for t in have) and have == tags,
        'advantage_established_rule': b_est is not None and b_est <= strongest / 1.5,
        'advantage_robustness_rule': b_rob is not None and b_rob <= strongest / 1.5,
        'timing_base_setup_hold_nonneg': base_ws >= 0 and base_hold >= 0,
        'timing_programmed_setup_nonneg': all(recs[t]['setup_ws_ns'] >= 0 for t in have) and have == tags,
        'base_drc_zero': base_drc == 0,
    }
    out = {'U': u, 'base_drc': base_drc, 'base_setup_ws': base_ws, 'base_hold_ws': base_hold,
           'T_established_ns': t_est, 'T_robust_ns': t_rob, 'AxT_B_established': b_est, 'AxT_B_robust': b_rob,
           'AxT_A75_credited': a_credit, 'AxT_P2_67_credited': p_credit, 'strongest_competitor': strongest,
           'threshold_AxT': strongest / 1.5,
           'ratio_vs_A75': a_credit / b_est if b_est else None, 'ratio_vs_P2_67': p_credit / b_est if b_est else None,
           'ratio_vs_A75_uncredited': axt(*A75) / b_est if b_est else None,
           'criteria': crit, 'PASS': all(crit.values()),
           'programs': {t: {k: recs[t][k] for k in ('drt_final', 'drt_iterations_run', 'grt', 'wirelength_um', 'vias',
                                                  'setup_ws_ns', 'hold_ws_ns', 'prog_setup_ws_ns', 'matches_numpy',
                                                  'mutation_detected')}
                        | {'invariants': recs[t]['invariance']['all_invariants_hold'],
                           'master_swaps': recs[t]['invariance']['n_master_swaps']} for t in have}}
    (G2 / 'r3' / f'r3_summary_u{u}.json').write_text(json.dumps(out, indent=1))
    print(f'## R3 at U{u}: base DRC {base_drc}, base setup/hold WS {base_ws:+.3f}/{base_hold:+.3f} ns')
    print('| W | DRT final (iterations) | GRT met4 / met5 usage (overflow) | met4 / met5 WL (µm) | vias | setup / hold / prog-path WS (ns) | = numpy | mutation | invariants (swaps) |')
    print('|---|---|---|---|---|---|---|---|---|')
    for t in have:
        r = recs[t]
        g = r['grt']
        print(f"| {t.upper()} | {r['drt_final']} ({r['drt_iterations_run']}) | {g['met4']['usage_pct']:.1f}% / {g['met5']['usage_pct']:.1f}% "
              f"({g['met4']['overflow'] + g['met5']['overflow']}) | {r['wirelength_um']['met4']:,.0f} / {r['wirelength_um']['met5']:,.0f} | {r['vias']} | "
              f"{r['setup_ws_ns']:+.3f} / {r['hold_ws_ns']:+.3f} / {r['prog_setup_ws_ns']:+.3f} | {r['matches_numpy']} | {r['mutation_detected']} | "
              f"{r['invariance']['all_invariants_hold']} ({r['invariance']['n_master_swaps']}) |")
    if b_est:
        print(f"\nT (established) {t_est:.4f} ns, T (robust) {t_rob:.4f} ns; A×T(B) {b_est:.4e} (robust {b_rob:.4e}); "
              f"threshold {strongest / 1.5:.4e}; ratio vs A75 {a_credit / b_est:.3f}, vs P2@67 {p_credit / b_est:.3f}")
    print('criteria:', json.dumps(crit))
    print('PASS' if out['PASS'] else 'FAIL')


if __name__ == '__main__':
    main(int(sys.argv[1]))
