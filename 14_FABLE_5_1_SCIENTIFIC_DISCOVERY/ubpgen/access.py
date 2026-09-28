"""Physical access: line taps, the custom cells, and the W-blind placement plans.

Access modes (config access.mode):
  r3 (validated UBP access): every line L gets K taps lt_L_s0..s{K-1} on the SAME base net L; the base routes the line
     as a W-independent spine (met1-met3) through its taps; rows split into K segments, a program connects a site in
     segment s only to its line's tap in segment s. Plan (FIRM before global placement, ORFS POST_PDN_TCL): one band
     per block (ubp) or input (g1, pc2); sites in one track-aligned column at the band centre, row i at (i + 0.5)/m;
     tap (line t of the band's T lines, segment s) at height (s + (t + 0.5)/T)/K, x = (t + 0.5)/T of the band.
  r2 (the historical per-input baselines' access): one tap lt_L per line (K = 1), placed by the R2 structured placer
     (taps right of the band's site column at heights (t + 0.5)/T).
Tap cells (config drivers.policy):
  historical: r3 -> LTAP2 (2 sites, buf_4 timing), r2 -> LTAP (8 sites, buf_4 timing) -- validated, bit-exact.
  w2_load_rule: physical taps (Week 2): LTAPB<k> (r3, single-track met4 pad) / LTAPBW<k> (r2, wide met4 pad like
     LTAP): area = 2-site via/pad + the sites of sky130 buf_<k>, timing = buf_<k> cloned per corner, and pin A carries
     max_transition = drivers.slew_target_ns (enforced on the spine by the flow's repair_design).
Cell text (LTAP2 LEF, via-site LEF/Liberty) and both placers are the validated ones (_legacy).
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

from . import arch, liberty, pdk
from ._legacy import CELL_LEF, DONT_TOUCH_R3, LTAP2_LEF, R2_PLACER, R3_PLACER, extract_cell, g2_cells_main, lib_cell, r3_build
from .config import TAP_CLASSES

TAP_RE = re.compile(r'  LTAP (lt_(\w+)) \(\n    \.A\((\w+)\)\n  \);\n')
RES = Path(__file__).resolve().parent / 'resources'
SITE_W, ROW_H = 0.46, 2.72
SITE_AREA = SITE_W * ROW_H          # 1.2512 um^2
PAD_SITES = 2                       # the via stack + met4 pad of a tap (LTAP2's footprint)
CORNERS = ('tt', 'ss', 'ff')


def mode(cfg) -> str:
    return cfg.raw['access']['mode']


def w2(cfg) -> bool:
    return cfg.raw['drivers']['policy'] == 'w2_load_rule'


def tap_master(cfg, tap_class: str | None = None) -> str:
    if not w2(cfg):
        return 'LTAP2' if mode(cfg) == 'r3' else 'LTAP'
    k = (tap_class or cfg.raw['drivers']['tap_class']).split('_')[1]
    return f'LTAPB{k}' if mode(cfg) == 'r3' else f'LTAPBW{k}'


def tap_names(cfg, line: str) -> list[str]:
    return [f'lt_{line}_s{s}' for s in range(cfg.K)] if mode(cfg) == 'r3' else [f'lt_{line}']


def buf_sites(k: str) -> int:
    """Sites of sky130_fd_sc_hd__<k> (from the tt Liberty area)."""
    return round(liberty.area(liberty.cell_block(liberty.text('tt'), f'sky130_fd_sc_hd__{k}')) / SITE_AREA)


def tap_sites(tap_class: str) -> int:
    return PAD_SITES + buf_sites(tap_class)


# ------------------------------------------------------------------------------------------------ netlist
def expand(cfg, root: Path) -> Path:
    """netlist_logic.v (one abstract LTAP per line) -> netlist_base.v (the configured taps)."""
    nd = root / 'netlist'
    net = (nd / 'netlist_logic.v').read_text()
    n_old = len(TAP_RE.findall(net))
    master = tap_master(cfg)

    def rep(m):
        return ''.join(f'  {master} {name} (\n    .A({m.group(3)})\n  );\n' for name in tap_names(cfg, m.group(2)))
    net2 = TAP_RE.sub(rep, net)
    n_lines = len(arch.lines(cfg))
    n_taps = n_lines * (cfg.K if mode(cfg) == 'r3' else 1)
    if not (n_old == n_lines and net2.count(f'  {master} lt_') == n_taps and (master == 'LTAP' or ' LTAP lt_' not in net2)):
        raise RuntimeError(f'access expansion: {n_old} taps found for {n_lines} lines')
    out = nd / 'netlist_base.v'
    out.write_text(net2)
    return out


# ------------------------------------------------------------------------------------------------ cells
def _lib_header(src: str, name: str) -> str:
    header = src[:re.search(r'\n\s*cell\s*\(', src).start()]
    return re.sub(r'library\s*\(\s*"?[\w]+"?\s*\)', f'library ("{name}")', header, count=1)


def clone_g2_lib(src: str, libname: str) -> str:
    """The via-site / LTAP Liberty of g2_cells.main, from any corner library (tt reproduces g2_cells.lib)."""
    buf1, buf4 = extract_cell(src, 'sky130_fd_sc_hd__buf_1'), extract_cell(src, 'sky130_fd_sc_hd__buf_4')
    cells = [lib_cell(buf1, 'VSITE_BUF', 1.84 * 2.72, {'X': 'Z'}), lib_cell(buf1, 'VSITE_ZERO', 1.84 * 2.72, {'X': 'Z'}),
             lib_cell(buf4, 'LTAP', 3.68 * 2.72, {'X': 'Z'}), lib_cell(buf1, 'VSITE_ONE', 1.84 * 2.72, {'X': 'Z'})]
    for k, fn in ((1, '0'), (3, '1')):
        z = re.sub(r'(?<!_)function\s*:\s*"[^"]*"', f'function : "{fn}"', cells[k])
        z = re.sub(r'timing\s*\(\s*\)\s*\{', 'timing_removed () {', z)
        cells[k] = re.sub(r'timing_removed \(\) \{.*?\n\s{12}\}\n', '', z, flags=re.S)
    for k, nm in enumerate(('VSITE_BUF', 'VSITE_ZERO', 'LTAP', 'VSITE_ONE')):
        cells[k] = re.sub(r'cell_footprint\s*:\s*"[^"]*"\s*;', f'cell_footprint : "g2_{nm.lower()}";\n        dont_use : true;', cells[k])
    return _lib_header(src, libname) + '\n' + '\n'.join(cells) + '\n}\n'


def clone_g2r3_lib(src: str, libname: str) -> str:
    """The LTAP2 Liberty of r3_build.cells, from any corner library (tt reproduces g2r3_cells.lib)."""
    cell = lib_cell(extract_cell(src, 'sky130_fd_sc_hd__buf_4'), 'LTAP2', 0.92 * 2.72, {'X': 'Z'})
    cell = re.sub(r'cell_footprint\s*:\s*"[^"]*"\s*;', 'cell_footprint : "g2_ltap2";\n        dont_use : true;', cell)
    return _lib_header(src, libname) + '\n' + cell + '\n}\n'


def w2_lib(src: str, libname: str, slew: float) -> str:
    """Physical taps: LTAPB<k> / LTAPBW<k> = buf_<k> timing, area = pad + buffer, pin A max_transition = slew."""
    cells = []
    for tc in TAP_CLASSES:
        k = tc.split('_')[1]
        base = extract_cell(src, f'sky130_fd_sc_hd__{tc}')
        for name in (f'LTAPB{k}', f'LTAPBW{k}'):
            c = lib_cell(base, name, tap_sites(tc) * SITE_AREA, {'X': 'Z'})
            c = re.sub(r'cell_footprint\s*:\s*"[^"]*"\s*;', f'cell_footprint : "w2_{name.lower()}";\n        dont_use : true;', c)
            cells.append(_set_input_max_transition(c, 'A', slew))
    return _lib_header(src, libname) + '\n' + '\n'.join(cells) + '\n}\n'


def _set_input_max_transition(cell: str, pin: str, slew: float) -> str:
    """Set the pin's max_transition to `slew`: the sky130 buffers already carry max_transition : 1.5 on their input
    pins, and the LAST attribute wins, so the existing one is replaced (exactly one remains)."""
    m = re.search(r'pin\s*\(\s*"%s"\s*\)\s*\{' % pin, cell)
    start, end = m.end(), liberty._block(cell, m.start()).__len__() + m.start()
    body = re.sub(r'\n\s*max_transition\s*:\s*[^;]*;', '', cell[start:end])
    body = f'\n            max_transition : {slew:.4f};' + body
    return cell[:start] + body + cell[end:]


def w2_lef() -> str:
    """LEF of the physical taps: LTAPB<k> keeps LTAP2's single-track pad and via stack in its first two sites;
    LTAPBW<k> keeps LTAP's wide pad (R2 placement is not track-aligned); the rest of the cell is the buffer body."""
    out = 'VERSION 5.7 ;\nBUSBITCHARS "[]" ;\nDIVIDERCHAR "/" ;\n\n'
    narrow = LTAP2_LEF[LTAP2_LEF.index('MACRO LTAP2'):LTAP2_LEF.index('END LTAP2') + len('END LTAP2')]
    for tc in TAP_CLASSES:
        k = tc.split('_')[1]
        w = tap_sites(tc) * SITE_W
        t = narrow.replace('LTAP2', f'LTAPB{k}').replace('SIZE 0.92 BY 2.72', f'SIZE {w:.2f} BY 2.72')
        t = t.replace('RECT 0.00 2.480 0.92 2.960', f'RECT 0.00 2.480 {w:.2f} 2.960').replace('RECT 0.00 -0.240 0.92 0.240', f'RECT 0.00 -0.240 {w:.2f} 0.240')
        out += t + '\n\n'
        out += CELL_LEF.format(name=f'LTAPBW{k}', w=w, li_pin='A', li_dir='INPUT', m4_pin='Z', m4_dir='OUTPUT', m4x2=w - 0.30) + '\n'
    return out + 'END LIBRARY\n'


