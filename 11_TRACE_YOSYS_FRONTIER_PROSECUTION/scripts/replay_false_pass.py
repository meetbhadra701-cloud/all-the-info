#!/usr/bin/env python3
"""For every FALSE_PASS in RESULTS.csv (TRACE 'Correct' on an oracle-INCORRECT netlist), record the oracle's concrete
mismatch replayed on the netlist: counterexamples/FALSE_PASS__<job_id>.json. The spec is the template TRACE checked."""
import csv, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import aigtool
from replay_all import template_spec
n = 0
for r in csv.DictReader(open(os.path.join(ROOT, 'RESULTS.csv'))):
    if r['class'] != 'FALSE_PASS':
        continue
    aig = aigtool.read_aig(os.path.join(ROOT, r['netlist']))
    spec_s = template_spec(r['trace_args'], aig)
    res = aigtool.check(aig, aigtool.parse_spec(spec_s))
    mm = res.get('first_mismatch') or {}
    rec = {'job_id': r['job_id'], 'netlist': r['netlist'], 'trace_args': r['trace_args'], 'trace_result': r['trace_result'],
           'template_spec': spec_s, 'oracle': {k: res[k] for k in ('status', 'exhaustive', 'vectors', 'mismatches')},
           'replayed_mismatch': mm}
    if mm:
        vec = int(mm['input_vector_hex'], 16)
        outs = aigtool.evaluate(aig, [(vec >> i) & 1 for i in range(aig['I'])], 1)
        got = sum(b << j for j, b in enumerate(outs))
        exp = aigtool.reference(aigtool.parse_spec(spec_s), aigtool.split_operands(vec, aigtool.parse_spec(spec_s)['widths']))
        rec['replay_check'] = {'got': hex(got), 'expected': hex(exp), 'mismatch': got != exp}
    json.dump(rec, open(os.path.join(ROOT, 'counterexamples', f"FALSE_PASS__{r['job_id']}.json"), 'w'), indent=1)
    n += 1
    print(r['job_id'], rec['oracle'], rec.get('replay_check'))
print(n, 'FALSE_PASS records')
