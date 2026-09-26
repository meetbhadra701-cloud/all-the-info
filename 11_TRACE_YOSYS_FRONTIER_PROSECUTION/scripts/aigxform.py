#!/usr/bin/env python3
"""Function-preserving AIG transformations used as controlled experiments (verified by aigtool.check).
  fold   <in> <out>          : constant-propagate AND gates with 0/1 fanins (removes constant-fanin ANDs)
  buffer <in> <out> <k>      : insert one buffer AND(x, TRUE) in front of fanin 0 of AND number k
  contra <in> <out> <i> <j>  : append g = AND(x_i, NOT x_i) (constant 0) and replace output j by OR(y_j, g)
  xorself <in> <out> <i> <j> : function-preserving copy of the Yosys PR-6231 pre-ABC pattern: k = XNOR(x_i, x_i) built as
                               NOR(AND(NOT x_i, x_i), AND(NOT x_i, x_i)) (= 1), then y_j' = XNOR(y_j, k) (= y_j)
  ctx <in> <out> <g>          : function-preserving graft of the exact PR-6231 pre-ABC context around AND gate g, which
                               must be AND(p, NOT x) with x a primary input: g is replaced by
                               NOT XOR(g', XNOR(x, x)) with g' = AND(p, NOT x) a duplicate, XNOR(x,x) = NOR(AND(NOT x, x),
                               AND(NOT x, x)) and XOR(u, k) = NOR(AND(u, k), AND(NOT u, NOT k)), as emitted by Yosys
  xorout <in> <out> <j> <lit>: MUTANT (not function-preserving): y_j' = y_j XOR lit, lit = AIGER literal (0/1 = const)
Both rebuild the AIG with fresh sequential literals (inputs keep 2..2I), preserving topological order."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aigtool

def rebuild(aig, gates, outputs_old, fold=True):
    """gates: list of (old_lhs, fanin0_old_or_('BUF',lit), fanin1_old) in topological order."""
    I = aig['I']
    m = {0: 0, 1: 1}
    for i in range(I):
        m[2 * (i + 1)] = 2 * (i + 1); m[2 * (i + 1) + 1] = 2 * (i + 1) + 1
    new_ands = []
    nxt = [2 * (I + 1)]
    def lit(old):
        return m[old & ~1] ^ (old & 1)
    def mk(a, b):
        if fold:
            if a == 0 or b == 0: return 0
            if a == 1: return b
            if b == 1: return a
            if a == b: return a
            if a == b ^ 1: return 0
        l = nxt[0]; nxt[0] += 2
        new_ands.append((l, max(a, b), min(a, b)))
        return l
    for g in gates:
        if g[0] == 'BUF':          # ('BUF', key, source_old_lit) -> buffer node registered under a temp key
            _, key, src = g
            l = nxt[0]; nxt[0] += 2
            new_ands.append((l, lit(src), 1))
            m[key] = l
            continue
        old, a, b = g
        m[old] = mk(lit(a) if not isinstance(a, str) else m[a], lit(b))
    outs = [lit(o) for o in outputs_old]
    return {'M': (nxt[0] // 2) - 1, 'I': I, 'O': len(outs), 'inputs': [2 * (i + 1) for i in range(I)],
            'outputs': outs, 'ands': new_ands}

def main():
    cmd, src, dst = sys.argv[1], sys.argv[2], sys.argv[3]
    aig = aigtool.read_aig(src)
    if cmd == 'fold':
        new = rebuild(aig, list(aig['ands']), aig['outputs'], fold=True)
    elif cmd == 'buffer':
        k = int(sys.argv[4])
        gates = []
        for idx, (l, r0, r1) in enumerate(aig['ands']):
            if idx == k:
                gates.append(('BUF', 'bufkey', r0 & ~1))
                # use buffered (possibly complemented) fanin: represent as key with same polarity
                gates.append((l, 'bufkey' if (r0 & 1) == 0 else 'bufkey_n', r1))
            else:
                gates.append((l, r0, r1))
        # handle complement polarity of buffered fanin
        new = None
        I = aig['I']
        # simple approach: rebuild without folding so the TRUE-fanin buffer survives
        m_gates = []
        for g in gates:
            m_gates.append(g)
        # patch: implement complemented key by post-processing in rebuild via mapping
        class M(dict):
            pass
        new = rebuild_with_polarity(aig, gates)
    elif cmd == 'contra':
        new = contra(aig, int(sys.argv[4]), int(sys.argv[5]))
    elif cmd == 'xorself':
        new = xorself(aig, int(sys.argv[4]), int(sys.argv[5]))
    elif cmd == 'ctx':
        new = ctx_graft(aig, int(sys.argv[4]))
    elif cmd == 'xorout':
        new = xorout(aig, int(sys.argv[4]), int(sys.argv[5]))
    aigtool.write_aig(new, dst)
    print({'in_ands': len(aig['ands']), 'out_ands': len(new['ands'])})


def ctx_graft(aig, target):
    I = aig['I']
    m = {0: 0, 1: 1}
    for i in range(I):
        m[2 * (i + 1)] = 2 * (i + 1)
    lit = lambda old: m[old & ~1] ^ (old & 1)
    new = []; nxt = [2 * (I + 1)]
    def mk(a, b):
        l = nxt[0]; nxt[0] += 2
        new.append((l, max(a, b), min(a, b)))
        return l
    found = False
    for l, r0, r1 in aig['ands']:
        a, b = lit(r0), lit(r1)
        if l != target:
            m[l] = mk(a, b)
            continue
        xin = [r for r in (r0, r1) if (r & 1) and 2 <= (r & ~1) <= 2 * I]
        assert xin, 'target gate must have a complemented primary-input fanin'
        x = xin[0] & ~1
        g2 = mk(a, b)                       # u = AND(p, NOT x)
        k1 = mk(x ^ 1, x); k2 = mk(x ^ 1, x)
        k = mk(k1 ^ 1, k2 ^ 1)              # XNOR(x, x) = 1
        a1 = mk(g2, k); a2 = mk(g2 ^ 1, k ^ 1)
        t = mk(a2 ^ 1, a1 ^ 1)              # XOR(u, k) = NOT u
        m[l] = t ^ 1                        # every reference to g now sees NOT XOR(u, k) = u = g
        found = True
    assert found, 'target gate not found'
    outs = [lit(o) for o in aig['outputs']]
    return {'M': nxt[0] // 2 - 1, 'I': I, 'O': len(outs), 'inputs': [2 * (i + 1) for i in range(I)], 'outputs': outs, 'ands': new}


def xorself(aig, i, j):
    ands = list(aig['ands'])
    x = aig['inputs'][i]
    n = 2 * (aig['M'] + 1)
    g1, g2, k, t1, t2, t3 = n, n + 2, n + 4, n + 6, n + 8, n + 10
    ands.append((g1, x | 1, x & ~1))                     # AND(NOT x, x)
    ands.append((g2, x | 1, x & ~1))                     # duplicate, as emitted by Yosys
    ands.append((k, max(g1 ^ 1, g2 ^ 1), min(g1 ^ 1, g2 ^ 1)))   # NOR(g1, g2) = XNOR(x, x) = 1
    y = aig['outputs'][j]
    ands.append((t1, max(y, k ^ 1), min(y, k ^ 1)))      # y AND NOT k
    ands.append((t2, max(y ^ 1, k), min(y ^ 1, k)))      # NOT y AND k
    ands.append((t3, max(t1 ^ 1, t2 ^ 1), min(t1 ^ 1, t2 ^ 1)))  # XNOR(y, k) = y
    outs = list(aig['outputs'])
    outs[j] = t3
    return {'M': aig['M'] + 6, 'I': aig['I'], 'O': len(outs), 'inputs': list(aig['inputs']), 'outputs': outs, 'ands': ands}


def xorout(aig, j, lit):
    """Deliberate mutant: output j becomes y_j XOR lit (lit 1 = unconditional flip)."""
    ands = list(aig['ands'])
    outs = list(aig['outputs'])
    y = outs[j]
    if lit in (0, 1):
        outs[j] = y ^ lit
        return {'M': aig['M'], 'I': aig['I'], 'O': len(outs), 'inputs': list(aig['inputs']), 'outputs': outs, 'ands': ands}
    nxt = 2 * (aig['M'] + 1)
    t1, t2, t3 = nxt, nxt + 2, nxt + 4
    ands.append((t1, max(y, lit ^ 1), min(y, lit ^ 1)))          # y AND NOT lit
    ands.append((t2, max(y ^ 1, lit), min(y ^ 1, lit)))          # NOT y AND lit
    ands.append((t3, max(t1 ^ 1, t2 ^ 1), min(t1 ^ 1, t2 ^ 1)))  # NOR(t1, t2)
    outs[j] = t3 ^ 1                                             # XOR = OR(t1, t2)
    return {'M': aig['M'] + 3, 'I': aig['I'], 'O': len(outs), 'inputs': list(aig['inputs']), 'outputs': outs, 'ands': ands}


def contra(aig, i, j):
    """Function-preserving: y_j' = OR(y_j, AND(x_i, NOT x_i)). Adds exactly one complementary-fanin AND."""
    ands = list(aig['ands'])
    x = aig['inputs'][i]
    nxt = 2 * (aig['M'] + 1)
    g = nxt
    ands.append((g, x | 1, x & ~1))
    h = nxt + 2
    yj = aig['outputs'][j]
    ands.append((h, max(yj ^ 1, g ^ 1), min(yj ^ 1, g ^ 1)))
    outs = list(aig['outputs'])
    outs[j] = h ^ 1
    return {'M': aig['M'] + 2, 'I': aig['I'], 'O': len(outs), 'inputs': list(aig['inputs']), 'outputs': outs, 'ands': ands}

def rebuild_with_polarity(aig, gates):
    I = aig['I']
    m = {0: 0, 1: 1}
    for i in range(I):
        m[2 * (i + 1)] = 2 * (i + 1)
    new_ands = []; nxt = [2 * (I + 1)]
    def lit(old): return m[old & ~1] ^ (old & 1)
    for g in gates:
        if g[0] == 'BUF':
            _, key, src = g
            l = nxt[0]; nxt[0] += 2
            new_ands.append((l, lit(src), 1)); m['bufkey'] = l; m['bufkey_n'] = l ^ 1
            continue
        old, a, b = g
        la = m[a] if isinstance(a, str) else lit(a)
        l = nxt[0]; nxt[0] += 2
        lb = lit(b)
        new_ands.append((l, max(la, lb), min(la, lb))); m[old] = l
    outs = [lit(o) for o in aig['outputs']]
    return {'M': nxt[0] // 2 - 1, 'I': I, 'O': len(outs), 'inputs': [2 * (i + 1) for i in range(I)], 'outputs': outs, 'ands': new_ands}

if __name__ == '__main__':
    main()
