"""SPEF for the ROUTED programmable nets of one program (R3 timing with routed geometry; not pre-registered, a rigor
check of the placement-parasitic model).

python3 r3_prog_spef.py PROGRAM_DEF OUT_SPEF
Each pgm_* net: wire length per layer from its routed DEF segments (met4/met5) and its via4 count, converted with
the platform's own RC (flow/platforms/sky130hd/setRC.tcl). Conservative lumped model: the whole wire capacitance
sits at one internal node behind the whole wire resistance; every sink hangs off that node with 1 mOhm.
Elmore delay to every sink is therefore >= that of any tree-shaped distribution of the same wire.
"""
from __future__ import annotations

import re
import sys

# setRC.tcl: capacitance pF/um, resistance kOhm/um (vias: kOhm per cut)
RC = {'met4': (1.48128e-4, 1.68093e-4), 'met5': (1.54087e-4, 1.83558e-5)}
VIA4_KOHM = 0.00580e-3


def main(def_path, out):
    d = open(def_path).read()
    units = int(re.search(r'UNITS DISTANCE MICRONS (\d+)', d).group(1))
    nets = d[d.index('\nNETS'):d.index('END NETS')]
    lines = ['*SPEF "ieee 1481-1999"', '*DESIGN "top"', '*DATE "r3"', '*VENDOR "r3_prog_spef"', '*PROGRAM "r3_prog_spef.py"',
             '*VERSION "1"', '*DESIGN_FLOW "NAME_SCOPE LOCAL" "PIN_CAP NONE"', '*DIVIDER /', '*DELIMITER :',
             '*BUS_DELIMITER []', '*T_UNIT 1 NS', '*C_UNIT 1 PF', '*R_UNIT 1 OHM', '*L_UNIT 1 HENRY', '']
    stats = []
    for blk in nets.split(';'):
        m = re.search(r'-\s+(pgm_\S+)', blk)
        if not m:
            continue
        name = m.group(1)
        pins = re.findall(r'\(\s*(\S+)\s+(\S+)\s*\)', blk.split('+')[0])
        drv = [f'{i}:{p}' for i, p in pins if i.startswith('lt_')]
        snk = [f'{i}:{p}' for i, p in pins if i.startswith('vs_')]
        length = {'met4': 0.0, 'met5': 0.0}
        nvia = 0
        for stmt in re.findall(r'(?:ROUTED|NEW)\s+(met4|met5)\s+(.*?)(?=\n\s*NEW|\Z)', blk, re.S):
            layer, body = stmt
            pts = []
            for tok in re.finditer(r'\(\s*([-\d*]+)\s+([-\d*]+)(?:\s+[-\d]+)?\s*\)|(\bM4M5\w*|\bvia4\w*)', body):
                if tok.group(3):
                    nvia += 1
                    continue
                x, y = tok.group(1), tok.group(2)
                if pts:
                    px, py = pts[-1]
                    x = px if x == '*' else int(x)
                    y = py if y == '*' else int(y)
                else:
                    x, y = int(x), int(y)
                pts.append((x, y))
            if 'RECT' in body:
                pts = pts[:1]          # patch shapes: not wire length
            for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                length[layer] += (abs(x2 - x1) + abs(y2 - y1)) / units
        c = sum(length[L] * RC[L][0] for L in length)
        r = (sum(length[L] * RC[L][1] for L in length) + nvia * VIA4_KOHM) * 1000.0
        stats.append((name, length['met4'], length['met5'], nvia, r, c))
        lines += [f'*D_NET {name} {c:.6e}', '*CONN']
        lines += [f'*I {p} O' for p in drv] + [f'*I {p} I' for p in snk]
        lines += ['*CAP', f'1 {name}:1 {c:.6e}', '*RES', f'1 {drv[0]} {name}:1 {max(r, 1e-3):.6e}']
        lines += [f'{k + 2} {name}:1 {p} 1.000000e-03' for k, p in enumerate(snk)]
        lines += ['*END', '']
    open(out, 'w').write('\n'.join(lines) + '\n')
    tot4 = sum(s[1] for s in stats); tot5 = sum(s[2] for s in stats)
    worst = max(stats, key=lambda s: s[4] * s[5])
    print(f'{len(stats)} programmable nets; met4 {tot4:,.0f} um, met5 {tot5:,.0f} um, vias {sum(s[3] for s in stats)}; '
          f'largest RC net {worst[0]}: R {worst[4]:.1f} Ohm, C {worst[5] * 1000:.1f} fF')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
