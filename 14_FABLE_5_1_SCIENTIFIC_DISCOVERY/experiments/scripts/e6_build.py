"""E6 builder (H1.2 evolution): BIT-SERIAL weight-independent regime-(V) fabrics for ORFS PnR.

python3 e6_build.py OUTDIR N DESIGN [DESIGN ...]      DESIGN in {g1, ubp3, ubp4}

Bit-serial protocol (LSB first, two's complement, T = ow cycles per word, `start` high on each word's cycle 0):
  * serial adder node: s = a^b^cz, c' = maj(a,b,cz), cz = start_l ? 0 : c_q; sum and carry registered (1 cycle/level)
  * serial subtractor (generator '-' patterns): b complemented, cz = start_l ? 1 : c_q
  * line negator (shared per line): neg = ~a + 1 serially; pos delayed 1 to stay aligned
  * TREE(L): balanced registered serial adder tree, per-level start taps from an internal shift register
  * GEN(g): all canonical patterns (parent +/- input, registered), aligned to latency g-1
Modules are weight-independent; W only sets top-level connections (the via program). Same flow/checks as E5,
with a sequential AIGER simulator (latches) for independent validation over K words.
"""
from __future__ import annotations

import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from e5_build import (LIB, XMAX, canon_patterns, dock, dont_use_cells, module_timing,  # noqa: E402
                      width)

CLOCK_NS = 3.0


def tree_rtl(name, L):
    """Registered serial adder tree over L leaves; returns (rtl, depth)."""
    V = [f'module {name}(input clk, input start, input [{L-1}:0] x, output y);']
    cur = [f'x[{i}]' for i in range(L)]
    lvl = 0
    k = 0
    starts = []
    while len(cur) > 1:
        lvl += 1
        st = 'start' if lvl == 1 else f'st{lvl}'
        if lvl > 1:
            V.append(f'  reg st{lvl}; always @(posedge clk) st{lvl} <= {"start" if lvl == 2 else f"st{lvl-1}"};')
        nxt = []
        for i in range(0, len(cur) - 1, 2):
            a, b = cur[i], cur[i + 1]
            V.append(f'  reg s{k}, c{k}; wire z{k} = {st} ? 1\'b0 : c{k};')
            V.append(f'  always @(posedge clk) begin s{k} <= {a} ^ {b} ^ z{k}; '
                     f'c{k} <= ({a} & {b}) | ({a} & z{k}) | ({b} & z{k}); end')
            nxt.append(f's{k}'); k += 1
        if len(cur) % 2:
            V.append(f'  reg d{k}; always @(posedge clk) d{k} <= {cur[-1]};')
            nxt.append(f'd{k}'); k += 1
        cur = nxt
    V.append(f'  assign y = {cur[0]};\nendmodule')
    return '\n'.join(V) + '\n', lvl


def negline_rtl(name):
    return (f'module {name}(input clk, input start, input a, output pos, output neg);\n'
            f'  reg p, n, c; wire z = start ? 1\'b1 : c; wire na = ~a;\n'
            f'  always @(posedge clk) begin p <= a; n <= na ^ z; c <= na & z; end\n'
            f'  assign pos = p; assign neg = n;\nendmodule\n')


