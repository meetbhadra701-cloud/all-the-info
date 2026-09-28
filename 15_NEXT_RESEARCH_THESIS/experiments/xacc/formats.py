"""XACC-E1a: exact-accumulator width of each low-precision format, by enumeration (04 Part 1).

Every representable magnitude of a format is written as M * 2^(E - bias_shift) with integer M. A contribution to a
dot product is either one element product (per-tensor-scaled formats: FP8, FP16, BF16) or one block's exact element
sum times the product of the two block scales (block-scaled formats). The exact accumulator needs
  LSB   = the smallest exponent any nonzero contribution can have,
  width = bits(n_contrib * max|contribution| / 2^LSB) + 1 (sign).
Per-tensor FP32 scales are applied once at readout and do not enter the window.
"""
from __future__ import annotations

import itertools
import json
import math
from fractions import Fraction
from pathlib import Path


def fp_codes(ebits: int, mbits: int, bias: int, signed: bool, nan_codes=(), inf_codes=()):
    """All finite nonzero magnitudes as (M, E) with value = M * 2^E (integers), plus 0."""
    out = set()
    for e in range(2 ** ebits):
        for m in range(2 ** mbits):
            if (e, m) in nan_codes or (e, m) in inf_codes:
                continue
            if e == 0:
                M, E = m, 1 - bias - mbits
            else:
                M, E = (1 << mbits) + m, e - bias - mbits
            if M:
                out.add((M, E))
    return sorted(out)


def as_fraction(M, E):
    return Fraction(M) * (Fraction(2) ** E)


# ---------------------------------------------------------------------------------------------- format catalogue
E2M1 = fp_codes(2, 1, 1, True)                                   # {0.5,1,1.5,2,3,4,6}
E4M3 = fp_codes(4, 3, 7, True, nan_codes={(15, 7)})               # OCP E4M3: max 448, NaN S.1111.111
UE4M3 = E4M3                                                      # NVFP4 block scale (sign unused)
UE5M3 = fp_codes(5, 3, 15, False, nan_codes={(31, 7)})            # Graphcore UE5M3 (assumed NaN at all-ones)
E5M2 = fp_codes(5, 2, 15, True, inf_codes={(31, m) for m in range(4)})
E8M0 = [(1, e - 127) for e in range(255)]                         # 2^(e-127), e = 255 is NaN
FP16 = fp_codes(5, 10, 15, True, inf_codes={(31, m) for m in range(1024)})
BF16 = fp_codes(8, 7, 127, True, inf_codes={(255, m) for m in range(128)})


def product_set(A, B):
    """(M, E) of every product of a magnitude from A and one from B."""
    return {(ma * mb, ea + eb) for (ma, ea), (mb, eb) in itertools.product(A, B)}


def window(contribs, n_contrib: int):
    """contribs: iterable of (M, E) magnitudes. Returns (lsb_exp, width_bits, max_contribution)."""
    lsb = min(E + ((M & -M).bit_length() - 1) for M, E in contribs)      # smallest set bit of any contribution
    mx = max(as_fraction(M, E) for M, E in contribs)
    bound = mx * n_contrib / (Fraction(2) ** lsb)                            # max |sum| in LSB units
    bits = math.ceil(math.log2(bound + 1)) if bound >= 1 else 1
    if (1 << bits) <= bound:
        bits += 1
    return lsb, bits + 1, mx


def block_format(elems, scales, block: int, K: int):
    """Block-scaled: contribution = (sum of `block` element products) * scale_a * scale_b."""
    ep = product_set(elems, elems)
    # exact block sum: every element product is an integer multiple of 2^e_lsb; the block sum lives on that grid
    e_lsb = min(E + ((M & -M).bit_length() - 1) for M, E in ep)
    emax = max(as_fraction(M, E) for M, E in ep)
    smax_units = int(emax * block / (Fraction(2) ** e_lsb))                 # max |block sum| in 2^e_lsb units
    sp = product_set(scales, scales)
    # contribution = S_units * 2^e_lsb * Ms * 2^Es ; S_units ranges over integers 1..smax_units
    contribs_lsb = min(e_lsb + Es + ((Ms & -Ms).bit_length() - 1) for Ms, Es in sp)
    cmax = max(Fraction(smax_units) * (Fraction(2) ** e_lsb) * as_fraction(Ms, Es) for Ms, Es in sp)
    n = K // block
    bound = cmax * n / (Fraction(2) ** contribs_lsb)
    bits = math.ceil(math.log2(bound + 1))
    if (1 << bits) <= bound:
        bits += 1
    span = max(Es for _, Es in sp) - min(Es for _, Es in sp)
    return {'lsb_exp': contribs_lsb, 'width_bits': bits + 1, 'max_contribution': float(cmax),
            'block_sum_max_units': smax_units, 'block_sum_bits': smax_units.bit_length() + 1,
            'scale_exponent_span': span, 'contributions': n}


