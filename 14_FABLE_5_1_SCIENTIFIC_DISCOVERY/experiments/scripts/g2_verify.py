"""Gate 2: functional check of (fixed base + via program) against numpy W @ x.

python3 g2_verify.py OUTDIR DESIGN TAG [NETLIST]
  NETLIST defaults to DESIGN/netlist_base.v, programmed here at the Verilog level (pre-PnR check).
  Given a post-PnR netlist written by OpenROAD after g2_apply_program, it is simulated as-is.
Protocols: ubp3s / g1s -> E6 serial words (sim_seq); pc2 -> G3 bit-plane (sim_bitplane).
Appends a record to OUTDIR/g2_verification.jsonl.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from e5_build import LIB, XMAX, dock, width  # noqa: E402
from e6_build import read_aag_seq, sim_seq  # noqa: E402
from g3_build import sim_bitplane  # noqa: E402

G2LIB = '/work/cells/g2_cells.lib'
G2R3LIB = '/work/cells/g2r3_cells.lib'
LATENCY = {'ubp3s': 8, 'g1s': 7, 'ubp3r3': 8}


def program_verilog(text: str, prog: dict) -> str:
    for src, sites in prog['nets'].items():
        text, k = re.subn(rf'(LTAP2? lt_{src} \(\n\s+\.A\(\w+\))(\n)', rf'\g<1>,\n    .Z(pg_{src})\g<2>', text)
        assert k == 1, src
        text = text.replace('module top(', f'module top(', 1)
        text = re.sub(r'(\n  input clk;)', rf'\n  wire pg_{src};\1', text, count=1)
        for s in sites:
            text, k = re.subn(rf'(VSITE_BUF {s} \(\n)(\s+)(\.Z\()', rf'\g<1>\g<2>.A(pg_{src}),\n\g<2>\g<3>', text)
            assert k == 1, s
    for z in prog['zeros']:
        text, k = re.subn(rf'VSITE_BUF {z} \(', f'VSITE_ZERO {z} (', text)
        assert k == 1, z
    for o in prog['ones']:
        text, k = re.subn(rf'VSITE_ZERO {o} \(', f'VSITE_ONE {o} (', text)
        assert k == 1, o
    return text


def main(out: Path, design: str, tag: str, netlist: str | None):
    wd = out / design
    prog = json.loads((wd / f'prog_{tag}.json').read_text())
    W = np.load(wd / f'W_{tag}.npy')
    ow = width(XMAX * W.shape[1])
    if netlist is None:
        vname = f'programmed_{tag}.v'
        (wd / vname).write_text(program_verilog((wd / 'netlist_base.v').read_text(), prog))
        src = 'pre-PnR (Verilog-level program)'
    else:
        vname = Path(netlist).name
        src = f'post-PnR ({vname})'
    p = dock(f"cd {design} && yosys -q -p 'read_liberty -ignore_miss_func {LIB}; read_liberty -ignore_miss_func {G2LIB}; read_liberty -ignore_miss_func {G2R3LIB}; "
             f"read_verilog {vname}; hierarchy -top top; flatten; synth -top top -noabc; dffunmap; setundef -zero -init; "
             f"aigmap; opt_clean; write_aiger -ascii -symbols v_{tag}.aag'", out)
    if p.returncode != 0:
        raise RuntimeError(p.stderr[-2500:])
    A = read_aag_seq(wd / f'v_{tag}.aag')
    W2 = W.copy(); i, j = map(int, np.argwhere(W != 0)[0]); W2[i, j] = -W2[i, j]
    if design == 'pc2':
        ok, lat = sim_bitplane(A, W, ow)
        neg = not sim_bitplane(A, W2, ow)[0]
    else:
        ok, lat = sim_seq(A, W, ow, LATENCY[design]), LATENCY[design]
        neg = not sim_seq(A, W2, ow, LATENCY[design])
    rec = {'design': design, 'tag': tag, 'netlist': src, 'matches_numpy': ok, 'mutation_detected': neg, 'latency': lat}
    print(json.dumps(rec))
    with open(out / 'g2_verification.jsonl', 'a') as fh:
        fh.write(json.dumps(rec) + '\n')


if __name__ == '__main__':
    main(Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
