"""RTL modules and their gate-level synthesis (Yosys + ABC, SKY130 HD, inside the ORFS container).

All modules are weight-independent. The module generators and the synthesis recipe are the validated E6/G3 ones
(imported via _legacy); this file only decides which modules a configuration needs, and applies the optional
W-independent spine-driver sizing to the synthesized line-driver module.
"""
from __future__ import annotations

import re
from pathlib import Path

from . import arch
from ._legacy import (canon_patterns, ctrl_rtl, dont_use_cells, gen_rtl, negline_rtl, pline_rtl, prow_rtl,
                      synth_seq, tree_rtl)

LINE_DRIVER_MODULE = {'ubp': 'SNEG', 'g1': 'SNEG', 'pc2': 'PLINE'}
LINE_PORTS = ('pos', 'neg')


def module_plan(cfg) -> dict:
    """name -> RTL text, plus derived module facts (pattern lists, generator latencies)."""
    mods, facts = {}, {}
    if cfg.fabric in ('ubp', 'g1'):
        mods['SNEG'] = negline_rtl('SNEG')
        if cfg.fabric == 'ubp':
            for gb in sorted({len(c) for c in arch.blocks(cfg)}):
                rtl, pats, D = gen_rtl(f'SGEN{gb}', gb)
                mods[f'SGEN{gb}'] = rtl
                facts[f'SGEN{gb}'] = {'patterns': [list(p) for p in pats], 'latency': D}
        L = arch.leaves_per_row(cfg)
        rtl, depth = tree_rtl(f'STREE_L{L}', L)
        mods[f'STREE_L{L}'] = rtl
        facts[f'STREE_L{L}'] = {'depth': depth}
    else:
        mods['CTRL'] = ctrl_rtl('CTRL', 1)
        mods['PLINE'] = pline_rtl('PLINE')
        name = f'PROW_pc2_L{cfg.n}'
        mods[name] = prow_rtl(name, [1] * cfg.n, arch.output_width(cfg), arch.CONST_BITS, 8)
    return {'rtl': mods, 'facts': facts}


def synthesize(cfg, rtl_dir: Path) -> list[str]:
    """Synthesize every module (deterministic; reused when the RTL text is unchanged). Returns *_gl.v names."""
    rtl_dir.mkdir(parents=True, exist_ok=True)
    du = dont_use_cells()
    plan = module_plan(cfg)
    files = []
    for name, text in plan['rtl'].items():
        synth_seq(rtl_dir, name, text, du)
        files.append(f'{name}_gl.v')
    if cfg.raw['spine_driver'] == 'drive4':
        size_line_drivers(rtl_dir / f'{LINE_DRIVER_MODULE[cfg.fabric]}_gl.v')
    return files


def size_line_drivers(gl_path: Path) -> list[tuple[str, str, str]]:
    """Upsize every cell whose output drives a line port (pos/neg) to the drive-4 member of its family.
    W-independent (applies to every line of the fabric). Rewrites the file; returns (instance, old, new)."""
    text = gl_path.read_text()
    changes = []

    def rep(m):
        master, inst, body = m.group(1), m.group(2), m.group(3)
        outs = re.findall(r'\.(?:Q|Y|X)\((\w+)\)', body)
        fam = re.fullmatch(r'(sky130_fd_sc_hd__(?:dfxtp|clkinv|inv|buf|clkbuf))_(\d+)', master)
        if fam and int(fam.group(2)) < 4 and any(o in LINE_PORTS for o in outs):
            new = f'{fam.group(1)}_4'
            changes.append((inst, master, new))
            return f'  {new} {inst} ({body});'
        return m.group(0)
    text2 = re.sub(r'  (sky130_fd_sc_hd__\w+) (\w+) \((.*?)\);', rep, text, flags=re.S)
    if len(changes) != len(LINE_PORTS):
        raise RuntimeError(f'spine-driver sizing: expected {len(LINE_PORTS)} line drivers in {gl_path.name}, '
                           f'found {changes}')
    gl_path.write_text(text2)
    return changes