def per_tensor_format(elems, K: int):
    """Closed form (the full product set of FP16/BF16 has ~4e9 pairs): the smallest set bit of a product is the sum of
    the two smallest set bits, and the largest product is the square of the largest magnitude."""
    lsb1 = min(E + ((M & -M).bit_length() - 1) for M, E in elems)
    mx1 = max(as_fraction(M, E) for M, E in elems)
    lsb, mx = 2 * lsb1, mx1 * mx1
    bound = mx * K / (Fraction(2) ** lsb)
    bits = math.ceil(math.log2(bound + 1))
    if (1 << bits) <= bound:
        bits += 1
    span = 2 * (max(E for _, E in elems) - min(E for _, E in elems))
    return {'lsb_exp': lsb, 'width_bits': bits + 1, 'max_contribution': float(mx), 'product_exponent_span': span,
            'contributions': K}


def _check_closed_form():
    """The closed form equals full enumeration where enumeration is affordable (E4M3, E5M2)."""
    for fmt in (E4M3, E5M2, E2M1):
        lsb, w, mx = window(product_set(fmt, fmt), 4096)
        d = per_tensor_format(fmt, 4096)
        assert (lsb, w, float(mx)) == (d['lsb_exp'], d['width_bits'], d['max_contribution']), (lsb, w, mx, d)


FORMATS = {
    'NVFP4 (E2M1, 16, UE4M3)': lambda K: block_format(E2M1, UE4M3, 16, K),
    'NVFP4-UE5M3 (E2M1, 16, UE5M3)': lambda K: block_format(E2M1, UE5M3, 16, K),
    'MXFP4 (E2M1, 32, E8M0)': lambda K: block_format(E2M1, E8M0, 32, K),
    'MXFP8 (E4M3, 32, E8M0)': lambda K: block_format(E4M3, E8M0, 32, K),
    'FP8-E4M3 per-tensor': lambda K: per_tensor_format(E4M3, K),
    'FP8-E5M2 per-tensor': lambda K: per_tensor_format(E5M2, K),
    'FP16': lambda K: per_tensor_format(FP16, K),
    'BF16': lambda K: per_tensor_format(BF16, K),
}


def nvfp4_contribution_check():
    """Exhaustive check of the hardware encoding used by the RTL: every E2M1 pair, every UE4M3 pair.
    P = S_int * M_ab with S_int in quarter units (|S_int| <= 16*144), t = E'a + E'b - 22, shift s = t + 20 in [0, 28]."""
    q = sorted({int(as_fraction(M, E) * 2) for M, E in E2M1})               # half-units: 1,2,3,4,6,8,12
    assert q == [1, 2, 3, 4, 6, 8, 12], q
    s_int_max = 16 * max(q) ** 2
    Ms, shifts = [], []
    for e in range(16):
        for m in range(8):
            if (e, m) == (15, 7):
                continue
            M, Ep = ((8 + m), e) if e else (m, 1)
            assert as_fraction(M, Ep - 10) == (as_fraction(8 + m, e - 10) if e else as_fraction(m, -9))
            Ms.append(M)
            shifts.append(Ep)
    p_max = s_int_max * max(a * b for a in Ms for b in Ms if a and b)
    s_range = (min(shifts) * 2 - 2, max(shifts) * 2 - 2)
    # the largest contribution in LSB (2^-20) units, and the exact width for K = 65536
    top = max((s_int_max * Ma * Mb) << (Ea + Eb - 2) for Ma, Ea in zip(Ms, shifts) for Mb, Eb in zip(Ms, shifts))
    return {'q_half_units': q, 'S_int_max': s_int_max, 'S_int_bits_signed': s_int_max.bit_length() + 1,
            'P_max': p_max, 'P_bits_signed': p_max.bit_length() + 1, 'shift_range': s_range,
            'X_bits_signed': (top).bit_length() + 1, 'max_contribution_lsb_units': top,
            'W_K65536': (top * 4096).bit_length() + 1, 'W_K16384': (top * 1024).bit_length() + 1,
            'W_K4096': (top * 256).bit_length() + 1}


def main(out: Path):
    _check_closed_form()
    res = {'formats': {}, 'nvfp4_encoding': nvfp4_contribution_check()}
    for name, fn in FORMATS.items():
        res['formats'][name] = {K: fn(K) for K in (4096, 16384, 65536)}
    out.mkdir(parents=True, exist_ok=True)
    (out / 'e1a_widths.json').write_text(json.dumps(res, indent=1, default=str))
    lines = ['| Format | W(4096) | W(16384) | W(65536) | LSB exponent | exponent span |', '|---|---|---|---|---|---|']
    for name, d in res['formats'].items():
        span = d[65536].get('scale_exponent_span', d[65536].get('product_exponent_span'))
        lines.append(f"| {name} | {d[4096]['width_bits']} | {d[16384]['width_bits']} | {d[65536]['width_bits']} | "
                     f"{d[65536]['lsb_exp']} | {span} |")
    (out / 'e1a_widths.md').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    print(json.dumps(res['nvfp4_encoding'], indent=1))


if __name__ == '__main__':
    main(Path(__file__).resolve().parent / 'results')
