"""Physical area accounting: what a physical flow changed in, or added to, its input netlist.

Origin: ubpgen/accounting.py. Decoupled: the netlist text, the final DEF text and the cell-area table are inputs
(build the table with harness.liberty.cell_areas + lef_sizes), so any design and any flow can be audited.

Why it exists (UBP Week 2): a figure of merit that uses the floorplan instance area -- measured BEFORE placement --
does not contain the buffers and upsized drivers the flow's resizer adds afterwards. For UBP this was 5,318 um^2 of
spine repeaters (+2.9%); reporting both the metric of record and the flow-inclusive area as a sensitivity kept the
comparison honest. Excluded classes (listed, never silently dropped) are those the established metric never counted.
"""
from __future__ import annotations

import collections
import re

from . import liberty

EXCLUDED ={'FILLER': 'fill', 'TAP': 'well tap', 'clkbuf': 'clock tree (CTS)', 'clkload': 'clock tree (CTS)',
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


def area_table(lib_texts: list[str], lef_text: str = '') -> dict[str, float]:
    """Cell -> area: Liberty areas first (standard, then custom libraries), then LEF SIZE for physical-only cells."""
    areas = liberty.cell_areas(lib_texts)
    for k, v in liberty.lef_sizes(lef_text).items():
        areas.setdefault(k, round(v, 4))
    return areas


def _class(name: str) -> str:
    m = re.match(r'([A-Za-z]+)', name.rsplit('/', 1)[-1])
    return m.group(1) if m else name


def flow_changes(netlist_text: str, def_text: str, area: dict[str, float], top: str = 'top',
                 excluded: dict[str, str] = EXCLUDED) -> dict:
    """Input netlist vs final DEF: resized instances (area delta), removed instances, inserted instances by name
    class; sizing area = resize delta + inserted (non-excluded) - removed."""
    src = flatten(netlist_text, top)
    fin = def_components(def_text)
    missing = sorted({m for _, m in fin if m not in area} | {m for m in src.values() if m not in area})
    if missing:
        raise KeyError(f'no area for {missing[:8]}')
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
    sizing_ins = {k: v for k, v in inserted.items() if k not in excluded}
    fmt = lambda d: {k: {'count': v['count'], 'area_um2': round(v['area_um2'], 3), 'masters': dict(v['masters'].most_common(6)),
                         'kind': excluded.get(k, 'resizer (driver sizing / repair)')} for k, v in sorted(d.items())}
    sizing = resized_delta + sum(v['area_um2'] for v in sizing_ins.values()) - sum(area[src[n]] for n in removed)
    return {'input_instances': len(src), 'final_components': len(fin),
            'input_area_um2': round(sum(area[m] for m in src.values()), 3),
            'resized': {'count': sum(resized.values()), 'delta_um2': round(resized_delta, 3), 'pairs': dict(resized.most_common(12))},
            'removed': {'count': len(removed), 'area_um2': round(sum(area[src[n]] for n in removed), 3), 'examples': removed[:6]},
            'inserted': fmt(inserted),
            'sizing_area_um2': round(sizing, 3),
            'final_logic_area_um2': round(sum(area[m] for n, m in fin if _class(n) not in ('FILLER', 'TAP')), 3)}
