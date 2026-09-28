"""Week-2 driver-sizing policy `w2_load_rule` (21_WEEK2_TIMING_CLOSURE.md 1.4).

Tap drivers: the smallest sky130 buf_<k> whose worst (rise, fall) NLDM output transition at input slew S and at the
worst-case W-independent programmable load is <= S (tt). Worst-case load C_wc = (m/K) * C_in(via-site A) + c_met4 *
L_RSMT, where L_RSMT is the rectilinear Steiner length of the tap plus every site of its segment in its band (all sites
of a band share one column), computed from the W-blind plan on the core the design implies (square, area = cell
area / U; fixed point over the tap class). No margin, no detour factor. Uniform per design (the worst tap decides).
Spine drivers: the tap A-pin max_transition = S is enforced physically by the ORFS flow (repair_design); nothing is
chosen here.

resolve()        -> the class, with the full evaluation table (recorded in generation.json / drivers.json);
                    with drivers.post_build_step = 1 the next larger class (the one permitted rebuild)
verify_built()   -> the same computation on the built base's actual geometry (6_final.def)
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

from . import access, arch, liberty, pdk
from ._legacy import LIB, dock
from .config import TAP_CLASSES

C_MET4_PF_PER_UM = 1.48128e-4       # platform setRC.tcl, met4
VSITE_PIN_OFFSET = (0.92, 1.36)     # centre of the via-site A pad (LEF: 0.30..1.54 x 0.80..1.92)
LTAP_AREA = 3.68 * 2.72             # the abstract LTAP of the logic netlist


def site_cap_pf() -> float:
    """Input capacitance of a via-site A pin = sky130 buf_1 A (VSITE_BUF is a buf_1 clone), tt."""
    return liberty.pin_cap(liberty.cell_block(liberty.text('tt'), 'sky130_fd_sc_hd__buf_1'), 'A')


def logic_area(root: Path) -> float:
    """Yosys `stat -liberty` area of netlist_logic.v (standard cells + via sites + one LTAP per line)."""
    p = dock(f"cd netlist && yosys -p 'read_liberty -lib {LIB}; read_liberty -lib /work/cells/g2_cells.lib; read_verilog netlist_logic.v; "
             f"hierarchy -top top; tee -q -o ../netlist/stat_logic.txt stat -top top -liberty {LIB} -liberty /work/cells/g2_cells.lib'", root)
    if p.returncode != 0:
        raise RuntimeError('yosys stat failed:\n' + p.stderr[-2000:])
    txt = (root / 'netlist' / 'stat_logic.txt').read_text()
    return float(re.search(r"Chip area for top module '\\top': ([0-9.]+)", txt).group(1))


def _worst_tap(cfg, W: float, H: float, tap_w: float, sites_xy, taps_xy):
    """Worst tap: max over taps of |x_tap - x_col| + vertical span of (its segment's sites + the tap)."""
    K, m = cfg.K, cfg.m
    seg = m // K
    worst = (0.0, None)
    for name, band, s, tx, ty in taps_xy:
        pts = [sites_xy[(i, band)] for i in range(s * seg, (s + 1) * seg) if (i, band) in sites_xy]
        xc = sum(p[0] for p in pts) / len(pts)
        ys = [p[1] for p in pts] + [ty]
        L = abs(tx - xc) + (max(ys) - min(ys)) + (max(p[0] for p in pts) - min(p[0] for p in pts))
        if L > worst[0]:
            worst = (L, name)
    return worst


def plan_geometry(cfg, side: float, tap_w: float):
    """Pin positions from the W-blind plan fractions on a square core of the given side (um)."""
    bands = arch.band_lines(cfg)
    nb = len(bands)
    bw = side / nb
    sites = {(i, b): ((b + 0.5) * bw, (i + 0.5) / cfg.m * side) for b in bands for i in range(cfg.m)}
    taps = []
    for b, lines in bands.items():
        T = len(lines)
        for t, L in enumerate(lines):
            if access.mode(cfg) == 'r3':   # R3 placer: cell centred at the home x; the pad is in the first two sites
                for s in range(cfg.K):
                    taps.append((f'lt_{L}_s{s}', b, s, (b + (t + 0.5) / T) * bw - tap_w / 2 + 0.46,
                                 (s + (t + 0.5) / T) / cfg.K * side))
            else:   # R2 placer: tap right of the site column (column half-width 0.92 + 0.46 gap); wide pad from +0.30
                taps.append((f'lt_{L}', b, 0, (b + 0.5) * bw + 0.92 + 0.46 + 0.30, (t + 0.5) / T * side))
    return sites, taps


def evaluate(cfg, tap_class: str, a_logic: float, n_lines: int) -> dict:
    n_taps = n_lines * (cfg.K if access.mode(cfg) == 'r3' else 1)
    area = a_logic - n_lines * LTAP_AREA + n_taps * access.tap_sites(tap_class) * access.SITE_AREA
    side = math.sqrt(area / (cfg.util / 100))
    tap_w = access.tap_sites(tap_class) * access.SITE_W
    sites, taps = plan_geometry(cfg, side, tap_w)
    L, name = _worst_tap(cfg, side, side, tap_w, sites, taps)
    S = cfg.raw['drivers']['slew_target_ns']
    c = (cfg.m // cfg.K) * site_cap_pf() + C_MET4_PF_PER_UM * L
    tr = liberty.output_transition(f'sky130_fd_sc_hd__{tap_class}', 'X', S, c, 'tt')
    return {'class': tap_class, 'cell_area_um2': round(area, 1), 'core_side_um': round(side, 2), 'worst_tap': name,
            'L_rsmt_um': round(L, 2), 'sinks': cfg.m // cfg.K, 'C_wc_fF': round(c * 1000, 2),
            'transition_ns': round(tr, 4), 'meets': tr <= S}


def resolve(cfg, root: Path) -> dict:
    """Apply the rule. Returns {'class': ..., 'evaluations': [...], ...}; raises if nothing meets the target."""
    a_logic = logic_area(root)
    n_lines = len(arch.lines(cfg))
    evals = []
    for tc in TAP_CLASSES:
        e = evaluate(cfg, tc, a_logic, n_lines)
        evals.append(e)
        if e['meets']:
            break
    rule_class = next((e['class'] for e in evals if e['meets']), None)
    step = cfg.raw['drivers']['post_build_step']
    chosen = rule_class
    if rule_class is not None and step:
        i = TAP_CLASSES.index(rule_class) + step
        if i >= len(TAP_CLASSES):
            raise RuntimeError(f'w2_load_rule: no class above {rule_class} for the post-build rebuild')
        chosen = TAP_CLASSES[i]
        evals.append(evaluate(cfg, chosen, a_logic, n_lines))
    S = cfg.raw['drivers']['slew_target_ns']
    rec = {'policy': 'w2_load_rule', 'slew_target_ns': S, 'corner': 'tt', 'candidates': list(TAP_CLASSES),
           'load_model': 'C_wc = (m/K) * C_in(VSITE A) + c_met4(setRC) * L_RSMT(tap + all segment sites); no margin',
           'C_in_site_pF': site_cap_pf(), 'c_met4_pF_per_um': C_MET4_PF_PER_UM, 'logic_area_um2': a_logic,
           'evaluations': evals, 'rule_class': rule_class, 'post_build_step': step, 'class': chosen,
           'tap_master': access.tap_master(cfg, chosen) if chosen else None,
           'spine': 'tap A-pin max_transition = S enforced by the ORFS flow repair_design (tt)'}
    if chosen is None:
        raise RuntimeError(f'w2_load_rule: no tap class meets {S} ns: {evals}')
    n = access.tap_sites(chosen)
    rec['tap_cell'] = {'master': rec['tap_master'], 'timing': f'sky130_fd_sc_hd__{chosen} (cloned per corner)',
                       'sites': n, 'pad_sites': access.PAD_SITES, 'buffer_sites': n - access.PAD_SITES,
                       'area_um2': round(n * access.SITE_AREA, 4), 'width_um': round(n * access.SITE_W, 2),
                       'pad': 'single-track met4 pad in the first two sites (r3)' if access.mode(cfg) == 'r3'
                              else 'wide met4 pad 0.30 um from each edge (r2)',
                       'count': n_lines * (cfg.K if access.mode(cfg) == 'r3' else 1)}
    rec['physical_constraints'] = {
        'tap_input_max_transition_ns': S, 'enforced_by': 'ORFS repair_design (3_4 resize, 5_1 global route; tt)',
        'tap_and_site_instances': 'dont_touch (FIXED base; POST_SYNTH hook), FIRM-placed by the W-blind plan',
        'utilization_pct': cfg.util, 'clock_ns': cfg.raw['clock_ns'], 'base_layers': 'met1-met3',
        'program_layers': 'met4-met5'}
    rec['signoff_libraries'] = pdk.provenance()
    return rec


COMP = re.compile(r'^\s*-\s+(\S+)\s+(\S+)\s+\+\s+(?:PLACED|FIRM|FIXED)\s+\(\s*(-?\d+)\s+(-?\d+)\s*\)\s+(\S+)', re.M)


def verify_built(cfg, root: Path, base_def: Path) -> dict:
    """The rule on the built base's actual pin geometry (W-independent)."""
    d = base_def.read_text()
    u = int(re.search(r'UNITS DISTANCE MICRONS (\d+)', d).group(1))
    comps = COMP.findall(d[d.index('\nCOMPONENTS'):d.index('END COMPONENTS')])
    tc = cfg.raw['drivers']['tap_class']
    tap_w = access.tap_sites(tc) * access.SITE_W
    sites, taps = {}, []
    for n, mst, x, y, o in comps:
        x, y = int(x) / u, int(y) / u
        m = re.match(r'vs_(\d+)_(\d+)$', n)
        if m:
            sites[(int(m.group(1)), int(m.group(2)))] = (x + VSITE_PIN_OFFSET[0], y + VSITE_PIN_OFFSET[1])
        elif n.startswith('lt_'):
            line = n[3:].rsplit('_s', 1)[0] if access.mode(cfg) == 'r3' else n[3:]
            s = int(n.rsplit('_s', 1)[1]) if access.mode(cfg) == 'r3' else 0
            band = int((arch.LINE_RE[cfg.fabric].match(line)).group(2))
            taps.append((n, band, s, x, y, mst))
    taps_xy = []
    for n, band, s, x, y, mst in taps:
        col = sum(sites[(i, band)][0] for i in range(cfg.m)) / cfg.m
        if access.mode(cfg) == 'r3':
            tx = x + 0.46
        else:
            tx = min(max(col, x + 0.30), x + tap_w - 0.30)
        taps_xy.append((n, band, s, tx, y + 1.36))
    L, name = _worst_tap(cfg, 0, 0, tap_w, sites, taps_xy)
    S = cfg.raw['drivers']['slew_target_ns']
    c = (cfg.m // cfg.K) * site_cap_pf() + C_MET4_PF_PER_UM * L
    tr = liberty.output_transition(f'sky130_fd_sc_hd__{tc}', 'X', S, c, 'tt')
    masters = sorted({t[5] for t in taps})
    return {'class': tc, 'tap_masters_in_def': masters, 'worst_tap': name, 'L_rsmt_um': round(L, 2),
            'C_wc_fF': round(c * 1000, 2), 'transition_ns': round(tr, 4), 'meets': tr <= S,
            'masters_ok': masters == [access.tap_master(cfg)]}


def write_record(root: Path, rec: dict, name: str = 'drivers.json'):
    (root / 'records').mkdir(exist_ok=True)
    p = root / 'records' / name
    old = json.loads(p.read_text()) if p.exists() else {}
    old.update(rec)
    p.write_text(json.dumps(old, indent=1))
