"""Copy the small, provenance-bearing outputs of a suite run into the repository (ubpgen_runs/ is not committed).

python3 -m ubpgen.snapshot ubpgen/configs/suite_r3_tables.json ubpgen/results/week1
Per design: config.json, generation.json (git/tools/config hash + sha256 of every generated file), records/*
(base, verify, physical, sign-off, accounting, golden comparisons, summary) and the sign-off reports (Week 2).
Plus tables.md / tables.json (Week 1) or week2.md / week2.json (Week 2). No netlists, ODBs or DEFs.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from . import config as C
from .__main__ import RUNS


def main(argv=None):
    argv = argv or sys.argv[1:]
    suite, dest = Path(argv[0]).resolve(), Path(argv[1])
    dest.mkdir(parents=True, exist_ok=True)
    s = json.loads(suite.read_text())
    for d in s['designs']:
        cfg = C.load(suite.parent / d['config'])
        src, out = RUNS / cfg.name, dest / cfg.name
        if not src.exists():
            continue
        (out / 'records').mkdir(parents=True, exist_ok=True)
        for f in ('config.json', 'generation.json'):
            shutil.copy(src / f, out / f)
        for f in (src / 'records').glob('*'):
            shutil.copy(f, out / 'records' / f.name)
        # Week 2: the sign-off reports (critical paths, transitions, spine drivers; text, a few kB each)
        for f in sorted((src / 'programs').glob('*/signoff/*.log')) + sorted((src / 'programs').glob('*/signoff/signoff.json')):
            d = out / 'signoff' / f.parent.parent.name
            d.mkdir(parents=True, exist_ok=True)
            shutil.copy(f, d / f.name)
        for f in ('base_cli.log',):
            if (src / f).exists():
                shutil.copy(src / f, out / f)
    for f in ('tables.md', 'tables.json', 'week2.md', 'week2.json'):
        p = RUNS / suite.stem / f
        if p.exists():
            shutil.copy(p, dest / f)
    print('snapshot ->', dest)


if __name__ == '__main__':
    main()
