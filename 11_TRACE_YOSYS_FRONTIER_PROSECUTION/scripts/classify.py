#!/usr/bin/env python3
"""Combine TRACE outputs with independent ground truth into the required result classes.

Inputs : evidence/trace_*_results.csv (trace_batch.py / trace_portfolio.py), evidence/ground_truth*.csv,
         evidence/witness_summary.csv (replay_all.py)
Outputs: RESULTS.csv                       one row per TRACE run (deduplicated by job_id, last row wins)
         evidence/portfolio_summary.csv    one row per (stage, netlist, TRACE mode): best verdict over configurations

Classes (per run)
  PASS         TRACE 'Correct' and the netlist is correct (oracle; 'exhaustive' where marked)
  FAIL         TRACE 'Buggy' and the netlist is incorrect w.r.t. the checked template; the remainder's witness replays
  FALSE_FAIL   TRACE 'Buggy' but the netlist is correct w.r.t. the checked template (witness spurious, or oracle
               exhaustive). FALSE_FAIL? = oracle not exhaustive and no spurious witness recorded
  FALSE_PASS   TRACE 'Correct' but the oracle replays a concrete mismatch against the checked template
  TIMEOUT      time or memory budget exhausted without a Result line (the basis says which)
  UNSUPPORTED  design intent is outside TRACE's templates (template_fit=NO); TRACE's raw result is reported, never
               counted as a verdict
  ERROR        no Result line and not a budget exhaustion (crash, invocation problem)
  UNKNOWN      insufficient evidence
Exit codes are never used as verdicts (TRACE exits 0 for both Correct and Buggy).
"""
import csv
import glob
import os
import re
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
EV = os.path.join(ROOT, 'evidence')


def load_gt():
    gt = {}
    def rd(name):
        p = os.path.join(EV, name)
        return list(csv.DictReader(open(p))) if os.path.exists(p) else []
    for r in rd('ground_truth.csv'):
        gt[f"netlists/{r['build']}/{r['design']}__{r['arch']}.aig"] = r
    for r in rd('ground_truth_extra.csv'):
        key = (f"netlists/CONTROL/{r['arch']}.aig" if r['build'] == 'CONTROL'
               else f"netlists/{r['build']}/{r['design']}__{r['arch']}.aig")
        gt[key] = r
    for name in ('ground_truth_mini.csv', 'ground_truth_sweep.csv'):
        for r in rd(name):
            gt[f"netlists/{r['build']}/{r['design']}__{r['arch']}.aig"] = r
    for r in rd('ground_truth_ctx.csv'):
        gt[r['netlist']] = r
    # the reproduction package holds byte-identical copies (see its README)
    rp = 'evidence/trace_phaseopt_minimal_repro/'
    if 'netlists/MINI_PATCH/B_mac_s_w3__tree_pre.aig' in gt:
        gt[rp + 'mac_s_w3_patched_noabc_CORRECT.aig'] = gt['netlists/MINI_PATCH/B_mac_s_w3__tree_pre.aig']
    if 'netlists/CONTROL/MUTX_PATCH_B_mac_s_w3__tree_pre__y6xor24.aig' in gt:
        gt[rp + 'mac_s_w3_zext_addend_mutant_INCORRECT.aig'] = gt['netlists/CONTROL/MUTX_PATCH_B_mac_s_w3__tree_pre__y6xor24.aig']
    return gt


GT = load_gt()
WIT = {}
_w = os.path.join(EV, 'witness_summary.csv')
if os.path.exists(_w):
    for r in csv.DictReader(open(_w)):
        WIT[r['job_id']] = r


def is_signed_dot(args):
    return '-dot=' in args and ' -s' in f' {args} '


def classify(row):
    note = row.get('note', '')
    fit = 'template_fit=NO' not in note
    st, res, exp = row['tool_status'], row['trace_result'].strip().lower(), row['expected']
    g = GT.get(row['rel_path'], {})
    exhaustive = str(g.get('exhaustive', '')) == 'True'
    wit = WIT.get(row['job_id'], {}).get('overall', '')
    if '-gen' in row['args'].split():
        return 'UNSUPPORTED', f'-gen (specification generation) prints no verdict and no polynomial in this build; tool_status={st}'
    if not fit:
        return 'UNSUPPORTED', f'template does not express the design intent; raw TRACE outcome={row["trace_result"] or st}'
    if st == 'TIMEOUT':
        return 'TIMEOUT', f'time budget {row["timeout_s"]} s exhausted (inner SIGKILL, monotonic clock)'
    if st == 'MEMOUT':
        m = re.search(r'mem=(\d+g)', note)
        return 'TIMEOUT', f'memory budget exhausted ({m.group(1) if m else "14g"} cgroup limit)'
    if st in ('KILLED', 'NO_RESULT'):
        lp = os.path.join(ROOT, 'logs', 'trace', row['job_id'] + '.log')
        txt = open(lp, 'rb').read().decode('utf-8', 'replace') if os.path.exists(lp) else ''
        crash = 'segfault: terminated by signal 11' if 'terminated by signal 11' in txt else st
        return 'ERROR', f'no Result line ({crash})'
    said_correct = res.startswith('correct')
    if not said_correct and not res.startswith('buggy'):
        return 'UNKNOWN', 'unrecognised TRACE result string: ' + row['trace_result']
    basis_truth = ('oracle exhaustive' if exhaustive else 'oracle 4096 corner + 16384 random') if g else 'jobs-file expectation (baseline/control)'
    if exp == 'CORRECT':
        if said_correct:
            return 'PASS', basis_truth
        if wit == 'WITNESS_CONFIRMED':
            # the netlist meets its design intent but violates the template TRACE was asked to check (a deliberate
            # wrong-flag control); the Buggy verdict is correct for the checked specification
            return 'FAIL', 'control: checked template differs from the design intent; witness replays against the template'
        extra = ' [DOT ignores -s]' if is_signed_dot(row['args']) else ''
        if wit == 'REMAINDER_INVALID' or exhaustive:
            return 'FALSE_FAIL', f'{basis_truth}; remainder replay: {wit or "n/a"}{extra}'
        return 'FALSE_FAIL?', f'{basis_truth}; remainder replay: {wit or "not run"}{extra}'
    if exp == 'INCORRECT':
        if said_correct:
            return 'FALSE_PASS', f'{basis_truth}; oracle mismatch replayed'
        if wit == 'WITNESS_CONFIRMED':
            return 'FAIL', 'remainder witness replays as a real mismatch'
        return 'FAIL', f'netlist incorrect ({basis_truth}); remainder replay: {wit or "not run"}'
    return 'UNKNOWN', 'no ground truth'


