#!/usr/bin/env python3
"""Ground truth for every synthesized netlist, independent of TRACE.

For each netlists/<BUILD>/<design>__<arch>.aig:
  1. port-order audit from the .map file: inputs must be a[0..], b[0..], ... in operand order,
     LSB first; outputs y[0..y_w-1] in order. Any deviation => ORDER_MISMATCH (not used for TRACE).
  2. functional check against the manifest's independent reference spec (aigtool.check):
     exhaustive if <= 20 input bits, else 4096 corner + 16384 random vectors.
Writes evidence/ground_truth.csv.
"""
import csv
import os
import sys
import json
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import aigtool  # noqa: E402

man = {r['design']: r for r in csv.DictReader(open(os.path.join(ROOT, 'rtl', 'manifest.csv')))}


def audit_map(path, widths, yw, aig=None):
    exp_in = []
    for name, w in zip('abcde', widths):
        exp_in += [(name, i) for i in range(w)]
    got_in, got_out = [], []
    for line in open(path):
        parts = line.split()
        if parts[0] == 'input':
            got_in.append((int(parts[1]), parts[3], int(parts[2])))
        elif parts[0] == 'output':
            got_out.append((int(parts[1]), parts[3], int(parts[2])))
    got_in.sort()
    got_out.sort()
    ins = [(n, b) for _, n, b in got_in]
    outs = [(n, b) for _, n, b in got_out]
    ok = ins == exp_in and outs == [('y', i) for i in range(yw)]
    if not ok and ins == exp_in and aig is not None and len(aig['outputs']) == yw:
        # Yosys omits constant-driven outputs from the -map file; accept only if the map lists y[0..k-1]
        # in order and every remaining AIG output is a literal constant (0 or 1).
        k = len(outs)
        if outs == [('y', i) for i in range(k)] and all(aig['outputs'][j] in (0, 1) for j in range(k, yw)):
            ok = True
    return ok, ins[:3], outs[:3]


def main():
    rows = []
    for build in ('MAIN', 'PATCH'):
        bdir = os.path.join(ROOT, 'netlists', build)
        if not os.path.isdir(bdir):
            continue
        for fn in sorted(os.listdir(bdir)):
            if not fn.endswith('.aig'):
                continue
            stem = fn[:-4]
            if '__' not in stem or not os.path.exists(os.path.join(bdir, stem + '.map')):
                continue
            design, arch = stem.split('__')
            m = man[design]
            widths = [int(x) for x in m['widths'].split(',')]
            yw = int(m['yw'])
            aig = aigtool.read_aig(os.path.join(bdir, fn))
            ok_order, fi, fo = audit_map(os.path.join(bdir, stem + '.map'), widths, yw, aig)
            t0 = time.time()
            res = aigtool.check(aig, aigtool.parse_spec(m['spec']))
            rows.append({'build': build, 'design': design, 'arch': arch, 'family': m['family'],
                         'spec': m['spec'], 'rtl_expectation': m['rtl_expectation'],
                         'ands': len(aig['ands']), 'port_order_ok': ok_order,
                         'oracle': res['status'], 'exhaustive': res.get('exhaustive'),
                         'vectors': res.get('vectors'), 'mismatches': res.get('mismatches'),
                         'first_mismatch': json.dumps(res.get('first_mismatch')) if res.get('first_mismatch') else '',
                         'oracle_seconds': round(time.time() - t0, 2)})
            print(build, stem, rows[-1]['oracle'], rows[-1]['port_order_ok'], flush=True)
    out = os.path.join(ROOT, 'evidence', 'ground_truth.csv')
    with open(out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print('wrote', out, len(rows))


if __name__ == '__main__':
    main()
