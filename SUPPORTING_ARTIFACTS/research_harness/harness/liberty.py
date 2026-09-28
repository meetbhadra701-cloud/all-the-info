"""Minimal Liberty reader / editor: cell and pin blocks, areas, pin capacitances, NLDM tables, and safe edits.

Origin: ubpgen/liberty.py (reader), ubpgen/access.py (_lib_header, _set_input_max_transition),
experiments/scripts/g2_cells.py (extract_cell, lib_cell). Decoupled: functions take Liberty TEXT; loading a library
from the ORFS image is a separate helper, so nothing here assumes a design.

Two UBP lessons are encoded here:
  * set_input_max_transition REPLACES the attribute. Liberty keeps the LAST value, and the sky130 buffers already
    carry max_transition : 1.5 on their inputs; inserting a new line in front of it silently did nothing (UBP Week 2,
    21_WEEK2_TIMING_CLOSURE.md 2.4). Every edit should be followed by a read-back check (count and value).
  * a custom cell's timing at another corner is the same edit applied to that corner's library (clone_library), so
    every corner times the same abstraction.
"""
from __future__ import annotations

import bisect
import functools
import re
import subprocess

TT_IN_ORFS = '/OpenROAD-flow-scripts/flow/platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib'


@functools.lru_cache(maxsize=8)
def image_file(image: str, path: str = TT_IN_ORFS) -> str:
    """A text file from inside a docker image (e.g. the ORFS platform tt library)."""
    return subprocess.run(['docker', 'run', '--rm', image, 'cat', path], capture_output=True, text=True, check=True).stdout


def _block(t: str, start: int) -> str:
    i = t.index('{', start)
    d = 0
    for j in range(i, len(t)):
        if t[j] == '{':
            d += 1
        elif t[j] == '}':
            d -= 1
            if d == 0:
                return t[start:j + 1]
    raise ValueError('unbalanced braces')


def cell_block(t: str, cell: str) -> str:
    m = re.search(r'cell\s*\(\s*"?%s"?\s*\)\s*\{' % re.escape(cell), t)
    if m is None:
        raise KeyError(cell)
    return _block(t, m.start())


extract_cell = cell_block      # g2_cells.extract_cell: same block, same text


def pin_block(cb: str, pin: str) -> str:
    m = re.search(r'pin\s*\(\s*"?%s"?\s*\)\s*\{' % re.escape(pin), cb)
    if m is None:
        raise KeyError(pin)
    return _block(cb, m.start())


def area(cb: str) -> float:
    return float(re.search(r'\barea\s*:\s*([\d.]+)', cb).group(1))


def pin_cap(cb: str, pin: str) -> float:
    """Worst of capacitance / rise_capacitance / fall_capacitance of an input pin (library units, pF in sky130)."""
    pb = pin_block(cb, pin)
    return max(float(x) for x in re.findall(r'\b(?:rise_|fall_)?capacitance\s*:\s*([\d.]+)', pb))


def tables(cb: str, pin: str, kind: str):
    """All NLDM tables of `kind` (cell_rise, rise_transition, ...) under a pin: [(index_1, index_2, rows)]."""
    pb = pin_block(cb, pin)
    out = []
    for m in re.finditer(kind + r'\s*\(\s*"?[\w]+"?\s*\)\s*\{', pb):
        b = _block(pb, m.start())
        i1 = [float(x) for x in re.search(r'index_1\s*\(\s*"([^"]+)"', b).group(1).split(',')]
        i2 = [float(x) for x in re.search(r'index_2\s*\(\s*"([^"]+)"', b).group(1).split(',')]
        rows = [[float(x) for x in r.split(',')] for r in re.findall(r'"([^"]+)"', re.search(r'values\s*\((.*?)\)\s*;', b, re.S).group(1))]
        out.append((i1, i2, rows))
    return out


def interp(tab, slew: float, cap: float) -> float:
    """Bilinear NLDM interpolation (extrapolates linearly beyond the table, like STA)."""
    i1, i2, v = tab

    def seg(ax, x):
        k = max(1, min(len(ax) - 1, bisect.bisect_left(ax, x)))
        return k - 1, k, (x - ax[k - 1]) / (ax[k] - ax[k - 1])
    a0, a1, fa = seg(i1, slew)
    b0, b1, fb = seg(i2, cap)
    return (v[a0][b0] * (1 - fa) * (1 - fb) + v[a1][b0] * fa * (1 - fb) + v[a0][b1] * (1 - fa) * fb + v[a1][b1] * fa * fb)


