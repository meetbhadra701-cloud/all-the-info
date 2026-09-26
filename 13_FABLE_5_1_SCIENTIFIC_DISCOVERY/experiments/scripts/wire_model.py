"""Analytic area model for via/metal-programmable (regime V) hardwired ternary layers.

THIS IS A MODEL, NOT A MEASUREMENT. It exposes the assumption that decides whether A1 pays in
regime V: the select wiring of block-pattern lines must fit above the per-row logic.

Per (row, block) programmable site, the area is max(logic, select-wiring) where
  logic  = the site's share of the row accumulation hardware
  wiring = (#candidate lines crossing the site) * (bits per line) * track_pitch * row_height
A universal generator per block is added once (shared by all m rows).

Arithmetic styles:
  bit-parallel : one w-bit ripple adder per site, w ~ bits of the running sum; lines are b-bit buses
  bit-serial   : one serial adder (1 FA + 1 carry DFF) per site; lines are single wires

SKY130 HD constants (liberty tt_025C_1v80, OBSERVED): FA_1 = 20.0192 um^2, DFXTP_1 = 20.0192 um^2,
row height 2.72 um. Track pitch is a parameter: 0.46 (met2), 0.68 (met3), 0.92 (met4) um.
"""
from __future__ import annotations

import math

FA = 20.0192
DFF = 20.0192
H = 2.72


def site_logic_parallel(n, g):
    # average adder width in a balanced tree summing ceil(n/g) values of width ~ 8+ceil(log2(g))+1
    leaves = math.ceil(n / g)
    w0 = 8 + math.ceil(math.log2(g)) + (1 if g > 1 else 0)
    # a balanced tree: level l has leaves/2^l adders of width w0 + l
    tot, cnt, cur, l = 0.0, 0, leaves, 1
    while cur > 1:
        a = cur // 2
        tot += a * (w0 + l); cnt += a
        cur = cur - a
        l += 1
    return FA * tot / leaves  # FA-equivalents per site (ripple adders)


def site_logic_serial():
    return FA + DFF


def generator_area(g, style, n):
    # universal generator per block: (3^g-1)/2 - g adders; per row-site amortization happens outside
    adders = (3 ** g - 1) // 2 - g
    if style == 'serial':
        return adders * (FA + DFF)
    w = 8 + math.ceil(math.log2(max(g, 2)))
    return adders * FA * w


def lines_per_site(g):
    # canonical patterns (sign handled by add/sub polarity at the site); g=1: the input itself
    return (3 ** g - 1) // 2


def area_V(m, n, g, style, pitch):
    nb = math.ceil(n / g)
    logic = site_logic_serial() if style == 'serial' else site_logic_parallel(n, g)
    bits = 1 if style == 'serial' else (8 + math.ceil(math.log2(g)) + (1 if g > 1 else 0))
    wiring = lines_per_site(g) * bits * pitch * H
    per_site = max(logic, wiring)
    return m * nb * per_site + nb * generator_area(g, style, n), logic, wiring


def main():
    print('# Regime-V analytic area model (MODEL, not measurement)\n')
    for m, n in [(1024, 1024), (4096, 4096)]:
        for style in ('parallel', 'serial'):
            for pitch in (0.46, 0.92):
                base, _, _ = area_V(m, n, 1, style, pitch)
                row = []
                for g in range(1, 7):
                    a, lg, wr = area_V(m, n, g, style, pitch)
                    row.append(f'g={g}: {base/a:.2f}x ({"wire" if wr > lg else "logic"}-bound)')
                print(f'm=n={n} {style:8s} pitch={pitch} um | area(g=1)/area(g): ' + '; '.join(row))
        print()


if __name__ == '__main__':
    main()
