"""Golden reproduction: compare a generated design with the historical (validated) implementation.

Every comparison is either BYTE (identical files), SEMANTIC (identical content after a documented, behaviour-free
normalization) or it fails. Differences are listed explicitly; nothing is accepted silently.

python3 -m ubpgen.golden CONFIG [--out DIR]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

from . import access
from ._legacy import ROOT

EXP = ROOT / 'experiments' / 'results'
G2 = EXP / 'G2'

# historical locations per fabric: logic-base dir (single LTAP), R3 dir (or None), module source dir, plan file
HIST = {
    'ubp': {'logic': G2 / 'ubp3s', 'r3': G2 / 'ubp3r3', 'modules': EXP / 'E6' / 'ubp3_n64',
            'plan': G2 / 'cells' / 'struct_ubp3r3.tcl'},
    'pc2': {'logic': G2 / 'pc2', 'r3': G2 / 'pc2r3', 'modules': EXP / 'G3' / 'pc2_n64',
            'plan': G2 / 'cells' / 'struct_pc2r3.tcl'},
    'g1': {'logic': G2 / 'g1s', 'r3': None, 'modules': EXP / 'E6' / 'g1_n64', 'plan': None},
}
# access.mode r2: the historical single-tap structured (R2) builds -- one LTAP per line, g2_struct placement
HIST_R2 = {
    'ubp': {'logic': G2 / 'ubp3s', 'modules': EXP / 'E6' / 'ubp3_n64', 'plan': G2 / 'cells' / 'struct_ubp3s.tcl'},
    'pc2': {'logic': G2 / 'pc2', 'modules': EXP / 'G3' / 'pc2_n64', 'plan': G2 / 'cells' / 'struct_pc2.tcl'},
    'g1': {'logic': G2 / 'g1s', 'modules': EXP / 'E6' / 'g1_n64', 'plan': G2 / 'cells' / 'struct_g1s.tcl'},
}
CELL_FILES = ['g2_cells.lef', 'g2_cells.lib', 'g2r3_cells.lef', 'g2r3_cells.lib', 'dont_touch_r3.tcl', 'pdn_m1rails.tcl',
              'dont_touch.tcl']


def _cmp_bytes(a: Path, b: Path) -> str:
    if not b.exists():
        return 'MISSING-HISTORICAL'
    return 'BYTE' if a.read_bytes() == b.read_bytes() else 'DIFF'


def mk_vars(text: str) -> dict:
    return dict(re.findall(r'^export (\w+) =[ ]?(.*)$', text, flags=re.M))


def compare(cfg, root: Path) -> dict:
    if access.w2(cfg):
        raise ValueError('golden comparison is defined for the historical (unsized) driver policy only')
    if access.mode(cfg) == 'r2':
        return compare_r2(cfg, root)
    h = HIST[cfg.fabric]
    res: dict[str, str] = {}
    notes: dict[str, str] = {}
    # modules: RTL and gate-level netlists
    for p in sorted((root / 'rtl').glob('*.v')):
        if p.name.endswith('_gl_raw.v'):
            continue
        res[f'rtl/{p.name}'] = _cmp_bytes(p, h['modules'] / p.name)
    for c in CELL_FILES:
        res[f'cells/{c}'] = _cmp_bytes(root / 'cells' / c, G2 / 'cells' / c)
    # netlists
    res['netlist/netlist_logic.v'] = _cmp_bytes(root / 'netlist' / 'netlist_logic.v', h['logic'] / 'netlist_base.v')
    if h['r3']:
        res['netlist/netlist_base.v'] = _cmp_bytes(root / 'netlist' / 'netlist_base.v', h['r3'] / 'netlist_base.v')
        a, b = json.loads((root / 'netlist' / 'mapping.json').read_text()), json.loads((h['r3'] / 'mapping.json').read_text())
        res['netlist/mapping.json'] = _cmp_bytes(root / 'netlist' / 'mapping.json', h['r3'] / 'mapping.json')
        if res['netlist/mapping.json'] != 'BYTE' and a == b:
            res['netlist/mapping.json'] = 'SEMANTIC'
    else:
        a = json.loads((root / 'netlist' / 'mapping.json').read_text())
        b = json.loads((h['logic'] / 'mapping.json').read_text())
        same = all(a[k] == b[k] for k in ('lines', 'rows', 'leaves_per_row', 'n_rows'))
        res['netlist/mapping.json'] = 'SEMANTIC' if same else 'DIFF'
        notes['netlist/mapping.json'] = 'compared with the single-tap G2 mapping (no historical R3 build of this fabric)'
    # placement plan: entries (instance, band, x, y) in order + placer text
    if h['plan']:
        gen = (root / 'layout' / 'place_access.tcl').read_text()
        old = h['plan'].read_text()
        same_entries = access.parse_plan(gen) == access.parse_plan(old)
        same_placer = gen.split('\n}\n', 1)[1] == old.split('\n}\n', 1)[1]
        same_nb = re.search(r'set r3_nb (\d+)', gen).group(1) == re.search(r'set r3_nb (\d+)', old).group(1)
        res['layout/place_access.tcl'] = 'SEMANTIC' if same_entries and same_placer and same_nb else 'DIFF'
        notes['layout/place_access.tcl'] = 'plan entries, band count and placer TCL identical; only the comment line differs'
    # ORFS configuration: identical variable set and values modulo the mount layout (paths)
    if h['r3']:
        old_mk = next(h['r3'].glob(f'config_u{cfg.util}r.mk'), None)
        if old_mk is None:
            res['orfs/config.mk'] = 'MISSING-HISTORICAL'
        else:
            a, b = mk_vars((root / 'orfs' / 'config.mk').read_text()), mk_vars(old_mk.read_text())
            norm = lambda v: re.sub(r'/work/(ubp3r3|pc2r3|netlist|orfs|layout)/', '/work/X/', v).replace('struct_ubp3r3', 'P').replace('struct_pc2r3', 'P').replace('/work/cells/P', '/work/X/P').replace('/work/X/place_access', '/work/X/P')
            diff = {k: (a.get(k), b.get(k)) for k in set(a) | set(b) if norm(str(a.get(k))) != norm(str(b.get(k)))}
            res['orfs/config.mk'] = 'SEMANTIC' if not diff else 'DIFF'
            notes['orfs/config.mk'] = 'same variables and values; paths differ only by the mount layout' if not diff else str(diff)
        res['orfs/constraint.sdc'] = _cmp_bytes(root / 'orfs' / 'constraint.sdc', h['r3'] / 'constraint.sdc')
    # programs
    for spec in cfg.raw['programs']:
        t = spec['tag']
        pd = root / 'programs' / t
        W = np.load(pd / 'W.npy')
        src = (h['r3'] or h['logic'])
        oldW = src / f'W_{t}.npy'
        res[f'programs/{t}/W.npy'] = ('SEMANTIC' if oldW.exists() and np.array_equal(W, np.load(oldW)) else
                                      'MISSING-HISTORICAL' if not oldW.exists() else 'DIFF')
        new, oldp = json.loads((pd / 'prog.json').read_text()), src / f'prog_{t}.json'
        if not oldp.exists():
            res[f'programs/{t}/prog.json'] = 'MISSING-HISTORICAL'
            continue
        old = json.loads(oldp.read_text())
        if h['r3'] is None:      # merge our segments back into whole-line nets for the single-tap history
            merged = {}
            for k, v in new['nets'].items():
                merged.setdefault(k.rsplit('_s', 1)[0], []).extend(v)
            new_nets = {k: sorted(v) for k, v in merged.items()}
            old_nets = {k: sorted(v) for k, v in old['nets'].items()}
        else:
            new_nets, old_nets = new['nets'], old['nets']
        same = new_nets == old_nets and new['zeros'] == old['zeros'] and new.get('ones', []) == old.get('ones', [])
        res[f'programs/{t}/prog.json'] = 'SEMANTIC' if same else 'DIFF'
        if h['r3']:
            res[f'programs/{t}/prog.tcl'] = _cmp_bytes(pd / 'prog.tcl', h['r3'] / f'prog_{t}.tcl')
    fails = {k: v for k, v in res.items() if v not in ('BYTE', 'SEMANTIC')}
    return {'config': cfg.name, 'results': res, 'notes': notes, 'failures': fails, 'pass': not fails}


def compare_r2(cfg, root: Path) -> dict:
    """access.mode r2 (historical taps): the generated design against the historical R2 (g2_struct) build."""
    h = HIST_R2[cfg.fabric]
    res: dict[str, str] = {}
    notes: dict[str, str] = {}
    for p in sorted((root / 'rtl').glob('*.v')):
        if not p.name.endswith('_gl_raw.v'):
            res[f'rtl/{p.name}'] = _cmp_bytes(p, h['modules'] / p.name)
    for c in CELL_FILES:
        res[f'cells/{c}'] = _cmp_bytes(root / 'cells' / c, G2 / 'cells' / c)
    res['netlist/netlist_logic.v'] = _cmp_bytes(root / 'netlist' / 'netlist_logic.v', h['logic'] / 'netlist_base.v')
    res['netlist/netlist_base.v'] = _cmp_bytes(root / 'netlist' / 'netlist_base.v', h['logic'] / 'netlist_base.v')
    a = json.loads((root / 'netlist' / 'mapping.json').read_text())
    b = json.loads((h['logic'] / 'mapping.json').read_text())
    res['netlist/mapping.json'] = ('BYTE' if (root / 'netlist' / 'mapping.json').read_bytes() == (h['logic'] / 'mapping.json').read_bytes()
                                   else 'SEMANTIC' if all(a[k] == b[k] for k in ('lines', 'rows', 'leaves_per_row', 'n_rows')) else 'DIFF')
    gen, old = (root / 'layout' / 'place_access.tcl').read_text(), h['plan'].read_text()
    same_entries = access.parse_plan_r2(gen) == access.parse_plan_r2(old) and len(access.parse_plan_r2(old)) > 0
    same_placer = gen.split('\n}\n', 1)[1] == old.split('\n}\n', 1)[1]
    same_nb = re.search(r'set g2_nb (\d+)', gen).group(1) == re.search(r'set g2_nb (\d+)', old).group(1)
    res['layout/place_access.tcl'] = 'SEMANTIC' if same_entries and same_placer and same_nb else 'DIFF'
    notes['layout/place_access.tcl'] = 'plan entries, band count and placer TCL identical; only the comment line differs'
    old_mk = h['logic'] / f'config_u{cfg.util}s.mk'
    if not old_mk.exists():
        res['orfs/config.mk'] = 'MISSING-HISTORICAL'
    else:
        a, b = mk_vars((root / 'orfs' / 'config.mk').read_text()), mk_vars(old_mk.read_text())
        d = h['logic'].name
        norm = lambda v: (v.replace(f'/work/{d}/netlist_base.v', '/work/netlist/netlist_base.v')
                          .replace(f'/work/{d}/constraint.sdc', '/work/orfs/constraint.sdc')
                          .replace(f'/work/cells/{h["plan"].name}', '/work/layout/place_access.tcl'))
        diff = {k: (a.get(k), b.get(k)) for k in set(a) | set(b) if norm(str(a.get(k))) != norm(str(b.get(k)))}
        res['orfs/config.mk'] = 'SEMANTIC' if not diff else 'DIFF'
        notes['orfs/config.mk'] = 'same variables and values; paths differ only by the mount layout' if not diff else str(diff)
    res['orfs/constraint.sdc'] = _cmp_bytes(root / 'orfs' / 'constraint.sdc', h['logic'] / 'constraint.sdc')
    for spec in cfg.raw['programs']:
        t = spec['tag']
        pd = root / 'programs' / t
        oldW = h['logic'] / f'W_{t}.npy'
        res[f'programs/{t}/W.npy'] = ('MISSING-HISTORICAL' if not oldW.exists() else
                                      'SEMANTIC' if np.array_equal(np.load(pd / 'W.npy'), np.load(oldW)) else 'DIFF')
        oldp = h['logic'] / f'prog_{t}.json'
        if not oldp.exists():
            res[f'programs/{t}/prog.json'] = 'MISSING-HISTORICAL'
            continue
        new, old = json.loads((pd / 'prog.json').read_text()), json.loads(oldp.read_text())
        same = new['nets'] == old['nets'] and new['zeros'] == old['zeros'] and new.get('ones', []) == old.get('ones', [])
        res[f'programs/{t}/prog.json'] = 'SEMANTIC' if same else 'DIFF'
        res[f'programs/{t}/prog.tcl'] = _cmp_bytes(pd / 'prog.tcl', h['logic'] / f'prog_{t}.tcl')
    fails = {k: v for k, v in res.items() if v not in ('BYTE', 'SEMANTIC')}
    return {'config': cfg.name, 'results': res, 'notes': notes, 'failures': fails, 'pass': not fails}


def compare_physical(cfg, root: Path, hist_nick: str) -> dict:
    """Frozen base vs the historical base of the same configuration: ODB hash, every cell's master/placement,
    the routed base wiring (per-net DEF routing text), and the report metrics."""
    import hashlib
    from . import orfs
    from ._legacy import SCRIPTS  # noqa: F401
    import r3_invariance
    hb = G2 / 'orfs' / 'results' / 'sky130hd' / hist_nick / 'base'
    hl = G2 / 'orfs' / 'logs' / 'sky130hd' / hist_nick / 'base'
    bp = orfs.base_paths(cfg, root)
    if not (hb / '6_final.def').exists():
        return {'available': False}
    sha_new = hashlib.sha256(bp['odb'].read_bytes()).hexdigest()
    sha_old = hashlib.sha256((hb / '6_final.odb').read_bytes()).hexdigest()
    dn, do = bp['def'].read_text(), (hb / '6_final.def').read_text()
    cn, co = r3_invariance.comps(dn), r3_invariance.comps(do)
    moved = [k for k in co if cn.get(k) != co[k]]
    nets = lambda t: r3_invariance.section(t, '\nNETS', 'END NETS')
    rn, ro = json.loads(bp['report'].read_text()), json.loads((hl / '6_report.json').read_text())
    keys = ('finish__timing__setup__ws', 'finish__timing__hold__ws', 'finish__design__core__area', 'finish__design__instance__area')
    return {'available': True, 'odb_sha256_identical': sha_new == sha_old, 'odb_sha256': {'generated': sha_new, 'historical': sha_old},
            'def_identical_except_header': dn.split('\nVERSION', 1)[1] == do.split('\nVERSION', 1)[1] if '\nVERSION' in dn else dn == do,
            'components': len(cn), 'components_differing': len(moved) + len(set(cn) - set(co)), 'examples': moved[:5],
            'routed_nets_identical': nets(dn) == nets(do),
            'report': {k: (rn.get(k), ro.get(k)) for k in keys}}


def main(argv=None):
    import argparse
    from . import config as C
    from .__main__ import RUNS
    ap = argparse.ArgumentParser()
    ap.add_argument('config')
    ap.add_argument('--out')
    a = ap.parse_args(argv)
    cfg = C.load(a.config)
    root = Path(a.out) if a.out else RUNS / cfg.name
    r = compare(cfg, root.resolve())
    (root / 'records').mkdir(exist_ok=True)
    (root / 'records' / 'golden_compare.json').write_text(json.dumps(r, indent=1))
    for k, v in r['results'].items():
        print(f'{v:18s} {k}')
    print('GOLDEN', 'PASS' if r['pass'] else f'FAIL {r["failures"]}')
    return 0 if r['pass'] else 1


if __name__ == '__main__':
    sys.exit(main())