def parse_path(rel):
    m = re.search(r'netlists/([A-Z_]+)/([A-Za-z0-9_]+?)__([A-Za-z0-9_]+)\.aig$', rel)
    if m:
        return m.group(1), m.group(2), m.group(3)
    m = re.search(r'netlists/CONTROL/(?:ctx/)?(.+)\.aig$', rel)
    if m:
        return 'CONTROL', m.group(1), ''
    return '', os.path.basename(rel), ''


def main():
    out_rows = []
    for p in sorted(glob.glob(os.path.join(EV, 'trace_*_results.csv'))):
        stage = os.path.basename(p)[len('trace_'):-len('_results.csv')]
        last = {}
        for r in csv.DictReader(open(p)):
            last[r['job_id']] = r
        for r in last.values():
            cls, why = classify(r)
            g = GT.get(r['rel_path'], {})
            b, d, a = parse_path(r['rel_path'])
            W = re.search(r'W=(\d+)', r.get('note', ''))
            clock = ''
            try:
                if float(r['wall_s'] or 0) > float(r['timeout_s']) + 60:
                    clock = ('timing unreliable: wall time exceeds the budget by > 60 s (WSL clock resync of ~26,700 s, or '
                             'container start/teardown delay under load); TRACE itself was bounded by the in-container '
                             'timeout, so the verdict is unaffected')
            except ValueError:
                pass
            cfg = ' '.join(t for t in r['args'].split() if t in ('-dyn', '-idx', '-ipc', '-igs', '-ips', '-igsm', '-p', '-c'))
            out_rows.append({'stage': stage, 'job_id': r['job_id'], 'build': b, 'design': d, 'arch': a,
                             'W': W.group(1) if W else '', 'netlist': r['rel_path'], 'trace_args': r['args'], 'config': cfg,
                             'oracle_truth': r['expected'], 'oracle_exhaustive': g.get('exhaustive', ''),
                             'trace_result': r['trace_result'], 'tool_status': r['tool_status'],
                             'class': cls, 'class_basis': why, 'wall_s': r['wall_s'], 'trace_elapsed_s': r['trace_elapsed_s'],
                             'cgroup_peak_mib': r.get('cgroup_peak_mib', ''), 'max_polynomial': r['max_polynomial'],
                             'and_gates': r['and_gates'], 'timeout_s': r['timeout_s'], 'timing_note': clock, 'note': r['note']})
    with open(os.path.join(ROOT, 'RESULTS.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)
    for stage in sorted(set(r['stage'] for r in out_rows)):
        c = Counter(r['class'] for r in out_rows if r['stage'] == stage)
        print(f'{stage:<22}', dict(sorted(c.items())))
    print('ALL', dict(sorted(Counter(r['class'] for r in out_rows).items())), len(out_rows), 'runs')
    # portfolio view: per (stage, netlist, mode) the set of per-configuration classes
    grp = defaultdict(list)
    for r in out_rows:
        mode = ' '.join(t for t in r['trace_args'].split() if t in ('-mul', '-mac', '-add', '-s') or t.startswith('-dot='))
        grp[(r['stage'], r['netlist'], mode)].append(r)
    rank = ['FALSE_PASS', 'PASS', 'FAIL', 'FALSE_FAIL', 'FALSE_FAIL?', 'UNSUPPORTED', 'TIMEOUT', 'ERROR', 'UNKNOWN']
    summ = []
    for (stage, net, mode), rs in grp.items():
        cls = Counter(x['class'] for x in rs)
        best = next((c for c in rank if c in cls), 'UNKNOWN')
        solved = [x for x in rs if x['class'] in ('PASS', 'FAIL')]
        fastest = min(solved, key=lambda x: float(x['trace_elapsed_s'] or x['wall_s'] or 1e9)) if solved else None
        summ.append({'stage': stage, 'netlist': net, 'mode': mode, 'build': rs[0]['build'], 'design': rs[0]['design'],
                     'arch': rs[0]['arch'], 'W': rs[0]['W'], 'oracle_truth': rs[0]['oracle_truth'],
                     'portfolio_class': best, 'configs_run': len(rs),
                     'per_config': '; '.join(f"{x['config']}={x['class']}" for x in rs),
                     'first_solving_config': fastest['config'] if fastest else '',
                     'solve_wall_s': fastest['wall_s'] if fastest else '',
                     'any_false_pass': 'FALSE_PASS' in cls, 'any_false_fail': any(k.startswith('FALSE_FAIL') for k in cls)})
    with open(os.path.join(EV, 'portfolio_summary.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(summ[0].keys()))
        w.writeheader()
        w.writerows(sorted(summ, key=lambda s: (s['stage'], s['netlist'], s['mode'])))
    print(len(summ), 'netlist/mode groups -> evidence/portfolio_summary.csv')


if __name__ == '__main__':
    main()
