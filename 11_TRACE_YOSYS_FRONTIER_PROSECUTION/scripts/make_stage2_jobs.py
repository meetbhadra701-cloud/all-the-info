#!/usr/bin/env python3
"""Stage 2 (stage-wise hypothesis): TRACE portfolio on PRE-ABC netlists not covered by the W<=32 portfolio.
Stage-wise certification of a post-ABC netlist N_post = (TRACE proves N_pre against the spec) + (ABC &cec proves
N_pre == N_post). evidence/cec_pre_post.csv covers the second half; this job list covers the first half at the widths
the first portfolio did not reach. Columns as jobs_portfolio_w32b.csv. Expected verdicts from ground_truth*.csv."""
import csv, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..'))
gt = {}
for f in ('ground_truth.csv', 'ground_truth_extra.csv'):
    for r in csv.DictReader(open(os.path.join(ROOT, 'evidence', f))):
        gt[(r['build'], r['design'], r['arch'])] = r['oracle']
man = {r['design']: r for r in csv.DictReader(open(os.path.join(ROOT, 'rtl', 'manifest.csv')))}
rows = []
def add(build, design, arch, rel=None, extra=''):
    m = man[design]; W = int(m['widths'].split(',')[0])
    mode = {'mul': '-mul', 'mac': '-mac', 'dot2': '-dot=2'}[m['kind']] + (' -s' if 's' in m['signs'] else '')
    rel = rel or f"netlists/{build}/{design}__{arch}.aig"
    key = (build, design, arch) if not rel.startswith('netlists/CONTROL') else ('CONTROL', design, os.path.basename(rel)[:-4])
    rows.append({'job_id': f"s2__{build}__{design}__{arch}", 'rel_path': rel, 'args': mode, 'expected': gt[key],
                 'note': f"W={W};family={m['family']};build={build};arch={arch};stage2{extra}"})
# conventional MAC/dot pre-ABC (post-ABC signed conventional MAC timed out on every config at W=8)
for W in (8, 16, 32):
    for d in (f'B_mac_u_w{W}', f'B_mac_s_w{W}', f'B_dot2_u_w{W}'):
        add('MAIN', d, 'norm_pre')
# arith_tree pre-ABC at W=32 (W 8/16 are in the first portfolio)
for d, b in (('B_mac_u_w32', 'MAIN'), ('B_dot2_u_w32', 'MAIN'), ('B_mac_s_w32', 'PATCH'), ('B_mac_s_w32', 'MAIN')):
    add(b, d, 'tree_pre')
# 64-bit pre-ABC
for d, a in (('A_mul_u_w64', 'norm_pre'), ('A_mul_s_w64', 'norm_pre'), ('A_mul_s_w64', 'booth_pre'),
             ('B_mac_u_w64', 'tree_pre'), ('B_mac_u_w64', 'norm_pre'), ('B_dot2_u_w64', 'tree_pre')):
    add('MAIN', d, a)
add('MAIN', 'A_mul_u_w64', 'booth_pre_folded', rel='netlists/CONTROL/A_mul_u_w64__booth_pre_folded.aig',
    extra=';derived=constant-folded copy of MAIN booth_pre')
add('PATCH', 'B_mac_s_w64', 'tree_pre'); add('MAIN', 'B_mac_s_w64', 'tree_pre')
rows.sort(key=lambda x: (int(x['note'].split('W=')[1].split(';')[0]), x['expected'] != 'CORRECT', x['job_id']))
with open(os.path.join(ROOT, 'evidence', 'jobs_stage2_pre.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['job_id', 'rel_path', 'args', 'expected', 'note']); w.writeheader(); w.writerows(rows)
for r in rows: print(r['job_id'], r['expected'])
print(len(rows), 'netlists')
