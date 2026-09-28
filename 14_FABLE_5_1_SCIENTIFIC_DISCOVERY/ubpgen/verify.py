"""Functional verification against the independent numpy oracle y = W @ x.

The netlist (pre-PnR: base + program applied at the Verilog level; post-PnR: the complete programmed netlist
written by OpenROAD) is converted by Yosys (liberty cell functions) into an AIGER model and simulated
cycle-accurately by our own simulators (bit-serial words or bit-planes) against numpy.

Two mutation controls, both must be detected (i.e. the check must FAIL on them):
  * oracle mutation (historical): the same circuit checked against W' = W with one non-zero weight negated;
  * program mutation (new): the circuit re-programmed with one leaf moved to a different line (or to zero)
    checked against the unmodified W.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import numpy as np

from . import arch, programs
from ._legacy import LIB, dock, read_aag_seq, sim_bitplane, sim_seq

LIBS = [LIB, '/work/cells/g2_cells.lib', '/work/cells/g2r3_cells.lib']


def to_aag(root: Path, netlist_rel: str, aag_rel: str):
    rl = ' '.join(f'read_liberty -ignore_miss_func {l};' for l in LIBS)
    p = dock(f"yosys -q -p '{rl} read_verilog {netlist_rel}; hierarchy -top top; flatten; synth -top top -noabc; "
             f"dffunmap; setundef -zero -init; aigmap; opt_clean; write_aiger -ascii -symbols {aag_rel}'", root)
    if p.returncode != 0:
        raise RuntimeError('yosys AIGER export failed:\n' + p.stderr[-3000:])
    return read_aag_seq(root / aag_rel)


def simulate(cfg, aag, W) -> tuple[bool, int | None]:
    ow = arch.output_width(cfg)
    v = cfg.raw['verify']
    if cfg.fabric == 'pc2':
        return sim_bitplane(aag, W, ow, K=10, seed=v['seed'])
    lat = arch.serial_latency(cfg)
    return sim_seq(aag, W, ow, lat, K=v['words'], seed=v['seed']), lat


def oracle_mutation(W: np.ndarray) -> np.ndarray:
    W2 = W.copy()
    i, j = map(int, np.argwhere(W != 0)[0])
    W2[i, j] = -W2[i, j]
    return W2


def program_mutation(cfg, prog: dict) -> tuple[dict, str]:
    """Move the first programmed leaf to another line of its band (same segment), deterministically."""
    p = copy.deepcopy(prog)
    src = next(iter(p['nets']))
    site = p['nets'][src][0]
    line, seg = src.rsplit('_s', 1)
    band_of = {L: b for b, ls in arch.band_lines(cfg).items() for L in ls}
    others = [L for L in arch.band_lines(cfg)[band_of[line]] if L != line]
    new = f'{others[0]}_s{seg}'
    p['nets'][src].remove(site)
    if not p['nets'][src]:
        del p['nets'][src]
    p['nets'].setdefault(new, []).append(site)
    return p, f'{site}: {src} -> {new}'


def check_prepnr(cfg, root: Path, tag: str, mutations: bool = True) -> dict:
    pd = root / 'programs' / tag
    prog = json.loads((pd / 'prog.json').read_text())
    W = np.load(pd / 'W.npy')
    base = (root / 'netlist' / 'netlist_base.v').read_text()
    (pd / 'programmed_prepnr.v').write_text(programs.program_verilog(base, prog))
    A = to_aag(root, f'programs/{tag}/programmed_prepnr.v', f'programs/{tag}/prepnr.aag')
    ok, lat = simulate(cfg, A, W)
    rec = {'tag': tag, 'netlist': 'pre-PnR (Verilog-level program)', 'matches_numpy': bool(ok), 'latency': lat}
    if mutations:
        rec['oracle_mutation_detected'] = not simulate(cfg, A, oracle_mutation(W))[0]
        pm, desc = program_mutation(cfg, prog)
        (pd / 'programmed_mutant.v').write_text(programs.program_verilog(base, pm))
        Am = to_aag(root, f'programs/{tag}/programmed_mutant.v', f'programs/{tag}/mutant.aag')
        rec['program_mutation'] = desc
        rec['program_mutation_detected'] = not simulate(cfg, Am, W)[0]
        for f in ('programmed_mutant.v', 'mutant.aag'):
            (pd / f).unlink()
    rec['pass'] = rec['matches_numpy'] and rec.get('oracle_mutation_detected', True) and rec.get('program_mutation_detected', True)
    (pd / 'prepnr.aag').unlink()
    return rec


def check_netlist(cfg, root: Path, tag: str, netlist_rel: str, label: str) -> dict:
    """Simulate an already-programmed netlist (e.g. OpenROAD's post-PnR write_verilog) vs numpy + oracle mutation."""
    W = np.load(root / 'programs' / tag / 'W.npy')
    aag_rel = netlist_rel.rsplit('.', 1)[0] + '.aag'
    A = to_aag(root, netlist_rel, aag_rel)
    ok, lat = simulate(cfg, A, W)
    rec = {'tag': tag, 'netlist': label, 'matches_numpy': bool(ok), 'latency': lat,
           'oracle_mutation_detected': not simulate(cfg, A, oracle_mutation(W))[0]}
    rec['pass'] = rec['matches_numpy'] and rec['oracle_mutation_detected']
    (root / aag_rel).unlink()
    return rec
