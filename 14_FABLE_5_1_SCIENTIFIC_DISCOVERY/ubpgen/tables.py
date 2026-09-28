"""Reproduce the R3 tables from one command (19_FINAL_UBP_DECISION.md, section H, Week 1).

python3 -m ubpgen.tables ubpgen/configs/suite_r3_tables.json [--run] [--only NAME,...]

For every design of the suite: generate -> golden compare -> pre-PnR verify -> frozen base -> each program
(route met4-met5, STA, post-PnR W@x, invariance) -> summary. Steps already recorded are not re-run (resumable).
Without --run, only existing records are tabulated. The table compares every measured value with the
historical R3 record (experiments/results/G2/r3/r3_results.jsonl); differences are listed, never hidden.
Output: ubpgen_runs/<suite>/tables.md and tables.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import config as C
from . import golden, pipeline
from .__main__ import RUNS
from ._legacy import ROOT

HIST = ROOT / 'experiments' / 'results' / 'G2' / 'r3'
HIST_KEYS = ('drt_final', 'drt_iterations_run', 'vias', 'setup_ws_ns', 'prog_setup_ws_ns')


def hist_records() -> dict:
    out = {}
    for line in (HIST / 'r3_results.jsonl').read_text().splitlines():
        r = json.loads(line)
        out[(r['design'], r['U'], r['tag'])] = r
    return out


def run_design(cfg, root: Path, tags: list[str], hist_nick: str | None = None) -> None:
    rec = root / 'records'
    if not (root / 'generation.json').exists():
        pipeline.generate(cfg, root)
    g = golden.compare(cfg, root) if cfg.fabric in golden.HIST else None
    if g is not None:
        rec.mkdir(exist_ok=True)
        (rec / 'golden_compare.json').write_text(json.dumps(g, indent=1))
    done_v = set()
    if (rec / 'verify.jsonl').exists():
        done_v = {json.loads(l)['result']['tag'] for l in (rec / 'verify.jsonl').read_text().splitlines()}
    todo = [t for t in tags if t not in done_v]
    if todo:
        bad = [r for r in pipeline.verify_prepnr(cfg, root, todo) if not r['pass']]
        if bad:
            raise RuntimeError(f'pre-PnR verification failed: {bad}')
    if not (rec / 'base.json').exists():
        pipeline.build_base(cfg, root)
    if hist_nick and not (rec / 'golden_physical.json').exists():
        (rec / 'golden_physical.json').write_text(json.dumps(golden.compare_physical(cfg, root, hist_nick), indent=1))
    done_p = set()
    if (rec / 'physical.jsonl').exists():
        done_p = {json.loads(l)['result']['tag'] for l in (rec / 'physical.jsonl').read_text().splitlines()}
    for t in tags:
        if t not in done_p:
            pipeline.run_program(cfg, root, t)


def tabulate(suite: dict, suite_dir: Path) -> dict:
    hist = hist_records()
    comp = suite['strongest_competitor_axt']
    rows, diffs, designs = [], [], {}
    for d in suite['designs']:
        cfg = C.load(suite_dir / d['config'])
        root = RUNS / cfg.name
        if not (root / 'records' / 'base.json').exists():
            continue
        s = pipeline.summarize(cfg, root, d.get('tags'))
        hd = d.get('historical_design')
        gold = json.loads((root / 'records' / 'golden_compare.json').read_text())['pass'] \
            if (root / 'records' / 'golden_compare.json').exists() else None
        hist_sha = d.get('historical_base_sha256')
        gp = root / 'records' / 'golden_physical.json'
        gphys = json.loads(gp.read_text()) if gp.exists() else None
        designs[cfg.name] = {'golden_physical': gphys and {k: gphys.get(k) for k in (
                                 'odb_sha256_identical', 'def_identical_except_header', 'components_differing', 'routed_nets_identical')},
                             'fabric': cfg.fabric, 'util': cfg.util, 'K': cfg.K, 'golden_inputs_pass': gold,
                             'base_odb_sha256': s['base']['odb_sha256'],
                             'base_odb_identical_to_historical': (s['base']['odb_sha256'] == hist_sha) if hist_sha else None,
                             'base': s['base'], 'T_established_ns': s.get('T_established_ns'),
                             'AxT_established': s.get('AxT_established'), 'AxT_robust': s.get('AxT_robust'),
                             'ratio_vs_strongest': comp / s['AxT_established'] if s.get('AxT_established') and cfg.fabric == 'ubp' else None,
                             'all_programs_pass': s.get('all_programs_pass')}
        for tag in d.get('tags', [p['tag'] for p in cfg.raw['programs']]):
            r = s['programs'].get(tag)
            if r is None:
                continue
            h = hist.get((hd, cfg.util, tag)) if hd else None
            row = {'design': cfg.name, 'tag': tag, **{k: r[k] for k in HIST_KEYS},
                   'wl_met4': r['wirelength_um'].get('met4'), 'wl_met5': r['wirelength_um'].get('met5'),
                   'post_pnr_numpy': r['post_pnr']['matches_numpy'], 'mutation': r['post_pnr']['oracle_mutation_detected'],
                   'invariants': r['invariance']['all_invariants_hold'], 'pass': r['pass']}
            if h:
                row['historical'] = {k: h[k] for k in HIST_KEYS} | {'wl_met4': h['wirelength_um']['met4'],
                                                                   'wl_met5': h['wirelength_um']['met5']}
                for k, v in row['historical'].items():
                    mine = row[k]
                    same = (abs(mine - v) < 1e-6) if isinstance(v, float) and mine is not None else mine == v
                    if not same:
                        diffs.append(f'{cfg.name} {tag} {k}: generated {mine} vs historical {v}')
            rows.append(row)
    bs = {n: d for n, d in designs.items() if d['fabric'] == 'ubp' and d['AxT_established']}
    cs = {n: d for n, d in designs.items() if d['fabric'] != 'ubp' and d['AxT_established']}
    matrix = {b: {c: cd['AxT_established'] / bd['AxT_established'] for c, cd in cs.items()} for b, bd in bs.items()}
    return {'designs': designs, 'programs': rows, 'differences_vs_historical': diffs, 'B_vs_measured_competitors': matrix}


def markdown(t: dict) -> str:
    L = ['# R3 tables reproduced by ubpgen', '',
         '| Design | U | K | Base DRC | Base setup / hold (ns) | Base ODB = historical | A×T | vs strongest (14.25e6) | All programs pass |',
         '|---|---|---|---|---|---|---|---|---|']
    for n, d in t['designs'].items():
        b = d['base']
        L.append(f"| {n} | {d['util']} | {d['K']} | {b['drc_final']} | {b['setup_ws_ns']:+.3f} / {b['hold_ws_ns']:+.3f} | "
                 f"{d['base_odb_identical_to_historical']} | {d['AxT_established'] or float('nan'):.4e} | "
                 + (f"{d['ratio_vs_strongest']:.3f}×" if d['ratio_vs_strongest'] else '— (competitor)')
                 + f" | {d['all_programs_pass']} |")
    L += ['', '| Design | W | DRT final (it.) | met4 / met5 WL (µm) | via4 | setup / prog-path WS (ns) | post-PnR = numpy, mutation | invariants | historical (it., met4 WL, prog WS) |',
          '|---|---|---|---|---|---|---|---|---|']
    for r in t['programs']:
        h = r.get('historical')
        hs = f"{h['drt_iterations_run']}, {h['wl_met4']:,.0f}, {h['prog_setup_ws_ns']:+.3f}" if h else '—'
        L.append(f"| {r['design']} | {r['tag']} | {r['drt_final']} ({r['drt_iterations_run']}) | {r['wl_met4']:,.0f} / {r['wl_met5']:,.0f} | "
                 f"{r['vias']} | {r['setup_ws_ns']:+.3f} / {r['prog_setup_ws_ns']:+.3f} | {r['post_pnr_numpy']}, {r['mutation']} | "
                 f"{r['invariants']} | {hs} |")
    if t.get('B_vs_measured_competitors'):
        comps = sorted({c for v in t['B_vs_measured_competitors'].values() for c in v})
        L += ['', '**B advantage over the competitors measured in this suite** (competitor A×T / B A×T, established rule):', '',
              '| B design | ' + ' | '.join(comps) + ' |', '|---|' + '---|' * len(comps)]
        for b, v in t['B_vs_measured_competitors'].items():
            L.append(f'| {b} | ' + ' | '.join(f'{v[c]:.3f}×' for c in comps) + ' |')
    L += ['', f"**Differences vs the historical records:** {len(t['differences_vs_historical'])}"]
    L += [f'- {x}' for x in t['differences_vs_historical']]
    return '\n'.join(L) + '\n'


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('suite')
    ap.add_argument('--run', action='store_true')
    ap.add_argument('--only')
    a = ap.parse_args(argv)
    sp = Path(a.suite).resolve()
    suite = json.loads(sp.read_text())
    only = set(a.only.split(',')) if a.only else None
    if a.run:
        for d in suite['designs']:
            cfg = C.load(sp.parent / d['config'])
            if only and cfg.name not in only:
                continue
            run_design(cfg, RUNS / cfg.name, d.get('tags', [p['tag'] for p in cfg.raw['programs']]), d.get('historical_nick'))
    t = tabulate(suite, sp.parent)
    out = RUNS / sp.stem
    out.mkdir(parents=True, exist_ok=True)
    (out / 'tables.json').write_text(json.dumps(t, indent=1))
    (out / 'tables.md').write_text(markdown(t))
    print(markdown(t))
    ok = all(d['all_programs_pass'] for d in t['designs'].values())
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
