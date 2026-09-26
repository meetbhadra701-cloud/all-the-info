#!/usr/bin/env python3
"""Generate the markdown tables used in INVESTIGATION_REPORT.md from RESULTS.csv / evidence/*.csv (no hand-typed numbers).
Output: evidence/report_tables.md"""
import csv
import os
import re
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
EV = os.path.join(ROOT, 'evidence')
R = list(csv.DictReader(open(os.path.join(ROOT, 'RESULTS.csv'))))
out = []


def secs(r):
    """Solve time: TRACE's own elapsed time when present and not affected by the clock jump, else wall."""
    if r.get('timing_note'):
        return None
    for k in ('trace_elapsed_s', 'wall_s'):
        try:
            return float(r[k])
        except (ValueError, TypeError):
            continue
    return None


def cell(rs):
    """Portfolio cell: best outcome over configurations for one netlist."""
    if not rs:
        return '–'
    by = Counter(r['class'] for r in rs)
    short = {'-dyn -p -c': 'dyn', '-idx -p -c': 'idx', '-ipc -p -c': 'ipc', '-igs -p -c': 'igs', '-ips -p -c': 'ips', '-igsm -p -c': 'igsm'}
    for want in ('FALSE_PASS', 'PASS', 'FAIL'):
        hit = [r for r in rs if r['class'] == want]
        if hit:
            best = min(hit, key=lambda r: secs(r) if secs(r) is not None else 1e9)
            t = secs(best)
            tag = {'PASS': 'PASS', 'FAIL': 'FAIL', 'FALSE_PASS': '**FALSE_PASS**'}[want]
            ts = f"{t:.0f} s" if t is not None and t >= 1 else ('<1 s' if t is not None else 't=n/a')
            return f"{tag} ({short.get(best['config'], best['config'])}, {ts})"
    if 'FALSE_FAIL' in by or 'FALSE_FAIL?' in by:
        return f"**FALSE_FAIL** ×{by.get('FALSE_FAIL', 0) + by.get('FALSE_FAIL?', 0)}, TIMEOUT ×{by.get('TIMEOUT', 0)}"
    if 'ERROR' in by:
        return 'ERROR (crash)'
    if set(by) == {'TIMEOUT'}:
        tmo = max(int(float(r['timeout_s'])) for r in rs)
        return f"TIMEOUT ×{len(rs)} (≤{tmo} s)"
    return ', '.join(f'{k}×{v}' for k, v in by.items())


def grid(title, stages, rows, widths, note=''):
    out.append(f'### {title}\n')
    if note:
        out.append(note + '\n')
    out.append('| netlist | ' + ' | '.join(f'W={w}' for w in widths) + ' |')
    out.append('|---|' + '---|' * len(widths))
    idx = defaultdict(list)
    for r in R:
        if r['stage'] in stages:
            idx[(r['build'], r['design'], r['arch'])].append(r)
    for label, key in rows:
        cells = []
        for w in widths:
            b, d, a = key(w)
            cells.append(cell(idx.get((b, d, a), [])))
        out.append(f'| {label} | ' + ' | '.join(cells) + ' |')
    out.append('')


# ---- Family A
WA = [8, 12, 16, 20, 24, 32, 64]
rowsA = []
for s in ('u', 's'):
    for a, lab in (('norm', 'default synth (post-ABC)'), ('booth', 'synth -booth (post-ABC)'), ('booth_lp', 'booth -lowpower (post-ABC)'),
                   ('norm_pre', 'default, pre-ABC'), ('booth_pre', 'booth, pre-ABC'), ('booth_pre_folded', 'booth, pre-ABC, const-folded')):
        if s == 'u' and a == 'booth_lp':
            continue
        if s == 's' and a == 'booth_pre_folded':
            continue
        if s == 'u' and a == 'booth_pre':
            continue   # the raw unsigned booth_pre crashes TRACE at every width (diag1/ctrlcrash); the folded copy is tabulated
        bld = 'CONTROL' if a == 'booth_pre_folded' else 'MAIN'
        rowsA.append((f'{"unsigned" if s == "u" else "signed"} · {lab}', (lambda w, s=s, a=a, bld=bld: (bld, f'A_mul_{s}_w{w}', a))))
