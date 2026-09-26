"""Post-hoc strong-baseline correction for E1's regime-(F) comparison (declared in E3_PREREGISTRATION.md).

Structural hashing (what Yosys opt_merge / ABC strash do automatically) is applied to every construction's
op list. Reports hashed unit costs. Same matrices as E1 (same seeding).
python3 e1_hashed.py > ../results/E1_hashed.md
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hwlayer import block_patterns, per_input, ternary  # noqa: E402


def hashcons_U(c):
    rep = {j: ('in', j) for j in range(c.n)}
    seen = {}
    for k in range(len(c.a)):
        a, b = rep[c.a[k]], rep[c.b[k]]
        if c.sa[k] == 1 and c.sb[k] == 1 and c.hb[k] == 0:
            key = ('+',) + tuple(sorted([a, b], key=repr))
        else:
            key = (c.sa[k], a, c.sb[k], c.hb[k], b)
        if key not in seen:
            seen[key] = ('op', len(seen))
        rep[c.n + k] = seen[key]
    return len(seen)


def main():
    print('# E1 strong-baseline correction: structurally hashed unit costs (regime F)\n')
    print('| n | p0 | seed | g1 U | g1 hashed | best UBP hashed (g) | best CBP hashed (g) | g1h / UBPh | g1h / CBPh |')
    print('|---|---|---|---|---|---|---|---|---|')
    for n in (64, 128, 256, 512, 1024):
        for p0 in (0.33, 0.5):
            for seed in ((0, 1, 2) if n <= 256 else (0,)):
                rng = np.random.default_rng(1000 * seed + int(100 * p0) + n)  # identical to E1
                W = ternary(n, n, p0, rng)
                c1 = per_input(W)
                g1h = hashcons_U(c1)
                bu = min((hashcons_U(block_patterns(W, g, True)), g) for g in range(2, 7))
                bc = min((hashcons_U(block_patterns(W, g, False)), g) for g in range(2, 7))
                print(f'| {n} | {p0} | {seed} | {c1.U} | {g1h} | {bu[0]} ({bu[1]}) | {bc[0]} ({bc[1]}) | {g1h/bu[0]:.3f} | {g1h/bc[0]:.3f} |', flush=True)


if __name__ == '__main__':
    main()
