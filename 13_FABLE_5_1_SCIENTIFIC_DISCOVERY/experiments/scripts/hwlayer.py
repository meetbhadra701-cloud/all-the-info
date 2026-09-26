"""Hardwired constant-matrix-vector constructions and an independent checker.

A circuit is an op list over a signal buffer:
  signals 0..n-1 are the inputs x_0..x_{n-1}
  op k creates signal n+k = sa*sig[a] + sb*sig[b]   (sa, sb in {+1,-1}; one adder/subtractor)
  outputs: list of (signal index or -1 for constant zero, sign in {+1,-1})

Costs:
  U = number of ops (unit adders)
  B = sum over ops of the result width (bits) from interval arithmetic on 8-bit signed inputs
      (ripple-carry adder area proxy)
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

XLO, XHI = -128, 127  # 8-bit signed activations


def width(lo: int, hi: int) -> int:
    """Two's-complement bits needed to hold every integer in [lo, hi]."""
    w = 1
    while not (-(1 << (w - 1)) <= lo and hi <= (1 << (w - 1)) - 1):
        w += 1
    return w


@dataclass
class Circuit:
    n: int
    a: list = field(default_factory=list)
    sa: list = field(default_factory=list)
    b: list = field(default_factory=list)
    sb: list = field(default_factory=list)
    hb: list = field(default_factory=list)  # left shift applied to operand b (free wiring)
    out: list = field(default_factory=list)  # (sig, sign)
    lo: list = field(default_factory=list)
    hi: list = field(default_factory=list)

    def __post_init__(self):
        self.lo = [XLO] * self.n
        self.hi = [XHI] * self.n

    def add(self, a: int, sa: int, b: int, sb: int, shb: int = 0) -> int:
        if shb < 0:
            raise ValueError('negative shift not modelled')
        self.a.append(a); self.sa.append(sa); self.b.append(b); self.sb.append(sb); self.hb.append(shb)
        la, ha = (self.lo[a], self.hi[a]) if sa > 0 else (-self.hi[a], -self.lo[a])
        lb, hb = (self.lo[b] << shb, self.hi[b] << shb) if sb > 0 else (-(self.hi[b] << shb), -(self.lo[b] << shb))
        self.lo.append(la + lb); self.hi.append(ha + hb)
        return self.n + len(self.a) - 1

    @property
    def U(self) -> int:
        return len(self.a)

    @property
    def B(self) -> int:
        return sum(width(self.lo[self.n + k], self.hi[self.n + k]) for k in range(len(self.a)))

    def reduce_terms(self, terms: list[tuple[int, int]]) -> tuple[int, int]:
        """Balanced pairwise reduction of signed terms; returns (sig, sign) or (-1, 1) if empty."""
        if not terms:
            return (-1, 1)
        cur = list(terms)
        while len(cur) > 1:
            nxt = []
            for i in range(0, len(cur) - 1, 2):
                (s0, g0), (s1, g1) = cur[i], cur[i + 1]
                # s = g0*sig0 + g1*sig1 ; normalise so that the first operand is positive
                if g0 > 0:
                    nxt.append((self.add(s0, 1, s1, g1), 1))
                else:  # -sig0 + g1*sig1 = -(sig0 - g1*sig1)
                    nxt.append((self.add(s0, 1, s1, -g1), -1))
            if len(cur) % 2:
                nxt.append(cur[-1])
            cur = nxt
        return cur[0]

    def evaluate(self, X: np.ndarray) -> np.ndarray:
        """X: (batch, n) int64 -> (batch, m). Level-by-level vectorised evaluation."""
        nops = len(self.a)
        A = np.asarray(self.a, dtype=np.int64); B_ = np.asarray(self.b, dtype=np.int64)
        SA = np.asarray(self.sa, dtype=np.int64)
        SB = np.asarray(self.sb, dtype=np.int64) * (np.int64(1) << np.asarray(self.hb, dtype=np.int64))
        level = np.zeros(self.n + nops, dtype=np.int64)
        for k in range(nops):  # levels (ops are in topological order by construction)
            level[self.n + k] = max(level[A[k]], level[B_[k]]) + 1
        sig = np.zeros((self.n + nops, X.shape[0]), dtype=np.int64)
        sig[: self.n] = X.T
        oplev = level[self.n:]
        for L in range(1, int(oplev.max(initial=0)) + 1):
            ks = np.nonzero(oplev == L)[0]
            sig[self.n + ks] = SA[ks, None] * sig[A[ks]] + SB[ks, None] * sig[B_[ks]]
        Y = np.zeros((X.shape[0], len(self.out)), dtype=np.int64)
        for i, o in enumerate(self.out):
            s, g = o[0], o[1]
            sh = o[2] if len(o) > 2 else 0
            if s >= 0:
                v = g * sig[s]
                if sh >= 0:
                    Y[:, i] = v << sh
                else:  # exact right shift only (fail closed if not divisible)
                    if np.any(v % (1 << -sh)):
                        raise ArithmeticError('non-integral output under negative shift')
                    Y[:, i] = v >> -sh
        return Y


