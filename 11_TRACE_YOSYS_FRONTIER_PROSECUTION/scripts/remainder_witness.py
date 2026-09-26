#!/usr/bin/env python3
"""Turn TRACE's 'Buggy' remainder polynomial into a concrete counterexample and replay it independently.

TRACE prints, after 'Result: Buggy', a line  'SP: {N} c1 m1 + c2 m2 + ...'  where each monomial is a product of
variables nK (K = AIGER literal of a primary input; input index = K/2 - 1) and ci are integer coefficients.
Procedure:
  1. parse the remainder R (multilinear over Boolean inputs)
  2. search random + structured assignments x with R(x) != 0 (mod 2^YW when the spec is modular)
  3. replay x on the ORIGINAL netlist with aigtool.evaluate and compare with the independent reference spec
Verdicts: WITNESS_CONFIRMED (real mismatch), WITNESS_SPURIOUS (R(x)!=0 but circuit matches the reference),
          NO_NONZERO_POINT_FOUND, NO_REMAINDER_IN_LOG
Variables 'iK' (seen only with phase optimisation on a netlist containing AND(x, NOT x)) are undocumented. They are
evaluated as the complement of node K by default (--i-means=complement) or as node K itself (--i-means=identity);
a verdict is only reported as WITNESS_SPURIOUS for such remainders when BOTH readings give a non-zero point that
replays as correct (callers run the script twice).
Usage: remainder_witness.py <trace log> <netlist.aig> <spec> [--i-means=complement|identity]
"""
import json
import random
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aigtool  # noqa: E402

ANSI = re.compile(r'\x1b\[[0-9;]*m')


def parse_remainder(txt):
    txt = ANSI.sub('', txt)
    m = re.search(r'SP:[ \t]*\{(\d+)\}[ \t]*([^\r\n]*)', txt)
    if not m:
        return None
    body = m.group(2).strip()
    terms = []
    if body == '' and m.group(1) == '1':
        # TRACE omits a coefficient of 1, so a remainder equal to the constant 1 prints as an empty body
        return 1, [(1, [])]
    for t in body.split(' + '):
        t = t.strip()
        if not t:
            continue
        mm = re.match(r'^(-?\d*)((?:[ni]\d+)*)$', t)
        if not mm:
            raise ValueError('cannot parse term: ' + t[:80])
        coef = int(mm.group(1)) if mm.group(1) not in (None, '', '-') else (-1 if mm.group(1) == '-' else 1)
        vars_ = [(k, int(v)) for k, v in re.findall(r'([ni])(\d+)', mm.group(2))]
        terms.append((coef, vars_))
    return int(m.group(1)), terms


def node_values(aig, x_bits):
    """Value of every AIG variable literal (even) for one input assignment."""
    val = {0: 0}
    for i, lit in enumerate(aig['inputs']):
        val[lit] = x_bits[i]
    def g(l):
        return val[l & ~1] ^ (l & 1)
    for l, r0, r1 in aig['ands']:
        val[l] = g(r0) & g(r1)
    return val


I_MEANS = 'complement'


def eval_poly(terms, x_bits, aig):
    """Evaluate the remainder; variables may be primary inputs OR internal AND nodes (TRACE left them unsubstituted)."""
    val = node_values(aig, x_bits)
    s = 0
    for c, vs in terms:
        if all((val[v] if k == 'n' or I_MEANS == 'identity' else 1 - val[v]) for k, v in vs):
            s += c
    return s


def main():
    global I_MEANS
    log, aigp, specs = sys.argv[1], sys.argv[2], sys.argv[3]
    for a in sys.argv[4:]:
        if a.startswith('--i-means='):
            I_MEANS = a.split('=', 1)[1]
    txt = open(log, 'rb').read().decode('utf-8', 'replace')
    parsed = parse_remainder(txt)
    if parsed is None:
        print(json.dumps({'verdict': 'NO_REMAINDER_IN_LOG'}))
        return
    n_terms, terms = parsed
    aig = aigtool.read_aig(aigp)
    spec = aigtool.parse_spec(specs)
    I = aig['I']
    mod = 1 << spec['yw']
    rng = random.Random(12345)
    cands = [[0] * I, [1] * I]
    # structured candidates: supports of the lowest-degree monomials
    internal = sorted({v for _, vs in terms for _, v in vs if v > 2 * I})
    for c, vs in sorted(terms, key=lambda t: len(t[1]))[:200]:
        x = [0] * I
        for _, v in vs:
            if v <= 2 * I:
                x[v // 2 - 1] = 1
        cands.append(x)
    for _ in range(20000):
        cands.append([rng.getrandbits(1) for _ in range(I)])
    if I <= 20:
        cands = [[(v >> i) & 1 for i in range(I)] for v in range(1 << I)]   # exhaustive when feasible
    for x in cands:
        r = eval_poly(terms, x, aig)
        if r % mod == 0:
            continue
        vec = sum(b << i for i, b in enumerate(x))
        outs = aigtool.evaluate(aig, x, 1)
        got = sum(b << j for j, b in enumerate(outs))
        exp = aigtool.reference(spec, aigtool.split_operands(vec, spec['widths']))
        print(json.dumps({'verdict': 'WITNESS_CONFIRMED' if got != exp else 'WITNESS_SPURIOUS', 'i_means': I_MEANS,
                          'remainder_terms': n_terms, 'internal_node_vars_in_remainder': internal, 'remainder_value': r, 'input_vector_hex': hex(vec),
                          'operands': [hex(o) for o in aigtool.split_operands(vec, spec['widths'])],
                          'netlist_output': hex(got), 'reference': hex(exp)}))
        return
    print(json.dumps({'verdict': 'NO_NONZERO_POINT_FOUND', 'remainder_terms': n_terms, 'candidates_tried': len(cands),
                      'exhaustive': I <= 20, 'internal_node_vars_in_remainder': internal}))


if __name__ == '__main__':
    main()
