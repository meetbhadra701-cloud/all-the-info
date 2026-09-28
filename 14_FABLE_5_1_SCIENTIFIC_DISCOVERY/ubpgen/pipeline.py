"""Configuration -> generation -> verification -> physical experiment -> metrics.

Output directory layout (one directory per configuration, mounted at /work for every EDA step):
  config.json            resolved configuration (all defaults explicit)
  generation.json        provenance + structural counts + sha256 of every generated file
  rtl/                   module RTL, Yosys logs, gate-level module netlists (*_gl.v)
  cells/                 via sites, taps (LEF/Liberty), dont_touch hook, PDN
  netlist/               top_base.v, netlist_logic.v (one abstract tap per line), netlist_base.v (R3 access), mapping.json
  layout/place_access.tcl  W-blind placement plan + placer (ORFS POST_PDN_TCL)
  orfs/                  config.mk, constraint.sdc
  programs/<tag>/        W.npy, weights.json (provenance), prog.json, prog.tcl; after runs: pnr_*.log, *.def, *.v
  physical/              ORFS work tree, base log, base_odb.sha256
  records/               verify.jsonl, physical.jsonl, base.json (one provenance-stamped JSON record per event)
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from . import access, arch, drivers, invariance, netlist, orfs, programs, provenance, rtl, signoff, verify
from .config import Config

GENERATED = ('rtl', 'cells', 'netlist', 'layout', 'orfs', 'programs')


def _append(root: Path, name: str, rec: dict):
    (root / 'records').mkdir(exist_ok=True)
    with open(root / 'records' / name, 'a') as fh:
        fh.write(json.dumps(rec) + '\n')


def file_hashes(root: Path) -> dict:
    out = {}
    for d in GENERATED:
        for p in sorted((root / d).rglob('*')):
            if p.is_file() and not p.name.startswith('pnr') and p.suffix not in ('.log', '.aag') and 'programmed' not in p.name:
                out[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def generate(cfg: Config, root: Path, config_dir: Path | None = None) -> dict:
    """Deterministic: the same configuration produces byte-identical files (see tests)."""
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    orfs.check_image(cfg)
    access.write_cells(cfg, root)
    mods = rtl.synthesize(cfg, root / 'rtl')
    netlist.link(cfg, root, mods)
    sizing = None
    if access.w2(cfg):                     # Week-2 rule: resolve (or check) the tap class before the taps exist
        sizing = drivers.resolve(cfg, root)
        want = cfg.raw['drivers']['tap_class']
        if want is not None and want != sizing['class']:
            raise RuntimeError(f"drivers.tap_class {want} differs from the rule's choice {sizing['class']}")
        cfg = cfg.with_overrides(drivers__tap_class=sizing['class'])
        drivers.write_record(root, {'selection': sizing})
    (root / 'config.json').write_text(cfg.to_json() + '\n')
    access.expand(cfg, root)
    netlist.write_mapping(cfg, root)
    access.write_plan(cfg, root)
    orfs.write(cfg, root)
    progs = [programs.write(cfg, root, spec, config_dir) for spec in cfg.raw['programs']]
    gen = provenance.record(cfg, 'generate', {
        'counts': arch.counts(cfg), 'modules': mods, 'programs': progs, 'driver_sizing': sizing,
        'module_facts': rtl.module_plan(cfg)['facts'], 'files': file_hashes(root)})
    (root / 'generation.json').write_text(json.dumps(gen, indent=1))
    return gen


def verify_prepnr(cfg: Config, root: Path, tags=None, mutations=True) -> list[dict]:
    root = root.resolve()
    cfg = resolved(cfg, root)
    out = []
    for spec in cfg.raw['programs']:
        if tags and spec['tag'] not in tags:
            continue
        rec = verify.check_prepnr(cfg, root, spec['tag'], mutations)
        _append(root, 'verify.jsonl', provenance.record(cfg, f'verify-prepnr {spec["tag"]}', {'result': rec}))
        out.append(rec)
    return out


def build_base(cfg: Config, root: Path, prune: bool = False) -> dict:
    root = root.resolve()
    cfg = resolved(cfg, root)
    m = orfs.build_base(cfg, root)
    if access.w2(cfg):     # the pre-registered verification of the tap-class rule on the built geometry
        m['tap_rule_verification'] = drivers.verify_built(cfg, root, orfs.base_paths(cfg, root)['def'])
        drivers.write_record(root, {'verification': m['tap_rule_verification']})
    if prune:
        m['pruned_stage_files'] = orfs.prune_base(cfg, root)
    rec = provenance.record(cfg, 'physical-base', {'result': m})
    (root / 'records').mkdir(exist_ok=True)
    (root / 'records' / 'base.json').write_text(json.dumps(rec, indent=1))
    return m


def resolved(cfg: Config, root: Path) -> Config:
    """The configuration as generated (config.json: the W2 tap class resolved), checked against the given one."""
    p = root.resolve() / 'config.json'
    if not p.exists():
        return cfg
    from .config import resolve
    gen = resolve(json.loads(p.read_text()))
    a, b = json.loads(gen.to_json()), json.loads(cfg.to_json())
    a['drivers']['tap_class'] = b['drivers']['tap_class'] = None
    if a != b:
        raise RuntimeError(f'{p} was generated from a different configuration')
    return gen


def run_signoff(cfg: Config, root: Path, tag: str) -> dict:
    """Merged base + program OpenRCX extraction and tt/ss/ff STA of an already-routed program (appends a record)."""
    root = root.resolve()
    cfg = resolved(cfg, root)
    rec = signoff.run(cfg, root, tag)
    _append(root, 'signoff.jsonl', provenance.record(cfg, f'signoff {tag}', {'result': rec}))
    return rec


def run_program(cfg: Config, root: Path, tag: str, with_signoff: bool = True) -> dict:
    """Route (met4-met5 only), STA, post-PnR functional check, invariance, sign-off -- one record."""
    root = root.resolve()
    cfg = resolved(cfg, root)
    pd = root / 'programs' / tag
    bp = orfs.base_paths(cfg, root)
    sha = (root / 'physical' / 'base_odb.sha256').read_text().split()[0]
    orfs.run_program(cfg, root, tag, 'route')
    orfs.run_program(cfg, root, tag, 'sta')
    rec = {'tag': tag, **orfs.route_metrics(pd), **orfs.sta_metrics(pd)}
    rec['post_pnr'] = verify.check_netlist(cfg, root, tag, f'programs/{tag}/pnr_programmed.v', 'post-PnR (OpenROAD write_verilog)')
    rec['invariance'] = invariance.check(bp['def'], pd / 'pnr_program.def', pd / 'prog.json', bp['odb'], sha)
    rec['pass'] = (rec['drt_final'] == 0 and rec['post_pnr']['pass'] and rec['invariance']['all_invariants_hold'])
    _append(root, 'physical.jsonl', provenance.record(cfg, f'physical-program {tag}', {'result': rec}))
    if with_signoff and rec['drt_final'] == 0:
        rec['signoff'] = run_signoff(cfg, root, tag)
    return rec


def axt(cell_area: float, util: int, cycles: int, t_ns: float) -> float:
    return cell_area / (util / 100) * cycles * t_ns


def summarize(cfg: Config, root: Path, required: list[str] | None = None) -> dict:
    """Latest record per program + A x T under the established (first program) and robust (worst program) rules."""
    root = root.resolve()
    base = json.loads((root / 'records' / 'base.json').read_text())['result']
    recs = {}
    p = root / 'records' / 'physical.jsonl'
    if p.exists():
        for line in p.read_text().splitlines():
            r = json.loads(line)['result']
            recs[r['tag']] = r
    required = required or [s['tag'] for s in cfg.raw['programs']]
    tags = [t for t in required if t in recs]
    cyc = arch.cycles_per_word(cfg)
    clk = cfg.raw['clock_ns']
    out = {'name': cfg.name, 'fabric': cfg.fabric, 'util': cfg.util, 'K': cfg.K, 'base': base, 'programs': recs}
    if tags:
        pw = [recs[t]['prog_setup_ws_ns'] for t in tags]
        t_est = clk - min(base['setup_ws_ns'], pw[0])
        t_rob = clk - min([base['setup_ws_ns']] + pw)
        out.update({'T_established_ns': t_est, 'T_robust_ns': t_rob,
                    'AxT_established': axt(base['cell_area_um2'], cfg.util, cyc, t_est),
                    'AxT_robust': axt(base['cell_area_um2'], cfg.util, cyc, t_rob),
                    'programs_required': required, 'programs_missing': [t for t in required if t not in recs],
                    'all_programs_pass': all(recs[t]['pass'] for t in tags) and len(tags) == len(required)})
    (root / 'records' / 'summary.json').write_text(json.dumps(out, indent=1))
    return out
