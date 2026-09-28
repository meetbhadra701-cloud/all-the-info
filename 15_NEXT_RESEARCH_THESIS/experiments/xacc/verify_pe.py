"""XACC-E2 functional validity (04 Part 1): a PE netlist (RTL or post-route 6_final.v) -> Yosys -> AIGER -> our own
bit-parallel simulator, against cycle-accurate goldens whose arithmetic is independent of the RTL:
  EXACT      Python/numpy int64 sums of block values computed from the format tables (units 2^-20);
  FP32 RNE   numpy float32 IEEE addition, cross-checked every step against an exact-integer RNE model;
  FP32 RZ    exact-integer truncation model.
Stimulus: 1024 streams x ~4100 cycles: random lanes (clr probability 1/8 or 1/64) and directed lanes (maximum
positive / negative contributions for 4096 blocks without clr, alternating-sign cancellation, subnormal scales).
Mutation controls: a design mutant (RTL shift off by one) and reference mutants (59-bit wrapping exact golden; RZ
golden for the RNE design) must all be detected.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from aigsim import AIGSim, pack_bits, unpack_bits  # noqa: E402

IMAGE = 'openroad/orfs:latest'
TT_LIB = '/OpenROAD-flow-scripts/flow/platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib'
E2M1_VAL = np.array([0, 0.5, 1, 1.5, 2, 3, 4, 6])
LAT = {'pe_exact': 4, 'pe_fp32_rne1': 4, 'pe_fp32_rz1': 4, 'pe_fp32_rne_i2': 5}
OUTW = {'pe_exact': 60, 'pe_fp32_rne1': 32, 'pe_fp32_rz1': 32, 'pe_fp32_rne_i2': 64}


def ue4m3_decode(code: np.ndarray):
    c = code & 0x7F
    e, m = c >> 3, c & 7
    M = np.where(e > 0, 8 + m, m).astype(np.int64)
    Ep = np.where(e > 0, e, 1).astype(np.int64)
    return M, Ep


# ------------------------------------------------------------------------------------------------ stimulus
def stimulus(T: int, lanes: int, seed: int):
    rng = np.random.default_rng(seed)
    na = rng.integers(0, 16, size=(T, lanes, 16), dtype=np.int64)
    nb = rng.integers(0, 16, size=(T, lanes, 16), dtype=np.int64)
    sa = rng.integers(0, 256, size=(T, lanes), dtype=np.int64)
    sb = rng.integers(0, 256, size=(T, lanes), dtype=np.int64)
    for s in (sa, sb):                                             # exclude the NaN code 0x7F / 0xFF
        bad = (s & 0x7F) == 0x7F
        s[bad] = s[bad] - 1
    p = np.where(np.arange(lanes) % 2 == 0, 1 / 8, 1 / 64)
    clr = (rng.random((T, lanes)) < p[None, :]).astype(np.int64)
    clr[0, :] = 1
    kind = np.array(['random'] * lanes, dtype=object)
    # directed lanes (the last 64 lanes)
    d0 = lanes - 64
    for j in range(64):
        L = d0 + j
        g = j % 8
        if g == 0:                                                 # maximum positive, 4096+ blocks, no clr
            na[:, L, :], nb[:, L, :], sa[:, L], sb[:, L], clr[1:, L], kind[L] = 7, 7, 0x7E, 0xFE, 0, 'max_pos'
        elif g == 1:                                               # maximum negative
            na[:, L, :], nb[:, L, :], sa[:, L], sb[:, L], clr[1:, L], kind[L] = 15, 7, 0x7E, 0x7E, 0, 'max_neg'
        elif g == 2:                                               # alternating sign (cancellation), no clr
            na[:, L, :] = np.where(np.arange(T)[:, None] % 2 == 0, 7, 15)
            nb[:, L, :], sa[:, L], sb[:, L], clr[1:, L], kind[L] = 7, 0x7E, 0x7E, 0, 'alternate'
        elif g == 3:                                               # subnormal scales (E' = 1)
            sa[:, L], sb[:, L] = rng.integers(1, 8, T), rng.integers(1, 8, T)
            kind[L] = 'subnormal_scales'
        elif g == 4:                                               # random codes, max scales, no clr
            sa[:, L], sb[:, L], clr[1:, L], kind[L] = 0x7E, 0x7E, 0, 'maxscale_random'
        elif g == 5:                                               # wide scale spread, no clr
            sa[:, L] = np.where(rng.random(T) < 0.5, 0x01, 0x7E)
            sb[:, L], clr[1:, L], kind[L] = rng.integers(0, 0x7F, T), 0, 'spread'
    return na, nb, sa, sb, clr, kind


def block_X(na, nb, sa, sb):
    """Exact block value in units of 2^-20 (int64), and (P, s): value = P * 2^(s-20)."""
    qa = (np.where(na >= 8, -1, 1) * E2M1_VAL[na & 7] * 2).astype(np.int64)
    qb = (np.where(nb >= 8, -1, 1) * E2M1_VAL[nb & 7] * 2).astype(np.int64)
    S = (qa * qb).sum(axis=-1)
    Ma, Ea = ue4m3_decode(sa)
    Mb, Eb = ue4m3_decode(sb)
    P = S * Ma * Mb
    s = Ea + Eb - 2
    return P << s, P, s


# ------------------------------------------------------------------------------------------------ goldens
POW2 = np.array([1 << k for k in range(63)], dtype=np.int64)


def bitlen(x: np.ndarray) -> np.ndarray:
    return np.searchsorted(POW2, x, side='right')


def round_int(v: np.ndarray, rne: bool) -> np.ndarray:
    """Round int64 values to 24 significant bits (RNE or toward zero), exactly."""
    sgn = np.sign(v)
    a = np.abs(v)
    n = bitlen(a)
    sh = np.maximum(n - 24, 0)
    q = a >> sh
    if rne:
        r = a - (q << sh)
        half = np.where(sh > 0, np.left_shift(np.int64(1), np.maximum(sh - 1, 0)), 0)
        up = (sh > 0) & ((r > half) | ((r == half) & ((q & 1) == 1)))
        q = q + up
    return sgn * (q << sh)


def golden(top: str, X, P, s, clr, T: int, wrap_bits: int | None = None, rz_for_rne: bool = False):
    """Cycle-accurate expected outputs: dict cycle -> (lanes,) python-int-compatible arrays (bit patterns)."""
    lanes = X.shape[1]
    lat = LAT[top]
    out = np.zeros((T, lanes), dtype=object)
    if top == 'pe_exact':
        acc = np.zeros(lanes, dtype=np.int64)
        for c in range(T - lat):
            acc = np.where(clr[c] == 1, 0, acc) + X[c]
            v = acc
            if wrap_bits:
                v = ((v + (1 << (wrap_bits - 1))) % (1 << wrap_bits)) - (1 << (wrap_bits - 1))
            out[c + lat] = [int(x) & ((1 << 60) - 1) for x in v]
        return out, {}
    if top in ('pe_fp32_rne1', 'pe_fp32_rz1'):
        rne = (top == 'pe_fp32_rne1') and not rz_for_rne
        accf = np.zeros(lanes, dtype=np.float32)
        acci = np.zeros(lanes, dtype=np.int64)                       # value * 2^20 (always an integer here)
        mism = 0
        for c in range(T - lat):
            F = np.ldexp(P[c].astype(np.float32), (s[c] - 20).astype(np.int32)).astype(np.float32)
            acci = round_int(np.where(clr[c] == 1, 0, acci) + X[c], rne)
            if rne:
                accf = (np.where(clr[c] == 1, np.float32(0), accf) + F).astype(np.float32)
                mism += int((accf.astype(np.float64) * 2.0 ** 20 != acci.astype(np.float64)).sum())
                bits = accf.view(np.uint32)
            else:
                bits = (acci.astype(np.float64) * 2.0 ** -20).astype(np.float32).view(np.uint32)   # exact: 24 bits
            out[c + lat] = [int(x) for x in bits]
        return out, {'numpy_vs_integer_rne_mismatches': mism}
    if top == 'pe_fp32_rne_i2':
        acc = np.zeros((2, lanes), dtype=np.float32)
        for c in range(T - lat):
            ph = (c + 3) % 2
            F = np.ldexp(P[c].astype(np.float32), (s[c] - 20).astype(np.int32)).astype(np.float32)
            acc[ph] = (np.where(clr[c] == 1, np.float32(0), acc[ph]) + F).astype(np.float32)
            b0, b1 = acc[0].view(np.uint32), acc[1].view(np.uint32)
            out[c + lat] = [int(x) | (int(y) << 32) for x, y in zip(b0, b1)]
        return out, {}
    raise KeyError(top)


# ------------------------------------------------------------------------------------------------ netlist -> AIG
def to_aag(workdir: Path, netlist: str, top: str, aag: str, liberty: bool) -> Path:
    libs = f'read_liberty -ignore_miss_func {TT_LIB};' if liberty else ''
    cmd = (f"yosys -q -p '{libs} read_verilog {netlist}; hierarchy -top {top}; flatten; synth -top {top} -noabc; "
           f"dffunmap; setundef -zero -init; aigmap; opt_clean; write_aiger -ascii -symbols {aag}'")
    p = subprocess.run(['docker', 'run', '--rm', '-v', f'{workdir}:/work', '-w', '/work', IMAGE, 'bash', '-c', cmd],
                       capture_output=True, text=True, timeout=7200)
    if p.returncode != 0:
        raise RuntimeError(p.stderr[-3000:])
    return workdir / aag


def simulate(aag: Path, top: str, na, nb, sa, sb, clr, T: int):
    sim = AIGSim(aag)
    lanes = na.shape[1]
    words = lanes // 64
    a_int = (na << (4 * np.arange(16))).sum(-1).astype(np.uint64)
    b_int = (nb << (4 * np.arange(16))).sum(-1).astype(np.uint64)
    W = OUTW[top]
    obits = np.zeros((T, W, lanes), dtype=np.uint8)
    names_a = [f'a[{i}]' for i in range(64)]
    names_b = [f'b[{i}]' for i in range(64)]

    def drive(c):
        d = {'clk': np.zeros(words, np.uint64), 'clr': pack_bits(clr[c])}
        for i in range(64):
            d[names_a[i]] = pack_bits((a_int[c] >> np.uint64(i)) & np.uint64(1))
            d[names_b[i]] = pack_bits((b_int[c] >> np.uint64(i)) & np.uint64(1))
        for i in range(8):
            d[f'sa[{i}]'] = pack_bits((sa[c] >> i) & 1)
            d[f'sb[{i}]'] = pack_bits((sb[c] >> i) & 1)
        return {k: v for k, v in d.items() if k in sim.in_var}

    def sample(c, get):
        for i in range(W):
            obits[c, i] = unpack_bits(get(f'acc[{i}]'))
    sim.run(T, words, drive, sample)
    weights = [1 << i for i in range(W)]
    vals = np.zeros((T, lanes), dtype=object)
    for c in range(T):
        col = obits[c]
        vals[c] = [sum(w for w, b in zip(weights, col[:, L]) if b) for L in range(lanes)]
    return vals


def compare(vals, gold, top: str, T: int):
    lat = LAT[top]
    bad = [(c, L) for c in range(lat, T) for L in range(vals.shape[1]) if vals[c, L] != gold[c, L]]
    return {'cycles_checked': T - lat, 'streams': int(vals.shape[1]), 'mismatches': len(bad), 'first': bad[:5]}


def verify(workdir: Path, netlist: str, top: str, liberty: bool, T: int = 4105, lanes: int = 1024, seed: int = 11,
           mutants: bool = True) -> dict:
    na, nb, sa, sb, clr, kind = stimulus(T, lanes, seed)
    X, P, s = block_X(na, nb, sa, sb)
    aag = to_aag(workdir, netlist, top, f'_{top}_sim.aag', liberty)
    vals = simulate(aag, top, na, nb, sa, sb, clr, T)
    aag.unlink()
    gold, gstat = golden(top, X, P, s, clr, T)
    rec = {'top': top, 'netlist': netlist, 'match': compare(vals, gold, top, T), 'golden': gstat,
           'directed_lanes': sorted(set(kind[lanes - 64:]))}
    rec['matches_golden'] = rec['match']['mismatches'] == 0
    if mutants:
        mut = {}
        if top == 'pe_exact':
            g2, _ = golden(top, X, P, s, clr, T, wrap_bits=59)
            mut['reference:exact_wrap59'] = compare(vals, g2, top, T)['mismatches'] > 0
        if top == 'pe_fp32_rne1':
            g2, _ = golden(top, X, P, s, clr, T, rz_for_rne=True)
            mut['reference:rne_golden_as_rz'] = compare(vals, g2, top, T)['mismatches'] > 0
        rec['mutants_detected'] = mut
    return rec


def design_mutant(workdir: Path, top: str, T: int = 600, lanes: int = 1024, seed: int = 12) -> dict:
    """RTL mutant: the exact shift, or the FP32 conversion exponent, off by one. Must be detected."""
    src = (HERE / 'rtl' / 'xacc_pe.v').read_text()
    if top == 'pe_exact':
        mut = src.replace('X2 <= Pext <<< s1;', 'X2 <= Pext <<< (s1 + 5\'d1);')
    else:
        mut = src.replace("8'd107;\n  assign f", "8'd108;\n  assign f")
    assert mut != src
    (workdir / '_mutant.v').write_text(mut)
    na, nb, sa, sb, clr, kind = stimulus(T, lanes, seed)
    X, P, s = block_X(na, nb, sa, sb)
    aag = to_aag(workdir, '_mutant.v', top, f'_{top}_mut.aag', False)
    vals = simulate(aag, top, na, nb, sa, sb, clr, T)
    aag.unlink()
    (workdir / '_mutant.v').unlink()
    gold, _ = golden(top, X, P, s, clr, T)
    c = compare(vals, gold, top, T)
    return {'design_mutant_detected': c['mismatches'] > 0, 'mismatches': c['mismatches']}


if __name__ == '__main__':
    # RTL-level check of every top (development gate before the physical runs)
    work = HERE / 'runs' / 'rtl_check'
    work.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copy(HERE / 'rtl' / 'xacc_pe.v', work / 'xacc_pe.v')
    tops = sys.argv[1:] or ['pe_exact', 'pe_fp32_rne1', 'pe_fp32_rz1', 'pe_fp32_rne_i2']
    res = {}
    for top in tops:
        r = verify(work, 'xacc_pe.v', top, liberty=False)
        if top in ('pe_exact', 'pe_fp32_rne1'):
            r.update(design_mutant(work, top))
        res[top] = r
        print(json.dumps(r), flush=True)
    (HERE / 'results').mkdir(exist_ok=True)
    (HERE / 'results' / 'e2_rtl_verify.json').write_text(json.dumps(res, indent=1))
