"""Gate 3 builder: the frontier-style competitor P (bit-plane popcount per-input fabric) and, conditionally,
the bounded revision Q (UBP3-bitplane). Same flow and conventions as E6 (weight-independent modules,
via program = top-level connections only, keep all instances, W-dependent ties only).

python3 g3_build.py OUTDIR N DESIGN [DESIGN ...]        DESIGN in {pc, pc2, ubpb3, ubpb3p}  (pc2/ubpb3p: pipelined compressor)

Bit-plane protocol (8-bit two's-complement activations, MSB plane first, T = 8 cycles per word):
  x[j] at port cycle c carries bit (7 - c%8) of word c//8; `start` is high at c%8 == 0.
P (pc):
  * per input: PLINE = DFF(bit) -> pos line, and an inverter -> neg line (shared by all rows);
  * per (row, input): the via selects pos (w=+1), neg (w=-1, complement lane) or tie-0 (w=0);
  * per row PROW: popcount of the n slots -> register -> MSB-first Horner accumulator
      acc <- first ? (~pc + 1) : (2*acc + pc + cinj),
    where cinj injects the via-programmed constant c = #(w=-1) bit by bit (bit 7-t at phase t), making the
    complement lanes exact (sum_t s_t 2^t (1-b) = -1 - x per negative weight);
  * the finished word is copied to a 14-bit output register and emitted 2 bits/cycle, LSB first.
Q (ubpb3): per block of 3 inputs a shared generator emits, each cycle, all 13 canonical pattern values of the
  3 current bits in both polarities, offset-coded to [0, |q|] (<= 2 bits); each (row, block) leaf selects one
  bus by via; per row the compressor sums <= 2-bit leaves; the per-row constant absorbs the offsets.
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
from e5_build import LIB, XMAX, canon_patterns, dock, dont_use_cells, module_timing, width  # noqa: E402
from e6_build import read_aag_seq, synth_seq  # noqa: E402

CLOCK_NS = 3.0
BW = 8  # activation bits


def add_tree(lines, vals, prefix):
    """Balanced sum of (name, width, signed=False) unsigned values with explicit wires. Returns (name, width)."""
    cur = list(vals)
    k = 0
    while len(cur) > 1:
        nxt = []
        for i in range(0, len(cur) - 1, 2):
            (a, wa), (b, wb) = cur[i], cur[i + 1]
            wn = max(wa, wb) + 1
            lines.append(f'  wire [{wn-1}:0] {prefix}{k} = {a} + {b};')
            nxt.append((f'{prefix}{k}', wn)); k += 1
        if len(cur) % 2:
            nxt.append(cur[-1])
        cur = nxt
    return cur[0]


def prow_rtl(name, leaves, ow, cbits, group=0):
    """Per-row datapath. leaves: list of leaf widths (1 for pc, <=2 for ubpb3).
    group>0: pipeline the compressor -- partial sums over `group` leaves are registered (one extra cycle)."""
    L = len(leaves)
    V = [f'module {name}(input clk, input [7:0] ph, input [{cbits-1}:0] c, input [{sum(leaves)-1}:0] x, output [1:0] y);']
    vals, off = [], 0
    for i, w in enumerate(leaves):
        V.append(f'  wire [{w-1}:0] l{i} = x[{off+w-1}:{off}];'); vals.append((f'l{i}', w)); off += w
    if group:
        regs = []
        for gi in range(0, L, group):
            ps, pw = add_tree(V, vals[gi:gi + group], f'g{gi}_')
            V.append(f'  reg [{pw-1}:0] pr{gi}; always @(posedge clk) pr{gi} <= {ps};')
            regs.append((f'pr{gi}', pw))
        vals = regs
    s, sw = add_tree(V, vals, 't')
    V.append(f'  reg [{sw-1}:0] pc; always @(posedge clk) pc <= {s};')
    V.append(f'  wire [{ow-1}:0] pce = {{{{{ow-sw}{{1\'b0}}}}, pc}};')
    # constant injection: bit (7-t) of c at phase t (t = 1..7); c has cbits <= 7 bits
    terms = [f'(ph[{t}] & c[{7-t}])' for t in range(1, 8) if 7 - t < cbits]
    cexpr = ' | '.join(terms) if terms else "1'b0"
    V.append(f'  wire cinj = {cexpr};')
    V.append(f'  reg [{ow-1}:0] acc;')
    V.append(f'  wire [{ow-1}:0] addend = ph[0] ? ~pce : pce;')
    V.append(f'  wire [{ow-1}:0] base = ph[0] ? {ow}\'d0 : {{acc[{ow-2}:0], 1\'b0}};')
    V.append(f'  wire cin = ph[0] | cinj;')
    V.append(f'  always @(posedge clk) acc <= base + addend + cin;')
    V.append(f'  reg [{ow-1}:0] outr; always @(posedge clk) outr <= ph[0] ? acc : {{2\'b00, outr[{ow-1}:2]}};')
    V.append('  assign y = outr[1:0];\nendmodule')
    return '\n'.join(V) + '\n'


def pline_rtl(name):
    return (f'module {name}(input clk, input a, output pos, output neg);\n'
            f'  reg q; always @(posedge clk) q <= a;\n  assign pos = q; assign neg = ~q;\nendmodule\n')


def gen3b_rtl(name, g):
    """UBP bit-plane generator: for g input bits, every canonical pattern q in both polarities, offset-coded:
    val(+q) = sum_j q_j b_j + #neg(q);  val(-q) = -sum_j q_j b_j + #pos(q); both in [0, |q|]."""
    pats = canon_patterns(g)
    V = [f'module {name}(input clk, input [{g-1}:0] a']
    outs = []
    for k, p in enumerate(pats):
        nz = [t for t, v in enumerate(p) if v]
        w = max(1, math.ceil(math.log2(len(nz) + 1)))
        outs.append((k, p, w))
    V[0] += ', ' + ', '.join(f'output [{w-1}:0] yp{k}, output [{w-1}:0] yn{k}' for k, p, w in outs) + ');'
    V.append(f'  reg [{g-1}:0] q; always @(posedge clk) q <= a;')
    for k, p, w in outs:
        pos_terms = [f'q[{j}]' for j, v in enumerate(p) if v > 0]
        negc_terms = [f'~q[{j}]' for j, v in enumerate(p) if v < 0]   # -b = ~b - 1 -> offset #neg
        # +q offset-coded: sum_{q_j=+1} b_j + sum_{q_j=-1} (1 - b_j)
        V.append(f'  assign yp{k} = ' + ' + '.join(f'{{{w-1}\'b0, {t}}}' if w > 1 else t for t in pos_terms + negc_terms) + ';')
        # -q offset-coded: sum_{q_j=+1} (1 - b_j) + sum_{q_j=-1} b_j
        negp = [f'~q[{j}]' for j, v in enumerate(p) if v > 0] + [f'q[{j}]' for j, v in enumerate(p) if v < 0]
        V.append(f'  assign yn{k} = ' + ' + '.join(f'{{{w-1}\'b0, {t}}}' if w > 1 else t for t in negp) + ';')
    V.append('endmodule')
    return '\n'.join(V) + '\n', outs


