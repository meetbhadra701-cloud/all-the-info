"""XACC-E1b: is FP32 accumulation of NVFP4 GEMMs order-sensitive in practice, and is the exact path order-free?
(04 Part 1, pre-registered). Also the E1 mutation control (a too-narrow, wrapping exact accumulator).

NVFP4 recipe: per-tensor scale s_t = amax / (6*448); block scale = RNE_UE4M3(block_amax / 6 / s_t);
elements = RNE_E2M1(x / (s_b * s_t)), saturating at +-6. Block contribution in the hardware encoding:
  S = sum of 16 products of half-unit codes (quarter units), P = S * Ma * Mb, shift s = E'a + E'b - 2 in [0, 28],
  X = P << s  (units of 2^-20);  value = X * 2^-20 * s_tA * s_tB.
The independent reference is an element-level integer GEMM (no blocks, no shifts): a_int = q_half * M * 2^(E'-1),
exact int64 matmul, units 2^-20.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

E2M1_GRID = np.array([0, 0.5, 1, 1.5, 2, 3, 4, 6])
E2M1_EVEN = np.array([1, 0, 1, 0, 1, 0, 1, 0], dtype=bool)          # mantissa bit 0 (ties go here)


def ue4m3_table():
    """(value, M, E', even) for every nonzero finite UE4M3 code, sorted by value."""
    rows = []
    for e in range(16):
        for m in range(8):
            if (e, m) == (15, 7) or (e, m) == (0, 0):
                continue
            M, Ep = ((8 + m), e) if e else (m, 1)
            rows.append((M * 2.0 ** (Ep - 10), M, Ep, m % 2 == 0))
    rows.sort()
    v = np.array([r[0] for r in rows])
    return v, np.array([r[1] for r in rows]), np.array([r[2] for r in rows]), np.array([r[3] for r in rows])


UE4M3_V, UE4M3_M, UE4M3_E, UE4M3_EVEN = ue4m3_table()


def rne_to_grid(x, grid, even):
    """Round |x| to the nearest grid value, ties to the even code. Returns grid indices."""
    ax = np.abs(x)
    hi = np.clip(np.searchsorted(grid, ax), 1, len(grid) - 1)
    lo = hi - 1
    dlo, dhi = ax - grid[lo], grid[hi] - ax
    pick_hi = (dhi < dlo) | ((dhi == dlo) & even[hi])
    idx = np.where(pick_hi, hi, lo)
    return np.where(ax >= grid[-1], len(grid) - 1, idx)


def quantize_nvfp4(X, axis_blocks: int):
    """X: 2-D float64; blocks of 16 along axis `axis_blocks`. Returns (q_half int64 same shape, M, E' per block, s_t)."""
    Xb = np.moveaxis(X, axis_blocks, -1)
    shp = Xb.shape
    Xb = Xb.reshape(shp[0], shp[1] // 16, 16)
    s_t = np.float32(np.abs(X).max() / (6 * 448))
    amax_b = np.abs(Xb).max(axis=-1)
    target = (amax_b / 6.0) / float(s_t)
    grid0 = np.concatenate([[0.0], UE4M3_V])
    even0 = np.concatenate([[True], UE4M3_EVEN])
    si = rne_to_grid(target, grid0, even0)                                   # 0 = zero scale
    sval = grid0[si]
    M = np.concatenate([[0], UE4M3_M])[si]
    Ep = np.concatenate([[1], UE4M3_E])[si]
    denom = (sval * float(s_t))[..., None]
    with np.errstate(divide='ignore', invalid='ignore'):
        y = np.where(denom > 0, Xb / np.where(denom > 0, denom, 1), 0.0)
    gi = rne_to_grid(y, E2M1_GRID, E2M1_EVEN)
    q_half = (np.sign(y) * E2M1_GRID[gi] * 2).astype(np.int64)
    q_half = q_half.reshape(shp)
    return np.moveaxis(q_half, -1, axis_blocks), M, Ep, s_t


def make_data(dist: str, K: int, rng):
    if dist == 'gauss':
        A, B = rng.standard_normal((64, K)), rng.standard_normal((K, 64))
    elif dist == 'student_t3':
        A, B = rng.standard_t(3, (64, K)), rng.standard_t(3, (K, 64))
    elif dist == 'outlier_channels':
        A = rng.standard_normal((64, K))
        ch = rng.choice(K, size=max(1, K // 100), replace=False)
        A[:, ch] *= 20.0
        B = rng.standard_normal((K, 64))
    else:
        raise KeyError(dist)
    return A, B


def contributions(qa, Ma, Ea, qb, Mb, Eb):
    """Per (i, block, j): X = S * Ma * Mb << (E'a + E'b - 2), int64 (units 2^-20); also P and s."""
    nb = qa.shape[1] // 16
    S = np.einsum('ibk,bkj->ibj', qa.reshape(64, nb, 16), qb.reshape(nb, 16, 64))
    P = S * Ma[:, :, None] * Mb[None, :, :]
    s = Ea[:, :, None] + Eb[None, :, :] - 2
    assert np.abs(P).max() < 2 ** 19 and s.min() >= 0 and s.max() <= 28
    return P, s, P << s


def fp32_accumulate(C32, order):
    """C32: (64, nb, 64) float32 contributions. order: ('seq',) | ('split', n) | ('tree',) | ('perm', idx)."""
    nb = C32.shape[1]
    kind = order[0]
    if kind in ('seq', 'perm'):
        idx = range(nb) if kind == 'seq' else order[1]
        acc = np.zeros((64, 64), np.float32)
        for b in idx:
            acc = acc + C32[:, b, :]
        return acc
    if kind == 'split':
        parts = []
        for chunk in np.array_split(np.arange(nb), order[1]):
            acc = np.zeros((64, 64), np.float32)
            for b in chunk:
                acc = acc + C32[:, b, :]
            parts.append(acc)
        out = np.zeros((64, 64), np.float32)
        for p in parts:
            out = out + p
        return out
    if kind == 'tree':
        cur = [C32[:, b, :] for b in range(nb)]
        while len(cur) > 1:
            nxt = [cur[i] + cur[i + 1] for i in range(0, len(cur) - 1, 2)]
            if len(cur) % 2:
                nxt.append(cur[-1])
            cur = nxt
        return cur[0]
    raise KeyError(kind)


def rne_int_to_f32(v: np.ndarray, lsb_exp: int) -> np.ndarray:
    """Exact round-to-nearest-even of int64 values * 2^lsb_exp to float32 (no double rounding)."""
    sgn = np.sign(v)
    mag = np.abs(v).astype(object)
    out = np.empty(v.shape, dtype=np.float32)
    flat_m, flat_o, flat_s = mag.ravel(), out.ravel(), sgn.ravel()
    for i, m in enumerate(flat_m):
        m = int(m)
        n = m.bit_length()
        if n > 24:
            sh = n - 24
            q, r = m >> sh, m & ((1 << sh) - 1)
            half = 1 << (sh - 1)
            if r > half or (r == half and (q & 1)):
                q += 1
            m = q << sh
        flat_o[i] = np.float32(np.ldexp(float(m), lsb_exp)) * flat_s[i]
    return out


def ulp_key(f32: np.ndarray) -> np.ndarray:
    """Monotone integer key of float32 values (for ULP distances)."""
    i = f32.view(np.int32).astype(np.int64)
    return np.where(i < 0, -(i & 0x7FFFFFFF), i)


def run(setting: dict, seed: int):
    rng = np.random.default_rng(seed)
    A, B = make_data(setting['dist'], setting['K'], rng)
    qa, Ma, Ea, sta = quantize_nvfp4(A, 1)
    qb, Mb, Eb, stb = quantize_nvfp4(B, 0)
    Mb, Eb = Mb.T, Eb.T                                              # (column, block) -> (block, column)
    P, s, X = contributions(qa, Ma, Ea, qb, Mb, Eb)
    nb = X.shape[1]
    # independent reference: element-level integers in units of 2^-10 per operand
    a_int = qa * np.repeat(Ma, 16, axis=1) * (1 << (np.repeat(Ea, 16, axis=1) - 1))
    b_int = qb * np.repeat(Mb, 16, axis=0) * (1 << (np.repeat(Eb, 16, axis=0) - 1))
    ref = a_int @ b_int
    # orders
    orders = [('seq',)] + [('split', n) for n in (2, 4, 8, 16, 32)] + [('tree',), ('perm', rng.permutation(nb))]
    names = ['seq', 'split2', 'split4', 'split8', 'split16', 'split32', 'tree', 'perm']
    scale = np.float32(sta) * np.float32(stb)
    C32 = np.ldexp(P.astype(np.float32), (s - 20).astype(np.int32)).astype(np.float32)
    assert np.array_equal(C32.astype(np.float64) * 2.0 ** 20, X.astype(np.float64))      # contributions exact in FP32
    fp = np.stack([fp32_accumulate(C32, o) * scale for o in orders])
    # exact path: integer sums in each order (int64 is exact and associative), one rounding at the end
    ex_sums = []
    for o in orders:
        if o[0] == 'perm':
            ex_sums.append(X[:, o[1], :].sum(axis=1))
        elif o[0] == 'split':
            ex_sums.append(sum(X[:, c, :].sum(axis=1) for c in np.array_split(np.arange(nb), o[1])))
        else:
            ex_sums.append(X.sum(axis=1))
    ex_sums = np.stack(ex_sums)
    exact_ok = bool(all(np.array_equal(e, ref) for e in ex_sums))
    ex = np.stack([rne_int_to_f32(e, -20) * scale for e in ex_sums])
    ex_true = rne_int_to_f32(ref, -20) * scale
    # mutation control: an exact accumulator that wraps at W-12 bits (W from E1a for this K)
    W = {4096: 56, 16384: 58}[setting['K']]
    wbits = W - 12
    wrap = ((X.sum(axis=1) + (1 << (wbits - 1))) % (1 << wbits)) - (1 << (wbits - 1))
    mutant_detected = bool(not np.array_equal(wrap, ref))
    k_fp, k_ex = ulp_key(fp), ulp_key(ex)
    differ_fp = (k_fp.max(0) != k_fp.min(0))
    differ_ex = (k_ex.max(0) != k_ex.min(0))
    rel = np.abs(fp[0].astype(np.float64) - ref * 2.0 ** -20 * float(scale)) / np.maximum(np.abs(ref * 2.0 ** -20 * float(scale)), 1e-300)
    return {'setting': setting, 'seed': seed, 'orders': names,
            'fp32_outputs_order_sensitive_frac': float(differ_fp.mean()),
            'fp32_max_ulp_spread': int((k_fp.max(0) - k_fp.min(0)).max()),
            'fp32_median_ulp_spread': float(np.median(k_fp.max(0) - k_fp.min(0))),
            'fp32_pairwise_differ_vs_seq': {n: float((k_fp[i] != k_fp[0]).mean()) for i, n in enumerate(names)},
            'fp32_seq_rel_err_vs_exact_median': float(np.median(rel)), 'fp32_seq_rel_err_vs_exact_max': float(rel.max()),
            'exact_outputs_order_sensitive_frac': float(differ_ex.mean()),
            'exact_sums_equal_independent_reference': exact_ok,
            'exact_rounded_equals_reference_rounded': bool(np.array_equal(ex[0].view(np.int32), ex_true.view(np.int32))),
            'mutation_wrap_bits': wbits, 'mutation_detected': mutant_detected,
            'max_abs_sum_bits': int(np.abs(ref).max()).bit_length() + 1,
            'blocks': nb, 'zero_scale_blocks': int((Ma == 0).sum() + (Mb == 0).sum())}


def main(out: Path):
    settings = [{'dist': d, 'K': K} for K in (4096, 16384) for d in ('gauss', 'student_t3', 'outlier_channels')]
    res = [run(st, 1000 + i) for i, st in enumerate(settings)]
    out.mkdir(parents=True, exist_ok=True)
    (out / 'e1b_order_invariance.json').write_text(json.dumps(res, indent=1))
    hdr = ('| Data | K | FP32: outputs order-sensitive | FP32 max / median ULP spread | FP32 rel. err. (median / max) | '
           'Exact: order-sensitive | Exact = independent reference | Wrap mutant detected |')
    lines = [hdr, '|---|---|---|---|---|---|---|---|']
    for r in res:
        st = r['setting']
        lines.append(f"| {st['dist']} | {st['K']} | {100 * r['fp32_outputs_order_sensitive_frac']:.1f}% | "
                     f"{r['fp32_max_ulp_spread']} / {r['fp32_median_ulp_spread']:.0f} | "
                     f"{r['fp32_seq_rel_err_vs_exact_median']:.2e} / {r['fp32_seq_rel_err_vs_exact_max']:.2e} | "
                     f"{100 * r['exact_outputs_order_sensitive_frac']:.1f}% | {r['exact_sums_equal_independent_reference']} | "
                     f"{r['mutation_detected']} (wrap {r['mutation_wrap_bits']} b; max |sum| {r['max_abs_sum_bits']} b) |")
    (out / 'e1b_order_invariance.md').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main(Path(__file__).resolve().parent / 'results')