# ---------------------------------------------------------------- constructions

def per_input(W: np.ndarray) -> Circuit:
    """g = 1: each row adds/subtracts/skips its inputs (ternary add/sub/skip; per-input sharing)."""
    m, n = W.shape
    c = Circuit(n)
    for i in range(m):
        nz = np.nonzero(W[i])[0]
        c.out.append(c.reduce_terms([(int(j), int(W[i, j])) for j in nz]))
    return c


def _canon(q: tuple) -> tuple[tuple, int]:
    """Canonical signed pattern: first nonzero coefficient is +1. Returns (pattern, sign)."""
    for v in q:
        if v != 0:
            s = 1 if v > 0 else -1
            return tuple(s * x for x in q), s
    return q, 0


def block_patterns(W: np.ndarray, g: int, universal: bool) -> Circuit:
    """Block-pattern construction.
    universal=True : every block generates ALL (3^g-1)/2 canonical ternary patterns (weight-independent base).
    universal=False: only patterns used by some row, plus their parent closure (weight-specific)."""
    m, n = W.shape
    c = Circuit(n)
    blocks = [list(range(s, min(s + g, n))) for s in range(0, n, g)]
    pat_sig: list[dict] = []
    for cols in blocks:
        k = len(cols)
        table: dict = {}
        # singletons are inputs (free)
        for t, j in enumerate(cols):
            e = [0] * k; e[t] = 1
            table[tuple(e)] = j
        if universal:
            wanted = set()
            # enumerate all canonical patterns in order of number of nonzeros
            import itertools
            for q in itertools.product((-1, 0, 1), repeat=k):
                cq, s = _canon(q)
                if s != 0:
                    wanted.add(cq)
        else:
            wanted = set()
            for i in range(m):
                q = tuple(int(v) for v in W[i, cols])
                cq, s = _canon(q)
                if s != 0:
                    wanted.add(cq)
        # parent closure: parent = pattern with its last nonzero removed (stays canonical)
        def ensure(p: tuple) -> int:
            if p in table:
                return table[p]
            nzs = [t for t, v in enumerate(p) if v != 0]
            last = nzs[-1]
            parent = list(p); parent[last] = 0
            ps = ensure(tuple(parent))
            sig = c.add(ps, 1, cols[last], p[last])
            table[p] = sig
            return sig
        for p in sorted(wanted, key=lambda p: sum(1 for v in p if v)):
            ensure(p)
        pat_sig.append(table)
    for i in range(m):
        terms = []
        for bi, cols in enumerate(blocks):
            q = tuple(int(v) for v in W[i, cols])
            cq, s = _canon(q)
            if s != 0:
                terms.append((pat_sig[bi][cq], s))
        c.out.append(c.reduce_terms(terms))
    return c