def output_transition(lib_text: str, cell: str, out_pin: str, slew: float, cap: float) -> float:
    cb = cell_block(lib_text, cell)
    return max(interp(tb, slew, cap) for tb in tables(cb, out_pin, 'rise_transition') + tables(cb, out_pin, 'fall_transition'))


def arc_delay(lib_text: str, cell: str, out_pin: str, slew: float, cap: float) -> float:
    cb = cell_block(lib_text, cell)
    return max(interp(tb, slew, cap) for tb in tables(cb, out_pin, 'cell_rise') + tables(cb, out_pin, 'cell_fall'))


# --------------------------------------------------------------------------------------------------------- edits
def header(src: str, name: str) -> str:
    """Library header (everything before the first cell) renamed to `name`."""
    h = src[:re.search(r'\n\s*cell\s*\(', src).start()]
    return re.sub(r'library\s*\(\s*"?[\w]+"?\s*\)', f'library ("{name}")', h, count=1)


def clone_cell(src: str, new: str, area_um2: float, rename: dict, func: str | None = None,
               prefix: str = r'sky130_fd_sc_hd__\w+') -> str:
    """A standard cell's block renamed to `new`, with a new area, renamed pins and optionally a new function."""
    body = re.sub(r'cell\s*\(\s*"?%s"?\s*\)' % prefix, f'cell ("{new}")', src, count=1)
    body = re.sub(r'area\s*:\s*[0-9.]+\s*;', f'area : {area_um2:.4f};', body, count=1)
    for a, b in rename.items():
        body = re.sub(rf'pin\s*\(\s*"?{a}"?\s*\)', f'pin ("{b}")', body)
        body = re.sub(rf'related_pin\s*:\s*"{a}"', f'related_pin : "{b}"', body)
        body = re.sub(rf'function\s*:\s*"{a}"', f'function : "{b}"', body)
    if func is not None:
        body = re.sub(r'function\s*:\s*"[^"]*"', f'function : "{func}"', body)
    return body


lib_cell = clone_cell          # g2_cells.lib_cell: same edit


def set_input_max_transition(cell: str, pin: str, slew: float) -> str:
    """Set an input pin's max_transition, replacing any existing attribute (exactly one remains)."""
    m = re.search(r'pin\s*\(\s*"%s"\s*\)\s*\{' % pin, cell)
    start, end = m.end(), len(_block(cell, m.start())) + m.start()
    body = re.sub(r'\n\s*max_transition\s*:\s*[^;]*;', '', cell[start:end])
    body = f'\n            max_transition : {slew:.4f};' + body
    return cell[:start] + body + cell[end:]


def pin_attribute_values(cell: str, pin: str, attr: str) -> list[str]:
    """Read-back check for edits: every value of `attr` directly in the pin's block."""
    return re.findall(rf'\n\s*{attr}\s*:\s*([^;]*);', pin_block(cell, pin))


def clone_library(src: str, libname: str, cells: list[dict]) -> str:
    """A custom-cell library derived from one corner library. cells: [{'from': std cell, 'name', 'area',
    'rename': {...}, 'func': optional, 'max_transition': optional {pin: ns}}]. Apply to every corner's library."""
    out = []
    for c in cells:
        t = clone_cell(cell_block(src, c['from']), c['name'], c['area'], c.get('rename', {}), c.get('func'))
        for pin, s in (c.get('max_transition') or {}).items():
            t = set_input_max_transition(t, pin, s)
        out.append(t)
    return header(src, libname) + '\n' + '\n'.join(out) + '\n}\n'


def cell_areas(lib_texts: list[str]) -> dict[str, float]:
    """cell -> area over several libraries (first definition wins), as ubpgen.accounting.cell_areas."""
    areas = {}
    for text in lib_texts:
        for m in re.finditer(r'\bcell\s*\(\s*"?(\w+)"?\s*\)\s*\{', text):
            a = re.search(r'\barea\s*:\s*([\d.]+)', text[m.end():m.end() + 4000])
            if a:
                areas.setdefault(m.group(1), float(a.group(1)))
    return areas


def lef_sizes(lef_text: str) -> dict[str, float]:
    """MACRO -> SIZE area (physical-only cells such as fill and well taps have no Liberty area)."""
    return {m.group(1): float(m.group(2)) * float(m.group(3))
            for m in re.finditer(r'MACRO\s+(\S+)\s.*?SIZE\s+([\d.]+)\s+BY\s+([\d.]+)', lef_text, flags=re.S)}
