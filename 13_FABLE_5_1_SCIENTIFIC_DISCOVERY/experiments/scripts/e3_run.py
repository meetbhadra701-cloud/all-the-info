"""E3: gate-level test of the regime-(V) claim with weight-independent components (see ../E3_PREREGISTRATION.md).

python3 e3_run.py OUTDIR
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
from e2_run import abc_map, read_aag, sim_aag, bus_index, yosys_to_aag  # noqa: E402
from hwlayer import _canon, width  # noqa: E402


def signed_bits(v, w):
    return [(int(v) >> t) & 1 for t in range(w)]


def check_component(aag, in_widths: list[int], out_widths: list[int], golden, rng, batch=64) -> bool:
    """Generic independent check. Inputs/outputs are flat buses x / y made of fields of given widths."""
    _, ins, outs, _, sym_in, sym_out = aag
    X = [[int(rng.integers(-(1 << (w - 1)), 1 << (w - 1))) for w in in_widths] for _ in range(batch)]
    in_off = np.cumsum([0] + in_widths)
    out_off = np.cumsum([0] + out_widths)
    bits = np.zeros((len(ins), batch), dtype=bool)
    for k in range(len(ins)):
        bus, b = bus_index(sym_in[k]); assert bus == 'x'
        f = int(np.searchsorted(in_off, b, side='right') - 1); t = b - in_off[f]
        for s in range(batch):
            bits[k, s] = (X[s][f] >> t) & 1
    O = sim_aag(aag, bits)
    for s in range(batch):
        want = golden(X[s])
        got = []
        for f, w in enumerate(out_widths):
            v = 0
            for k in range(len(outs)):
                bus, b = bus_index(sym_out[k]); assert bus == 'y'
                if out_off[f] <= b < out_off[f + 1]:
                    v |= int(O[k, s]) << (b - out_off[f])
            if v >> (w - 1):
                v -= 1 << w
            got.append(v)
        if got != want:
            return False
    return True


def tree_v(L, w):
    ow = w + max(1, math.ceil(math.log2(L)))
    terms = ' + '.join(f'$signed(x[{w*i+w-1}:{w*i}])' for i in range(L))
    v = (f'module top(input [{w*L-1}:0] x, output [{ow-1}:0] y);\n'
         f'  wire signed [{ow-1}:0] s = {terms};\n  assign y = s;\nendmodule\n')
    return v, [w] * L, [ow], (lambda xs: [sum(xs)])


def neg_v(w):
    v = (f'module top(input [{w-1}:0] x, output [{w}:0] y);\n'
         f'  wire signed [{w}:0] s = -$signed(x);\n  assign y = s;\nendmodule\n')
    return v, [w], [w + 1], (lambda xs: [-xs[0]])


def gen_v(g):
    """All canonical patterns of g 8-bit inputs, parent + one input (same construction as hwlayer.block_patterns)."""
    pats = sorted({_canon(q)[0] for q in itertools.product((-1, 0, 1), repeat=g) if any(q)},
                  key=lambda p: (sum(1 for v in p if v), p))
    lines = [f'module top(input [{8*g-1}:0] x, output [{{OW}}:0] y);']
    for j in range(g):
        lines.append(f'  wire signed [7:0] i{j} = x[{8*j+7}:{8*j}];')
    name = {}
    for p in pats:
        nz = [t for t, v in enumerate(p) if v]
        if len(nz) == 1:
            name[p] = f'i{nz[0]}'; continue
        parent = list(p); parent[nz[-1]] = 0; parent = tuple(parent)
        w = width(-128 * len(nz), 128 * len(nz))
        op = '+' if p[nz[-1]] > 0 else '-'
        name[p] = f'p{len(name)}'
        lines.append(f'  wire signed [{w-1}:0] {name[p]} = {name[parent]} {op} i{nz[-1]};')
    ow = width(-128 * g, 128 * g)
    outs = [p for p in pats if sum(1 for v in p if v) >= 2]
    for k, p in enumerate(outs):
        lines.append(f'  wire signed [{ow-1}:0] o{k} = {name[p]};')
        lines.append(f'  assign y[{ow*k+ow-1}:{ow*k}] = o{k};')
    lines.append('endmodule')
    v = '\n'.join(lines).replace('{OW}', str(ow * len(outs) - 1)) + '\n'
    golden = (lambda xs, outs=outs: [sum(c * x for c, x in zip(p, xs)) for p in outs])
    return v, [8] * g, [ow] * len(outs), golden, len(outs)


def run_component(wd: Path, verilog, in_w, out_w, golden, rng):
    wd.mkdir(parents=True, exist_ok=True)
    (wd / 'src.v').write_text(verilog)
    aag = yosys_to_aag(wd / 'src.v', wd)
    A = read_aag(aag)
    rec = {'aig_ands': len(A[3]), 'aig_check': check_component(A, in_w, out_w, golden, rng)}
    rec['map_delay'] = abc_map(wd, None, 'delay')
    return rec


def main(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(2026)
    comps = {}
    GS = (2, 3, 4)
    for g in GS:
        v, iw, ow, gold, nout = gen_v(g)
        comps[f'GEN{g}'] = run_component(out / f'GEN{g}', v, iw, ow, gold, rng)
        comps[f'GEN{g}']['patterns_ge2'] = nout
        print('GEN', g, json.dumps(comps[f'GEN{g}']['map_delay']), comps[f'GEN{g}']['aig_check'], flush=True)
    for w in sorted({8} | {8 + math.ceil(math.log2(g)) for g in GS}):
        v, iw, ow, gold = neg_v(w)
        comps[f'NEG{w}'] = run_component(out / f'NEG{w}', v, iw, ow, gold, rng)
        print('NEG', w, json.dumps(comps[f'NEG{w}']['map_delay']), comps[f'NEG{w}']['aig_check'], flush=True)
    results = []
    for n in (128, 1024):
        trees = {}
        trees['g1'] = (n, 8)
        for g in GS:
            trees[f'g{g}'] = (math.ceil(n / g), 8 + math.ceil(math.log2(g)))
        for key, (L, w) in trees.items():
            name = f'TREE_n{n}_{key}_L{L}_w{w}'
            if name not in comps:
                v, iw, ow, gold = tree_v(L, w)
                comps[name] = run_component(out / name, v, iw, ow, gold, rng)
                print('TREE', n, key, L, w, json.dumps(comps[name]['map_delay']), comps[name]['aig_check'], flush=True)
        # iso-delay budget
        d = lambda c: comps[c]['map_delay']['delay_ps']
        path = {'g1': d('NEG8') + d(f'TREE_n{n}_g1_L{n}_w8')}
        for g in GS:
            L, w = trees[f'g{g}']
            path[f'g{g}'] = d(f'GEN{g}') + d(f'NEG{w}') + d(f'TREE_n{n}_g{g}_L{L}_w{w}')
        dstar = max(path.values())
        rec = {'n': n, 'm': n, 'D_star': dstar, 'paths': path, 'designs': {}}
        for key, (L, w) in trees.items():
            name = f'TREE_n{n}_{key}_L{L}_w{w}'
            if key == 'g1':
                budget = dstar - d('NEG8')
            else:
                g = int(key[1:])
                budget = dstar - d(f'GEN{g}') - d(f'NEG{w}')
            iso = abc_map(out / name, budget, f'iso_n{n}')
            comps[name][f'iso_n{n}'] = iso
            if key == 'g1':
                area = n * iso['area'] + n * comps['NEG8']['map_delay']['area']
                parts = {'trees': n * iso['area'], 'neg': n * comps['NEG8']['map_delay']['area']}
            else:
                g = int(key[1:])
                nb = math.ceil(n / g)
                npat = (3 ** g - 1) // 2
                gen_area = nb * comps[f'GEN{g}']['map_delay']['area']
                neg_area = nb * npat * comps[f'NEG{w}']['map_delay']['area']
                area = n * iso['area'] + gen_area + neg_area
                parts = {'trees': n * iso['area'], 'gen': gen_area, 'neg': neg_area}
            rec['designs'][key] = {'L': L, 'w': w, 'tree_budget_ps': budget, 'tree_iso': iso,
                                   'fabric_area_um2': area, 'parts': parts}
            print('ISO', n, key, round(area), json.dumps(parts), iso['cec'], flush=True)
        results.append(rec)
        (out / 'E3_results.json').write_text(json.dumps({'components': comps, 'fabrics': results}, indent=1))


if __name__ == '__main__':
    main(Path(sys.argv[1]))