def gen_rtl(name, g):
    """Serial generator: all canonical patterns of g serial inputs, outputs aligned to latency g-1."""
    pats = canon_patterns(g)
    D = g - 1
    V = [f'module {name}(input clk, input start, input [{g-1}:0] x, output [{len(pats)-1}:0] y);']
    # delayed copies of inputs and start
    for j in range(g):
        prev = f'x[{j}]'
        for t in range(1, D + 1):
            V.append(f'  reg x{j}_d{t}; always @(posedge clk) x{j}_d{t} <= {prev};')
            prev = f'x{j}_d{t}'
    prev = 'start'
    for t in range(1, D + 1):
        V.append(f'  reg st_d{t}; always @(posedge clk) st_d{t} <= {prev};')
        prev = f'st_d{t}'
    xd = lambda j, t: f'x[{j}]' if t == 0 else f'x{j}_d{t}'
    sd = lambda t: 'start' if t == 0 else f'st_d{t}'
    name_of, lat = {}, {}
    k = 0
    for p in pats:
        nz = [t for t, v in enumerate(p) if v]
        if len(nz) == 1:
            name_of[p] = None; lat[p] = 0; continue
        parent = list(p); parent[nz[-1]] = 0; parent = tuple(parent)
        pl = lat[parent]
        pa = xd(nz[0], 0) if name_of[parent] is None else name_of[parent]
        xb = xd(nz[-1], pl)
        st = sd(pl)
        if p[nz[-1]] > 0:
            V.append(f'  reg g{k}, gc{k}; wire gz{k} = {st} ? 1\'b0 : gc{k};')
            V.append(f'  always @(posedge clk) begin g{k} <= {pa} ^ {xb} ^ gz{k}; gc{k} <= ({pa} & {xb}) | ({pa} & gz{k}) | ({xb} & gz{k}); end')
        else:
            V.append(f'  reg g{k}, gc{k}; wire gz{k} = {st} ? 1\'b1 : gc{k}; wire gn{k} = ~{xb};')
            V.append(f'  always @(posedge clk) begin g{k} <= {pa} ^ gn{k} ^ gz{k}; gc{k} <= ({pa} & gn{k}) | ({pa} & gz{k}) | (gn{k} & gz{k}); end')
        name_of[p] = f'g{k}'; lat[p] = pl + 1; k += 1
    # align all pattern outputs to latency D
    for i, p in enumerate(pats):
        src = xd([t for t, v in enumerate(p) if v][0], 0) if name_of[p] is None else name_of[p]
        cur = src
        for t in range(lat[p], D):
            V.append(f'  reg al{i}_{t}; always @(posedge clk) al{i}_{t} <= {cur};')
            cur = f'al{i}_{t}'
        V.append(f'  assign y[{i}] = {cur};')
    V.append('endmodule')
    return '\n'.join(V) + '\n', pats, D


def synth_seq(wd: Path, name: str, rtl: str, dont_use: list[str]):
    if (wd / f'{name}_gl.v').exists() and (wd / f'{name}.v').exists() and (wd / f'{name}.v').read_text() == rtl:
        return  # identical RTL already synthesized (deterministic flow): reuse
    (wd / f'{name}.v').write_text(rtl)
    du = ' '.join(f'-dont_use {c}' for c in dont_use)
    script = (f'read_verilog {name}.v; synth -flatten -top {name}; '
              f'dfflibmap -liberty {LIB} {du}; abc -liberty {LIB} {du}; opt_clean; '
              f'hilomap -singleton -hicell sky130_fd_sc_hd__conb_1 HI -locell sky130_fd_sc_hd__conb_1 LO; '
              f'opt_clean -purge; write_verilog -noattr -noexpr -nohex -nodec {name}_gl_raw.v')
    p = dock(f"yosys -q -l {name}_synth.log -p '{script}'", wd)
    if p.returncode != 0 or not (wd / f'{name}_gl_raw.v').exists():
        raise RuntimeError(f'seq synth failed: {name}\n{p.stderr[-2000:]}')
    (wd / f'{name}_gl.v').write_text((wd / f'{name}_gl_raw.v').read_text().replace(' signed ', ' '))


def ff(q, d):
    """Top-level D flip-flop as an explicit library cell (OpenSTA's netlist reader takes no behavioural processes)."""
    return f'  wire {q}; sky130_fd_sc_hd__dfxtp_1 {q}_ff (.CLK(clk), .D({d}), .Q({q}));'