def write_cells(cfg, root: Path):
    """cells/: via sites + LTAP (G2), LTAP2 + dont_touch (R3), physical taps (W2), the met1-rail PDN (D-G2.2), and the
    ss / ff clones of every custom cell for sign-off (when the corner libraries are available)."""
    cd = root / 'cells'
    g2_cells_main(cd)
    r3_build.cells(root)                       # writes root/cells/g2r3_cells.{lef,lib}, dont_touch_r3.tcl
    assert (cd / 'dont_touch_r3.tcl').read_text() == DONT_TOUCH_R3
    shutil.copy(RES / 'pdn_m1rails.tcl', cd / 'pdn_m1rails.tcl')
    shutil.copy(RES / 'dont_touch_g2.tcl', cd / 'dont_touch.tcl')
    slew = cfg.raw['drivers']['slew_target_ns']
    (cd / 'w2_cells.lef').write_text(w2_lef())
    (cd / 'w2_cells.lib').write_text(w2_lib(liberty.text('tt'), 'w2_cells', slew))
    if pdk.available():
        for c in ('ss', 'ff'):
            src = liberty.text(c)
            (cd / f'g2_cells_{c}.lib').write_text(clone_g2_lib(src, f'g2_cells_{c}'))
            (cd / f'g2r3_cells_{c}.lib').write_text(clone_g2r3_lib(src, f'g2r3_cells_{c}'))
            (cd / f'w2_cells_{c}.lib').write_text(w2_lib(src, f'w2_cells_{c}', slew))


