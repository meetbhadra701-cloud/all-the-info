"""Architecture: blocks, canonical patterns, programmable lines, bands, and the W -> leaf selection rule.

Everything here is a pure function of the configuration (and of W for `leaf_source`). Names are the historical
ones (R3 / G2), so generated artifacts are directly comparable with the validated implementation.

  fabric 'ubp' (B): blocks of g inputs; per block all canonical signed patterns P_g (first non-zero entry +1),
      each line pair pp{b}_{i} / pn{b}_{i}; leaf (row i, block b) selects +-pattern or the local zero.
  fabric 'g1'  (A): one line pair lp{j} / ln{j} per input; leaf (i, j) selects lp / ln / zero.
  fabric 'pc2' (P2): one line pair lp{j} / ln{j} per input (bit-plane); per-row 7-bit constant #(w_ij = -1)
      programmed through constant sites cst_{i}_{b}.
"""
from __future__ import annotations

import math
import re

import numpy as np

from ._legacy import XMAX, canon_patterns, width

LINE_RE = {'ubp': re.compile(r'p([pn])(\d+)_(\d+)$'), 'g1': re.compile(r'l([pn])(\d+)$'),
           'pc2': re.compile(r'l([pn])(\d+)$')}
CONST_BITS = 7          # pc2 per-row constant width


def blocks(cfg):
    g = cfg.g if cfg.fabric == 'ubp' else 1
    return [list(range(s, min(s + g, cfg.n))) for s in range(0, cfg.n, g)]


def leaves_per_row(cfg) -> int:
    return len(blocks(cfg))


def lines(cfg) -> list[str]:
    """All programmable line nets, sorted as strings (the historical tap order)."""
    if cfg.fabric == 'ubp':
        out = []
        for b, cols in enumerate(blocks(cfg)):
            for i in range(len(canon_patterns(len(cols)))):
                out += [f'pp{b}_{i}', f'pn{b}_{i}']
    else:
        out = [f'l{p}{j}' for j in range(cfg.n) for p in 'pn']
    return sorted(out)


def band_lines(cfg) -> dict[int, list[str]]:
    """Band = one block (ubp) or one input (g1, pc2). Line order inside a band: (pattern index, polarity p < n).
    Dict order = first appearance of the band in the string-sorted line list ('pn0_' < 'pn10_' < 'pn1_'): this is the
    order in which the validated R3 placer placed the taps (0, 10, 11, ..., 19, 1, 20, 21, 2, ...), and placement is sequential, so it is kept."""
    rx = LINE_RE[cfg.fabric]
    bands: dict[int, list[tuple[int, int, str]]] = {}
    for L in lines(cfg):
        m = rx.match(L)
        idx = int(m.group(3)) if cfg.fabric == 'ubp' else 0
        bands.setdefault(int(m.group(2)), []).append((idx, 0 if m.group(1) == 'p' else 1, L))
    return {b: [L for _, _, L in sorted(v)] for b, v in bands.items()}


def output_width(cfg) -> int:
    return width(XMAX * cfg.n)


def cycles_per_word(cfg) -> int:
    return 8 if cfg.fabric == 'pc2' else output_width(cfg)


def serial_latency(cfg) -> int:
    """Bit-serial latency (word start -> first output bit): line latency + tree depth. pc2: found by simulation."""
    if cfg.fabric == 'pc2':
        return None
    L = leaves_per_row(cfg)
    depth = math.ceil(math.log2(L)) if L > 1 else 0
    if cfg.fabric == 'g1':
        line_lat = 1
    else:
        line_lat = max(len(c) for c in blocks(cfg)) - 1 + 1     # generator latency g-1, plus the negator
    return line_lat + depth


def leaf_source(cfg, W, i: int, k: int):
    """Line net feeding leaf (row i, slot k) for weight matrix W, or None for the local zero option.
    Identical rule to e6_build / g3_build / g2_build.leaf_source."""
    if cfg.fabric in ('g1', 'pc2'):
        w = int(W[i, k])
        return None if w == 0 else (f'lp{k}' if w > 0 else f'ln{k}')
    cols = blocks(cfg)[k]
    q = tuple(int(W[i, c]) for c in cols)
    if not any(q):
        return None
    s = next(v for v in q if v)
    idx = canon_patterns(len(cols)).index(tuple(s * v for v in q))
    return f'pp{k}_{idx}' if s > 0 else f'pn{k}_{idx}'


def row_constant(W, i: int) -> int:
    """pc2 only: number of negative weights in row i (the complement-lane correction)."""
    return int((W[i] < 0).sum())


def counts(cfg) -> dict:
    """Exact structural counts (DERIVED) used by tests and provenance."""
    L = lines(cfg)
    lpr = leaves_per_row(cfg)
    return {'lines': len(L), 'taps': len(L) * cfg.K, 'sites': cfg.m * lpr, 'leaves_per_row': lpr,
            'bands': len(band_lines(cfg)), 'const_sites': cfg.m * CONST_BITS if cfg.fabric == 'pc2' else 0,
            'segment_rows': cfg.m // cfg.K, 'output_width': output_width(cfg), 'cycles_per_word': cycles_per_word(cfg)}


def check_weights(cfg, W: np.ndarray):
    if W.shape != (cfg.m, cfg.n):
        raise ValueError(f'W has shape {W.shape}, expected {(cfg.m, cfg.n)}')
    if not np.isin(W, (-1, 0, 1)).all():
        raise ValueError('W must be ternary {-1, 0, 1}')
    if cfg.fabric == 'pc2' and int((W < 0).sum(axis=1).max(initial=0)) >= 2 ** CONST_BITS:
        raise ValueError('pc2: a row has too many negative weights for the 7-bit constant')
