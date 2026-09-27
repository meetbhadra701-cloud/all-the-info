"""Gate 3 post-PnR validation: the ORFS final routed netlist of a bit-plane design (P / P2) simulated by our own
cycle-accurate simulator against numpy W@x, with the mutation control.   python3 g3_post_validate.py G3_DIR DESIGN NICK"""
import json, shutil, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from e5_build import LIB, XMAX, dock, width
from e6_build import read_aag_seq
from g3_build import sim_bitplane
g3, design, nick = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
wd = g3 / f'{design}_n64'
shutil.copy(g3 / 'orfs' / 'results' / 'sky130hd' / nick / 'base' / '6_final.v', wd / f'final_{nick}_gl_raw.v')
p = dock(f"yosys -q -p 'read_liberty -ignore_miss_func {LIB}; read_verilog final_{nick}_gl_raw.v; hierarchy -top top; flatten; "
         f"synth -top top -noabc; dffunmap; setundef -zero -init; aigmap; opt_clean; write_aiger -ascii -symbols final_{nick}.aag'", wd)
if p.returncode != 0:
    raise RuntimeError(p.stderr[-2000:])
A = read_aag_seq(wd / f'final_{nick}.aag'); W = np.load(g3 / 'W_n64.npy'); ow = width(XMAX * 64)
ok, lat = sim_bitplane(A, W, ow)
W2 = W.copy(); i, j = map(int, np.argwhere(W != 0)[0]); W2[i, j] = -W2[i, j]
rec = {'design': design, 'nick': nick, 'final_netlist_matches_numpy': ok, 'latency': lat, 'mutation_detected': not sim_bitplane(A, W2, ow)[0]}
print(json.dumps(rec)); open(g3 / 'post_pnr_validation.jsonl', 'a').write(json.dumps(rec) + '\n')