grid('Family A — `y = a*b` (portfolio over six configurations, plus the longer/uncontended reruns; best outcome, solving configuration, TRACE time)',
     ('portfolio_w32', 'stage2_pre', 'w64post', 'long', 'long64'), rowsA, WA,
     'Unsigned `booth_pre` (raw) crashes TRACE at every width (constant-fan-in AND); the folded copy is the same function.')

# ---- Family B
WB = [8, 12, 16, 24, 32, 64]
rowsB = []
for k, kl in (('mac', 'a*b+c'), ('dot2', 'a*b+c*d')):
    for s in ('u', 's'):
        if k == 'dot2' and s == 's':
            continue
        for a, lab in (('norm', 'default (post-ABC)'), ('norm_pre', 'default, pre-ABC'), ('tree', 'arith_tree (post-ABC)'),
                       ('tree_pre', 'arith_tree, pre-ABC'), ('tree_nofma', 'arith_tree -no-fma'), ('tree_fa', 'arith_tree -strategy fa'),
                       ('tree_ripple', 'arith_tree -final ripple')):
            rowsB.append((f'MAIN {kl} {"u" if s == "u" else "s"} · {lab}', (lambda w, k=k, s=s, a=a: ('MAIN', f'B_{k}_{s}_w{w}', a))))
    if k == 'mac':
        for a, lab in (('tree', 'arith_tree (post-ABC)'), ('tree_pre', 'arith_tree, pre-ABC'), ('tree_fa', 'arith_tree -strategy fa'), ('tree_ripple', 'arith_tree -final ripple')):
            rowsB.append((f'PATCH a*b+c s · {lab}', (lambda w, a=a: ('PATCH', f'B_mac_s_w{w}', a))))
grid('Family B — fused arithmetic (MAIN = unpatched; PATCH = PR #6231; portfolio plus longer/uncontended reruns)', ('portfolio_w32', 'stage2_pre', 'w64post', 'long', 'long64'), rowsB, WB,
     'MAIN signed `a*b+c` trees (except `-no-fma`) are INCORRECT by the oracle (the real Yosys defect): FAIL is the correct outcome there. Signed `dot2` is excluded: `-dot=2 -s` ignores `-s` (every run a FALSE_FAIL; `dotspec` stage).')

# ---- Onset sweep
sw = [r for r in R if r['stage'] == 'sweep']
if sw:
    out.append('### Onset sweep (`y = a*b`, W = 4..16, 60 s per configuration)\n')
    idx = defaultdict(list)
    for r in sw:
        idx[(r['design'].split('_w')[0], r['arch'], int(r['W']))].append(r)
    Ws = sorted({int(r['W']) for r in sw})
    out.append('| netlist | ' + ' | '.join(str(w) for w in Ws) + ' |')
    out.append('|---|' + '---|' * len(Ws))
    for d in ('A_mul_u', 'A_mul_s'):
        for a in ('norm', 'booth', 'booth_lp'):
            rs = [idx.get((d, a, w), []) for w in Ws]
            if not any(rs):
                continue
            def mark(x):
                if not x:
                    return '–'
                if any(r['class'] == 'PASS' for r in x):
                    return '✓'
                if all(r['class'] == 'TIMEOUT' for r in x):
                    return '⏱'
                return '/'.join(sorted({r['class'] for r in x}))
            out.append(f'| {d} {a} | ' + ' | '.join(mark(x) for x in rs) + ' |')
    out.append('\n✓ = proved by at least one of the configurations run; ⏱ = every configuration timed out.\n')

# ---- Stage-wise table
cec = {(r['build'], r['design'], r['arch']): r for r in csv.DictReader(open(os.path.join(EV, 'cec_pre_post.csv')))}
out.append('### Stage-wise certification: TRACE on the pre-ABC netlist + ABC `&cec` pre ≡ post\n')
out.append('| design (build) | W | TRACE on pre-ABC netlist | `&cec` pre≡post | TRACE directly on post-ABC |')
out.append('|---|---|---|---|---|')
idx = defaultdict(list)
for r in R:
    if r['stage'] in ('portfolio_w32', 'stage2_pre', 'w64post', 'long', 'long64', 'isolation'):
        idx[(r['build'], r['design'], r['arch'])].append(r)
