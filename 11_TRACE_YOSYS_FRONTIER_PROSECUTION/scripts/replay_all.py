#!/usr/bin/env python3
"""Replay every TRACE 'Buggy' verdict in evidence/trace_*results*.csv with an independent evaluator.

For each Buggy row:
  * the TEMPLATE spec is the specification TRACE was asked to check, rebuilt from its arguments and the netlist's
    I/O counts (-mul: y = a*b, W = I/2, O = 2W; -mac: F(2n+1) = A(n)*B(n) + S(2n); -dot=k: sum of k products;
    '-s' = two's complement for every operand and the output)
  * remainder_witness.py searches for a point where TRACE's remainder is non-zero (exhaustively when the netlist has
    <= 20 inputs) and replays that point on the netlist against the template spec
  * remainders containing the undocumented 'iK' variables are evaluated under both readings (complement, identity)
Writes counterexamples/<job_id>.json (one file per Buggy verdict) and evidence/witness_summary.csv.
WITNESS_CONFIRMED = the netlist really violates the template at that point (a genuine counterexample, which is a FAIL
if the template matches the design intent, and UNSUPPORTED if it does not); WITNESS_SPURIOUS / NO_NONZERO_POINT_FOUND
on an exhaustive search = the remainder does not describe a real mismatch (FALSE_FAIL evidence)."""
import csv, glob, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import aigtool

def template_spec(args, aig):
    I, O = aig['I'], len(aig['outputs'])
    s = ' -s' in f' {args} '
    if '-mul' in args.split():
        W = I // 2
        return f"mul:{'ss' if s else 'uu'}:{W},{W}:{O}"
    if '-mac' in args.split():
        n = I // 4
        return f"mac:{'sss' if s else 'uuu'}:{n},{n},{2*n}:{O}"
    m = re.search(r'-dot=(\d+)', args)
    if m and m.group(1) == '2':
        n = I // 4
        return f"dot2:{'ssss' if s else 'uuuu'}:{n},{n},{n},{n}:{O}"
    return None

def overall_of(rec):
    """Primary reading: 'iK' = complement of node K (1 - nK). Every Buggy verdict on an INCORRECT netlist whose remainder
    contains iK variables replays as a real mismatch under this reading (and not under the identity reading), which is
    how the reading was established. A remainder is called invalid only if the identity reading does not confirm either."""
    prim = rec.get('witness_complement', {}).get('verdict', 'SCRIPT_ERROR')
    ident = rec.get('witness_identity', {}).get('verdict')
    if prim == 'SCRIPT_ERROR' or ident == 'SCRIPT_ERROR':
        return 'SCRIPT_ERROR'
    if prim == 'WITNESS_CONFIRMED':
        return 'WITNESS_CONFIRMED'
    if ident == 'WITNESS_CONFIRMED':
        return 'AMBIGUOUS_IVAR_READING'
    w = rec['witness_complement']
    if prim == 'WITNESS_SPURIOUS' or w.get('exhaustive'):
        return 'REMAINDER_INVALID'
    return 'NO_WITNESS_FOUND'


def summary_row(r, rec):
    w0 = rec.get('witness_complement', {})
    return {'job_id': r['job_id'], 'netlist': r['rel_path'], 'args': r['args'], 'oracle': r['expected'],
            'template_spec': rec.get('template_spec', ''), 'i_vars': rec.get('i_vars', ''), 'overall': rec.get('overall', ''),
            'input_vector_hex': w0.get('input_vector_hex', ''), 'netlist_output': w0.get('netlist_output', ''),
            'template_reference': w0.get('reference', '')}


def main():
    os.makedirs(os.path.join(ROOT, 'counterexamples'), exist_ok=True)
    out = []
    seen = set()
    for f in sorted(glob.glob(os.path.join(ROOT, 'evidence', 'trace_*results*.csv'))):
        for r in csv.DictReader(open(f)):
            if not r['trace_result'].lower().startswith('buggy') or r['job_id'] in seen:
                continue
            seen.add(r['job_id'])
            cx = os.path.join(ROOT, 'counterexamples', r['job_id'] + '.json')
            if os.path.exists(cx) and '--force' not in sys.argv:
                try:
                    rec = json.load(open(cx))
                    rec['overall'] = overall_of(rec)
                    json.dump(rec, open(cx, 'w'), indent=1)
                    if rec['overall'] != 'SCRIPT_ERROR':
                        out.append(summary_row(r, rec))
                        print(f"{r['job_id']:<66} {rec['overall']} (cached)", flush=True)
                        continue
                except Exception:
                    pass
            log = os.path.join(ROOT, 'logs', 'trace', r['job_id'] + '.log')
            net = os.path.join(ROOT, r['rel_path'])
            aig = aigtool.read_aig(net)
            spec = template_spec(r['args'], aig)
            rec = {'job_id': r['job_id'], 'results_csv': os.path.basename(f), 'netlist': r['rel_path'], 'args': r['args'],
                   'expected_by_oracle': r['expected'], 'template_spec': spec}
            txt = open(log, 'rb').read().decode('utf-8', 'replace')
            has_i = bool(re.search(r'SP:\s*\{\d+\}[^\n]*\di\d|SP:\s*\{\d+\}[^\n]*[ -]i\d', re.sub(r'\x1b\[[0-9;]*m', '', txt)))
            readings = ['complement', 'identity'] if has_i else ['complement']
            for rd in readings:
                p = subprocess.run([sys.executable, os.path.join(HERE, 'remainder_witness.py'), log, net, spec, f'--i-means={rd}'],
                                   capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=3600)
                try:
                    rec['witness_' + rd] = json.loads((p.stdout or '').strip().splitlines()[-1])
                except Exception:
                    rec['witness_' + rd] = {'verdict': 'SCRIPT_ERROR', 'stderr': (p.stderr or '')[-600:]}
            rec['overall'] = overall_of(rec)
            rec['i_vars'] = has_i
            json.dump(rec, open(cx, 'w'), indent=1)
            out.append(summary_row(r, rec))
            print(f"{r['job_id']:<66} {rec["overall"]}", flush=True)
    with open(os.path.join(ROOT, 'evidence', 'witness_summary.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    print(len(out), 'Buggy verdicts replayed')

if __name__ == '__main__':
    main()
