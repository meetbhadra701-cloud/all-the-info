#!/usr/bin/env python3
"""Ground truth for netlists created after evidence/ground_truth.csv was written:
  * MAIN/PATCH netlists with a .map file that are not yet in ground_truth.csv (e.g. the 64-bit pre-ABC runs)
  * every derived netlist in netlists/CONTROL (port order inherited from the source netlist; the spec is taken
    from the design name embedded in the file name)
Same oracle as validate_netlists.py (exhaustive <= 20 input bits, else 4096 corner + 16384 random vectors).
Writes evidence/ground_truth_extra.csv."""
import csv, os, re, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import aigtool
import validate_netlists as vn

man = {r['design']: r for r in csv.DictReader(open(os.path.join(ROOT, 'rtl', 'manifest.csv')))}
done = {(r['build'], r['design'], r['arch']) for r in csv.DictReader(open(os.path.join(ROOT, 'evidence', 'ground_truth.csv')))}
rows = []

def row(build, design, arch, path, order_ok, derived=''):
    m = man[design]
    aig = aigtool.read_aig(path)
    t0 = time.time()
    res = aigtool.check(aig, aigtool.parse_spec(m['spec']))
    rows.append({'build': build, 'design': design, 'arch': arch, 'family': m['family'], 'spec': m['spec'],
                 'rtl_expectation': m['rtl_expectation'], 'ands': len(aig['ands']), 'port_order_ok': order_ok,
                 'oracle': res['status'], 'exhaustive': res.get('exhaustive'), 'vectors': res.get('vectors'),
                 'mismatches': res.get('mismatches'),
                 'first_mismatch': json.dumps(res.get('first_mismatch')) if res.get('first_mismatch') else '',
                 'oracle_seconds': round(time.time() - t0, 2), 'derived_from': derived})
    print(build, design, arch, res['status'], flush=True)

for build in ('MAIN', 'PATCH'):
    bdir = os.path.join(ROOT, 'netlists', build)
    for fn in sorted(os.listdir(bdir)):
        if not fn.endswith('.aig') or '__' not in fn:
            continue
        stem = fn[:-4]; design, arch = stem.split('__')
        if (build, design, arch) in done or not os.path.exists(os.path.join(bdir, stem + '.map')):
            continue
        m = man[design]
        widths = [int(x) for x in m['widths'].split(',')]
        aig = aigtool.read_aig(os.path.join(bdir, fn))
        ok, _, _ = vn.audit_map(os.path.join(bdir, stem + '.map'), widths, int(m['yw']), aig)
        row(build, design, arch, os.path.join(bdir, fn), ok)

cdir = os.path.join(ROOT, 'netlists', 'CONTROL')
for fn in sorted(os.listdir(cdir)):
    if not fn.endswith('.aig'):
        continue
    mm = re.search(r'((?:A|B|C)_[a-z0-9]+_[us]_w\d+(?:_y\d+)?)__([a-z_]+?)(?:_(folded|buffered|contra_\w+|xorself_\w+))?(?:__(y16xor\d+))?\.aig$', fn)
    design, arch = mm.group(1), mm.group(2)
    build = 'PATCH' if 'PATCH_' in fn else 'MAIN'
    src = os.path.join('netlists', build, f'{design}__{arch}.aig')
    row('CONTROL', design, fn[:-4], os.path.join(cdir, fn), 'inherited', src.replace(os.sep, '/'))

with open(os.path.join(ROOT, 'evidence', 'ground_truth_extra.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(len(rows), 'rows')
