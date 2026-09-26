"""E2 gate-level flow for one design: Yosys (YoWASP 0.69) + ABC onto a liberty library.

Steps (all logged):
  1. RTL functional check: `eval` on K vectors vs numpy (independent of the construction checker).
  2. synth -flatten ; abc -liberty LIB [-D period] ; stat -liberty LIB  -> area, cell count
  3. mapped-netlist functional check: read_liberty (cell functions) + mapped netlist, `eval` on K vectors.
Fail closed: any mismatch, parse failure or tool error marks the design INVALID.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

YOSYS = 'yowasp-yosys'


def pack(vec, bits=8):
    v = 0
    for j, x in enumerate(vec):
        v |= (int(x) & ((1 << bits) - 1)) << (bits * j)
    return v


def unpack(v, m, ow):
    out = []
    for i in range(m):
        u = (v >> (ow * i)) & ((1 << ow) - 1)
        if u >> (ow - 1):
            u -= 1 << ow
        out.append(u)
    return out


def run_yosys(script: str, log: Path, timeout: int) -> str:
    """YoWASP (WASI) only sees the working directory: run inside log.parent with relative paths."""
    t = time.time()
    p = subprocess.run([YOSYS, '-p', script], capture_output=True, text=True, timeout=timeout, cwd=log.parent)
    log.write_text(p.stdout + '\n--- STDERR ---\n' + p.stderr + f'\n--- rc={p.returncode} wall={time.time()-t:.1f}s\n')
    if p.returncode != 0:
        raise RuntimeError(f'yosys rc={p.returncode}, see {log}')
    return p.stdout


def eval_script(prefix: str, X, n: int) -> str:
    cmds = [prefix]
    for vec in X:
        cmds.append(f"eval -set x {8*n}'h{pack(vec):x} -show y")
    return '; '.join(cmds)


def parse_evals(out: str, K: int):
    vals = re.findall(r"Eval result: \\y = (\d+)'([01xz]+)\.", out)
    if len(vals) != K:
        raise RuntimeError(f'expected {K} eval results, got {len(vals)}')
    res = []
    for _, bits in vals:
        if any(b in 'xz' for b in bits):
            raise RuntimeError('x/z in eval result')
        res.append(int(bits, 2))
    return res


def flow(rtl: Path, lib: Path, workdir: Path, X, Y, m: int, n: int, ow: int, period_ps: int | None = None,
         synth_opts: str = '', timeout: int = 7200) -> dict:
    import shutil
    workdir.mkdir(parents=True, exist_ok=True)
    rec = {'rtl': str(rtl), 'lib': lib.name, 'synth_opts': synth_opts, 'period_ps': period_ps}
    shutil.copy(rtl, workdir / 'rtl.v')
    if not (workdir / lib.name).exists():
        shutil.copy(lib, workdir / lib.name)
    rtl, lib = Path('rtl.v'), Path(lib.name)
    K = len(X)
    # 1. RTL eval
    out = run_yosys(eval_script(f'read_verilog {rtl}; hierarchy -top top; proc; flatten; opt_clean', X, n),
                    workdir / 'rtl_eval.log', timeout)
    got = [unpack(v, m, ow) for v in parse_evals(out, K)]
    rec['rtl_check'] = got == [list(map(int, y)) for y in Y]
    # 2. synthesis
    mapped = Path('mapped.v')
    D = f' -D {period_ps}' if period_ps else ''
    t = time.time()
    out = run_yosys(f'read_verilog {rtl}; synth -flatten -top top {synth_opts}; abc -liberty {lib}{D}; '
                    f'opt_clean; stat -liberty {lib}; write_verilog -noattr {mapped}', workdir / 'synth.log', timeout)
    rec['synth_wall'] = time.time() - t
    ma = re.findall(r'Chip area for (?:top module|module) .*?: ([0-9.]+)', out)
    mc = re.findall(r'^\s+(\d+)\s+(?:[0-9.]+\s+)?cells\s*$', out, flags=re.M)
    if not ma:
        raise RuntimeError('no area in stat output')
    rec['area'] = float(ma[-1])
    rec['cells'] = int(mc[-1]) if mc else None
    # 3. mapped-netlist eval with liberty cell functions
    out = run_yosys(eval_script(f'read_liberty -ignore_miss_func {lib}; read_verilog {mapped}; hierarchy -top top; flatten; opt_clean', X, n),
                    workdir / 'mapped_eval.log', timeout)
    got = [unpack(v, m, ow) for v in parse_evals(out, K)]
    rec['mapped_check'] = got == [list(map(int, y)) for y in Y]
    rec['valid'] = bool(rec['rtl_check'] and rec['mapped_check'])
    return rec


if __name__ == '__main__':
    meta = json.load(open(sys.argv[1]))
    rec = flow(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]), meta['X'], meta['Y'],
               len(meta['Y'][0]), len(meta['X'][0]), int(sys.argv[5]))
    print(json.dumps(rec, indent=1))
