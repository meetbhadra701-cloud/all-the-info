"""R3 fairness numbers: the pre-registered P2-R3 measurement (09, R3) plus the post-hoc driver-sizing what-if (D-R3.4).

python3 r3_fairness.py   -> results/G2/r3/fairness_summary.json and a markdown summary on stdout
All A×T use the established rule: base cell area / U × cycles × T, T = 3.0 − min(base final setup WS, program-path WS).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

G2 = Path('results/G2')
R3 = G2 / 'r3'
TAP_CREDIT = 128 * (10.0096 - 2.5024)
AREA = {'ubp3r3': 169952.0, 'pc2r3': 274662.0}
CYC = {'ubp3r3': 14, 'pc2r3': 8}


def axt(area, u, cyc, t):
    return area / u * cyc * t


def base_ws(nick):
    rep = json.loads((G2 / 'orfs' / 'logs' / 'sky130hd' / nick / 'base' / '6_report.json').read_text())
    return rep['finish__timing__setup__ws'], rep['finish__timing__hold__ws']


def base_drc(nick):
    drc = None
    for line in (G2 / 'orfs' / 'logs' / 'sky130hd' / nick / 'base' / '5_2_route.log').read_text().splitlines():
        if 'Number of violations =' in line:
            drc = int(line.split('=')[-1].strip().rstrip('.'))
    return drc


def whatif(d, t, u):
    log = (R3 / f'whatif_drivers_{d}_{t}_u{u}.log').read_text()
    b = re.search(r'WHATIF_BEFORE setup_ws=(\S+) hold_ws=(\S+) prog_ws=(\S+)', log)
    r = re.search(r'WHATIF_ROOTS n_roots=(\d+) upsized=(\d+) delta_area_um2=(\S+) masters=(.*)', log)
    a = re.search(r'WHATIF_AFTER setup_ws=(\S+) hold_ws=(\S+) prog_ws=(\S+)', log)
    return {'prog_ws_before_ns': float(b.group(3)) * 1e9, 'prog_ws_after_ns': float(a.group(3)) * 1e9,
            'n_roots': int(r.group(1)), 'upsized': int(r.group(2)), 'delta_area_um2': float(r.group(3)),
            'root_masters': r.group(4).strip()}


def main():
    a75 = axt(356417.0 - TAP_CREDIT, 0.75, 14, 3.0 - 0.853041)
    p2_67 = axt(274662.0 - TAP_CREDIT, 0.67, 8, 3.0 + 1.568512431)
    s = {u: json.loads((R3 / f'r3_summary_u{u}.json').read_text()) for u in (52, 60)}
    b = {52: s[52]['AxT_B_established'], 60: s[60]['AxT_B_established']}
    b_rob = {52: s[52]['AxT_B_robust'], 60: s[60]['AxT_B_robust']}

    # --- pre-registered P2-R3 measurement at U67 ---
    nick = 'g2r3_pc2r3_u67'
    p_ws, p_hold = base_ws(nick)
    recs = [json.loads(x) for x in (R3 / 'r3_results.jsonl').read_text().splitlines() if x.strip()]
    w4 = [r for r in recs if r['design'] == 'pc2r3' and r['tag'] == 'w4'][-1]
    sta_w1 = (G2 / 'pc2r3' / 'prog_w1_u67r_sta.log').read_text()
    w1_prog = float(re.search(r'G2_PROG_WS setup=(\S+)', sta_w1).group(1)) * 1e9
    ver = [json.loads(x) for x in (G2 / 'g2_verification.jsonl').read_text().splitlines()
           if '"design": "pc2r3"' in x and 'prog_w1_u67r_programmed' in x][-1]
    grt = {}
    for t in ('w1', 'w2', 'w3', 'w4', 'w5'):
        rows = [json.loads(x) for x in (G2 / 'g2_grt_screen.jsonl').read_text().splitlines()
                if '"design": "pc2r3"' in x and f'"tag": "{t}"' in x]
        if rows:
            grt[t] = {k: rows[-1][k] for k in rows[-1] if k in ('grt_wl_um', 'met4_usage_overflow', 'met5_usage_overflow')}
    t_meas = 3.0 - min(p_ws, w1_prog)
    p2r3 = axt(AREA['pc2r3'], 0.67, 8, t_meas)
    p2r3_bo = axt(AREA['pc2r3'], 0.67, 8, 3.0 - p_ws)

    # --- post-hoc what-if (D-R3.4): spine-root drivers -> drive 4, both designs ---
    wi = {f'{d}_{t}_u{u}': whatif(d, t, u) for d, t, u in
          [('pc2r3', 'w1', 67), ('pc2r3', 'w4', 67), ('ubp3r3', 'w1', 52), ('ubp3r3', 'w5', 52),
           ('ubp3r3', 'w1', 60), ('ubp3r3', 'w4', 60), ('ubp3r3', 'w5', 60)]}
    da_p = wi['pc2r3_w1_u67']['delta_area_um2']
    p2r3_ds = axt(AREA['pc2r3'] + da_p, 0.67, 8, 3.0 - min(p_ws, wi['pc2r3_w1_u67']['prog_ws_after_ns']))
    p2r3_ds_w4 = axt(AREA['pc2r3'] + da_p, 0.67, 8, 3.0 - min(p_ws, wi['pc2r3_w4_u67']['prog_ws_after_ns']))
    da_b = wi['ubp3r3_w1_u52']['delta_area_um2']
    b_ds = {}
    for u, tags in ((52, ('w1', 'w5')), (60, ('w1', 'w4', 'w5'))):
        bws = s[u]['base_setup_ws']
        worst = min(wi[f'ubp3r3_{t}_u{u}']['prog_ws_after_ns'] for t in tags)
        b_ds[u] = {'T_W1_rule': 3.0 - min(bws, wi[f'ubp3r3_w1_u{u}']['prog_ws_after_ns']),
                   'T_worst_tested': 3.0 - min(bws, worst)}
        b_ds[u]['AxT_W1_rule'] = axt(AREA['ubp3r3'] + da_b, u / 100, 14, b_ds[u]['T_W1_rule'])
        b_ds[u]['AxT_worst_tested'] = axt(AREA['ubp3r3'] + da_b, u / 100, 14, b_ds[u]['T_worst_tested'])
    # a designer sizes the drivers only where it pays: best of as-built and sized, per density
    b_best = {u: min(b[u], b_ds[u]['AxT_W1_rule']) for u in (52, 60)}
    b_bo = {u: axt(AREA['ubp3r3'], u / 100, 14, 3.0 - s[u]['base_setup_ws']) for u in (52, 60)}

    comp = {'A75_credited': a75, 'P2_67_credited': p2_67, 'P2R3_67_measured': p2r3,
            'P2R3_67_driver_sized_whatif': p2r3_ds, 'P2R3_67_driver_sized_whatif_W4': p2r3_ds_w4,
            'P2R3_67_base_only_bound': p2r3_bo}
    out = {'P2R3_preregistered': {
               'U': 67, 'base_drc': base_drc(nick), 'base_setup_ws_ns': p_ws, 'base_hold_ws_ns': p_hold,
               'base_sha256': (R3 / 'base_sha256_pc2r3_u67.txt').read_text().split()[0],
               'grt_all_five': grt, 'largest_wl_program': 'w4',
               'w4_drt_final': w4['drt_final'], 'w4_drt_iterations': w4['drt_iterations_run'],
               'w4_invariants': w4['invariance']['all_invariants_hold'],
               'w4_matches_numpy': w4['matches_numpy'], 'w4_mutation_detected': w4['mutation_detected'],
               'w4_prog_ws_ns': w4['prog_setup_ws_ns'],
               'w1_prog_ws_ns': w1_prog, 'w1_matches_numpy': ver['matches_numpy'], 'w1_mutation_detected': ver['mutation_detected'],
               'T_ns': t_meas, 'AxT': p2r3, 'valid_point': base_drc(nick) == 0 and w4['drt_final'] == 0,
               'below_A75': p2r3 < a75,
               'P2R3_base_only_bound_AxT': p2r3_bo, 'P2_R2_base_only_bound_AxT_U60': 13.38e6},
           'whatif_driver_sizing_posthoc': wi, 'B_driver_sized': b_ds, 'B_best_of_as_built_and_sized': b_best,
           'B_base_only_bound': b_bo, 'B_as_built': b, 'B_as_built_robust': b_rob, 'competitors_AxT': comp,
           'ratios': {name: {'vs_B52_as_built': v / b[52], 'vs_B60_as_built': v / b[60], 'vs_B60_robust': v / b_rob[60],
                             'vs_B52_best': v / b_best[52], 'vs_B60_best': v / b_best[60]} for name, v in comp.items()},
           'both_base_only': {'U52': p2r3_bo / b_bo[52], 'U60': p2r3_bo / b_bo[60]}}
    (R3 / 'fairness_summary.json').write_text(json.dumps(out, indent=1))
    print('| Competitor (A×T, µm²·ns) | A×T | vs B 52% | vs B 60% (as built / robust) | vs B 60% (driver-sized) |')
    print('|---|---|---|---|---|')
    for name, v in comp.items():
        r = out['ratios'][name]
        print(f"| {name} | {v:.3e} | {r['vs_B52_best']:.3f} | {r['vs_B60_as_built']:.3f} / {r['vs_B60_robust']:.3f} | {v / b_ds[60]['AxT_W1_rule']:.3f} |")
    print(json.dumps({k: out['P2R3_preregistered'][k] for k in ('base_drc', 'w4_drt_final', 'w4_drt_iterations', 'T_ns',
                                                                  'AxT', 'valid_point', 'below_A75')}))
    print('B driver-sized:', json.dumps(b_ds))
    print('both base-only:', json.dumps(out['both_base_only']))


if __name__ == '__main__':
    main()
