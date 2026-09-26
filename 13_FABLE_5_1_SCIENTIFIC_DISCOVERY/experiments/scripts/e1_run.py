"""E1: unit/bit cost of hardwired ternary CMVM constructions (see ../E1_PREREGISTRATION.md).

Usage: python3 e1_run.py OUT.jsonl
Explicit op lists are built and independently checked for m=n<=1024 (all methods) and for the
universal block-pattern construction at every size (small batch). g=1 at m=n>=2048 is costed in
cost-only mode (its closed form sum(nnz-1) is asserted), because its explicit op list (~11M ops)
exceeds this machine's memory budget for the checker. da4ml runs in a subprocess with a 600 s cap.
"""
from __future__ import annotations

import json
import multiprocessing as mp
import sys
import time

import numpy as np

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from hwlayer import (Circuit, block_patterns, check, from_da4ml, per_input, solve_da4ml,  # noqa: E402
                     ternary, width)

SIZES = [64, 128, 256, 512, 1024, 2048, 4096]
P0S = [0.33, 0.50]
SEEDS = [0, 1, 2]
GMAX = 8
DA4ML_CAP_S = 600


class CostOnly(Circuit):
    """Same construction code path, but only accumulates U and B (no op storage)."""

    def __post_init__(self):
        super().__post_init__()
        self._U = 0
        self._B = 0

    def add(self, a, sa, b, sb, shb=0):
        la, ha = (self.lo[a], self.hi[a]) if sa > 0 else (-self.hi[a], -self.lo[a])
        lb, hb = (self.lo[b] << shb, self.hi[b] << shb) if sb > 0 else (-(self.hi[b] << shb), -(self.lo[b] << shb))
        self.lo.append(la + lb); self.hi.append(ha + hb)
        self._U += 1
        self._B += width(la + lb, ha + hb)
        return len(self.lo) - 1

    @property
    def U(self):
        return self._U

    @property
    def B(self):
        return self._B


def per_input_cost(W):
    m, n = W.shape
    c = CostOnly(n)
    for i in range(m):
        nz = np.nonzero(W[i])[0]
        c.out.append(c.reduce_terms([(int(j), int(W[i, j])) for j in nz]))
    return c


def block_cost(W, g, universal):
    # reuse the construction with a CostOnly circuit by monkeypatching the class used
    import hwlayer
    orig = hwlayer.Circuit
    hwlayer.Circuit = CostOnly
    try:
        return hwlayer.block_patterns(W, g, universal)
    finally:
        hwlayer.Circuit = orig


def _da4ml_worker(W, q):
    try:
        t = time.time()
        pipe = solve_da4ml(W)
        dt = time.time() - t
        c = from_da4ml(pipe, W.shape[1], W.shape[0])
        ok = check(c, W, np.random.default_rng(12345), batch=16)
        q.put({'U': c.U, 'B': c.B, 'reported_cost': float(pipe.cost), 'wall': dt, 'check': ok})
    except Exception as e:  # fail closed
        q.put({'error': repr(e)})


def run_da4ml(W):
    q = mp.Queue()
    p = mp.Process(target=_da4ml_worker, args=(W, q))
    t = time.time()
    p.start()
    p.join(DA4ML_CAP_S + 60)
    if p.is_alive():
        p.kill(); p.join()
        return {'timeout': True, 'wall': time.time() - t}
    return q.get() if not q.empty() else {'error': 'no result'}


def main(out):
    fh = open(out, 'a')
    da4ml_dead = set()  # (p0) sizes at which da4ml timed out: skip larger sizes for that p0
    for n in SIZES:
        for p0 in P0S:
            for seed in SEEDS:
                rng = np.random.default_rng(1000 * seed + int(100 * p0) + n)
                W = ternary(n, n, p0, rng)
                rec = {'m': n, 'n': n, 'p0': p0, 'seed': seed, 'nnz': int((W != 0).sum())}
                big = n >= 2048
                t = time.time()
                c1 = per_input_cost(W) if big else per_input(W)
                assert c1.U == int(np.maximum((W != 0).sum(axis=1) - 1, 0).sum())
                rec['g1'] = {'U': c1.U, 'B': c1.B, 'check': None if big else check(c1, W, rng, 32), 'wall': time.time() - t}
                for g in range(2, GMAX + 1):
                    for uni in (True, False):
                        key = f"{'UBP' if uni else 'CBP'}{g}"
                        t = time.time()
                        if big and not (uni):
                            c = block_cost(W, g, uni); chk = None
                        elif big:
                            if (3 ** g - 1) // 2 * (n // g) > 6_000_000:
                                c = block_cost(W, g, uni); chk = None
                            else:
                                c = block_patterns(W, g, uni); chk = check(c, W, rng, 4)
                        else:
                            c = block_patterns(W, g, uni); chk = check(c, W, rng, 32)
                        rec[key] = {'U': c.U, 'B': c.B, 'check': chk, 'wall': time.time() - t}
                        del c
                if n in (64, 128, 256, 512) and (p0, 'dead') not in da4ml_dead:
                    r = run_da4ml(W)
                    rec['da4ml'] = r
                    if r.get('timeout'):
                        da4ml_dead.add((p0, 'dead'))
                else:
                    rec['da4ml'] = {'skipped': True}
                fh.write(json.dumps(rec) + '\n'); fh.flush()
                best = min((rec[k]['U'], k) for k in rec if k.startswith('UBP'))
                print(n, p0, seed, 'g1', rec['g1']['U'], 'bestUBP', best, 'da4ml', rec['da4ml'].get('U', rec['da4ml']), flush=True)


if __name__ == '__main__':
    main(sys.argv[1])
