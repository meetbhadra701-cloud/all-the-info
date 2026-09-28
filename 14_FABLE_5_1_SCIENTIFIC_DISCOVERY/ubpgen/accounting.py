"""Physical area accounting (Week 2, 21_WEEK2_TIMING_CLOSURE.md 2.1): what the unchanged ORFS flow changed in, or
added to, the input netlist of a frozen base.

A x T uses the floorplan instance area, which the flow measures BEFORE placement. Every cell the flow's resizer
adds or upsizes after that (repair_design at global placement / 3_4 resize / 5_1 global route: the spine sizing
the Week-2 max_transition constraint asks for) is physical area that the floorplan number does not contain:

  sizing area = sum over input-netlist instances of (final master area - input master area)
              + area of every instance the flow inserted, except the classes below.

Excluded, for every design alike (they are not driver sizing and the established metric never counted them): fill,
well taps, clock-tree cells (CTS), hold-repair delay cells, I/O port buffers and antenna diodes. Each is still listed.
Instances are matched by their flattened hierarchical name (input: netlist_base.v; final: 6_final.def COMPONENTS);
areas come from the tt Liberty (standard cells) and the design's custom-cell Liberty files.
"""
from __future__ import annotations

import collections
import functools
import re
import subprocess
from pathlib import Path

from . import access, liberty
from ._legacy import IMAGE

EXCLUDED = {'FILLER': 'fill', 'TAP': 'well tap', 'clkbuf': 'clock tree (CTS)', 'clkload': 'clock tree (CTS)',
            'ANTENNA': 'antenna diode', 'hold': 'hold repair', 'input': 'port buffer', 'output': 'port buffer'}


def flatten(verilog: str, top: str = 'top') -> dict[str, str]:
    """Flattened instance name -> master of a structural (hierarchical) netlist."""
    mods = {}
    for m in re.finditer(r'^module\s+(\S+?)\s*\(.*?^endmodule', verilog, flags=re.M | re.S):
        body = m.group(0)
        mods[m.group(1)] = re.findall(r'^\s+(\S+)\s+(\\\S+\s|\S+)\s*\($', body, flags=re.M)
    out = {}

    def walk(mod, prefix):
        for master, name in mods[mod]:
            name = name.strip().lstrip('\\')
            full = prefix + name
            if master in mods:
                walk(master, full + '/')
            else:
                out[full] = master
    walk(top, '')
    return out


def def_components(def_text: str) -> list[tuple[str, str]]:
    sec = def_text[def_text.index('\nCOMPONENTS'):def_text.index('END COMPONENTS')]
    return [(n.replace('\\', ''), m) for n, m in re.findall(r'^\s*-\s+(\S+)\s+(\S+)', sec, flags=re.M)]


MERGED_LEF = '/OpenROAD-flow-scripts/flow/platforms/sky130hd/lef/sky130_fd_sc_hd_merged.lef'


@functools.lru_cache(maxsize=1)
def _lef_sizes() -> dict[str, float]:
    """Physical-only cells (fill, well taps) have no Liberty area: their LEF SIZE."""
    txt = subprocess.run(['docker', 'run', '--rm', IMAGE, 'cat', MERGED_LEF], capture_output=True, text=True, check=True).stdout
    return {m.group(1): float(m.group(2)) * float(m.group(3))
            for m in re.finditer(r'MACRO\s+(\S+)\s.*?SIZE\s+([\d.]+)\s+BY\s+([\d.]+)', txt, flags=re.S)}


def cell_areas(root: Path) -> dict[str, float]:
    areas = {}
    for text in [liberty.text('tt')] + [(root / c).read_text() for c in access.custom_libs('tt') if (root / c).exists()]:
        for m in re.finditer(r'\bcell\s*\(\s*"?(\w+)"?\s*\)\s*\{', text):
            a = re.search(r'\barea\s*:\s*([\d.]+)', text[m.end():m.end() + 4000])
            if a:
                areas.setdefault(m.group(1), float(a.group(1)))
    for k, v in _lef_sizes().items():
        areas.setdefault(k, round(v, 4))
    return areas


def _class(name: str) -> str:
    m = re.match(r'([A-Za-z]+)', name.rsplit('/', 1)[-1])
    return m.group(1) if m else name


def flow_changes(root: Path, base_def: Path) -> dict:
    root = root.resolve()
    src = flatten((root / 'netlist' / 'netlist_base.v').read_text())
    fin = def_components(base_def.read_text())
    area = cell_areas(root)
    missing = sorted({m for _, m in fin if m not in area} | {m for m in src.values() if m not in area})
    if missing:
        raise KeyError(f'no Liberty area for {missing[:8]}')
    seen = set()
    resized = collections.Counter()
    resized_delta = 0.0
    inserted = collections.defaultdict(lambda: {'count': 0, 'area_um2': 0.0, 'masters': collections.Counter()})
    for n, m in fin:
        if n in src:
            seen.add(n)
            if src[n] != m:
                resized[f'{src[n]} -> {m}'] += 1
                resized_delta += area[m] - area[src[n]]
            continue
        k = _class(n)
        inserted[k]['count'] += 1
        inserted[k]['area_um2'] += area[m]
        inserted[k]['masters'][m] += 1
    removed = sorted(set(src) - seen)
    sizing_ins = {k: v for k, v in inserted.items() if k not in EXCLUDED}
    fmt = lambda d: {k: {'count': v['count'], 'area_um2': round(v['area_um2'], 3), 'masters': dict(v['masters'].most_common(6)),
                         'kind': EXCLUDED.get(k, 'resizer (driver sizing / repair)')} for k, v in sorted(d.items())}
    sizing = resized_delta + sum(v['area_um2'] for v in sizing_ins.values()) - sum(area[src[n]] for n in removed)
    return {'input_instances': len(src), 'final_components': len(fin),
            'input_area_um2': round(sum(area[m] for m in src.values()), 3),
            'resized': {'count': sum(resized.values()), 'delta_um2': round(resized_delta, 3), 'pairs': dict(resized.most_common(12))},
            'removed': {'count': len(removed), 'area_um2': round(sum(area[src[n]] for n in removed), 3), 'examples': removed[:6]},
            'inserted': fmt(inserted),
            'sizing_area_um2': round(sizing, 3),
            'final_logic_area_um2': round(sum(area[m] for n, m in fin if _class(n) not in ('FILLER', 'TAP')), 3)}
