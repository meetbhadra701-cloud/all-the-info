"""Independent functional verification: gate-level netlist -> AIGER -> our own cycle simulator vs an oracle, with
mandatory mutation controls.

Origin: experiments/scripts/e6_build.py (read_aag_seq, the cycle loop of sim_seq) and ubpgen/verify.py (to_aag,
the two mutation controls). Decoupled: stimulus, oracle and output decoding are callables; nothing assumes UBP.

The contract that kept every UBP correctness claim honest:
  1. the design under test is simulated by code that shares nothing with the generator (Yosys maps the netlist with
     the Liberty cell functions; our simulator evaluates the AIG);
  2. the reference is an independent oracle (NumPy for UBP);
  3. the check must FAIL on every mutation control -- an oracle mutation (same circuit, perturbed reference) and a
     design mutation (perturbed circuit, same reference). A check that passes a mutant is blind, and its "pass" means
     nothing: verdict() then reports FAIL even if the unmutated comparison matched.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Callable

import numpy as np

YOSYS_TO_AAG = ("yosys -q -p '{libs} read_verilog {netlist}; hierarchy -top {top}; flatten; synth -top {top} -noabc; "
                "dffunmap; setundef -zero -init; aigmap; opt_clean; write_aiger -ascii -symbols {aag}'")


def netlist_to_aag(image: str, root: Path, netlist_rel: str, aag_rel: str, libs: list[str], top: str = 'top') -> Path:
    """Yosys (in the image) maps a gate-level netlist through the Liberty cell functions to an ASCII AIGER model.
    libs: paths as seen in the container (root is /work)."""
    rl = ' '.join(f'read_liberty -ignore_miss_func {lib};' for lib in libs)
    cmd = YOSYS_TO_AAG.format(libs=rl, netlist=netlist_rel, top=top, aag=aag_rel)
    p = subprocess.run(['docker', 'run', '--rm', '-v', f'{Path(root).resolve()}:/work', '-w', '/work', image, 'bash', '-c', cmd],
                       capture_output=True, text=True, timeout=7200)
    if p.returncode != 0:
        raise RuntimeError('yosys AIGER export failed:\n' + p.stderr[-3000:])
    return Path(root) / aag_rel


def read_aag_seq(path: Path):
    """ASCII AIGER with latches and symbols -> (M, inputs, latches[(cur, next, init)], outputs, ands, sym_in, sym_out)."""
    lines = Path(path).read_text().splitlines()
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


def simulate(aag, cycles: int, drive: Callable[[int, str], bool]) -> dict[str, np.ndarray]:
    """Cycle-accurate simulation of a sequential AIG. drive(cycle, input_symbol) -> bool. Per cycle: inputs, latch
    outputs, AND gates in file order (AIGER guarantees topological order), outputs sampled, latches updated.
    Returns {output_symbol: bool array over cycles}."""
    M, ins, lat, outs, ands, sym_in, sym_out = aag
    val = np.zeros(M + 1, dtype=bool)
    state = {cur >> 1: bool(init) for cur, nxt, init in lat}

    def lv(lit):
        v = val[lit >> 1]
        return (not v) if lit & 1 else bool(v)
    trace = {sym_out[k]: np.zeros(cycles, dtype=bool) for k in range(len(outs))}
    for cyc in range(cycles):
        for k, lit in enumerate(ins):
            val[lit >> 1] = bool(drive(cyc, sym_in[k]))
        for cur, s in state.items():
            val[cur] = s
        for lhs, r0, r1 in ands:
            val[lhs >> 1] = lv(r0) and lv(r1)
        for k, o in enumerate(outs):
            trace[sym_out[k]][cyc] = lv(o)
        state = {cur >> 1: lv(nxt) for cur, nxt, init in lat}
    return trace


def bus(trace: dict[str, np.ndarray], name: str) -> np.ndarray:
    """Output bits of bus `name[i]` as an int array [cycles, width] (missing indices are 0)."""
    idx = {int(k[len(name) + 1:-1]): v for k, v in trace.items() if k.startswith(name + '[')}
    if not idx:
        return np.zeros((len(next(iter(trace.values()))), 0), dtype=np.int64)
    out = np.zeros((len(next(iter(idx.values()))), max(idx) + 1), dtype=np.int64)
    for i, v in idx.items():
        out[:, i] = v
    return out


def serial_word(bits: np.ndarray, signed: bool = True) -> int:
    """LSB-first bit-serial word -> integer (two's complement if signed)."""
    v = 0
    for t, b in enumerate(bits):
        v |= int(b) << t
    if signed and len(bits) and v >> (len(bits) - 1):
        v -= 1 << len(bits)
    return v


# ------------------------------------------------------------------------------------------------ mutation controls
def verdict(matches: bool, mutants: dict[str, bool]) -> dict:
    """matches: the design agrees with the oracle. mutants: {description: check PASSED on that mutant}.
    PASS requires agreement AND every mutant rejected; a blind check is reported as such."""
    blind = sorted(k for k, passed in mutants.items() if passed)
    return {'matches_oracle': bool(matches), 'mutants': len(mutants), 'mutants_detected': len(mutants) - len(blind),
            'blind_to': blind, 'pass': bool(matches) and not blind and len(mutants) > 0}


def checked(check: Callable[..., bool], design, reference, design_mutants: dict = None, reference_mutants: dict = None) -> dict:
    """Run check(design, reference) and the same check on every mutant; at least one mutant is required."""
    muts = {}
    for k, d in (design_mutants or {}).items():
        muts[f'design:{k}'] = bool(check(d, reference))
    for k, r in (reference_mutants or {}).items():
        muts[f'reference:{k}'] = bool(check(design, r))
    return verdict(check(design, reference), muts)
