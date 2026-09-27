"""Gate 2: build the W-INDEPENDENT base netlist of a fabric and the per-W via programs.

python3 g2_build.py base    OUTDIR DESIGN SRCDIR      # DESIGN in {ubp3s, g1s, pc2}; SRCDIR = validated source design dir
python3 g2_build.py program OUTDIR DESIGN TAG SEED P0 [same_rows]   # writes OUTDIR/DESIGN/prog_TAG.{json,tcl} + W_TAG.npy

Base = the source top netlist with every W-dependent connection removed:
  * each leaf (row i, slot k) is driven by a via-site VSITE_BUF vs_i_k (Z -> leaf); its programmable pin A (met4) is open;
  * each line polarity net L gets a line tap LTAP lt_L (A <- L); its programmable pin Z (met4) is open;
  * pc2's per-row correction constant bits become via-selected constant sites (VSITE_ZERO default);
  * W-dependent tie cells are removed (zero leaves/constants are the sites' local tie option).
Program(W): for each line tap with >= 1 selecting leaf, one programmable net {LTAP.Z, VSITE.A...}; zero leaves ->
master VSITE_ZERO; constant bits = 1 -> VSITE_ONE. Identical footprints: the program never moves a cell.
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from e5_build import LIB, canon_patterns, dock  # noqa: E402

G2LIB = '/work/cells/g2_cells.lib'
ROW_RE = re.compile(r'^\s*(\w+) (row\d+) \((.*)\);\s*$')


def parse_rows(top: str):
    rows = {}
    for ln in top.splitlines():
        m = ROW_RE.match(ln)
        if m:
            rows[m.group(2)] = (m.group(1), m.group(3))
    return rows


def base(out: Path, design: str, src: Path):
    wd = out / design
    wd.mkdir(parents=True, exist_ok=True)
    top = (src / 'top.v').read_text()
    lines_nets = sorted(set(re.findall(r'\.(?:pos|neg)\((\w+)\)', top)))
    V = []
    rows = parse_rows(top)
    n_rows = len(rows)
    leaves_per_row = None
    for ln in top.splitlines():
        if ROW_RE.match(ln) or ln.strip() == 'endmodule':
            continue
        # W-dependent ties -> site-local options. Remove only the tie instance: other statements may share the line.
        ln = re.sub(r'sky130_fd_sc_hd__conb_1 (tie0|ctie\d+) \([^;]*\);', '', ln)
        ln = re.sub(r'wire hi\d+, lo\d+;', '', ln)
        if ln.strip():
            V.append(ln)
    for L in lines_nets:
        V.append(f'  LTAP lt_{L} (.A({L}), .Z());')      # programmable pin Z has NO net in the base
    mapping = {'lines': lines_nets, 'rows': {}}
    for rname in sorted(rows, key=lambda s: int(s[3:])):
        cell, ports = rows[rname]
        i = int(rname[3:])
        xm = re.search(r'\.x\(\{(.*?)\}\)', ports)
        slots = [s.strip() for s in xm.group(1).split(',')]
        # pc2/ubpb leaves may be 2-bit '{zero, src}' groups; E6 serial leaves are single names
        nslots = len(slots)
        leaves_per_row = nslots
        new_slots = []
        for k in range(nslots):                                  # slot k = x[k]; concat lists MSB first
            V.append(f'  wire lf_{i}_{k}; VSITE_BUF vs_{i}_{k} (.A(), .Z(lf_{i}_{k}));')
        new_slots = [f'lf_{i}_{k}' for k in reversed(range(nslots))]
        new_ports = ports.replace(xm.group(0), '.x({' + ', '.join(new_slots) + '})')
        cm = re.search(r'\.c\(\{(.*?)\}\)', new_ports)
        if cm:
            nb = len(cm.group(1).split(','))
            for b in range(nb):
                V.append(f'  wire cs_{i}_{b}; VSITE_ZERO cst_{i}_{b} (.A(), .Z(cs_{i}_{b}));')
            new_ports = new_ports.replace(cm.group(0), '.c({' + ', '.join(f'cs_{i}_{b}' for b in reversed(range(nb))) + '})')
        V.append(f'  {cell} {rname} ({new_ports});')
        mapping['rows'][rname] = nslots
    V.append('endmodule')
    base_top = '\n'.join(V) + '\n'
    # 'zero' may still be referenced (e.g. by nothing); drop its declaration only if unused
    if re.search(r'\bzero\b', base_top.replace('wire zero;', '')) is None:
        base_top = base_top.replace('  wire zero;', '')
    (wd / 'top_base.v').write_text(base_top)
    mods = sorted(f.name for f in src.glob('*_gl.v'))
    for f in mods:
        (wd / f).write_text((src / f).read_text())
    (wd / 'constraint.sdc').write_text((src / 'constraint.sdc').read_text())
    rd = ' '.join(f'read_verilog {f};' for f in mods + ['top_base.v'])
    p = dock(f"yosys -q -p 'read_liberty -lib {LIB}; read_liberty -lib {G2LIB}; {rd} hierarchy -top top; setattr -set keep 1 top/t:*; "
             f"opt_clean -purge; write_verilog -noattr -noexpr -nohex -nodec netlist_raw.v'", out)
    # dock mounts `out` at /work; the design files live in /work/<design>
    if p.returncode != 0:
        p = dock(f"cd {design} && yosys -q -p 'read_liberty -lib {LIB}; read_liberty -lib {G2LIB}; {rd} hierarchy -top top; "
                 f"setattr -set keep 1 top/t:*; opt_clean -purge; write_verilog -noattr -noexpr -nohex -nodec netlist_raw.v'", out)
        if p.returncode != 0:
            raise RuntimeError(p.stderr[-2000:])
    raw = (wd / 'netlist_raw.v') if (wd / 'netlist_raw.v').exists() else (out / 'netlist_raw.v')
    (wd / 'netlist_base.v').write_text(raw.read_text().replace(' signed ', ' '))
    mapping['leaves_per_row'] = leaves_per_row
    mapping['n_rows'] = n_rows
    (wd / 'mapping.json').write_text(json.dumps(mapping, indent=1))
    cfg = (f"export DESIGN_NAME = top\nexport PLATFORM = sky130hd\n"
           f"export SYNTH_NETLIST_FILES = /work/{design}/netlist_base.v\nexport VERILOG_FILES = /work/{design}/netlist_base.v\n"
           f"export SDC_FILE = /work/{design}/constraint.sdc\nexport CORE_ASPECT_RATIO = 1\nexport CORE_MARGIN = 2\n"
           f"export ADDITIONAL_LEFS = /work/cells/g2_cells.lef\nexport ADDITIONAL_LIBS = /work/cells/g2_cells.lib\n"
           f"export PDN_TCL = /work/cells/pdn_m1rails.tcl\nexport MAX_ROUTING_LAYER = met3\nexport MIN_CLK_ROUTING_LAYER = met2\n"
           f"export PWR_NETS_VOLTAGES =\nexport GND_NETS_VOLTAGES =\nexport POST_SYNTH_TCL = /work/cells/dont_touch.tcl\n")
    for util in (45, 60, 75):
        (wd / f'config_u{util}.mk').write_text(cfg + f"export DESIGN_NICKNAME = g2_{design}_u{util}\nexport CORE_UTILIZATION = {util}\n")
    print(design, 'lines', len(lines_nets), 'rows', n_rows, 'leaves/row', leaves_per_row)


def leaf_source(design, W, i, k, n):
    """Return the line-net name feeding leaf (i, k) for weight matrix W, or None for a zero leaf.
    Same selection rule as e6_build / g3_build."""
    if design in ('g1s', 'pc2'):
        w = int(W[i, k])
        return None if w == 0 else (f'lp{k}' if w > 0 else f'ln{k}')
    g = 3
    cols = list(range(k * g, min(k * g + g, n)))
    q = tuple(int(W[i, c]) for c in cols)
    if not any(q):
        return None
    s = next(v for v in q if v)
    pats = canon_patterns(len(cols))
    idx = pats.index(tuple(s * v for v in q))
    return f'pp{k}_{idx}' if s > 0 else f'pn{k}_{idx}'


def program(out: Path, design: str, tag: str, seed: int, p0: float, same_rows: bool):
    wd = out / design
    mp = json.loads((wd / 'mapping.json').read_text())
    n = m = mp['n_rows']
    rng = np.random.default_rng(seed)
    pw = [(1 - p0) / 2, p0, (1 - p0) / 2]
    if same_rows:
        row = rng.choice(np.array([-1, 0, 1], dtype=np.int8), size=(1, n), p=pw)
        W = np.repeat(row, m, axis=0)
    else:
        W = rng.choice(np.array([-1, 0, 1], dtype=np.int8), size=(m, n), p=pw)
    np.save(wd / f'W_{tag}.npy', W)
    nets, zeros, ones = {}, [], []
    for i in range(m):
        for k in range(mp['leaves_per_row']):
            srcn = leaf_source(design, W, i, k, n)
            if srcn is None:
                zeros.append(f'vs_{i}_{k}')
            else:
                nets.setdefault(srcn, []).append(f'vs_{i}_{k}')
        if design == 'pc2':
            c = int((W[i] < 0).sum())
            ones += [f'cst_{i}_{b}' for b in range(7) if (c >> b) & 1]
    prog = {'tag': tag, 'seed': seed, 'p0': p0, 'same_rows': same_rows, 'nets': nets, 'zeros': zeros, 'ones': ones,
            'n_prog_nets': len(nets), 'n_prog_pins': sum(len(v) for v in nets.values()) + len(nets)}
    (wd / f'prog_{tag}.json').write_text(json.dumps(prog))
    T = ['proc g2_apply_program {} {', '  set blk [ord::get_db_block]', '  set db [ord::get_db]',
         '  set mz [$db findMaster VSITE_ZERO]', '  set mo [$db findMaster VSITE_ONE]']
    for z in zeros:
        T.append(f'  [$blk findInst {z}] swapMaster $mz')
    for o in ones:
        T.append(f'  [$blk findInst {o}] swapMaster $mo')
    for srcn, sites in nets.items():
        T.append(f'  set net [odb::dbNet_create $blk pgm_{srcn}]')
        T.append(f'  [[$blk findInst lt_{srcn}] findITerm Z] connect $net')
        for s in sites:
            T.append(f'  [[$blk findInst {s}] findITerm A] connect $net')
    T.append('}')
    (wd / f'prog_{tag}.tcl').write_text('\n'.join(T) + '\n')
    print(design, tag, 'nets', prog['n_prog_nets'], 'pins', prog['n_prog_pins'], 'zeros', len(zeros), 'ones', len(ones))


if __name__ == '__main__':
    if sys.argv[1] == 'base':
        base(Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4]))
    else:
        program(Path(sys.argv[2]), sys.argv[3], sys.argv[4], int(sys.argv[5]), float(sys.argv[6]),
                len(sys.argv) > 7 and sys.argv[7] == 'same_rows')
