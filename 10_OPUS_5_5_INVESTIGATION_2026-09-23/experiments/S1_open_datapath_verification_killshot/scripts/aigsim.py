"""Minimal independent AIGER (binary 'aig' format, combinational) evaluator.
Used to replay a counterexample on the original netlists without relying on ABC or Yosys."""
import sys

def read_aig(path):
    data = open(path, 'rb').read()
    nl = data.index(b'\n')
    hdr = data[:nl].decode().split()
    assert hdr[0] == 'aig', hdr
    M, I, L, O, A = map(int, hdr[1:6])
    assert L == 0, 'combinational only'
    pos = nl + 1
    outs = []
    for _ in range(O):
        e = data.index(b'\n', pos)
        outs.append(int(data[pos:e]))
        pos = e + 1
    def dec():
        nonlocal pos
        x = 0; i = 0
        while True:
            ch = data[pos]; pos += 1
            x |= (ch & 0x7f) << (7 * i)
            if ch & 0x80 == 0:
                return x
            i += 1
    ands = []
    for k in range(A):
        lhs = 2 * (I + L + k + 1)
        d0 = dec(); d1 = dec()
        rhs0 = lhs - d0; rhs1 = rhs0 - d1
        ands.append((lhs, rhs0, rhs1))
    return I, outs, ands

def evaluate(aig, invals):
    I, outs, ands = aig
    val = {0: 0}
    for i in range(I):
        val[2 * (i + 1)] = invals[i]
    def lit(l):
        return val[l & ~1] ^ (l & 1)
    for lhs, r0, r1 in ands:
        val[lhs] = lit(r0) & lit(r1)
    return [lit(o) for o in outs]

def to_int(bits):
    return sum(b << i for i, b in enumerate(bits))

if __name__ == '__main__':
    base = sys.argv[1]
    vec = int(sys.argv[2], 16)
    names = sys.argv[3:]
    for n in names:
        aig = read_aig(f'{base}/{n}.aig')
        I = aig[0]
        inv = [(vec >> i) & 1 for i in range(I)]
        print(n, 'y =', hex(to_int(evaluate(aig, inv))))
