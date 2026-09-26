#!/usr/bin/env python3
"""Independent oracle for the TRACE-vs-Yosys experiment (no EDA dependencies).

Capabilities
  * read/write binary AIGER ("aig") and ASCII ("aag"), combinational only
  * bit-parallel evaluation: each node value is a Python int holding K test vectors
  * reference arithmetic for the specification families used here (exact integers,
    two's complement where signed, reduced modulo 2^Y_WIDTH)
  * exhaustive check when total input bits <= EXHAUSTIVE_MAX, otherwise corner + random vectors
  * counterexample replay on the original netlist
  * gate-level mutation (flip one fanin polarity of one AND) with a behaviour-change witness

Specification string grammar (operands are listed in AIG input order, LSB-first within each):
  kind:SIGNS:WIDTHS:YW
    kind  = mul   (y = a*b)                 operands a,b
          | mac   (y = a*b + c)             operands a,b,c
          | msub  (y = c - a*b)             operands a,b,c
          | dot2  (y = a0*b0 + a1*b1)       operands a0,b0,a1,b1
          | dot2c (y = a0*b0 + a1*b1 + c)   operands a0,b0,a1,b1,c
          | macci (y = a*b + c + cin)       operands a,b,c,cin (GenMac NMAC examples)
    SIGNS  = one char per operand: s|u
    WIDTHS = comma separated operand widths
    YW     = output width
  Example: mac:ssu:8,8,16:17
"""
import random
import sys
import json

EXHAUSTIVE_MAX = 20


# ---------------------------------------------------------------- AIGER I/O
def read_aig(path):
    data = open(path, 'rb').read()
    nl = data.index(b'\n')
    hdr = data[:nl].decode().split()
    fmt = hdr[0]
    M, I, L, O, A = map(int, hdr[1:6])
    if L != 0:
        raise ValueError('sequential AIG not supported')
    pos = nl + 1
    inputs, outputs, ands = [], [], []
    if fmt == 'aag':
        lines = data.decode().splitlines()[1:]
        k = 0
        for _ in range(I):
            inputs.append(int(lines[k])); k += 1
        for _ in range(O):
            outputs.append(int(lines[k])); k += 1
        for _ in range(A):
            l, r0, r1 = map(int, lines[k].split()); k += 1
            ands.append((l, r0, r1))
        return {'M': M, 'I': I, 'O': O, 'inputs': inputs, 'outputs': outputs, 'ands': ands}
    assert fmt == 'aig', fmt
    inputs = [2 * (i + 1) for i in range(I)]
    for _ in range(O):
        e = data.index(b'\n', pos)
        outputs.append(int(data[pos:e]))
        pos = e + 1

    def dec():
        nonlocal pos
        x = 0
        i = 0
        while True:
            ch = data[pos]
            pos += 1
            x |= (ch & 0x7f) << (7 * i)
            if ch & 0x80 == 0:
                return x
            i += 1
    for k in range(A):
        lhs = 2 * (I + k + 1)
        d0 = dec()
        d1 = dec()
        r0 = lhs - d0
        r1 = r0 - d1
        ands.append((lhs, r0, r1))
    return {'M': M, 'I': I, 'O': O, 'inputs': inputs, 'outputs': outputs, 'ands': ands}


def write_aig(aig, path):
    """Binary AIGER writer; requires inputs 2..2I and ANDs in topological index order."""
    I, O, A = aig['I'], aig['O'], len(aig['ands'])
    assert aig['inputs'] == [2 * (i + 1) for i in range(I)]
    out = bytearray(f"aig {I + A} {I} 0 {O} {A}\n".encode())
    for o in aig['outputs']:
        out += f"{o}\n".encode()

    def enc(x):
        b = bytearray()
        while x & ~0x7f:
            b.append((x & 0x7f) | 0x80)
            x >>= 7
        b.append(x)
        return b
    for k, (l, r0, r1) in enumerate(aig['ands']):
        assert l == 2 * (I + k + 1)
        if r0 < r1:
            r0, r1 = r1, r0
        assert l > r0 >= r1
        out += enc(l - r0) + enc(r0 - r1)
    open(path, 'wb').write(bytes(out))


# ---------------------------------------------------------------- evaluation
def evaluate(aig, in_words, K):
    """in_words[i] is an int with K bits: bit t = value of input i in vector t."""
    mask = (1 << K) - 1
    val = {0: 0}
    for i, lit in enumerate(aig['inputs']):
        val[lit] = in_words[i]

    def get(l):
        v = val[l & ~1]
        return (v ^ mask) if (l & 1) else v
    for l, r0, r1 in aig['ands']:
        val[l] = get(r0) & get(r1)
    return [get(o) for o in aig['outputs']]


# ---------------------------------------------------------------- specification
def parse_spec(s):
    kind, signs, widths, yw = s.split(':')
    widths = [int(x) for x in widths.split(',')]
    assert len(signs) == len(widths)
    return {'kind': kind, 'signs': signs, 'widths': widths, 'yw': int(yw)}


def to_signed(v, w):
    return v - (1 << w) if (v >> (w - 1)) & 1 else v


