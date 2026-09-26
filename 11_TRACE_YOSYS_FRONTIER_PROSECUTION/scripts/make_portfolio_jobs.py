#!/usr/bin/env python3
"""Portfolio job list (W <= 32 first pass). Columns: job_id, rel_path, args (mode only), expected, note.
Only template-fitting netlists (mul, mac at natural width, dot2 at natural width); expected from ground truth.
Includes: Family A (norm, booth; W 8..32), A diagnostics (pre-ABC; folded pre-ABC unsigned Booth; low-power signed Booth),
Family B mac/dot2 (norm, tree; W 8..32) for MAIN, PATCH signed trees, B diagnostics at W 8/16, and all MUT netlists."""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
gt = list(csv.DictReader(open(os.path.join(ROOT, 'evidence', 'ground_truth.csv'))))
man = {r['design']: r for r in csv.DictReader(open(os.path.join(ROOT, 'rtl', 'manifest.csv')))}
rows = []


def add(rel, design, arch, build, expected, extra=''):
    m = man[design]
    W = int(m['widths'].split(',')[0])
    mode = {'mul': '-mul', 'mac': '-mac', 'dot2': '-dot=2'}[m['kind']]
    if 's' in m['signs']:
        mode += ' -s'
    rows.append({'job_id': f"pf__{build}__{design}__{arch}", 'rel_path': rel, 'args': mode, 'expected': expected,
                 'note': f"W={W};family={m['family']};build={build};arch={arch}{extra}"})


def fits(m):
    ws = [int(x) for x in m['widths'].split(',')]
    W, yw = ws[0], int(m['yw'])
    return ((m['kind'] == 'mul' and ws == [W, W] and yw == 2 * W) or
            (m['kind'] == 'mac' and ws == [W, W, 2 * W] and yw == 2 * W + 1) or
            (m['kind'] == 'dot2' and ws == [W] * 4 and yw == 2 * W + 1))


for r in gt:
    d, a, b = r['design'], r['arch'], r['build']
    m = man[d]
    if not fits(m):
        continue
    W = int(m['widths'].split(',')[0])
    if W > 32:
        continue
    fam = m['family']
    rel = f"netlists/{b}/{d}__{a}.aig"
    keep = False
    if fam == 'A' and a in ('norm', 'booth'):
        keep = True
    if fam == 'A' and W in (8, 16, 32) and a in ('norm_pre', 'booth_lp') or (fam == 'A' and a == 'booth_pre' and 's' in m['signs'] and W in (8, 16, 32)):
        keep = True
    if fam == 'B' and a in ('norm', 'tree'):
        keep = True
    if fam == 'B' and W in (8, 16) and a in ('tree_nofma', 'tree_fa', 'tree_ripple', 'tree_pre'):
        keep = True
    if fam == 'MUT':
        keep = True
    if keep:
        add(rel, d, a, b, r['oracle'])
# unsigned pre-ABC Booth: original crashes TRACE (constant-fanin AND); use the oracle-verified folded copies
for W in (8, 16, 32):
    add(f"netlists/CONTROL/A_mul_u_w{W}__booth_pre_folded.aig", f"A_mul_u_w{W}", 'booth_pre_folded', 'MAIN', 'CORRECT',
        ';derived=constant-folded copy of MAIN booth_pre')
rows.sort(key=lambda x: (int(x['note'].split('W=')[1].split(';')[0]), x['expected'] != 'CORRECT', x['job_id']))
out = os.path.join(ROOT, 'evidence', 'jobs_portfolio_w32.csv')
with open(out, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['job_id', 'rel_path', 'args', 'expected', 'note'])
    w.writeheader()
    w.writerows(rows)
from collections import Counter
print(len(rows), 'netlists ->', out)
print(Counter((r['note'].split('family=')[1].split(';')[0], r['expected']) for r in rows))
