"""Copy the small, provenance-bearing outputs of a suite run into the repository (ubpgen_runs/ is not committed).

python3 -m ubpgen.snapshot ubpgen/configs/suite_r3_tables.json ubpgen/results/week1
Per design: config.json, generation.json (git/tools/config hash + sha256 of every generated file), records/*
(base, verify, physical, golden comparisons, summary). Plus tables.md / tables.json. No netlists, ODBs or DEFs.
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
    for f in ('tables.md', 'tables.json'):
        p = RUNS / suite.stem / f
        if p.exists():
            shutil.copy(p, dest / f)
    print('snapshot ->', dest)


if __name__ == '__main__':
    main()
