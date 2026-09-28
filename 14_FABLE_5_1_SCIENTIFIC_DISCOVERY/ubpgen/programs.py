"""Weight programs: W (seeded or from file) -> the via program of the fixed base.

A program is exactly:
  * one programmable net per used (line, segment): {lt_<line>_s<seg>.Z, vs_i_k.A for every leaf of that line in
    that row segment} -- routed later on met4/met5 only;
  * master swaps of identical footprint: VSITE_BUF -> VSITE_ZERO for zero leaves, VSITE_ZERO -> VSITE_ONE for
    pc2 constant bits equal to 1.
Nothing else in the base changes.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from . import arch
from ._legacy import SCRIPTS  # noqa: F401  (path set-up for g2_verify)

import g2_verify  # noqa: E402  (validated Verilog-level programming, reused)


def make_weights(cfg, spec: dict, base_dir: Path | None = None) -> np.ndarray:
    if 'file' in spec:
        p = Path(spec['file'])
        if not p.is_absolute() and base_dir is not None:
            p = base_dir / p
        W = np.load(p).astype(np.int8)
    else:
        rng = np.random.default_rng(spec['seed'])
        p0 = spec['p0']
        pw = [(1 - p0) / 2, p0, (1 - p0) / 2]
        vals = np.array([-1, 0, 1], dtype=np.int8)
        if spec.get('same_rows'):
            W = np.repeat(rng.choice(vals, size=(1, cfg.n), p=pw), cfg.m, axis=0)
        else:
            W = rng.choice(vals, size=(cfg.m, cfg.n), p=pw)
    arch.check_weights(cfg, W)
    return W


def weight_provenance(spec: dict, W: np.ndarray) -> dict:
    rec = {k: v for k, v in spec.items()}
    rec['generator'] = ('numpy.random.default_rng(seed).choice([-1,0,1], p=[(1-p0)/2, p0, (1-p0)/2])'
                        + (' (one row repeated)' if spec.get('same_rows') else '')) if 'seed' in spec else 'file'
    rec['numpy_version'] = np.__version__
    rec['shape'] = list(W.shape)
    rec['sha256_int8'] = hashlib.sha256(np.ascontiguousarray(W.astype(np.int8)).tobytes()).hexdigest()
    rec['density'] = {'neg': float((W < 0).mean()), 'zero': float((W == 0).mean()), 'pos': float((W > 0).mean())}
    return rec


def derive(cfg, W: np.ndarray, tag: str, spec: dict) -> dict:
    """Program from W. Leaves are scanned row-major; nets are split by row segment (historical ordering)."""
    arch.check_weights(cfg, W)
    whole, zeros, ones = {}, [], []
    for i in range(cfg.m):
        for k in range(arch.leaves_per_row(cfg)):
            L = arch.leaf_source(cfg, W, i, k)
            if L is None:
                zeros.append(f'vs_{i}_{k}')
            else:
                whole.setdefault(L, []).append(f'vs_{i}_{k}')
        if cfg.fabric == 'pc2':
            c = arch.row_constant(W, i)
            ones += [f'cst_{i}_{b}' for b in range(arch.CONST_BITS) if (c >> b) & 1]
    seg = cfg.m // cfg.K
    nets = {}
    for L, sites in whole.items():
        for s in sites:
            nets.setdefault(f'{L}_s{int(s.split("_")[1]) // seg}', []).append(s)
    prog = {'tag': tag, **{k: v for k, v in spec.items() if k != 'tag'}, 'nets': nets, 'zeros': zeros, 'ones': ones,
            'n_prog_nets': len(nets), 'n_prog_pins': sum(len(v) for v in nets.values()) + len(nets)}
    return prog


def program_tcl(prog: dict) -> str:
    T = ['proc g2_apply_program {} {', '  set blk [ord::get_db_block]', '  set db [ord::get_db]',
         '  set mz [$db findMaster VSITE_ZERO]', '  set mo [$db findMaster VSITE_ONE]']
    T += [f'  [$blk findInst {z}] swapMaster $mz' for z in prog['zeros']]
    T += [f'  [$blk findInst {o}] swapMaster $mo' for o in prog.get('ones', [])]
    for src, sites in prog['nets'].items():
        T.append(f'  set net [odb::dbNet_create $blk pgm_{src}]')
        T.append(f'  [[$blk findInst lt_{src}] findITerm Z] connect $net')
        T += [f'  [[$blk findInst {s}] findITerm A] connect $net' for s in sites]
    T.append('}')
    return '\n'.join(T) + '\n'


def program_verilog(base_netlist: str, prog: dict) -> str:
    """Apply a program at the Verilog level (pre-PnR functional check). Reuses the validated g2_verify routine,
    whose tap pattern `LTAP2? lt_<net>` matches the per-segment tap names lt_<line>_s<seg>."""
    return g2_verify.program_verilog(base_netlist, prog)


def write(cfg, root: Path, spec: dict, base_dir: Path | None = None) -> dict:
    tag = spec['tag']
    pd = root / 'programs' / tag
    pd.mkdir(parents=True, exist_ok=True)
    W = make_weights(cfg, spec, base_dir)
    np.save(pd / 'W.npy', W)
    prog = derive(cfg, W, tag, {k: v for k, v in spec.items() if k != 'file'})
    (pd / 'prog.json').write_text(json.dumps(prog))
    (pd / 'prog.tcl').write_text(program_tcl(prog))
    prov = weight_provenance(spec, W)
    (pd / 'weights.json').write_text(json.dumps(prov, indent=1))
    return {'tag': tag, 'n_prog_nets': prog['n_prog_nets'], 'n_prog_pins': prog['n_prog_pins'],
            'zeros': len(prog['zeros']), 'ones': len(prog['ones']), 'W_sha256': prov['sha256_int8']}
