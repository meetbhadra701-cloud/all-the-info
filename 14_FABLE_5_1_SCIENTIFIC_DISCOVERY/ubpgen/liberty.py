"""Minimal Liberty reader for the driver-sizing rule: cell blocks, areas, pin capacitances and NLDM tables."""
from __future__ import annotations

import bisect
import functools
import re
import subprocess

from ._legacy import IMAGE, LIB
from . import pdk


@functools.lru_cache(maxsize=4)
def text(corner: str = 'tt') -> str:
    if corner == 'tt':
        return subprocess.run(['docker', 'run', '--rm', IMAGE, 'cat', LIB], capture_output=True, text=True, check=True).stdout
    pdk.require()
    return pdk.lib_path(corner).read_text()


def _block(t: str, start: int) -> str:
    i = t.index('{', start)
    d = 0
    for j in range(i, len(t)):
        if t[j] == '{':
            d += 1
        elif t[j] == '}':
            d -= 1
            if d == 0:
                return t[start:j + 1]
    raise ValueError('unbalanced braces')


def cell_block(t: str, cell: str) -> str:
    m = re.search(r'cell\s*\(\s*"?%s"?\s*\)\s*\{' % re.escape(cell), t)
    if m is None:
        raise KeyError(cell)
    return _block(t, m.start())


def pin_block(cb: str, pin: str) -> str:
    m = re.search(r'pin\s*\(\s*"?%s"?\s*\)\s*\{' % re.escape(pin), cb)
    return _block(cb, m.start())


def area(cb: str) -> float:
    return float(re.search(r'\barea\s*:\s*([\d.]+)', cb).group(1))


def pin_cap(cb: str, pin: str) -> float:
    """Worst of capacitance / rise_capacitance / fall_capacitance of an input pin (pF)."""
    pb = pin_block(cb, pin)
    vals = [float(x) for x in re.findall(r'\b(?:rise_|fall_)?capacitance\s*:\s*([\d.]+)', pb)]
    return max(vals)


def tables(cb: str, pin: str, kind: str):
    pb = pin_block(cb, pin)
    out = []
    for m in re.finditer(kind + r'\s*\(\s*"?[\w]+"?\s*\)\s*\{', pb):
        b = _block(pb, m.start())
        i1 = [float(x) for x in re.search(r'index_1\s*\(\s*"([^"]+)"', b).group(1).split(',')]
        i2 = [float(x) for x in re.search(r'index_2\s*\(\s*"([^"]+)"', b).group(1).split(',')]
        rows = [[float(x) for x in r.split(',')] for r in re.findall(r'"([^"]+)"', re.search(r'values\s*\((.*?)\)\s*;', b, re.S).group(1))]
        out.append((i1, i2, rows))
    return out


def interp(tab, slew: float, cap: float) -> float:
    """Bilinear NLDM interpolation (extrapolates linearly beyond the table, like STA)."""
    i1, i2, v = tab

    def seg(ax, x):
        k = max(1, min(len(ax) - 1, bisect.bisect_left(ax, x)))
        return k - 1, k, (x - ax[k - 1]) / (ax[k] - ax[k - 1])
    a0, a1, fa = seg(i1, slew)
    b0, b1, fb = seg(i2, cap)
    return (v[a0][b0] * (1 - fa) * (1 - fb) + v[a1][b0] * fa * (1 - fb) + v[a0][b1] * (1 - fa) * fb + v[a1][b1] * fa * fb)


def output_transition(cell: str, out_pin: str, slew: float, cap: float, corner: str = 'tt') -> float:
    cb = cell_block(text(corner), cell)
    return max(interp(tb, slew, cap) for tb in tables(cb, out_pin, 'rise_transition') + tables(cb, out_pin, 'fall_transition'))
