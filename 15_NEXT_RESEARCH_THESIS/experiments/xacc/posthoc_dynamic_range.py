"""POST HOC (not pre-registered, not decisive): why is FP32 accumulation of NVFP4 blocks order-invariant, and how does
that depend on within-row dynamic range? Diagnosis of the E1b kill, not a rescue (the classification stands)."""
import json
from pathlib import Path

import numpy as np

import order_invariance as oi


def run(scale_outlier: float, frac: float, K: int, seed: int):
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((64, K))
    ch = rng.choice(K, size=max(1, int(K * frac)), replace=False)
    A[:, ch] *= scale_outlier
    B = rng.standard_normal((K, 64))
    qa, Ma, Ea, sta = oi.quantize_nvfp4(A, 1)
    qb, Mb, Eb, stb = oi.quantize_nvfp4(B, 0)
    Mb, Eb = Mb.T, Eb.T
    P, s, X = oi.contributions(qa, Ma, Ea, qb, Mb, Eb)
    C32 = np.ldexp(P.astype(np.float32), (s - 20).astype(np.int32)).astype(np.float32)
    nb = X.shape[1]
    orders = [('seq',)] + [('split', n) for n in (2, 4, 8, 16, 32)] + [('tree',), ('perm', rng.permutation(nb))]
    fp = np.stack([oi.fp32_accumulate(C32, o) for o in orders])
    k = oi.ulp_key(fp)
    # rounding events in the sequential order: partial sums that are not exact in FP32
    acc = np.zeros((64, 64), np.float32)
    exact = np.zeros((64, 64), np.int64)
    inexact = 0
    for b in range(nb):
        acc = acc + C32[:, b, :]
        exact = exact + X[:, b, :]
        inexact += int((acc.astype(np.float64) * 2.0 ** 20 != exact.astype(np.float64)).sum())
    active = X != 0
    s_act = np.where(active, s, -1)
    span = np.array([[np.ptp(s[i, active[i, :, j], j]) if active[i, :, j].any() else 0 for j in range(64)] for i in range(64)])
    return {'outlier_scale': scale_outlier, 'outlier_frac': frac, 'K': K,
            'fp32_order_sensitive_frac': float((k.max(0) != k.min(0)).mean()),
            'fp32_max_ulp_spread': int((k.max(0) - k.min(0)).max()),
            'seq_partial_sums_inexact_frac': inexact / (64 * 64 * nb),
            'shift_span_median': float(np.median(span)), 'shift_span_max': int(span.max())}


if __name__ == '__main__':
    out = []
    for K in (16384, 65536):
        for sc, fr in ((1.0, 0.0), (20.0, 0.01), (100.0, 0.001), (1000.0, 0.001), (10000.0, 0.0005)):
            r = run(sc, fr, K, 7)
            out.append(r)
            print(r, flush=True)
    Path('results/posthoc_dynamic_range.json').write_text(json.dumps(out, indent=1))