for (b, d, a), c in sorted(cec.items(), key=lambda kv: (int(kv[0][1].split('_w')[1]), kv[0][1], kv[0][2])):
    W = d.split('_w')[1]
    pre_arch = a + '_pre'
    pre = idx.get((b, d, pre_arch), [])
    if (a == 'booth' and d.startswith('A_mul_u')) or a == 'booth_lp':
        # the raw pre-ABC Booth netlists crash TRACE (constant-fan-in AND); the constant-folded copy is the same function
        pre = idx.get(('CONTROL', d, pre_arch + '_folded'), []) or pre
    post = idx.get((b, d, a), [])
    cv = f"{c['verdict']} ({c['seconds']} s)" if c['verdict'] != 'MISSING' else 'no netlist (synthesis timeout)'
    out.append(f'| {d} {a} ({b}) | {W} | {cell(pre)} | {cv} | {cell(post)} |')
out.append('')

# ---- phase-optimisation defect evidence
ABBR = {'PASS': 'P', 'FAIL': 'F', 'FALSE_FAIL': '**FF**', 'FALSE_FAIL?': '**FF?**', 'FALSE_PASS': '**FP**', 'TIMEOUT': 't', 'ERROR': 'E',
        'UNSUPPORTED': 'U', 'UNKNOWN': '?'}
CFGS = ['-dyn -p -c', '-dyn -p', '-igs -p -c', '-igs -p', '-idx -p -c', '-dyn -c', '-dyn', '-igs -c', '-igs', '-idx -c', '-idx', '-idx -p', '-ipc -p -c', '-ips -p -c', '-igsm -p -c']
def cfg_table(title, rows_sel, label_of, note=''):
    sel = [r for r in R if rows_sel(r)]
    if not sel:
        return
    cfgs = [c for c in CFGS if any(r['config'] == c for r in sel)]
    out.append(f'### {title}\n')
    if note:
        out.append(note + '\n')
    out.append('| netlist (oracle) | ' + ' | '.join(f'`{c}`' for c in cfgs) + ' |')
    out.append('|---|' + '---|' * len(cfgs))
    grp = defaultdict(dict)
    for r in sel:
        grp[label_of(r)][r['config']] = ABBR.get(r['class'], r['class'])
    for lab in sorted(grp):
        out.append(f'| {lab} | ' + ' | '.join(grp[lab].get(c, '') for c in cfgs) + ' |')
    out.append('')

cfg_table('Phase-optimisation defect: natural netlists and mutants (P PASS, F FAIL, FF FALSE_FAIL, FP FALSE_PASS, t TIMEOUT)',
          lambda r: r['stage'] in ('mini', 'phaseopt_probe', 'contra', 'repro') and ('MUTX' in r['netlist'] or 'tree_pre' in r['netlist'] or 'repro' in r['netlist'])
          and 'contra_' not in r['netlist'] and 'xorself' not in r['netlist'],
          lambda r: f"{r['build'] or 'REPRO'}/{os.path.basename(r['netlist'])[:-4]} ({r['oracle_truth'][:4]})",
          'Mutants `…y{MSB}xor{lit}`: lit = sign bit of c (even literal) gives exactly `a*b + zext(c)`; odd literal = its complement; `xor1` = unconditional MSB flip. `_folded` = constant-folded (pattern removed).')
cx = [r for r in R if r['stage'] == 'ctx']
if cx:
    out.append('### Causal graft of the six-gate Yosys context into unrelated correct netlists (`ctx`, 55 graft positions)\n')
    out.append('| source netlist | grafts | ' + ' | '.join(f'`{c}` FF / P / t' for c in ('-dyn -p -c', '-igs -p -c', '-dyn -p', '-dyn -c')) + ' |')
    out.append('|---|---|---|---|---|---|')
    agg = defaultdict(lambda: defaultdict(Counter))
    npos = defaultdict(set)
    for r in cx:
        src = r['design'].split('__ctx')[0]
        agg[src][r['config']][r['class']] += 1
        npos[src].add(r['design'])
    for src in sorted(agg):
        cells = []
        for c in ('-dyn -p -c', '-igs -p -c', '-dyn -p', '-dyn -c'):
            k = agg[src][c]
            cells.append(f"{k.get('FALSE_FAIL', 0) + k.get('FALSE_FAIL?', 0)} / {k.get('PASS', 0)} / {k.get('TIMEOUT', 0)}")
        out.append(f'| {src} | {len(npos[src])} | ' + ' | '.join(cells) + ' |')
    out.append('')

