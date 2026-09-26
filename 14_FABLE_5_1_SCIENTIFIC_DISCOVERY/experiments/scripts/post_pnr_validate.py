"""Physical-level validation (pre-registered E5 item 4, applied to E5 and E6):
the ORFS *final routed* netlist (6_final.v: repair buffers, resized cells, CTS, hold buffers, ties, fillers)
is converted by Yosys (liberty cell functions) to an AIG and simulated by our own simulator against numpy W@x.
This is simulation-based equivalence (64 random vectors comb. / 12 back-to-back words seq.), not a formal cec.

python3 post_pnr_validate.py EDIR N DESIGN UTIL [serial]
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e5_build import LIB, XMAX, dock, validate, width  # noqa: E402
from e6_build import read_aag_seq, sim_seq  # noqa: E402


def main(edir: Path, n: int, design: str, util: int, mode: str):
    serial = mode == 'serial'
    nick = f"{'s_' if serial else ''}{design}_n{n}_u{util}"
    src = edir / 'orfs' / 'results' / 'sky130hd' / nick / 'base' / '6_final.v'
    wd = edir / f'{design}_n{n}'
    dst = wd / f'final_u{util}_gl_raw.v'   # ignored by .gitignore (*_gl_raw.v); large
    shutil.copy(src, dst)
    W = np.load(edir / f'W_n{n}.npy')
    ow = width(XMAX * n)
    if not serial:
        ok = validate(wd, [dst.name], W, ow, np.random.default_rng(99), tag=f'final_u{util}')
        W2 = W.copy(); i, j = map(int, np.argwhere(W != 0)[0]); W2[i, j] = -W2[i, j]
        neg = not validate(wd, [dst.name], W2, ow, np.random.default_rng(99), tag=f'final_u{util}')
    else:
        build = json.loads((edir / f'build_n{n}.json').read_text())
        lat = build['designs'][design]['latency_cycles']
        p = dock(f"yosys -q -p 'read_liberty -ignore_miss_func {LIB}; read_verilog {dst.name}; hierarchy -top top; flatten; "
                 f"synth -top top -noabc; dffunmap; setundef -zero -init; aigmap; opt_clean; write_aiger -ascii -symbols final_u{util}.aag'", wd)
        if p.returncode != 0:
            raise RuntimeError(p.stderr[-2000:])
        A = read_aag_seq(wd / f'final_u{util}.aag')
        ok = sim_seq(A, W, ow, lat, seed=99)
        W2 = W.copy(); i, j = map(int, np.argwhere(W != 0)[0]); W2[i, j] = -W2[i, j]
        neg = not sim_seq(A, W2, ow, lat, seed=99)
    rec = {'design': design, 'n': n, 'util': util, 'mode': mode, 'final_netlist_matches_numpy': ok, 'mutation_detected': neg}
    print(json.dumps(rec))
    with open(edir / 'post_pnr_validation.jsonl', 'a') as fh:
        fh.write(json.dumps(rec) + '\n')


if __name__ == '__main__':
    main(Path(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), sys.argv[5] if len(sys.argv) > 5 else 'parallel')
