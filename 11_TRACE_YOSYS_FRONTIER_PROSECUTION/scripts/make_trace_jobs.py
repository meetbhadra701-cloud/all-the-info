#!/usr/bin/env python3
"""Build TRACE job lists from evidence/ground_truth.csv (+ manifest).

Only netlists with port_order_ok == True are scheduled. 'expected' comes from the independent oracle
(CORRECT / INCORRECT), never from TRACE. Mode selection follows TRACE's documented templates:
  mul -> -mul ; mac -> -mac ; dot2 -> -dot=2 ; signed designs add -s.
Designs whose operation has no TRACE template (dot2c, msub, and any shape that differs from the
template's natural widths) are scheduled with the closest template anyway and flagged
template_fit=NO so the result can be classified UNSUPPORTED rather than as a tool verdict.

Usage: make_trace_jobs.py <stage> <out.csv>
  stage1: core matrix, config '-dyn -p -c'
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
gt = list(csv.DictReader(open(os.path.join(ROOT, 'evidence', 'ground_truth.csv'))))
man = {r['design']: r for r in csv.DictReader(open(os.path.join(ROOT, 'rtl', 'manifest.csv')))}


def template(m):
    kind = m['kind']
    ws = [int(x) for x in m['widths'].split(',')]
    yw = int(m['yw'])
    W = ws[0]
    if kind == 'mul':
        return '-mul', (ws == [W, W] and yw == 2 * W)
    if kind == 'mac':
        return '-mac', (ws == [W, W, 2 * W] and yw == 2 * W + 1)
    if kind == 'dot2':
        return '-dot=2', (ws == [W] * 4 and yw == 2 * W + 1)
    if kind == 'msub':
        return '-mac', False
    if kind == 'dot2c':
        return '-dot=2', False
    return '', False


def main():
    stage, out = sys.argv[1], sys.argv[2]
    rows = []
    for r in gt:
        if r['port_order_ok'] != 'True':
            continue
        m = man[r['design']]
        mode, fit = template(m)
        W = int(m['widths'].split(',')[0])
        signed = 's' in m['signs']
        if stage == 'stage1':
            core_arch = {'A': ('norm', 'booth'), 'B': ('norm', 'tree'), 'C': ('norm', 'tree'),
                         'MUT': ('norm', 'tree', 'booth')}[r['family']]
            if r['arch'] not in core_arch:
                continue
            if r['family'] == 'A' and W not in (8, 16, 32, 64):
                continue
            if r['family'] == 'B' and W not in (8, 16, 32, 64):
                continue
            if r['family'] == 'C' and W not in (4, 8, 16):
                continue
            cfg = '-dyn -p -c'
        else:
            raise SystemExit('unknown stage')
        args = f"{mode}{' -s' if signed else ''} {cfg} -no-steps"
        tmo = 1800 if W >= 64 else 900
        jid = f"{stage}__{r['build']}__{r['design']}__{r['arch']}"
        rows.append({'job_id': jid, 'rel_path': f"netlists/{r['build']}/{r['design']}__{r['arch']}.aig",
                     'args': args, 'timeout_s': tmo, 'expected': r['oracle'],
                     'note': f"template_fit={'YES' if fit else 'NO'};family={r['family']};W={W}"})
    # schedule small widths first so early results are informative
    rows.sort(key=lambda x: (int(x['note'].split('W=')[1]), x['job_id']))
    with open(out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['job_id', 'rel_path', 'args', 'timeout_s', 'expected', 'note'])
        w.writeheader()
        w.writerows(rows)
    print(len(rows), 'jobs ->', out)


if __name__ == '__main__':
    main()