# ---- ABC-step and gate-library isolation, onset at 40..64 bits, pre-ABC low-power Booth, calibration
def best_mark(rs):
    if not rs:
        return '–'
    if any(r['class'] == 'PASS' for r in rs):
        t = min((secs(r) for r in rs if r['class'] == 'PASS' and secs(r) is not None), default=None)
        return '✓' + (f' {t:.0f} s' if t is not None and t >= 1 else '')
    if all(r['class'] == 'TIMEOUT' for r in rs):
        return '⏱'
    return '/'.join(sorted({r['class'] for r in rs}))
ab = [r for r in R if r['stage'] == 'isolation' and r['job_id'].startswith('abcstep__')]
if ab:
    steps = ['strash', 'balance', 'rewrite', 'refactor', 'dc2', 'resyn2', 'fraig', 'dch', 'yosysnomap']
    out.append('### Which ABC step destroys verifiability? One ABC step applied to the pre-ABC netlist (`-dyn -p -c` and `-idx -p -c`; ✓ = proved by either)\n')
    out.append('`yosysnomap` = Yosys\'s default ABC script without the final technology mapping: `&fraig -x; scorr; dc2; dretime; strash; &dch -f`.\n')
    out.append('| pre-ABC source | ' + ' | '.join(steps) + ' | full `synth` (post-ABC) |')
    out.append('|---|' + '---|' * (len(steps) + 1))
    grp = defaultdict(lambda: defaultdict(list))
    for r in ab:
        d, arch, step = os.path.basename(r['netlist'])[:-4].split('__')
        grp[(d, arch)][step].append(r)
    post = {('A_mul_u_w8', 'booth_pre_folded'): ('MAIN', 'A_mul_u_w8', 'booth'), ('A_mul_s_w8', 'booth_lp_pre'): ('MAIN', 'A_mul_s_w8', 'booth_lp'),
            ('B_dot2_u_w16', 'norm_pre'): ('MAIN', 'B_dot2_u_w16', 'norm')}
    pidx = defaultdict(list)
    for r in R:
        if r['stage'] in ('portfolio_w32', 'long'):
            pidx[(r['build'], r['design'], r['arch'])].append(r)
    for key in sorted(grp):
        out.append(f'| {key[0]} {key[1]} | ' + ' | '.join(best_mark(grp[key].get(s, [])) for s in steps) + f' | {best_mark(pidx.get(post.get(key), []))} |')
    out.append('')
am = [r for r in R if r['stage'] == 'abcmap']
if am:
    libs = ['g_aig', 'g_gates', 'g_simple', 'default']
    out.append('### Does the ABC target gate library matter? (`synth … -noabc; abc -g <lib>; aigmap`; `default` is byte-identical to the real post-ABC netlist)\n')
    out.append('| design | ' + ' | '.join(libs) + ' |')
    out.append('|---|' + '---|' * len(libs))
    grp = defaultdict(lambda: defaultdict(list))
    for r in am:
        d, arch, lib = os.path.basename(r['netlist'])[:-4].split('__')
        grp[(d, arch)][lib].append(r)
    for key in sorted(grp):
        out.append(f'| {key[0]} {key[1]} | ' + ' | '.join(best_mark(grp[key].get(l, [])) for l in libs) + ' |')
    out.append('')
