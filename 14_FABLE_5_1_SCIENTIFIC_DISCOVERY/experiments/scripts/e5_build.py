"""E5 builder: weight-independent regime-(V) fabrics as hierarchy-preserving gate-level netlists for ORFS PnR.

python3 e5_build.py OUTDIR N DESIGN [DESIGN ...]      DESIGN in {g1, ubp3, ubp4}

Pipeline per design:
  1. module RTL (TREE/GEN/NEG), each synthesized ONCE (Yosys+ABC, SKY130 HD) inside the ORFS container;
  2. top netlist = module instances + tie-low cells; the per-leaf connection (line, negated line, or tie)
     is the via program derived from W (i.i.d. ternary, seed 14);
  3. independent validation: Yosys (liberty cell functions) -> AIG -> our simulator vs numpy W@x, plus a
     one-connection mutation negative control;
  4. ORFS configs for CORE_UTILIZATION in {30,45,60} with a 6.0 ns virtual clock.
Symmetric INT8 activations in [-127,127] (negation never overflows).
"""
from __future__ import annotations

import itertools
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]  # repo root
sys.path.insert(0, str(ROOT / '13_FABLE_5_1_SCIENTIFIC_DISCOVERY/experiments/scripts'))
from e2_run import read_aag, sim_aag, bus_index  # noqa: E402  (our independent AIGER simulator)

IMAGE = 'openroad/orfs:latest'
PLAT = '/OpenROAD-flow-scripts/flow/platforms/sky130hd'
LIB = f'{PLAT}/lib/sky130_fd_sc_hd__tt_025C_1v80.lib'
XMAX = 127
LOGIC_TARGET_NS = 4.5   # iso-delay logic budget: NEG/GEN delay-optimal, TREE gets the remainder
CLOCK_NS = 20.0   # Amendment A1: relaxed clock; natural delay reported separately


def width(v: int) -> int:  # two's complement bits to hold [-v, v]
    return max(2, v.bit_length() + 1)


def canon_patterns(g):
    pats = set()
    for q in itertools.product((-1, 0, 1), repeat=g):
        if any(q):
            s = next(v for v in q if v)
            pats.add(tuple(s * v for v in q))
    return sorted(pats, key=lambda p: (sum(1 for v in p if v), [abs(v) for v in p], p))


# ---------------------------------------------------------------- module RTL
def tree_rtl(name, L, w, ow):
    lines = [f'module {name}(input [{w*L-1}:0] x, output [{ow-1}:0] y);']
    cur = []
    for i in range(L):
        lines.append(f'  wire signed [{w-1}:0] l{i} = x[{w*i+w-1}:{w*i}];')
        cur.append(f'l{i}')
    k = 0
    while len(cur) > 1:
        nxt = []
        for i in range(0, len(cur) - 1, 2):
            lines.append(f'  wire signed [{ow-1}:0] t{k} = {cur[i]} + {cur[i+1]};')
            nxt.append(f't{k}'); k += 1
        if len(cur) % 2:
            nxt.append(cur[-1])
        cur = nxt
    lines.append(f'  wire signed [{ow-1}:0] s = {cur[0]};\n  assign y = s;\nendmodule')
    return '\n'.join(lines) + '\n'


def gen_rtl(name, g, wl):
    """All canonical patterns (incl. singletons) of g signed 8-bit inputs, each output wl bits (sign-extended)."""
    pats = canon_patterns(g)
    L = [f'module {name}(input [{8*g-1}:0] x, output [{wl*len(pats)-1}:0] y);']
    for j in range(g):
        L.append(f'  wire signed [7:0] i{j} = x[{8*j+7}:{8*j}];')
    nm = {}
    for p in pats:
        nz = [t for t, v in enumerate(p) if v]
        if len(nz) == 1:
            nm[p] = f'i{nz[0]}'; continue
        parent = list(p); parent[nz[-1]] = 0; parent = tuple(parent)
        op = '+' if p[nz[-1]] > 0 else '-'
        nm[p] = f'p{len(nm)}'
        L.append(f'  wire signed [{wl-1}:0] {nm[p]} = {nm[parent]} {op} i{nz[-1]};')
    for k, p in enumerate(pats):
        L.append(f'  wire signed [{wl-1}:0] o{k} = {nm[p]};')
        L.append(f'  assign y[{wl*k+wl-1}:{wl*k}] = o{k};')
    L.append('endmodule')
    return '\n'.join(L) + '\n', pats


