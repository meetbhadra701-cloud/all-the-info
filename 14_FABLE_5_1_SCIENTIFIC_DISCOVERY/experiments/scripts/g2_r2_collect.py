"""Gate 2 / R2 collector: per (design, U) on the STRUCTURED bases, the pre-registered primary and secondary criteria,
modeled period and A×T; then the R2 conditions. python3 g2_r2_collect.py G2_DIR   (writes G2_DIR/g2_r2_summary.json)

Pre-registered (09_PREREGISTRATION.md, R2):
  primary   : base DRC 0 (met1-met3) and GRT overflow 0 on met4-met5 for all five W
  secondary : DRT (20 iterations) on the W with the largest GRT wirelength converges to 0 violations
  A×T       : G2 base synthesized cell area / U × cycles/word × T,
              T = 3.0 ns - min(final setup WS of the base, modeled WS of the W1-programmed netlist through programmable nets)
Sensitivity (NOT the pre-registered metric, reported alongside): T_base = 3.0 - base final setup WS (ignores the
programmable-path delay, which favours designs with heavily loaded lines).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

CELL_AREA = {'ubp3s': 169952, 'pc2': 274662, 'g1s': 356417}
CYCLES = {'ubp3s': 14, 'pc2': 8, 'g1s': 14}
NAME = {'ubp3s': 'B (UBP3-serial)', 'pc2': 'P2 (popcount)', 'g1s': 'A (g1-serial)'}


def grab(path: Path, pat: str):
    if not path.exists():
        return None
    m = re.findall(pat, path.read_text())
    return m[-1] if m else None


def main(g2: Path):
    screens = [json.loads(line) for line in (g2 / 'g2_grt_screen.jsonl').read_text().splitlines() if line.strip()]
    ver = [json.loads(line) for line in (g2 / 'g2_verification.jsonl').read_text().splitlines() if line.strip()]
    out = []
    for d in CELL_AREA:
        for u in sorted({s['util'] for s in screens if s['design'] == d and s.get('base') == 'structured'}, reverse=True):
            nick = f'g2s_{d}_u{u}'
            rep = g2 / 'orfs' / 'logs' / 'sky130hd' / nick / 'base' / '6_report.json'
            rj = json.loads(rep.read_text()) if rep.exists() else {}
            base_drc = grab(g2 / 'orfs' / 'logs' / 'sky130hd' / nick / 'base' / '5_2_route.log', r'Number of violations = (\d+)')
            sc = {s['tag']: s for s in screens if s['design'] == d and s.get('base') == 'structured' and s['util'] == u}
            ovf = {t: sum(int(x.split()[-1]) for x in (s['met4_usage_overflow'], s['met5_usage_overflow'])) for t, s in sc.items()}
            primary = (base_drc == '0' and len(ovf) == 5 and all(v == 0 for v in ovf.values()))
            hardest = max(sc, key=lambda t: sc[t]['grt_wl_um']) if sc else None
            drt = grab(g2 / d / f'prog_{hardest}_u{u}s_route.log', r'G2_RESULT drc=(\d+)') if hardest else None
            traj = None
            if hardest and (g2 / d / f'prog_{hardest}_u{u}s_route.log').exists():
                traj = [int(x) for x in re.findall(r'Number of violations = (\d+)', (g2 / d / f'prog_{hardest}_u{u}s_route.log').read_text())]
            sta = g2 / d / f'prog_w1_u{u}s_sta.log'
            ws_all = grab(sta, r'G2_TIMING setup_ws=(\S+)')
            ws_prog = grab(sta, r'G2_PROG_WS setup=(\S+)')
            base_ws = rj.get('finish__timing__setup__ws')
            rec = {'design': d, 'U': u, 'base_drc': base_drc, 'base_setup_ws': base_ws,
                   'base_hold_ws': rj.get('finish__timing__hold__ws'), 'grt_overflow': ovf,
                   'grt_wl_um': {t: s['grt_wl_um'] for t, s in sc.items()}, 'primary': primary,
                   'drt_W': hardest, 'drt_final': None if drt is None else int(drt), 'drt_trajectory': traj,
                   'secondary': None if drt is None else int(drt) == 0,
                   'modeled_ws_all_w1': None if ws_all is None else float(ws_all) * 1e9,
                   'modeled_ws_prog_w1': None if ws_prog is None or ws_prog == 'none' else float(ws_prog) * 1e9}
            if base_ws is not None and rec['modeled_ws_prog_w1'] is not None:
                T = 3.0 - min(base_ws, rec['modeled_ws_prog_w1'])
                area = CELL_AREA[d] / (u / 100)
                rec.update({'T_ns': round(T, 3), 'area_um2': round(area), 'AxT': area * CYCLES[d] * T,
                            'T_base_only_ns': round(3.0 - base_ws, 3), 'AxT_base_only': area * CYCLES[d] * (3.0 - base_ws)})
            rec['verified_post_pnr'] = sorted({v['tag'] for v in ver if v['design'] == d and f'u{u}s_' in v['netlist']
                                               and v['matches_numpy'] and v['mutation_detected']})
            out.append(rec)
    (g2 / 'g2_r2_summary.json').write_text(json.dumps(out, indent=1))
    print('| design | U | base DRC | primary (5 W GRT) | hardest W | DRT final (20 it) | T ns | A×T | A×T (T base-only) | verified |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    for r in out:
        axt = f"{r['AxT']:.3g}" if 'AxT' in r else '—'
        axb = f"{r['AxT_base_only']:.3g}" if 'AxT_base_only' in r else '—'
        print(f"| {NAME[r['design']]} | {r['U']} | {r['base_drc']} | {r['primary']} | {r['drt_W']} | {r['drt_final']} | "
              f"{r.get('T_ns', '—')} | {axt} | {axb} | {','.join(r['verified_post_pnr']) or '—'} |")


if __name__ == '__main__':
    main(Path(sys.argv[1]))