def ctrl_rtl(name, extra=0):
    """Shared phase generator: ph[0] = start delayed by 2+extra (input DFF + [pipeline] + popcount register)."""
    d = ' '.join(f's{k+2} <= s{k+1};' for k in range(extra))
    return (f'module {name}(input clk, input start, output [7:0] ph);\n'
            f'  reg {", ".join(f"s{k+1}" for k in range(extra + 1))}; reg [7:0] r;\n'
            f'  always @(posedge clk) begin s1 <= start; {d} r <= {{r[6:0], s{extra+1}}}; end\n'
            f'  assign ph = r;\nendmodule\n')


def ff(q, d):
    return f'  wire {q}; sky130_fd_sc_hd__dfxtp_1 {q}_ff (.CLK(clk), .D({d}), .Q({q}));'


def build_top(design, n, W, mods, ow):
    m = n
    V = [f'module top(input clk, input start, input [{n-1}:0] x, output [{2*m-1}:0] y);',
         f'  wire [7:0] ph; {mods["CTRL"]} ctl (.clk(clk), .start(start), .ph(ph));',
         '  wire zero; sky130_fd_sc_hd__conb_1 tie0 (.HI(), .LO(zero));']
    if design == 'pc':
        for j in range(n):
            V.append(f'  wire lp{j}, ln{j}; {mods["LINE"]} ln_{j} (.clk(clk), .a(x[{j}]), .pos(lp{j}), .neg(ln{j}));')
        def row_leaves(i):
            parts = []
            for j in range(n):
                w = int(W[i, j]); parts.append('zero' if w == 0 else (f'lp{j}' if w > 0 else f'ln{j}'))
            return parts, int((W[i] < 0).sum())
    else:
        g = int(design[4:])
        blocks = [list(range(s, min(s + g, n))) for s in range(0, n, g)]
        lines = {}
        for b, cols in enumerate(blocks):
            gb = len(cols); outs = mods[f'OUTS{gb}']
            ports = [f'.clk(clk)', '.a({' + ', '.join(f'x[{c}]' for c in reversed(cols)) + '})']
            for k, p, w in outs:
                V.append(f'  wire [{w-1}:0] gp{b}_{k}, gn{b}_{k};')
                ports += [f'.yp{k}(gp{b}_{k})', f'.yn{k}(gn{b}_{k})']
                lines[(b, p)] = (f'gp{b}_{k}', f'gn{b}_{k}', w, sum(1 for v in p if v < 0), sum(1 for v in p if v > 0))
            V.append(f'  {mods[f"GEN{gb}"]} gen{b} ({", ".join(ports)});')
        LW = 2  # every leaf is a 2-bit slot (1-bit buses are zero-extended by tie)
        def row_leaves(i):
            parts, const = [], 0
            for b, cols in enumerate(blocks):
                q = tuple(int(W[i, c]) for c in cols)
                if not any(q):
                    parts.append('{zero, zero}'); continue
                s = next(v for v in q if v)
                pos, neg, w, nneg, npos = lines[(b, tuple(s * v for v in q))]
                if s > 0:
                    src, off = pos, nneg
                else:
                    src, off = neg, npos
                parts.append(src if w == 2 else '{zero, ' + src + '}')
                const += off
            return parts, const
    cb = 7
    for i in range(m):
        parts, const = row_leaves(i)
        assert const < 2 ** cb
        V.append(f'  wire hi{i}, lo{i}; sky130_fd_sc_hd__conb_1 ctie{i} (.HI(hi{i}), .LO(lo{i}));')
        cbits = ', '.join(f'hi{i}' if (const >> k) & 1 else f'lo{i}' for k in reversed(range(cb)))
        V.append(f'  {mods["ROW"]} row{i} (.clk(clk), .ph(ph), .c({{{cbits}}}), .x({{{", ".join(reversed(parts))}}}), .y(y[{2*i+1}:{2*i}]));')
    V.append('endmodule')
    return '\n'.join(V) + '\n'


