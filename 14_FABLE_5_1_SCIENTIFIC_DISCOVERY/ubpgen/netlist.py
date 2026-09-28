"""The weight-independent base netlist.

Stage 1 (logic base): top = shared line generators + one abstract line tap LTAP per line (programmable pin Z
open) + one via site VSITE_BUF per leaf (programmable pin A open) + the per-row trees; pc2 adds VSITE_ZERO
constant sites. It is emitted directly from the configuration: no W is involved at any point. Yosys links it with
the synthesized modules (every top-level instance kept: nothing is pruned).
Stage 2 (R3 access, access.py) expands each LTAP into K two-site taps on the same base net.

The statement order equals that of the historical pipeline (E6/G3 top with W, then g2_build's removal of every
W-dependent connection), so Yosys emits a byte-identical netlist for the validated configurations.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from . import arch
from ._legacy import LIB, canon_patterns, dock

CELLS_LIB = '/work/cells/g2_cells.lib'


def ff(q, d):
    return f'  wire {q}; sky130_fd_sc_hd__dfxtp_1 {q}_ff (.CLK(clk), .D({d}), .Q({q}));'


def _serial_front(cfg) -> tuple[list[str], str]:
    """Line generators and start alignment of the bit-serial fabrics (E6 build_top without the leaves)."""
    n = cfg.n
    V = [f'module top(input clk, input start, input [{n-1}:0] x, output [{cfg.m-1}:0] y);']
    if cfg.fabric == 'g1':
        line_lat = 1
        for j in range(n):
            V.append(f'  wire lp{j}, ln{j}; SNEG ng{j} (.clk(clk), .start(start), .a(x[{j}]), .pos(lp{j}), .neg(ln{j}));')
    else:
        bl = arch.blocks(cfg)
        Dmax = max(len(c) for c in bl) - 1
        for b, cols in enumerate(bl):
            gb = len(cols)
            pats, D = canon_patterns(gb), gb - 1
            V.append(f'  wire [{len(pats)-1}:0] gy{b};')
            V.append(f'  SGEN{gb} gen{b} (.clk(clk), .start(start), .x({{{", ".join(f"x[{c}]" for c in reversed(cols))}}}), .y(gy{b}));')
            for i in range(len(pats)):
                src = f'gy{b}[{i}]'
                for t in range(D, Dmax):
                    V.append(ff(f'ba{b}_{i}_{t}', src))
                    src = f'ba{b}_{i}_{t}'
                V.append(f'  wire pp{b}_{i}, pn{b}_{i}; SNEG ng{b}_{i} (.clk(clk), .start(st_line), .a({src}), .pos(pp{b}_{i}), .neg(pn{b}_{i}));')
        line_lat = Dmax + 1
        prev = 'start'
        for t in range(1, Dmax + 1):
            V.append(ff(f'sd{t}', prev)); prev = f'sd{t}'
        V.insert(1, '  wire st_line;')
        V.append(f'  assign st_line = {prev};')
    prev = 'start'
    for t in range(1, line_lat + 1):
        V.append(ff(f'stt{t}', prev)); prev = f'stt{t}'
    V.append(f'  wire st_tree = {prev};')
    return V, f'STREE_L{arch.leaves_per_row(cfg)}'


def top_base(cfg) -> str:
    lpr = arch.leaves_per_row(cfg)
    if cfg.fabric == 'pc2':
        n = cfg.n
        V = [f'module top(input clk, input start, input [{n-1}:0] x, output [{2*cfg.m-1}:0] y);',
             '  wire [7:0] ph; CTRL ctl (.clk(clk), .start(start), .ph(ph));']
        for j in range(n):
            V.append(f'  wire lp{j}, ln{j}; PLINE ln_{j} (.clk(clk), .a(x[{j}]), .pos(lp{j}), .neg(ln{j}));')
        row_cell = f'PROW_pc2_L{n}'
    else:
        V, row_cell = _serial_front(cfg)
    for L in arch.lines(cfg):
        V.append(f'  LTAP lt_{L} (.A({L}), .Z());')          # programmable pin Z has NO net in the base
    for i in range(cfg.m):
        for k in range(lpr):
            V.append(f'  wire lf_{i}_{k}; VSITE_BUF vs_{i}_{k} (.A(), .Z(lf_{i}_{k}));')
        xs = ', '.join(f'lf_{i}_{k}' for k in reversed(range(lpr)))
        if cfg.fabric == 'pc2':
            for b in range(arch.CONST_BITS):
                V.append(f'  wire cs_{i}_{b}; VSITE_ZERO cst_{i}_{b} (.A(), .Z(cs_{i}_{b}));')
            cs = ', '.join(f'cs_{i}_{b}' for b in reversed(range(arch.CONST_BITS)))
            V.append(f'  {row_cell} row{i} (.clk(clk), .ph(ph), .c({{{cs}}}), .x({{{xs}}}), .y(y[{2*i+1}:{2*i}]));')
        else:
            V.append(f'  {row_cell} row{i} (.clk(clk), .start(st_tree), .x({{{xs}}}), .y(y[{i}]));')
    V.append('endmodule')
    return '\n'.join(V) + '\n'


def link(cfg, root: Path, module_files: list[str]) -> Path:
    """Write netlist/top_base.v and link it with the module netlists into netlist/netlist_logic.v.
    root is mounted at /work (cells/ and rtl/ live under it)."""
    nd = root / 'netlist'
    nd.mkdir(parents=True, exist_ok=True)
    (nd / 'top_base.v').write_text(top_base(cfg))
    rd = ' '.join(f'read_verilog ../rtl/{f};' for f in module_files) + ' read_verilog top_base.v;'
    p = dock(f"cd netlist && yosys -q -p 'read_liberty -lib {LIB}; read_liberty -lib {CELLS_LIB}; {rd} hierarchy -top top; "
             f"setattr -set keep 1 top/t:*; opt_clean -purge; write_verilog -noattr -noexpr -nohex -nodec netlist_raw.v'", root)
    if p.returncode != 0:
        raise RuntimeError('yosys link failed:\n' + p.stderr[-3000:])
    out = nd / 'netlist_logic.v'
    out.write_text((nd / 'netlist_raw.v').read_text().replace(' signed ', ' '))
    (nd / 'netlist_raw.v').unlink()
    return out


def mapping(cfg) -> dict:
    """Historical mapping.json content (lines, rows, leaves_per_row, n_rows) plus the R3 access fields."""
    lpr = arch.leaves_per_row(cfg)
    rowname = lambda i: f'row{i}'
    mp = {'lines': arch.lines(cfg), 'rows': {rowname(i): lpr for i in range(cfg.m)},
          'leaves_per_row': lpr, 'n_rows': cfg.m}
    K = cfg.K
    mp.update({'taps_per_line': K, 'segment_rows': cfg.m // K,
               'taps': {L: [f'lt_{L}_s{s}' for s in range(K)] for L in mp['lines']}})
    return mp


def write_mapping(cfg, root: Path) -> Path:
    p = root / 'netlist' / 'mapping.json'
    p.write_text(json.dumps(mapping(cfg)))
    return p