def reference(spec, operands):
    ops = [to_signed(v, w) if s == 's' else v for v, s, w in zip(operands, spec['signs'], spec['widths'])]
    k = spec['kind']
    if k == 'mul':
        r = ops[0] * ops[1]
    elif k == 'mac':
        r = ops[0] * ops[1] + ops[2]
    elif k == 'msub':
        r = ops[2] - ops[0] * ops[1]
    elif k == 'dot2':
        r = ops[0] * ops[1] + ops[2] * ops[3]
    elif k == 'dot2c':
        r = ops[0] * ops[1] + ops[2] * ops[3] + ops[4]
    elif k == 'macci':
        r = ops[0] * ops[1] + ops[2] + ops[3]
    else:
        raise ValueError(k)
    return r % (1 << spec['yw'])


def split_operands(vec, widths):
    ops, sh = [], 0
    for w in widths:
        ops.append((vec >> sh) & ((1 << w) - 1))
        sh += w
    return ops


def check(aig, spec, n_random=1 << 14, seed=1):
    nin = sum(spec['widths'])
    if nin != aig['I'] or spec['yw'] != aig['O']:
        return {'status': 'SHAPE_MISMATCH', 'aig_I': aig['I'], 'aig_O': aig['O'], 'spec_in': nin, 'spec_out': spec['yw']}
    rng = random.Random(seed)
    vectors = []
    exhaustive = nin <= EXHAUSTIVE_MAX
    if exhaustive:
        vectors = list(range(1 << nin))
    else:
        corners = set()
        for pat in (0, (1 << nin) - 1):
            corners.add(pat)
        # per-operand corners: 0, 1, max, min-signed, max-signed
        cvals = []
        for w in spec['widths']:
            cvals.append([0, 1, (1 << w) - 1, 1 << (w - 1), (1 << (w - 1)) - 1])
        for _ in range(4096):
            v, sh = 0, 0
            for w, cv in zip(spec['widths'], cvals):
                v |= rng.choice(cv + [rng.getrandbits(w)]) << sh
                sh += w
            corners.add(v)
        vectors = list(corners) + [rng.getrandbits(nin) for _ in range(n_random)]
    first_bad = None
    nbad = 0
    B = 4096
    for base in range(0, len(vectors), B):
        chunk = vectors[base:base + B]
        K = len(chunk)
        words = [0] * nin
        for t, v in enumerate(chunk):
            x = v
            i = 0
            while x:
                if x & 1:
                    words[i] |= 1 << t
                x >>= 1
                i += 1
        outs = evaluate(aig, words, K)
        for t, v in enumerate(chunk):
            got = 0
            for j, ow in enumerate(outs):
                if (ow >> t) & 1:
                    got |= 1 << j
            exp = reference(spec, split_operands(v, spec['widths']))
            if got != exp:
                nbad += 1
                if first_bad is None:
                    first_bad = {'input_vector_hex': hex(v), 'operands': [hex(x) for x in split_operands(v, spec['widths'])],
                                 'got': hex(got), 'expected': hex(exp), 'diff_bits': [j for j in range(spec['yw']) if ((got ^ exp) >> j) & 1]}
    return {'status': 'CORRECT' if nbad == 0 else 'INCORRECT', 'exhaustive': exhaustive, 'vectors': len(vectors),
            'mismatches': nbad, 'first_mismatch': first_bad}


# ---------------------------------------------------------------- mutation
def mutate_flip_fanin(aig, and_index, which):
    ands = list(aig['ands'])
    l, r0, r1 = ands[and_index]
    if which == 0:
        r0 ^= 1
    else:
        r1 ^= 1
    ands[and_index] = (l, r0, r1)
    m = dict(aig)
    m['ands'] = ands
    return m


def main():
    cmd = sys.argv[1]
    if cmd == 'check':
        aig = read_aig(sys.argv[2])
        res = check(aig, parse_spec(sys.argv[3]))
        print(json.dumps(res))
    elif cmd == 'replay':
        # replay one input vector (hex, AIG input order, LSB = input 0) on one or more AIGs
        vec = int(sys.argv[2], 16)
        spec = parse_spec(sys.argv[3])
        exp = reference(spec, split_operands(vec, spec['widths']))
        for p in sys.argv[4:]:
            aig = read_aig(p)
            outs = evaluate(aig, [(vec >> i) & 1 for i in range(aig['I'])], 1)
            got = sum(b << j for j, b in enumerate(outs))
            print(json.dumps({'aig': p, 'got': hex(got), 'expected': hex(exp), 'match': got == exp}))
    elif cmd == 'mutate':
        # mutate <in.aig> <out.aig> <spec> <seed> : pick random AND/fanin until behaviour changes
        aig = read_aig(sys.argv[2])
        spec = parse_spec(sys.argv[4])
        rng = random.Random(int(sys.argv[5]))
        for attempt in range(200):
            k = rng.randrange(len(aig['ands']))
            w = rng.randrange(2)
            m = mutate_flip_fanin(aig, k, w)
            res = check(m, spec, n_random=1 << 12, seed=attempt + 7)
            if res['status'] == 'INCORRECT':
                write_aig(m, sys.argv[3])
                print(json.dumps({'mutated_and_index': k, 'fanin': w, 'attempt': attempt, 'witness': res['first_mismatch'],
                                  'mismatch_rate': res['mismatches'] / res['vectors']}))
                return
        print(json.dumps({'status': 'NO_BEHAVIOUR_CHANGING_MUTATION_FOUND'}))
    elif cmd == 'info':
        aig = read_aig(sys.argv[2])
        print(json.dumps({'I': aig['I'], 'O': aig['O'], 'A': len(aig['ands'])}))
    else:
        raise SystemExit('usage: aigtool.py check|replay|mutate|info ...')


if __name__ == '__main__':
    main()
