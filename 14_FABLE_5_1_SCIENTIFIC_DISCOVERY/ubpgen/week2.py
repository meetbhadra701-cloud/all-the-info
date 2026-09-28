"""Week-2 results: per-design physical summary and the kill / pass decision (21_WEEK2_TIMING_CLOSURE.md 1.7, 2.1).

python3 -m ubpgen.week2 [ubpgen/configs/suite_week2.json] [--out DIR]
    tabulates every design of the suite that has records; writes DIR/week2.json and DIR/week2.md
    (DIR defaults to ubpgen_runs/suite_week2). Nothing is run here; missing data is reported as missing.

Per design
  area (decisive)   A = the established floorplan instance area (every Week-2 tap is a physical cell in it: 2-site
                    pad + its buffer). The die is A / U; the flow's later sizing sits inside it.
  physical cost     flow sizing (accounting.py: resized input cells + resizer-inserted buffers, after synthesis) of the
                    design and of its unsized counterpart; the increment is the Week-2 policy's spine-sizing cost
  sensitivities     A_incr = A + increment; A_phys = input-netlist area + all flow sizing; A_conv = A with every tap at
                    2 sites (the historical convention). Reported, never decisive.
  timing            T(program, corner) = 3.0 ns - setup WNS of the merged, extracted base + program (signoff.py)
  A x T             A / U x cycles per word x T
                    nominal: tt, T of W1 (the established rule) and the worst of W1-W5
                    conservative (decisive): ss (the worst setup corner), the worst of W1-W5
  hold              min hold slack over W1-W5 at every corner; must be >= 0
  correct           every program: 0 DRT, frozen-base invariance, post-PnR netlist = numpy W@x with the oracle mutation
                    detected, and the pre-PnR check (numpy, oracle and program mutations)
Decision: R = min over the complete competitors of A x T_cons / A x T_cons(B); R < kill_ratio -> KILL.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import access, accounting, arch, config as C, orfs
from .__main__ import RUNS
from ._legacy import ROOT

CORNERS = ('tt', 'ss', 'ff')


def _latest(root: Path, name: str) -> dict:
    p = root / 'records' / name
    out = {}
    if p.exists():
        for line in p.read_text().splitlines():
            r = json.loads(line)['result']
            out[r['tag']] = r
    return out


def axt(area: float, util: int, cycles: int, t_ns: float) -> float:
    return area / (util / 100) * cycles * t_ns


def tap_sites(cfg) -> int:
    if access.w2(cfg):
        return access.tap_sites(cfg.raw['drivers']['tap_class'])
    return 2 if access.mode(cfg) == 'r3' else 8          # LTAP2 / LTAP


def accounting_record(cfg, root: Path) -> dict:
    p = root / 'records' / 'accounting.json'
    bdef = orfs.base_paths(cfg, root)['def']
    sha = (root / 'physical' / 'base_odb.sha256').read_text().split()[0]
    if p.exists():
        rec = json.loads(p.read_text())
        if rec.get('base_odb_sha256') == sha:
            return rec
    rec = {'base_odb_sha256': sha, **accounting.flow_changes(root, bdef)}
    p.write_text(json.dumps(rec, indent=1))
    return rec


def program_row(t: str, phys: dict, ver: dict, so: dict) -> dict:
    p, v, s = phys.get(t), ver.get(t), so.get(t)
    row = {'tag': t, 'routed': p is not None, 'signed_off': s is not None, 'prepnr_checked': v is not None}
    if p:
        row.update({'drt_final': p['drt_final'], 'drt_iterations_run': p['drt_iterations_run'],
                    'post_pnr_numpy': p['post_pnr']['matches_numpy'],
                    'post_pnr_oracle_mutation_detected': p['post_pnr']['oracle_mutation_detected'],
                    'invariance': p['invariance']['all_invariants_hold'], 'grt': p.get('grt'),
                    'wirelength_um': p.get('wirelength_um'), 'vias': p.get('vias'),
                    'placement_sta_setup_ws_ns': p.get('setup_ws_ns'), 'placement_sta_prog_ws_ns': p.get('prog_setup_ws_ns')})
    if v:
        row.update({'prepnr_numpy': v['matches_numpy'], 'prepnr_oracle_mutation_detected': v.get('oracle_mutation_detected'),
                    'prepnr_program_mutation_detected': v.get('program_mutation_detected')})
    if s:
        row['corners'] = {}
        for c in CORNERS:
            k = s['corners'][c]
            sp = k['setup_path']
            row['corners'][c] = {
                'T_ns': k['T_ns'], 'setup_ws_ns': k['setup_ws_ns'], 'hold_ws_ns': k['hold_ws_ns'],
                'prog_setup_ws_ns': k.get('prog_setup_ws_ns'),
                'critical': {'start': sp.get('startpoint'), 'end': sp.get('endpoint'),
                             'through_programmable_net': sp.get('through_programmable_net'),
                             'largest_stage': sp.get('largest_stage')},
                'tap_input_max_transition_ns': k.get('transitions', {}).get('tap_input_max_ns'),
                'site_input_max_transition_ns': k.get('transitions', {}).get('site_input_max_ns'),
                'spine_drivers': k.get('spine_drivers')}
    row['correct'] = bool(p and v and p['drt_final'] == 0 and p['post_pnr']['pass'] and p['invariance']['all_invariants_hold']
                          and v['pass'])
    return row


def counterpart_sizing(entry: dict, suite: dict, suite_dir: Path) -> dict | None:
    """Flow sizing of the unsized counterpart (another suite design, or a generated golden + a historical base DEF)."""
    cp = entry.get('counterpart')
    if not cp:
        return None
    if 'key' in cp:
        e = next(x for x in suite['designs'] if x['key'] == cp['key'])
        cfg = C.load(suite_dir / e['config'])
        root = RUNS / cfg.name
        if not (root / 'records' / 'base.json').exists():
            return None
        return {'design': cfg.name, **_sizing_summary(accounting_record(cfg, root))}
    cfg = C.load(suite_dir / cp['config'])
    root = RUNS / cfg.name
    bdef = (ROOT / cp['base_def']) if 'base_def' in cp else orfs.base_paths(cfg, root)['def']
    if not (root / 'netlist' / 'netlist_base.v').exists() or not bdef.exists():
        return None
    p = root / 'records' / 'accounting_counterpart.json'
    if p.exists():
        rec = json.loads(p.read_text())
    else:
        rec = {'base_def': str(bdef.relative_to(ROOT)) if bdef.is_relative_to(ROOT) else str(bdef),
               **accounting.flow_changes(root, bdef)}
        (root / 'records').mkdir(exist_ok=True)
        p.write_text(json.dumps(rec, indent=1))
    return {'design': cfg.name, 'base_def': rec['base_def'], **_sizing_summary(rec)}


def _sizing_summary(acct: dict) -> dict:
    ins = {k: v['count'] for k, v in acct['inserted'].items() if v['kind'].startswith('resizer')}
    return {'sizing_area_um2': acct['sizing_area_um2'], 'resized': acct['resized']['count'],
            'resizer_buffers': ins, 'input_area_um2': acct['input_area_um2']}


def design(entry: dict, suite: dict, suite_dir: Path, tags: list[str]) -> dict | None:
    cfg = C.load(suite_dir / entry['config'])
    root = RUNS / cfg.name
    if not (root / 'records' / 'base.json').exists():
        return None
    cfg = C.resolve(json.loads((root / 'config.json').read_text()))
    base = json.loads((root / 'records' / 'base.json').read_text())['result']
    acct = accounting_record(cfg, root)
    cps = counterpart_sizing(entry, suite, suite_dir)
    phys, ver, so = _latest(root, 'physical.jsonl'), _latest(root, 'verify.jsonl'), _latest(root, 'signoff.jsonl')
    progs = {t: program_row(t, phys, ver, so) for t in tags}
    cyc = arch.cycles_per_word(cfg)
    n_taps = arch.counts(cfg)['taps'] if access.mode(cfg) == 'r3' else len(arch.lines(cfg))
    ts = tap_sites(cfg)
    a_in = acct['input_area_um2']
    A = float(base['cell_area_um2'])                                  # the established floorplan instance area
    incr = acct['sizing_area_um2'] - cps['sizing_area_um2'] if cps else None
    areas = {'A_um2': A, 'input_um2': round(a_in, 1), 'flow_sizing_um2': acct['sizing_area_um2'],
             'counterpart_flow_sizing_um2': cps and cps['sizing_area_um2'], 'sizing_increment_um2': incr,
             'A_incr_um2': None if incr is None else round(A + incr, 1),
             'A_phys_um2': round(a_in + acct['sizing_area_um2'], 1),
             'conv_2site_um2': round(A - n_taps * (ts - 2) * access.SITE_AREA, 1),
             'taps': n_taps, 'tap_sites': ts, 'tap_area_um2': round(n_taps * ts * access.SITE_AREA, 1)}
    d = {'key': entry['key'], 'label': entry['label'], 'role': entry['role'], 'config': cfg.name,
         'fabric': cfg.fabric, 'access': access.mode(cfg), 'K': cfg.K, 'util': cfg.util, 'cycles_per_word': cyc,
         'driver_policy': cfg.raw['drivers']['policy'] + (f" ({cfg.raw['drivers']['tap_class']} taps, "
                                                           f"S = {cfg.raw['drivers']['slew_target_ns']} ns)" if access.w2(cfg) else ''),
         'tap_master': access.tap_master(cfg), 'base': {k: base.get(k) for k in (
             'odb_sha256', 'drc_final', 'setup_ws_ns', 'hold_ws_ns', 'core_area_um2', 'cell_area_um2', 'instance_count')},
         'tap_rule_verification': base.get('tap_rule_verification'), 'areas': areas, 'accounting': acct,
         'counterpart_sizing': cps,
         'programs': progs}
    signed = [t for t in tags if progs[t]['signed_off']]
    d['complete'] = len(signed) == len(tags) and all(progs[t]['routed'] for t in tags)
    d['correct'] = all(progs[t]['correct'] for t in tags)
    d['drc'] = {'base': base.get('drc_final'), 'programs_max': max((progs[t].get('drt_final', 0) or 0) for t in tags if progs[t]['routed'])
                if any(progs[t]['routed'] for t in tags) else None}
    if signed:
        T = {c: {t: progs[t]['corners'][c]['T_ns'] for t in signed} for c in CORNERS}
        worst = {c: max(T[c], key=T[c].get) for c in CORNERS}
        hold = {c: min(progs[t]['corners'][c]['hold_ws_ns'] for t in signed) for c in CORNERS}
        d['timing'] = {'T_ns': T, 'worst_program': worst, 'T_worst_ns': {c: T[c][worst[c]] for c in CORNERS},
                       'hold_min_ns': hold, 'hold_ok': all(h >= 0 for h in hold.values()),
                       'worst_corner': max(CORNERS, key=lambda c: T[c][worst[c]])}
        tw1 = T['tt'].get('w1')
        tn, tc = T['tt'][worst['tt']], T['ss'][worst['ss']]
        d['AxT'] = {'nominal_w1': axt(A, cfg.util, cyc, tw1) if tw1 else None, 'nominal_worst': axt(A, cfg.util, cyc, tn),
                    'conservative': axt(A, cfg.util, cyc, tc),
                    'conservative_A_incr': axt(areas['A_incr_um2'], cfg.util, cyc, tc) if areas['A_incr_um2'] else None,
                    'conservative_A_phys': axt(areas['A_phys_um2'], cfg.util, cyc, tc),
                    'conservative_conv_2site': axt(areas['conv_2site_um2'], cfg.util, cyc, tc),
                    'ff_worst': axt(A, cfg.util, cyc, T['ff'][worst['ff']])}
    return d


def decide(ds: dict, kill: float) -> dict:
    B = ds.get('B60')
    comps = [d for d in ds.values() if d and d['role'] == 'competitor']
    required = ['AR2', 'P2R3', 'P2R2']
    missing = [k for k in required if not (ds.get(k) and ds[k]['complete'])]
    out = {'kill_ratio': kill, 'missing': missing + ([] if B and B['complete'] else ['B60'])}
    if out['missing']:
        out['verdict'] = 'INCOMPLETE'
        return out
    full = [d for d in comps if d['complete']]

    def ratios(key, b):
        r = {d['key']: d['AxT'][key] / b['AxT'][key] for d in full if d['AxT'].get(key) and b['AxT'].get(key)}
        if not r:
            return None
        k = min(r, key=r.get)
        return {'R': r[k], 'strongest': k, 'all': r}
    out['conservative'] = ratios('conservative', B)
    out['nominal_w1'] = ratios('nominal_w1', B)
    out['nominal_worst'] = ratios('nominal_worst', B)
    out['sens_A_incr'] = ratios('conservative_A_incr', B)
    out['sens_A_phys'] = ratios('conservative_A_phys', B)
    out['sens_conv_2site'] = ratios('conservative_conv_2site', B)
    out['ff'] = ratios('ff_worst', B)
    B52 = ds.get('B52')
    if B52 and B52['complete']:
        out['B52_conservative'] = ratios('conservative', B52)
    out['B_valid'] = {'correct': B['correct'], 'hold_ok': B['timing']['hold_ok'],
                      'drc_zero': B['drc']['base'] == 0 and B['drc']['programs_max'] == 0}
    ok = all(out['B_valid'].values())
    out['verdict'] = 'PASSED' if (ok and out['conservative']['R'] >= kill) else 'KILL'
    return out


def _f(x, n=0):
    return '—' if x is None else f'{x:,.{n}f}'


def markdown(ds: dict, dec: dict) -> str:
    B = ds.get('B60')
    L = ['# Week 2 results (generated by `python3 -m ubpgen.week2`)', '']
    L += ['## Decision table (60%; A×T conservative = floorplan area / U × cycles × T(worst of W1–W5 at ss))', '',
          '| Design | U | Driver policy | Area (µm²) | Worst-program period (tt) | Worst-corner period (ss) | A×T | Relative to UBP | DRC | Correct |',
          '|---|---|---|---|---|---|---|---|---|---|']
    for d in ds.values():
        if d is None or d['role'] in ('B52',) or (d['key'] == 'B52_hist'):
            continue
        tm = d.get('timing')
        rel = (d['AxT']['conservative'] / B['AxT']['conservative']) if (tm and B and B.get('AxT')) else None
        L.append(f"| {d['label']} | {d['util']}% | {d['driver_policy']} | {_f(d['areas']['A_um2'])} | "
                 f"{_f(tm and tm['T_worst_ns']['tt'], 3)} ns ({tm and tm['worst_program']['tt']}) | "
                 f"{_f(tm and tm['T_worst_ns']['ss'], 3)} ns ({tm and tm['worst_program']['ss']}) | "
                 f"{_f(d.get('AxT', {}).get('conservative'), 0)} | {_f(rel, 2)}× | "
                 f"base {d['drc']['base']}, programs {d['drc']['programs_max']} | {'yes' if d['correct'] else 'NO'} |")
    L += ['', '## Per design and corner', '']
    L += ['| Design | Area A (floorplan) | flow sizing (increment vs unsized) | T tt W1 | T tt worst | T ss worst | T ff worst | hold min tt / ss / ff | A×T nominal (W1) | A×T conservative |',
          '|---|---|---|---|---|---|---|---|---|---|']
    for d in ds.values():
        if d is None or 'timing' not in d:
            continue
        tm, a = d['timing'], d['areas']
        L.append(f"| {d['label']} | {_f(a['A_um2'])} | {_f(a['flow_sizing_um2'])} ({_f(a['sizing_increment_um2'])}) | "
                 f"{_f(tm['T_ns']['tt'].get('w1'), 3)} | {_f(tm['T_worst_ns']['tt'], 3)} | {_f(tm['T_worst_ns']['ss'], 3)} | "
                 f"{_f(tm['T_worst_ns']['ff'], 3)} | {_f(tm['hold_min_ns']['tt'], 3)} / {_f(tm['hold_min_ns']['ss'], 3)} / "
                 f"{_f(tm['hold_min_ns']['ff'], 3)} | {_f(d['AxT']['nominal_w1'])} | {_f(d['AxT']['conservative'])} |")
    L += ['', '## Decision', '', '```', json.dumps(dec, indent=1), '```', '']
    return '\n'.join(L)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('suite', nargs='?', default=str(Path(__file__).resolve().parent / 'configs' / 'suite_week2.json'))
    ap.add_argument('--out')
    a = ap.parse_args(argv)
    sp = Path(a.suite).resolve()
    s = json.loads(sp.read_text())
    ds = {e['key']: design(e, s, sp.parent, s['tags']) for e in s['designs']}
    dec = decide(ds, s['kill_ratio'])
    out = Path(a.out) if a.out else RUNS / s['name']
    out.mkdir(parents=True, exist_ok=True)
    (out / 'week2.json').write_text(json.dumps({'designs': ds, 'decision': dec}, indent=1))
    (out / 'week2.md').write_text(markdown(ds, dec))
    print(json.dumps({k: (None if v is None else {'complete': v['complete'], 'correct': v['correct'],
                                                  'AxT_cons': v.get('AxT', {}).get('conservative')}) for k, v in ds.items()}))
    print(json.dumps({k: dec[k] for k in ('verdict', 'missing') if k in dec}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