def build_top(design, n, W, mods, depth):
    m = n
    V = [f'module top(input clk, input start, input [{n-1}:0] x, output [{m-1}:0] y);']
    if design == 'g1':
        line_lat = 1
        for j in range(n):
            V.append(f'  wire lp{j}, ln{j}; {mods["NEG"]} ng{j} (.clk(clk), .start(start), .a(x[{j}]), .pos(lp{j}), .neg(ln{j}));')
        L = n
        def leaf(i, k):
            w = int(W[i, k]); return None if w == 0 else (f'lp{k}' if w > 0 else f'ln{k}')
    else:
        g = int(design[3:])
        blocks = [list(range(s, min(s + g, n))) for s in range(0, n, g)]
        lines = {}
        line_lat = None
        for b, cols in enumerate(blocks):
            gb = len(cols)
            pats, D = mods[f'PATS{gb}'], mods[f'D{gb}']
            V.append(f'  wire [{len(pats)-1}:0] gy{b};')
            V.append(f'  {mods[f"GEN{gb}"]} gen{b} (.clk(clk), .start(start), .x({{{", ".join(f"x[{c}]" for c in reversed(cols))}}}), .y(gy{b}));')
            # align this block's lines to the global max generator latency, then negate
            Dmax = max(mods[k] for k in mods if k.startswith('D'))
            for i, p in enumerate(pats):
                src = f'gy{b}[{i}]'
                for t in range(D, Dmax):
                    V.append(ff(f'ba{b}_{i}_{t}', src))
                    src = f'ba{b}_{i}_{t}'
                V.append(f'  wire pp{b}_{i}, pn{b}_{i}; {mods["NEG"]} ng{b}_{i} (.clk(clk), .start(st_line), .a({src}), .pos(pp{b}_{i}), .neg(pn{b}_{i}));')
                lines[(b, p)] = (f'pp{b}_{i}', f'pn{b}_{i}')
            line_lat = Dmax + 1
        L = len(blocks)
        def leaf(i, b):
            q = tuple(int(W[i, c]) for c in blocks[b])
            if not any(q):
                return None
            s = next(v for v in q if v)
            pos, neg = lines[(b, tuple(s * v for v in q))]
            return pos if s > 0 else neg
    # start alignment: generators use `start`; line negators use start delayed by generator latency; trees by line latency
    if design != 'g1':
        Dmax = line_lat - 1
        prev = 'start'
        for t in range(1, Dmax + 1):
            V.append(ff(f'sd{t}', prev)); prev = f'sd{t}'
        V.insert(1, '  wire st_line;')
        V.append(f'  assign st_line = {prev};')
    prev = 'start'
    for t in range(1, line_lat + 1):
        V.append(ff(f'stt{t}', prev)); prev = f'stt{t}'
    V.append(f'  wire st_tree = {prev}; wire zero; sky130_fd_sc_hd__conb_1 tie0 (.HI(), .LO(zero));')
    for i in range(m):
        parts = [leaf(i, k) or 'zero' for k in range(L)]
        V.append(f'  {mods["TREE"]} row{i} (.clk(clk), .start(st_tree), .x({{{", ".join(reversed(parts))}}}), .y(y[{i}]));')
    V.append('endmodule')
    return '\n'.join(V) + '\n', line_lat + depth


# ---------------------------------------------------------------- sequential AIGER simulation (independent)
def read_aag_seq(path: Path):
    lines = path.read_text().splitlines()
    M, I, L, O, A = map(int, lines[0].split()[1:6])
    ins = [int(lines[1 + k]) for k in range(I)]
    lat = []
    for k in range(L):
        f = lines[1 + I + k].split()
        lat.append((int(f[0]), int(f[1]), int(f[2]) if len(f) > 2 else 0))
    outs = [int(lines[1 + I + L + k]) for k in range(O)]
    ands = [tuple(map(int, lines[1 + I + L + O + k].split())) for k in range(A)]
    sym_in, sym_out = {}, {}
    for ln in lines[1 + I + L + O + A:]:
        if ln[:1] in 'io' and ln[1:2].isdigit():
            k, nm = ln[1:].split(' ', 1)
            (sym_in if ln[0] == 'i' else sym_out)[int(k)] = nm.split()[0]
        elif ln.startswith('c'):
            break
    return M, ins, lat, outs, ands, sym_in, sym_out


def sim_seq(aag, W, ow, latency, K=12, seed=3):
    M, ins, lat, outs, ands, sym_in, sym_out = aag
    n, m = W.shape[1], W.shape[0]
    rng = np.random.default_rng(seed)
    X = rng.integers(-XMAX, XMAX + 1, size=(K, n), dtype=np.int64)
    T = ow
    cycles = K * T + latency + T
    val = np.zeros(M + 1, dtype=bool)
    state = {cur >> 1: bool(init) for cur, nxt, init in lat}
    def lv(l):
        v = val[l >> 1]
        return (not v) if l & 1 else bool(v)
    idx = {}
    for k in range(len(ins)):
        nm = sym_in[k]
        idx[k] = nm
    outbits = np.zeros((cycles, m), dtype=np.int64)
    for cyc in range(cycles):
        w, t = divmod(cyc, T)
        for k, lit in enumerate(ins):
            nm = idx[k]
            if nm == 'start':
                v = (t == 0 and w < K)
            elif nm == 'clk':
                v = False
            else:
                j = int(nm[nm.index('[') + 1:-1])
                xv = X[w, j] if w < K else 0
                v = bool((xv >> min(t, 62)) & 1)
            val[lit >> 1] = v
        for cur, s in state.items():
            val[cur] = s
        for lhs, r0, r1 in ands:
            val[lhs >> 1] = lv(r0) and lv(r1)
        for k, o in enumerate(outs):
            nm = sym_out[k]
            i = int(nm[nm.index('[') + 1:-1])
            outbits[cyc, i] = lv(o)
        state = {cur >> 1: lv(nxt) for cur, nxt, init in lat}
    ok = True
    for w in range(K):
        start = w * T + latency
        for i in range(m):
            v = 0
            for t in range(T):
                v |= int(outbits[start + t, i]) << t
            if v >> (T - 1):
                v -= 1 << T
            if v != int(X[w] @ W[i].astype(np.int64)):
                ok = False
    return ok


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
SDC = """create_clock -name clk -period {period} [get_ports clk]
set_input_delay 0 -clock clk [delete_from_list [all_inputs] [get_ports clk]]
set_output_delay 0 -clock clk [all_outputs]
"""