def sim_bitplane(aag, W, ow, K=10, seed=3):
    """Cycle-accurate: MSB-first planes, 8 cycles/word; outputs 2 bits/cycle LSB first over 7 cycles.
    Finds the output latency (first cycle of word 0's y bits) and checks every word; returns (ok, latency)."""
    M, ins, lat, outs, ands, sym_in, sym_out = aag
    n, m = W.shape[1], W.shape[0]
    rng = np.random.default_rng(seed)
    X = rng.integers(-XMAX, XMAX + 1, size=(K, n), dtype=np.int64)
    cycles = K * 8 + 30
    val = np.zeros(M + 1, dtype=bool)
    state = {cur >> 1: bool(init) for cur, nxt, init in lat}
    lv = lambda l: (not val[l >> 1]) if l & 1 else bool(val[l >> 1])
    ob = np.zeros((cycles, 2 * m), dtype=np.int64)
    for cyc in range(cycles):
        w, p = divmod(cyc, 8)
        for k, lit in enumerate(ins):
            nm = sym_in[k]
            if nm == 'start':
                v = (p == 0)   # keep word framing after the last word so its result is emitted
            elif nm == 'clk':
                v = False
            else:
                j = int(nm[nm.index('[') + 1:-1])
                xv = int(X[w, j]) & 0xFF if w < K else 0
                v = bool((xv >> (7 - p)) & 1)
            val[lit >> 1] = v
        for cur, s in state.items():
            val[cur] = s
        for lhs, r0, r1 in ands:
            val[lhs >> 1] = lv(r0) and lv(r1)
        for k, o in enumerate(outs):
            nm = sym_out[k]; ob[cyc, int(nm[nm.index('[') + 1:-1])] = lv(o)
        state = {cur >> 1: lv(nxt) for cur, nxt, init in lat}
    ref = X @ W.T.astype(np.int64)
    for L in range(0, 24):
        ok = True
        for w in range(K):
            for i in range(m):
                v = 0
                for t in range(7):
                    c = L + 8 * w + t
                    if c >= cycles:
                        ok = False; break
                    v |= int(ob[c, 2 * i]) << (2 * t) | int(ob[c, 2 * i + 1]) << (2 * t + 1)
                if v >> (ow - 1):
                    v -= 1 << ow
                if v != int(ref[w, i]):
                    ok = False; break
            if not ok:
                break
        if ok:
            return True, L
    return False, None


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
    W = rng.choice(np.array([-1, 0, 1], dtype=np.int8), size=(n, n), p=[0.3, 0.4, 0.3])  # identical to E5/E6
    np.save(out / f'W_n{n}.npy', W)
    du = dont_use_cells()
    ow = width(XMAX * n)
    bj = out / f'build_n{n}.json'
    report = json.loads(bj.read_text()) if bj.exists() else {'n': n, 'ow': ow, 'protocol': 'bit-plane MSB-first, 8 cycles/word, 2 output bits/cycle', 'designs': {}}
    for design in designs:
        wd = out / f'{design}_n{n}'
        wd.mkdir(parents=True, exist_ok=True)
        mods, files = {}, []
        piped = design.endswith('p') or design == 'pc2'
        base_design = 'pc' if design.startswith('pc') else design.rstrip('p')
        synth_seq(wd, 'CTRL', ctrl_rtl('CTRL', 1 if piped else 0), du); mods['CTRL'] = 'CTRL'; files.append('CTRL_gl.v')
        if base_design == 'pc':
            synth_seq(wd, 'PLINE', pline_rtl('PLINE'), du); mods['LINE'] = 'PLINE'; files.append('PLINE_gl.v')
            leaves = [1] * n
        else:
            g = int(base_design[4:])
            for gb in sorted({len(range(s, min(s + g, n))) for s in range(0, n, g)}):
                rtl, outs = gen3b_rtl(f'BGEN{gb}', gb)
                synth_seq(wd, f'BGEN{gb}', rtl, du)
                mods[f'GEN{gb}'] = f'BGEN{gb}'; mods[f'OUTS{gb}'] = outs; files.append(f'BGEN{gb}_gl.v')
            leaves = [2] * math.ceil(n / g)
        rname = f'PROW_{design}_L{len(leaves)}'
        grp = (8 if base_design == 'pc' else 4) if piped else 0
        synth_seq(wd, rname, prow_rtl(rname, leaves, ow, 7, grp), du); mods['ROW'] = rname; files.append(f'{rname}_gl.v')
        (wd / 'top.v').write_text(build_top(base_design, n, W, mods, ow))
        rd = ' '.join(f'read_verilog {f};' for f in files + ['top.v'])
        p = dock(f"yosys -q -p 'read_liberty -lib {LIB}; {rd} hierarchy -top top; setattr -set keep 1 top/t:*; opt_clean -purge; "
                 f"write_verilog -noattr -noexpr -nohex -nodec netlist_raw.v'", wd)
        if p.returncode != 0:
            raise RuntimeError(p.stderr[-2000:])
        (wd / 'netlist.v').write_text((wd / 'netlist_raw.v').read_text().replace(' signed ', ' '))
        p = dock(f"yosys -q -p 'read_liberty -ignore_miss_func {LIB}; read_verilog netlist.v; hierarchy -top top; flatten; "
                 f"synth -top top -noabc; dffunmap; setundef -zero -init; aigmap; opt_clean; write_aiger -ascii -symbols val.aag'", wd)
        if p.returncode != 0:
            raise RuntimeError(p.stderr[-2000:])
        A = read_aag_seq(wd / 'val.aag')
        ok, L = sim_bitplane(A, W, ow)
        W2 = W.copy(); i, j = map(int, np.argwhere(W != 0)[0]); W2[i, j] = -W2[i, j]
        neg_ok, _ = sim_bitplane(A, W2, ow)
        (wd / 'constraint.sdc').write_text(SDC.format(period=CLOCK_NS))
        for util in (45, 60, 75):
            (wd / f'config_u{util}.mk').write_text(ORFS_CFG.format(nick=f'g3_{design}_n{n}_u{util}', design=f'{design}_n{n}', util=util))
        tim = {f: module_timing(wd, f[:-5]) for f in files}
        report['designs'][design] = {'validation': ok, 'negctl_detects': not neg_ok, 'output_latency_cycles': L,
                                     'cycles_per_word': 8, 'module_timing': tim}
        print(design, json.dumps(report['designs'][design]), flush=True)
    (out / f'build_n{n}.json').write_text(json.dumps(report, indent=1))


if __name__ == '__main__':
    main(Path(sys.argv[1]), int(sys.argv[2]), sys.argv[3:])
