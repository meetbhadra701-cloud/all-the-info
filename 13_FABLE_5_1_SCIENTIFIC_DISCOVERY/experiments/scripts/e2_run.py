"""E2 runner (see ../E2_PREREGISTRATION.md).

python3 e2_run.py OUTDIR [n] [p0 ...]
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from emit_verilog import emit, emit_behavioral  # noqa: E402
from hwlayer import block_patterns, check, from_da4ml, per_input, solve_da4ml, ternary  # noqa: E402

LIB = HERE.parent / 'inputs/lib/sky130_fd_sc_hd__tt_025C_1v80.lib'
ABC = Path('/tmp/abc_src/abc')
YOSYS = 'yowasp-yosys'


# ------------------------------------------------------------------ AIGER (ascii) simulator (independent)
def read_aag(path: Path):
    lines = path.read_text().splitlines()
    hdr = lines[0].split()
    assert hdr[0] == 'aag', 'ascii AIGER expected'
    M, I, L, O, A = map(int, hdr[1:6])
    assert L == 0, 'combinational design expected'
    ins = [int(lines[1 + k]) for k in range(I)]
    outs = [int(lines[1 + I + k]) for k in range(O)]
    ands = [tuple(map(int, lines[1 + I + O + k].split())) for k in range(A)]
    sym_in, sym_out = {}, {}
    for ln in lines[1 + I + O + A:]:
        if ln.startswith('i'):
            k, name = ln[1:].split(' ', 1); sym_in[int(k)] = name
        elif ln.startswith('o'):
            k, name = ln[1:].split(' ', 1); sym_out[int(k)] = name
        elif ln.startswith('c'):
            break
    return M, ins, outs, ands, sym_in, sym_out


def sim_aag(aag, bits_in: np.ndarray) -> np.ndarray:
    """bits_in: (I, batch) bool. Returns (O, batch) bool."""
    M, ins, outs, ands, _, _ = aag
    val = np.zeros((M + 1, bits_in.shape[1]), dtype=bool)
    for k, lit in enumerate(ins):
        val[lit >> 1] = bits_in[k]

    def lv(lit):
        v = val[lit >> 1]
        return ~v if lit & 1 else v
    for lhs, r0, r1 in ands:  # ands are topologically ordered in AIGER
        val[lhs >> 1] = lv(r0) & lv(r1)
    return np.stack([lv(o) for o in outs]) if outs else np.zeros((0, bits_in.shape[1]), bool)


def bus_index(name: str):
    m = re.match(r'(\w+)\[(\d+)\]$', name)
    return (m.group(1), int(m.group(2))) if m else (name, 0)


def check_aag(aag, W: np.ndarray, ow: int, rng, batch=64) -> bool:
    m, n = W.shape
    X = rng.integers(-128, 128, size=(batch, n), dtype=np.int64)
    _, ins, outs, _, sym_in, sym_out = aag
    bits = np.zeros((len(ins), batch), dtype=bool)
    for k in range(len(ins)):
        bus, b = bus_index(sym_in[k])
        assert bus == 'x'
        j, t = divmod(b, 8)
        bits[k] = (X[:, j] >> t) & 1
    O = sim_aag(aag, bits)
    Y = np.zeros((batch, m), dtype=np.int64)
    for k in range(len(outs)):
        bus, b = bus_index(sym_out[k])
        assert bus == 'y'
        i, t = divmod(b, ow)
        Y[:, i] |= O[k].astype(np.int64) << t
    Y = np.where(Y >> (ow - 1) & 1, Y - (1 << ow), Y)  # sign
    return bool(np.array_equal(Y, X @ W.T.astype(np.int64)))


# ------------------------------------------------------------------ tool wrappers
def yosys_to_aag(rtl: Path, wd: Path) -> Path:
    shutil.copy(rtl, wd / 'rtl.v')
    t = time.time()
    p = subprocess.run([YOSYS, '-p', 'read_verilog rtl.v; synth -flatten -top top -noabc; aigmap; opt_clean; '
                        'write_aiger -ascii -symbols design.aag'], cwd=wd, capture_output=True, text=True, timeout=7200)
    (wd / 'yosys.log').write_text(p.stdout + p.stderr + f'\nrc={p.returncode} wall={time.time()-t:.1f}\n')
    if p.returncode != 0 or not (wd / 'design.aag').exists():
        raise RuntimeError(f'yosys failed in {wd}')
    return wd / 'design.aag'


def abc_map(wd: Path, dtarget: float | None, tag: str) -> dict:
    D = f' -D {dtarget:.2f}' if dtarget else ''
    script = (f'read_lib -w {LIB}; read_aiger design.aag; strash; dch; map{D}; topo; stime -p; print_stats; '
              f'write_blif mapped_{tag}.blif; cec design.aag')
    t = time.time()
    p = subprocess.run([str(ABC), '-c', script], cwd=wd, capture_output=True, text=True, timeout=7200)
    out = p.stdout + p.stderr
    (wd / f'abc_{tag}.log').write_text(out + f'\nrc={p.returncode} wall={time.time()-t:.1f}\n')
    rec = {'tag': tag, 'D_target': dtarget, 'wall': time.time() - t}
    ma = re.search(r'Area\s*=\s*([0-9.]+)', out)
    md = re.search(r'Delay\s*=\s*([0-9.]+)\s*ps', out)
    mg = re.search(r'Gates\s*=\s*(\d+)', out)
    rec['area'] = float(ma.group(1)) if ma else None
    rec['delay_ps'] = float(md.group(1)) if md else None
    rec['gates'] = int(mg.group(1)) if mg else None
    rec['cec'] = 'Networks are equivalent' in out
    return rec


def main(outdir: Path, n: int, p0s):
    outdir.mkdir(parents=True, exist_ok=True)
    results = []
    for p0 in p0s:
        seed = 0
        rng = np.random.default_rng(1000 * seed + int(100 * p0) + n)  # identical to E1 seed 0
        W = ternary(n, n, p0, rng)
        crng = np.random.default_rng(99)
        designs = {'g1': per_input(W)}
        for g in (2, 3, 4):
            designs[f'ubp{g}'] = block_patterns(W, g, True)
        designs['cbp4'] = block_patterns(W, 4, False)
        designs['da4ml'] = from_da4ml(solve_da4ml(W), n, n)
        recs = {}
        for name, c in list(designs.items()) + [('beh', None)]:
            wd = outdir / f'n{n}_p{int(100*p0)}' / name
            wd.mkdir(parents=True, exist_ok=True)
            if c is not None:
                assert check(c, W, crng), name
                v, ow = emit(c, n)
                rec = {'U': c.U, 'B': c.B}
            else:
                v, ow = emit_behavioral(W)
                rec = {}
            (wd / 'src.v').write_text(v)
            aag = yosys_to_aag(wd / 'src.v', wd)
            A = read_aag(aag)
            rec['aig_ands'] = len(A[3])
            rec['aig_check'] = check_aag(A, W, ow, crng)
            rec['ow'] = ow
            rec['map_delay'] = abc_map(wd, None, 'delay')
            recs[name] = rec
            print(p0, name, json.dumps(rec), flush=True)
        dstar = max(r['map_delay']['delay_ps'] for r in recs.values())
        for name, rec in recs.items():
            wd = outdir / f'n{n}_p{int(100*p0)}' / name
            rec['map_iso'] = abc_map(wd, dstar, 'iso')
            rec['D_star'] = dstar
            print(p0, name, 'ISO', json.dumps(rec['map_iso']), flush=True)
        results.append({'n': n, 'p0': p0, 'seed': seed, 'designs': recs})
        (outdir / 'E2_results.json').write_text(json.dumps(results, indent=1))


if __name__ == '__main__':
    out = Path(sys.argv[1])
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 128
    p0s = [float(x) for x in sys.argv[3:]] or [0.33, 0.50]
    main(out, n, p0s)