def neg_rtl(name, w):
    return (f'module {name}(input [{w-1}:0] x, output [{w-1}:0] y);\n'
            f'  wire signed [{w-1}:0] s = -$signed(x);\n  assign y = s;\nendmodule\n')


# ---------------------------------------------------------------- docker helpers
def dock(cmd: str, wd: Path, timeout=7200) -> subprocess.CompletedProcess:
    return subprocess.run(['docker', 'run', '--rm', '-v', f'{wd}:/work', '-w', '/work', IMAGE, 'bash', '-c', cmd],
                          capture_output=True, text=True, timeout=timeout)


def dont_use_cells() -> list[str]:
    p = subprocess.run(['docker', 'run', '--rm', IMAGE, 'bash', '-c',
                        f"sed -n '/DONT_USE_CELLS/,/^$/p' {PLAT}/config.mk"], capture_output=True, text=True)
    cells = []
    for tok in p.stdout.replace('\\', ' ').split():
        if tok.startswith('sky130_'):
            cells.append(tok)
    return cells


def synth_module(wd: Path, name: str, rtl: str, dont_use: list[str], dtarget_ps: float | None = None) -> Path:
    """Yosys synth + ABC liberty mapping; dtarget_ps None => area-oriented default (Amendment A1)."""
    (wd / f'{name}.v').write_text(rtl)
    du = ' '.join(f'-dont_use {c}' for c in dont_use)
    script = (f'read_verilog {name}.v; synth -flatten -top {name}; '
              f'abc -liberty {LIB}{"" if dtarget_ps is None else f" -D {max(1, int(dtarget_ps))}"} {du}; opt_clean; '
              f'hilomap -singleton -hicell sky130_fd_sc_hd__conb_1 HI -locell sky130_fd_sc_hd__conb_1 LO; '
              f'opt_clean -purge; write_verilog -noattr -noexpr -nohex -nodec {name}_gl_raw.v')
    p = dock(f"yosys -q -l {name}_synth.log -p '{script}'", wd)
    if p.returncode != 0 or not (wd / f'{name}_gl_raw.v').exists():
        raise RuntimeError(f'module synth failed: {name}\n{p.stderr[-2000:]}')
    (wd / f'{name}_gl.v').write_text((wd / f'{name}_gl_raw.v').read_text().replace(' signed ', ' '))
    return wd / f'{name}_gl.v'


def module_timing(wd: Path, name: str) -> dict:
    """OpenSTA (inside OpenROAD) worst input->output delay and cell area of a synthesized module."""
    tcl = (f'read_lef {PLAT}/lef/sky130_fd_sc_hd.tlef\nread_lef {PLAT}/lef/sky130_fd_sc_hd_merged.lef\n'
           f'read_liberty {LIB}\nread_verilog {name}_gl.v\nlink_design {name}\n'
           'create_clock -name clk -period 100\nset_input_delay 0 -clock clk [all_inputs]\n'
           'set_output_delay 0 -clock clk [all_outputs]\nset_load 0.005 [all_outputs]\n'
           'puts "WS [sta::worst_slack_cmd max]"\nputs "AREA [rsz::design_area]"\nexit\n')
    (wd / f'{name}_sta.tcl').write_text(tcl)
    p = dock(f'/OpenROAD-flow-scripts/tools/install/OpenROAD/bin/openroad -no_init -exit {name}_sta.tcl', wd)
    ws = area = None
    for ln in p.stdout.splitlines():
        if ln.startswith('WS '):
            ws = float(ln.split()[1])
        if ln.startswith('AREA '):
            area = float(ln.split()[1])
    if ws is None:
        raise RuntimeError(f'STA failed for {name}\n{p.stdout[-1500:]}\n{p.stderr[-1500:]}')
    # OpenSTA time unit for this library is ns; area in m^2 from rsz -> convert to um^2
    return {'delay_ns': 100.0 - ws * 1e9, 'area_um2': area * 1e12 if area and area < 1 else area}


