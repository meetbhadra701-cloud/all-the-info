"""Emit a Circuit (hwlayer.py) as structural, synthesizable Verilog.

Ports: input  [8*n-1:0] x  (x_j = x[8j+7:8j], two's complement)
       output [OW*m-1:0] y (y_i = y[OW*i+OW-1:OW*i], two's complement)
Every op becomes one `assign` of one two-operand add/sub on signed wires sized from the op's
interval (same widths as the B cost). Shifts are wiring.
"""
from __future__ import annotations

import numpy as np

from hwlayer import Circuit, width


def emit(c: Circuit, m: int, name: str = 'top') -> tuple[str, int]:
    n = c.n
    # output width: enough for every output value range
    ow = 2
    for o in c.out:
        s = o[0]
        if s >= 0:
            sh = o[2] if len(o) > 2 else 0
            lo, hi = c.lo[s], c.hi[s]
            if sh >= 0:
                lo, hi = lo << sh, hi << sh
            else:
                lo, hi = -((-lo) >> -sh) - 1, hi >> -sh
            ow = max(ow, width(min(lo, -hi), max(hi, -lo)))
    L = [f'module {name}(input [{8*n-1}:0] x, output [{ow*m-1}:0] y);']
    for j in range(n):
        L.append(f'  wire signed [7:0] s{j} = x[{8*j+7}:{8*j}];')
    for k in range(len(c.a)):
        idx = n + k
        w = width(c.lo[idx], c.hi[idx])
        a, b = c.a[k], c.b[k]
        sa = '' if c.sa[k] > 0 else '-'
        op = '+' if c.sb[k] > 0 else '-'
        hb = c.hb[k]
        bterm = f's{b}' if hb == 0 else f'(s{b} <<< {hb})'
        # all wires are signed: Verilog sign-extends every operand to the (context) width w
        L.append(f'  wire signed [{w-1}:0] s{idx} = {sa}s{a} {op} {bterm};')
    for i, o in enumerate(c.out):
        s, g = o[0], o[1]
        sh = o[2] if len(o) > 2 else 0
        if s < 0:
            L.append(f'  assign y[{ow*i+ow-1}:{ow*i}] = {ow}\'sd0;')
            continue
        e = f's{s}'
        if sh > 0:
            e = f'({e} <<< {sh})'
        elif sh < 0:
            e = f'({e} >>> {-sh})'
        e = e if g > 0 else f'(-{e})'
        L.append(f'  wire signed [{ow-1}:0] o{i} = {e};')
        L.append(f'  assign y[{ow*i+ow-1}:{ow*i}] = o{i};')
    L.append('endmodule')
    return '\n'.join(L) + '\n', ow


def emit_behavioral(W: np.ndarray, name: str = 'top') -> tuple[str, int]:
    """y_i = sum_j W_ij * x_j written as one multi-operand expression per row (generic synthesis baseline)."""
    m, n = W.shape
    maxabs = int(np.abs(W).sum(axis=1).max()) * 128
    ow = width(-maxabs, maxabs)
    L = [f'module {name}(input [{8*n-1}:0] x, output [{ow*m-1}:0] y);']
    for j in range(n):
        L.append(f'  wire signed [{ow-1}:0] s{j} = $signed(x[{8*j+7}:{8*j}]);')
    for i in range(m):
        terms = [(f'+ s{j}' if W[i, j] > 0 else f'- s{j}') for j in np.nonzero(W[i])[0]]
        e = ' '.join(terms) if terms else f"{ow}'sd0"
        if e.startswith('+ '):
            e = e[2:]
        L.append(f'  wire signed [{ow-1}:0] o{i} = {e};')
        L.append(f'  assign y[{ow*i+ow-1}:{ow*i}] = o{i};')
    L.append('endmodule')
    return '\n'.join(L) + '\n', ow