def custom_libs(corner: str) -> list[str]:
    """Custom-cell Liberty files (relative to the design root) of one corner."""
    sfx = '' if corner == 'tt' else f'_{corner}'
    return [f'cells/g2_cells{sfx}.lib', f'cells/g2r3_cells{sfx}.lib', f'cells/w2_cells{sfx}.lib']


def orfs_lefs(cfg) -> list[str]:
    if w2(cfg):
        return ['cells/g2_cells.lef', 'cells/w2_cells.lef']
    return ['cells/g2_cells.lef', 'cells/g2r3_cells.lef'] if mode(cfg) == 'r3' else ['cells/g2_cells.lef']


def orfs_libs(cfg) -> list[str]:
    return [p.replace('.lef', '.lib') for p in orfs_lefs(cfg)]


# ------------------------------------------------------------------------------------------------ placement plans
def plan_entries(cfg, netlist_base: str) -> list[tuple[str, int, float, float]]:
    """r3: (instance, band, x fraction within band, y fraction of core), in placement order."""
    K, m = cfg.K, cfg.m
    plan = []
    for i, k in re.findall(r'VSITE_BUF vs_(\d+)_(\d+) ', netlist_base):
        plan.append((f'vs_{i}_{k}', int(k), 0.5, (int(i) + 0.5) / m))
    for b, lines in arch.band_lines(cfg).items():
        T = len(lines)
        for t, L in enumerate(lines):
            for s in range(K):
                plan.append((f'lt_{L}_s{s}', b, (t + 0.5) / T, (s + (t + 0.5) / T) / K))
    return plan


