#!/usr/bin/env python3
"""Regenerate every derived artefact from the raw results, in dependency order:
replay_all.py (witnesses for every Buggy verdict) -> classify.py (RESULTS.csv, portfolio_summary.csv)
-> replay_false_pass.py (oracle counterexamples for every FALSE_PASS) -> make_tables.py (evidence/report_tables.md)
-> splice the tables into INVESTIGATION_REPORT.md after the '<!-- TABLES -->' marker."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
for s in ('replay_all.py', 'classify.py', 'replay_false_pass.py', 'make_tables.py'):
    p = subprocess.run([sys.executable, os.path.join(HERE, s)], cwd=ROOT, capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    tail = (p.stdout or '').strip().splitlines()[-3:]
    print(f'{s}: exit {p.returncode}; ' + ' | '.join(tail))
    if p.returncode != 0:
        print(p.stderr[-2000:])
        sys.exit(1)
rep = os.path.join(ROOT, 'INVESTIGATION_REPORT.md')
txt = open(rep, encoding='utf-8').read()
marker = '<!-- TABLES -->'
head = txt.split(marker)[0]
tables = open(os.path.join(ROOT, 'evidence', 'report_tables.md'), encoding='utf-8').read()
open(rep, 'w', encoding='utf-8').write(head + marker + '\n\n' + tables)
print('tables spliced into INVESTIGATION_REPORT.md')