# ---------------------------------------------------------------- top netlist (the via program)
def build_top(design: str, n: int, W: np.ndarray, modules: dict) -> str:
    m = n
    ow = width(XMAX * n)
    V = [f'module top(input [{8*n-1}:0] x, output [{ow*m-1}:0] y);']
    if design == 'g1':
        w = 8
        for j in range(n):
            V.append(f'  wire [7:0] ln{j} = x[{8*j+7}:{8*j}]; wire [7:0] lnn{j};')
            V.append(f'  {modules["NEG"]} neg{j} (.x(ln{j}), .y(lnn{j}));')
        leaves_per_row = n
        def leaf(i, k):
            wv = int(W[i, k])
            return None if wv == 0 else (f'ln{k}' if wv > 0 else f'lnn{k}')
    else:
        g = int(design[3:])
        blocks = [list(range(s, min(s + g, n))) for s in range(0, n, g)]
        wl = width(XMAX * g)
        w = wl
        lines = {}  # (block, canonical pattern) -> (pos wire, neg wire)
        for b, cols in enumerate(blocks):
            gb = len(cols)
            mod = modules[f'GEN{gb}']
            pats = modules[f'PATS{gb}']
            xin = '{' + ', '.join(f'x[{8*j+7}:{8*j}]' for j in reversed(cols)) + '}'
            V.append(f'  wire [{wl*len(pats)-1}:0] gb{b};')
            V.append(f'  {mod} gen{b} (.x({xin}), .y(gb{b}));')
            for k, p in enumerate(pats):
                V.append(f'  wire [{wl-1}:0] pl{b}_{k} = gb{b}[{wl*k+wl-1}:{wl*k}]; wire [{wl-1}:0] pn{b}_{k};')
                V.append(f'  {modules["NEG"]} neg{b}_{k} (.x(pl{b}_{k}), .y(pn{b}_{k}));')
                lines[(b, p)] = (f'pl{b}_{k}', f'pn{b}_{k}')
        leaves_per_row = len(blocks)
        def leaf(i, b):
            cols = blocks[b]
            q = tuple(int(W[i, c]) for c in cols)
            if not any(q):
                return None
            s = next(v for v in q if v)
            cq = tuple(s * v for v in q)
            pos, neg = lines[(b, cq)]
            return pos if s > 0 else neg
    tree = modules['TREE']
    for i in range(m):
        V.append(f'  wire z{i}; sky130_fd_sc_hd__conb_1 tie{i} (.HI(), .LO(z{i}));')
        parts = []
        for k in range(leaves_per_row):
            src = leaf(i, k)
            parts.append(src if src else '{' + f'{w}{{z{i}}}' + '}')
        V.append(f'  {tree} row{i} (.x({{{", ".join(reversed(parts))}}}), .y(y[{ow*i+ow-1}:{ow*i}]));')
    V.append('endmodule')
    return '\n'.join(V) + '\n', ow


# ---------------------------------------------------------------- independent validation
def validate(wd: Path, files: list[str], W: np.ndarray, ow: int, rng, batch=64, tag='val') -> bool:
    script = (f'read_liberty -ignore_miss_func {LIB}; ' + ' '.join(f'read_verilog {f};' for f in files) +
              ' hierarchy -top top; flatten; synth -top top -noabc; aigmap; opt_clean; '
              f'write_aiger -ascii -symbols {tag}.aag')
    p = dock(f"yosys -q -p '{script}'", wd)
    if p.returncode != 0:
        raise RuntimeError(f'validation elaboration failed\n{p.stderr[-2000:]}')
    A = read_aag(wd / f'{tag}.aag')
    n = W.shape[1]; m = W.shape[0]
    X = rng.integers(-XMAX, XMAX + 1, size=(batch, n), dtype=np.int64)
    _, ins, outs, _, sym_in, sym_out = A
    bits = np.zeros((len(ins), batch), dtype=bool)
    for k in range(len(ins)):
        bus, b = bus_index(sym_in[k]); assert bus == 'x'
        j, t = divmod(b, 8)
        bits[k] = (X[:, j] >> t) & 1
    O = sim_aag(A, bits)
    Y = np.zeros((batch, m), dtype=np.int64)
    for k in range(len(outs)):
        bus, b = bus_index(sym_out[k]); assert bus == 'y'
        i, t = divmod(b, ow)
        Y[:, i] |= O[k].astype(np.int64) << t
    Y = np.where((Y >> (ow - 1)) & 1, Y - (1 << ow), Y)
    return bool(np.array_equal(Y, X @ W.T.astype(np.int64)))


ORFS_CFG = """export DESIGN_NAME = top
export DESIGN_NICKNAME = {nick}
export PLATFORM = sky130hd
export SYNTH_NETLIST_FILES = /work/{design}/netlist.v
export VERILOG_FILES = /work/{design}/netlist.v
export SDC_FILE = /work/{design}/constraint.sdc
export CORE_UTILIZATION = {util}
export CORE_ASPECT_RATIO = 1
export CORE_MARGIN = 2
"""
SDC = """create_clock -name clk -period {period}
set_input_delay 0 -clock clk [all_inputs]
set_output_delay 0 -clock clk [all_outputs]
"""