def plan_entries_r2(cfg, netlist_base: str) -> list[tuple[str, int, float, str]]:
    """r2: (instance, band, y fraction, kind), taps first then sites (the order of g2_struct.plan)."""
    plan = []
    for b, lines in arch.band_lines(cfg).items():
        for t, L in enumerate(lines):
            plan.append((f'lt_{L}', b, (t + 0.5) / len(lines), 'tap'))
    for i, k in re.findall(r'VSITE_BUF vs_(\d+)_(\d+) ', netlist_base):
        plan.append((f'vs_{i}_{k}', int(k), (int(i) + 0.5) / cfg.m, 'site'))
    return plan


def write_plan(cfg, root: Path) -> Path:
    net = (root / 'netlist' / 'netlist_base.v').read_text()
    nb = len(arch.band_lines(cfg))
    if mode(cfg) == 'r3':
        plan = plan_entries(cfg, net)
        tcl = [f'# generated by ubpgen for {cfg.name}: {nb} bands, {len(plan)} cells (sites + {cfg.K} taps per line)',
               f'set r3_nb {nb}', 'set r3_plan {']
        tcl += [f'  {{{n} {b} {xf:.6f} {yf:.6f}}}' for n, b, xf, yf in plan]
        tcl += ['}', R3_PLACER]
    else:
        plan = plan_entries_r2(cfg, net)
        tcl = [f'# generated by ubpgen for {cfg.name}: {nb} bands, {len(plan)} cells', f'set g2_nb {nb}', 'set g2_plan {']
        tcl += [f'  {{{n} {k} {yf:.6f} {kind}}}' for n, k, yf, kind in plan]
        tcl += ['}', R2_PLACER]
    ld = root / 'layout'
    ld.mkdir(exist_ok=True)
    out = ld / 'place_access.tcl'
    out.write_text('\n'.join(tcl) + '\n')
    return out


def parse_plan(tcl_text: str) -> list[tuple[str, int, str, str]]:
    return re.findall(r'^  \{(\S+) (\d+) ([\d.]+) ([\d.]+)\}$', tcl_text, flags=re.M)


def parse_plan_r2(tcl_text: str) -> list[tuple[str, str, str, str]]:
    return re.findall(r'^  \{(\S+) (\d+) ([\d.]+) (tap|site)\}$', tcl_text, flags=re.M)