def _combine(c: Circuit, t0: tuple, t1: tuple) -> tuple:
    """Terms are (sig, sign, shift) meaning sign * 2^shift * sig[sig]; sig == -1 is the constant 0.
    Returns a term for t0 + t1 using at most one adder (shift factoring is free wiring)."""
    if t0[0] < 0:
        return t1
    if t1[0] < 0:
        return t0
    (s0, g0, h0), (s1, g1, h1) = t0, t1
    if h1 < h0:  # make operand a the one with the smaller shift
        (s0, g0, h0), (s1, g1, h1) = (s1, g1, h1), (s0, g0, h0)
    # value = 2^h0 * (g0*sig0 + g1*2^(h1-h0)*sig1)
    if g0 > 0:
        return (c.add(s0, 1, s1, g1, h1 - h0), 1, h0)
    return (c.add(s0, 1, s1, -g1, h1 - h0), -1, h0)


def solve_da4ml(W: np.ndarray, **kw):
    """da4ml expects kernel (n_in, n_out) with y = x @ kernel. It must be C-contiguous: da4ml 0.6.0
    silently reads an F-ordered array as its transpose (observed 2026-09-26, see evidence/)."""
    from da4ml.cmvm import solve
    K = np.ascontiguousarray(W.T, dtype=np.float32)
    pipe = solve(K, **kw)
    if not np.array_equal(pipe.kernel, K):
        raise AssertionError('da4ml returned a pipeline whose kernel differs from the request')
    return pipe


def from_da4ml(pipe, n: int, m: int) -> Circuit:
    """Translate a (possibly multi-stage) da4ml Pipeline into our Circuit, independently of da4ml's
    own interpreter. Supports opcodes -1 (copy), 0 (add), 1 (sub) with non-negative shifts.
    Fails closed on anything else."""
    c = Circuit(n)
    stage_in = [(j, 1, 0) for j in range(n)]  # terms feeding the current stage
    for sol in pipe.solutions:
        buf: dict[int, tuple] = {}
        for k, op in enumerate(sol.ops):
            if op.opcode == -1:
                sh = int(sol.inp_shifts[op.id0])
                s, g, h = stage_in[op.id0]
                buf[k] = (s, g, h + sh) if s >= 0 else (-1, 1, 0)
            elif op.opcode in (0, 1):
                s1, g1, h1 = buf[op.id1]
                t1 = (s1, g1 if op.opcode == 0 else -g1, h1 + int(op.data))
                buf[k] = _combine(c, buf[op.id0], t1)
            else:
                raise ValueError(f'opcode {op.opcode} not modelled')
        outs = []
        for oi, osh, neg in zip(sol.out_idxs, sol.out_shifts, sol.out_negs):
            if oi < 0:
                outs.append((-1, 1, 0)); continue
            s, g, h = buf[oi]
            outs.append((s, -g if neg else g, h + int(osh)) if s >= 0 else (-1, 1, 0))
        stage_in = outs
    c.out = stage_in
    return c


def check(c: Circuit, W: np.ndarray, rng: np.random.Generator, batch: int = 64) -> bool:
    X = rng.integers(XLO, XHI + 1, size=(batch, W.shape[1]), dtype=np.int64)
    Y = c.evaluate(X)
    return bool(np.array_equal(Y, X @ W.T.astype(np.int64)))


def ternary(m: int, n: int, p0: float, rng: np.random.Generator) -> np.ndarray:
    return rng.choice(np.array([-1, 0, 1], dtype=np.int8), size=(m, n), p=[(1 - p0) / 2, p0, (1 - p0) / 2])


def analytic_universal_U(W: np.ndarray, g: int) -> int:
    """Closed-form unit cost of the universal construction (used only for sizes where the explicit
    op list is not built; equality with the explicit construction is asserted at smaller sizes)."""
    m, n = W.shape
    total = 0
    nb = math.ceil(n / g)
    for bi in range(nb):
        k = min(g, n - bi * g)
        total += (3 ** k - 1) // 2 - k
    Wb = W[:, : (n // g) * g].reshape(m, n // g, g)
    nzb = (Wb != 0).any(axis=2).sum(axis=1)
    if n % g:
        nzb = nzb + (W[:, (n // g) * g:] != 0).any(axis=1)
    total += int(np.maximum(nzb - 1, 0).sum())
    return total