def main(out: Path, n: int, designs):
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(14)
    W = rng.choice(np.array([-1, 0, 1], dtype=np.int8), size=(n, n), p=[0.3, 0.4, 0.3])
    np.save(out / f'W_n{n}.npy', W)
    du = dont_use_cells()
    ow = width(XMAX * n)
    report = {'n': n, 'ow': ow, 'designs': {}}
    for design in designs:
        wd = out / f'{design}_n{n}'
        wd.mkdir(parents=True, exist_ok=True)
        mods, files = {}, []
        synth_seq(wd, 'SNEG', negline_rtl('SNEG'), du); mods['NEG'] = 'SNEG'; files.append('SNEG_gl.v')
        if design == 'g1':
            L = n
        else:
            g = int(design[3:])
            L = math.ceil(n / g)
            for gb in sorted({len(range(s, min(s + g, n))) for s in range(0, n, g)}):
                rtl, pats, D = gen_rtl(f'SGEN{gb}', gb)
                synth_seq(wd, f'SGEN{gb}', rtl, du)
                mods[f'GEN{gb}'] = f'SGEN{gb}'; mods[f'PATS{gb}'] = pats; mods[f'D{gb}'] = D
                files.append(f'SGEN{gb}_gl.v')
        trtl, depth = tree_rtl(f'STREE_L{L}', L)
        synth_seq(wd, f'STREE_L{L}', trtl, du); mods['TREE'] = f'STREE_L{L}'; files.append(f'STREE_L{L}_gl.v')
        top, latency = build_top(design, n, W, mods, depth)
        (wd / 'top.v').write_text(top)
        rd = ' '.join(f'read_verilog {f};' for f in files + ['top.v'])
        p = dock(f"yosys -q -p 'read_liberty -lib {LIB}; {rd} hierarchy -top top; opt_clean -purge; "
                 f"write_verilog -noattr -noexpr -nohex -nodec netlist_raw.v'", wd)
        if p.returncode != 0:
            raise RuntimeError(p.stderr[-2000:])
        (wd / 'netlist.v').write_text((wd / 'netlist_raw.v').read_text().replace(' signed ', ' '))
        p = dock(f"yosys -q -p 'read_liberty -ignore_miss_func {LIB}; read_verilog netlist.v; hierarchy -top top; flatten; "
                 f"synth -top top -noabc; dffunmap; setundef -zero -init; aigmap; opt_clean; write_aiger -ascii -symbols val.aag'", wd)
        if p.returncode != 0:
            raise RuntimeError(p.stderr[-2000:])
        A = read_aag_seq(wd / 'val.aag')
        ok = sim_seq(A, W, ow, latency)
        W2 = W.copy(); i, j = map(int, np.argwhere(W != 0)[0]); W2[i, j] = -W2[i, j]
        neg_detect = not sim_seq(A, W2, ow, latency)
        (wd / 'constraint.sdc').write_text(SDC.format(period=CLOCK_NS))
        for util in (45, 60, 75):
            (wd / f'config_u{util}.mk').write_text(ORFS_CFG.format(nick=f's_{design}_n{n}_u{util}', design=f'{design}_n{n}', util=util))
        area = {f: module_timing(wd, f[:-5])['area_um2'] for f in files}
        report['designs'][design] = {'validation': ok, 'negctl_detects': neg_detect, 'latency_cycles': latency,
                                     'cycles_per_word': ow, 'module_area_um2': area}
        print(design, json.dumps(report['designs'][design]), flush=True)
    (out / f'build_n{n}.json').write_text(json.dumps(report, indent=1))


if __name__ == '__main__':
    main(Path(sys.argv[1]), int(sys.argv[2]), sys.argv[3:])