on = [r for r in R if (r['stage'] == 'isolation' and r['job_id'].startswith('onset__')) or r['stage'] in ('long64',)]
if on:
    out.append('### Onset of 64-bit pre-ABC cost (`-dyn -p -c`; W = 64 from `stage2_pre` under contention and `long64` uncontended)\n')
    out.append('| netlist | W=32 | W=40 | W=48 | W=56 | W=64 (900 s, contended) | W=64 (3600 s, uncontended) |')
    out.append('|---|---|---|---|---|---|---|')
    idx = defaultdict(list)
    for r in R:
        if r['stage'] in ('isolation', 'stage2_pre', 'long64') and r['arch'] in ('norm_pre', 'tree_pre') and r['design'].startswith(('B_mac_u', 'B_dot2_u')):
            if r['stage'] == 'stage2_pre' and r['config'] != '-dyn -p -c':
                continue
            idx[(r['design'].split('_w')[0], r['arch'], int(r['W']), r['stage'])].append(r)
    for d, a in (('B_mac_u', 'norm_pre'), ('B_mac_u', 'tree_pre'), ('B_dot2_u', 'tree_pre')):
        c32 = [r for r in R if r['stage'] == 'stage2_pre' and r['design'] == f'{d}_w32' and r['arch'] == a] or \
              [r for r in R if r['stage'] == 'portfolio_w32' and r['design'] == f'{d}_w32' and r['arch'] == a]
        cells = [best_mark(c32)] + [best_mark(idx.get((d, a, w, 'isolation'), [])) for w in (40, 48, 56)] + \
                [best_mark(idx.get((d, a, 64, 'stage2_pre'), [])), best_mark(idx.get((d, a, 64, 'long64'), []))]
        out.append(f'| {d} {a} | ' + ' | '.join(cells) + ' |')
    out.append('')
lp = [r for r in R if r['stage'] == 'isolation' and r['job_id'].startswith('lppre__')]
if lp:
    out.append('### Signed low-power Booth before ABC (`booth -lowpower`, no ABC)\n')
    out.append('| W | raw pre-ABC netlist | constant-folded copy | post-ABC (portfolio) | `&cec` pre ≡ post |')
    out.append('|---|---|---|---|---|')
    cecd = {(r['design'], r['arch']): r for r in csv.DictReader(open(os.path.join(EV, 'cec_pre_post.csv')))}
    for W in (8, 16, 32):
        raw = [r for r in lp if r['design'] == f'A_mul_s_w{W}' and r['arch'] == 'booth_lp_pre']
        fol = [r for r in lp if r['design'] == f'A_mul_s_w{W}' and r['arch'] == 'booth_lp_pre_folded']
        pst = [r for r in R if r['stage'] == 'portfolio_w32' and r['design'] == f'A_mul_s_w{W}' and r['arch'] == 'booth_lp']
        c = cecd.get((f'A_mul_s_w{W}', 'booth_lp'))
        rawm = 'ERROR (segfault)' if raw and all(r['class'] == 'ERROR' for r in raw) else best_mark(raw)
        out.append(f"| {W} | {rawm} | {best_mark(fol)} | {best_mark(pst)} | {c['verdict'] + ' (' + c['seconds'] + ' s)' if c else '–'} |")
    out.append('')
cal = [r for r in R if r['stage'] in ('calib', 'long64', 'long')]
if cal:
    out.append('### Longer or uncontended reruns of TIMEOUT results\n')
    out.append('| stage | netlist | configuration | budget | outcome | TRACE time | cgroup peak MiB |')
    out.append('|---|---|---|---|---|---|---|')
    for r in cal:
        t = secs(r)
        out.append(f"| {r['stage']} | {r['design']} {r['arch']} | `{r['config']}` | {r['timeout_s']} s | {r['class']} | {f'{t:.0f} s' if t is not None and r['class'] != 'TIMEOUT' else '–'} | {r['cgroup_peak_mib']} |")
    out.append('')

# ---- class totals per stage
out.append('### Class totals per stage (`RESULTS.csv`)\n')
classes = ['PASS', 'FAIL', 'FALSE_FAIL', 'FALSE_FAIL?', 'FALSE_PASS', 'TIMEOUT', 'UNSUPPORTED', 'ERROR', 'UNKNOWN']
out.append('| stage | ' + ' | '.join(classes) + ' | runs |')
out.append('|---|' + '---|' * (len(classes) + 1))
for st in sorted({r['stage'] for r in R}):
    c = Counter(r['class'] for r in R if r['stage'] == st)
    out.append(f'| {st} | ' + ' | '.join(str(c.get(k, 0)) for k in classes) + f' | {sum(c.values())} |')
c = Counter(r['class'] for r in R)
out.append('| **all** | ' + ' | '.join(str(c.get(k, 0)) for k in classes) + f' | {sum(c.values())} |\n')

open(os.path.join(EV, 'report_tables.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('wrote evidence/report_tables.md,', len(out), 'lines')