def main(out: Path, n: int, designs: list[str]):
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(14)
    W = rng.choice(np.array([-1, 0, 1], dtype=np.int8), size=(n, n), p=[0.3, 0.4, 0.3])
    np.save(out / f'W_n{n}.npy', W)
    du = dont_use_cells()
    report = {'n': n, 'dont_use': du, 'designs': {}}
    for design in designs:
        wd = out / f'{design}_n{n}'
        wd.mkdir(parents=True, exist_ok=True)
        ow = width(XMAX * n)
        mods, files = {}, []
        if design == 'g1':
            specs = [('NEG', f'NEG_W8', neg_rtl('NEG_W8', 8)),
                     ('TREE', f'TREE_L{n}_W8', tree_rtl(f'TREE_L{n}_W8', n, 8, ow))]
        else:
            g = int(design[3:])
            wl = width(XMAX * g)
            gsizes = sorted({len(range(s, min(s + g, n))) for s in range(0, n, g)})
            specs = [('NEG', f'NEG_W{wl}', neg_rtl(f'NEG_W{wl}', wl)),
                     ('TREE', f'TREE_L{math.ceil(n/g)}_W{wl}', tree_rtl(f'TREE_L{math.ceil(n/g)}_W{wl}', math.ceil(n / g), wl, ow))]
            for gb in gsizes:
                rtl, pats = gen_rtl(f'GEN{gb}_W{wl}', gb, wl)
                specs.append((f'GEN{gb}', f'GEN{gb}_W{wl}', rtl))
                mods[f'PATS{gb}'] = pats
        timing = {}
        pre = 0.0
        for key, name, rtl in specs:
            if key == 'TREE':
                continue
            synth_module(wd, name, rtl, du)
            timing[name] = module_timing(wd, name)
            mods[key] = name
            files.append(f'{name}_gl.v')
        pre = timing[mods['NEG']]['delay_ns'] + max([timing[mods[k]]['delay_ns'] for k in mods if k.startswith('GEN')] or [0.0])
        tkey, tname, trtl = next(sp for sp in specs if sp[0] == 'TREE')
        budget_ns = LOGIC_TARGET_NS - pre
        synth_module(wd, tname, trtl, du)
        timing[tname] = module_timing(wd, tname)
        mods['TREE'] = tname
        files.append(f'{tname}_gl.v')
        top, ow = build_top(design, n, W, mods)
        (wd / 'top.v').write_text(top)
        # netlist for ORFS: re-emit modules + top through Yosys as strict structural Verilog.
        # No flatten, no cross-module optimization: only hierarchy resolution and dangling-wire purge.
        rd = ' '.join(f'read_verilog {f};' for f in files + ['top.v'])
        p = dock(f"yosys -q -p 'read_liberty -lib {LIB}; {rd} hierarchy -top top; opt_clean -purge; "
                 f"write_verilog -noattr -noexpr -nohex -nodec netlist_raw.v'", wd)
        if p.returncode != 0:
            raise RuntimeError(f'netlist emission failed\n{p.stderr[-2000:]}')
        raw = (wd / 'netlist_raw.v').read_text().replace(' signed ', ' ')
        (wd / 'netlist.v').write_text(raw)
        ok = validate(wd, ['netlist.v'], W, ow, np.random.default_rng(7))
        # negative control: flip one nonzero connection polarity
        W2 = W.copy(); i, j = map(int, np.argwhere(W != 0)[0]); W2[i, j] = -W2[i, j]
        bad = validate(wd, ['netlist.v'], W2, ow, np.random.default_rng(7), tag='negctl')
        (wd / 'constraint.sdc').write_text(SDC.format(period=CLOCK_NS))
        for util in (45, 60, 75):
            (wd / f'config_u{util}.mk').write_text(ORFS_CFG.format(nick=f'{design}_n{n}_u{util}', design=f'{design}_n{n}', util=util))
        report['designs'][design] = {'modules': mods if design == 'g1' else {k: v for k, v in mods.items() if not k.startswith('PATS')},
                                     'validation': ok, 'negctl_detects': (not bad), 'ow': ow,
                                     'module_timing': timing, 'tree_budget_ns': budget_ns,
                                     'logic_path_ns': pre + timing[mods['TREE']]['delay_ns']}
        print(design, json.dumps(report['designs'][design]), flush=True)
    (out / f'build_n{n}.json').write_text(json.dumps(report, indent=1))


if __name__ == '__main__':
    main(Path(sys.argv[1]), int(sys.argv[2]), sys.argv[3:])
