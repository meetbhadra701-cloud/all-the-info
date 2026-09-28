"""ubpgen command line.  Run from 14_FABLE_5_1_SCIENTIFIC_DISCOVERY/:

  python3 -m ubpgen generate CONFIG [--out DIR]          # generate every artifact (no PnR)
  python3 -m ubpgen verify   CONFIG [--out DIR] [--tags w1,w2] [--no-mutations]   # pre-PnR W@x checks
  python3 -m ubpgen base     CONFIG [--out DIR]          # ORFS flow of the W-independent base, frozen (sha256)
  python3 -m ubpgen program  CONFIG [--out DIR] --tags w1,...   # route/STA/post-PnR check/invariance per program
  python3 -m ubpgen summary  CONFIG [--out DIR]          # A x T and per-program table
  python3 -m ubpgen all      CONFIG [--out DIR]          # generate -> verify -> base -> every program -> summary
  python3 -m ubpgen params                               # print the documented parameter table

DIR defaults to ubpgen_runs/<name> (not committed). Exit status is non-zero on any failed check.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import config as C
from . import pipeline

RUNS = Path(__file__).resolve().parent.parent / 'ubpgen_runs'


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog='ubpgen')
    ap.add_argument('cmd', choices=['generate', 'verify', 'base', 'program', 'summary', 'all', 'params'])
    ap.add_argument('config', nargs='?')
    ap.add_argument('--out')
    ap.add_argument('--tags')
    ap.add_argument('--no-mutations', action='store_true')
    a = ap.parse_args(argv)
    if a.cmd == 'params':
        for k, (d, doc) in C.PARAMS.items():
            print(f'{k:28s} default {d!r:24s} {doc}')
        return 0
    cfg = C.load(a.config)
    root = Path(a.out) if a.out else RUNS / cfg.name
    cdir = Path(a.config).resolve().parent
    tags = a.tags.split(',') if a.tags else None
    ok = True
    if a.cmd in ('generate', 'all'):
        g = pipeline.generate(cfg, root, cdir)
        print(json.dumps({'generated': str(root), 'counts': g['counts'], 'programs': g['programs']}))
    if a.cmd in ('verify', 'all'):
        for r in pipeline.verify_prepnr(cfg, root, tags, not a.no_mutations):
            print(json.dumps(r)); ok &= r['pass']
    if a.cmd in ('base', 'all') and ok:
        print(json.dumps(pipeline.build_base(cfg, root)))
    if a.cmd in ('program', 'all') and ok:
        for t in tags or [p['tag'] for p in cfg.raw['programs']]:
            r = pipeline.run_program(cfg, root, t)
            print(json.dumps({k: r[k] for k in ('tag', 'drt_final', 'drt_iterations_run', 'setup_ws_ns', 'prog_setup_ws_ns', 'pass')}))
            ok &= r['pass']
    if a.cmd in ('summary', 'all'):
        s = pipeline.summarize(cfg, root)
        print(json.dumps({k: v for k, v in s.items() if k != 'programs'}))
        ok &= s.get('all_programs_pass', False) if a.cmd == 'all' else True
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
