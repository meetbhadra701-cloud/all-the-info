"""Amendment A2: re-emit an existing design's top netlist WITHOUT W-dependent pruning, then re-validate.

The original emission (`hierarchy; opt_clean -purge`) removed negator instances whose pattern line no row
selects, i.e. a weight-dependent optimization forbidden in regime V. Here every top-level instance is kept
(`setattr -set keep 1 top/t:*`), the netlist is re-validated against numpy (with the mutation control), the
number of negator instances is checked against the full universal fabric, and the full cell area is measured
with Yosys `stat -liberty`. Module netlists (*_gl.v) are reused unchanged (identical to the E5/E6 builds).

python3 reemit_a2.py EDIR N DESIGN [serial]
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e5_build import LIB, XMAX, dock, validate, width  # noqa: E402
from e6_build import read_aag_seq, sim_seq  # noqa: E402


def expected_negs(design: str, n: int) -> int:
    if design == 'g1':
        return n
    g = int(design[3:])
    return sum((3 ** len(range(s, min(s + g, n))) - 1) // 2 for s in range(0, n, g))


def main(edir: Path, n: int, design: str, mode: str):
    serial = mode == 'serial'
    wd = edir / f'{design}_n{n}'
    files = sorted(f.name for f in wd.glob('*_gl.v'))
    rd = ' '.join(f'read_verilog {f};' for f in files + ['top.v'])
    p = dock(f"yosys -q -p 'read_liberty -lib {LIB}; {rd} hierarchy -top top; setattr -set keep 1 top/t:*; opt_clean -purge; "
             f"write_verilog -noattr -noexpr -nohex -nodec netlist_raw.v'", wd)
    if p.returncode != 0:
        raise RuntimeError(p.stderr[-2000:])
    (wd / 'netlist.v').write_text((wd / 'netlist_raw.v').read_text().replace(' signed ', ' '))
    top = (wd / 'netlist.v').read_text().split('module top(')[1]
    negs = len(re.findall(r'^\s+S?NEG(_W\d+)? ', top, flags=re.M))
    p = dock(f"yosys -p 'read_liberty -lib {LIB}; read_verilog netlist.v; hierarchy -top top; tee -q -o stat_a2.txt stat -liberty {LIB}'", wd)
    area = float(re.search(r"Chip area for top module '\\top': ([0-9.]+)", (wd / 'stat_a2.txt').read_text()).group(1))
    W = np.load(edir / f'W_n{n}.npy')
    ow = width(XMAX * n)
    W2 = W.copy(); i, j = map(int, np.argwhere(W != 0)[0]); W2[i, j] = -W2[i, j]
    build = json.loads((edir / f'build_n{n}.json').read_text())
    if serial:
        p = dock(f"yosys -q -p 'read_liberty -ignore_miss_func {LIB}; read_verilog netlist.v; hierarchy -top top; flatten; "
                 f"synth -top top -noabc; dffunmap; setundef -zero -init; aigmap; opt_clean; write_aiger -ascii -symbols val.aag'", wd)
        if p.returncode != 0:
            raise RuntimeError(p.stderr[-2000:])
        A = read_aag_seq(wd / 'val.aag')
        lat = build['designs'][design]['latency_cycles']
        ok, neg = sim_seq(A, W, ow, lat), not sim_seq(A, W2, ow, lat)
    else:
        ok = validate(wd, ['netlist.v'], W, ow, np.random.default_rng(7))
        neg = not validate(wd, ['netlist.v'], W2, ow, np.random.default_rng(7), tag='negctl')
    rec = {'validation': ok, 'negctl_detects': neg, 'neg_instances': negs, 'neg_expected_full_fabric': expected_negs(design, n),
           'full_fabric': negs == expected_negs(design, n), 'yosys_stat_area_um2': area}
    build['designs'][design]['reemit_A2'] = rec
    (edir / f'build_n{n}.json').write_text(json.dumps(build, indent=1))
    print(design, json.dumps(rec), flush=True)


if __name__ == '__main__':
    main(Path(sys.argv[1]), int(sys.argv[2]), sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else 'parallel')
