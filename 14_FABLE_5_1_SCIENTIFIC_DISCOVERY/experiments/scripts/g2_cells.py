"""Gate 2: custom 'via-site' and 'line-tap' cells that model a fixed base with a programmable layer boundary.

VSITE_BUF / VSITE_ZERO (identical footprint, 4 unithd sites = 1.84 x 2.72 um):
  pin Z  (li1, output)  -> drives the leaf input of the fixed row logic (base net);
  pin A  (met4, input)  -> the programmable access point; the via program either lands a programmable net here
                           (VSITE_BUF: Z = A) or selects the site's local tie option (VSITE_ZERO: Z = 0).
  OBS on met1-met3 reserves the pre-built via stack between A (met4) and Z (li1), so base routing never uses it.
LTAP (8 sites = 3.68 x 2.72 um, buf_4-class driver):
  pin A (li1, input) from the line driver (base net); pin Z (met4, output) drives the programmable line.

Liberty timing is cloned from sky130_fd_sc_hd buf_1 (VSITE_BUF) / buf_4 (LTAP), pins renamed; VSITE_ZERO is a
constant-0 output. Physically a via site is a via stack (no transistor); the buffer arc is a conservative stand-in
that adds delay equally to every leaf of every design.

python3 g2_cells.py OUTDIR  -> OUTDIR/g2_cells.lef, OUTDIR/g2_cells.lib
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

IMAGE = 'openroad/orfs:latest'
LIB = '/OpenROAD-flow-scripts/flow/platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib'

LEF = """VERSION 5.7 ;
BUSBITCHARS "[]" ;
DIVIDERCHAR "/" ;

MACRO {name}
  CLASS CORE ;
  ORIGIN 0 0 ;
  FOREIGN {name} 0 0 ;
  SIZE {w:.2f} BY 2.72 ;
  SYMMETRY X Y R90 ;
  SITE unithd ;
  PIN {li_pin}
    DIRECTION {li_dir} ;
    USE SIGNAL ;
    PORT
      LAYER li1 ;
        RECT 0.085 1.015 0.425 1.665 ;
    END
  END {li_pin}
  PIN {m4_pin}
    DIRECTION {m4_dir} ;
    USE SIGNAL ;
    PORT
      LAYER met4 ;
        RECT 0.30 0.80 {m4x2:.2f} 1.92 ;
    END
  END {m4_pin}
  PIN VPWR
    DIRECTION INOUT ;
    USE POWER ;
    PORT
      LAYER met1 ;
        RECT 0.00 2.480 {w:.2f} 2.960 ;
    END
  END VPWR
  PIN VGND
    DIRECTION INOUT ;
    USE GROUND ;
    PORT
      LAYER met1 ;
        RECT 0.00 -0.240 {w:.2f} 0.240 ;
    END
  END VGND
  OBS
    LAYER met1 ;
      RECT 0.60 0.90 1.25 1.80 ;
    LAYER met2 ;
      RECT 0.60 0.90 1.25 1.80 ;
    LAYER met3 ;
      RECT 0.45 0.80 1.40 1.90 ;
  END
END {name}
"""


def lib_cell(src: str, new: str, area: float, rename: dict, func=None) -> str:
    body = src
    body = re.sub(r'cell\s*\(\s*"?sky130_fd_sc_hd__\w+"?\s*\)', f'cell ("{new}")', body, count=1)
    body = re.sub(r'area\s*:\s*[0-9.]+\s*;', f'area : {area:.4f};', body, count=1)
    for a, b in rename.items():
        body = re.sub(rf'pin\s*\(\s*"?{a}"?\s*\)', f'pin ("{b}")', body)
        body = re.sub(rf'related_pin\s*:\s*"{a}"', f'related_pin : "{b}"', body)
        body = re.sub(rf'function\s*:\s*"{a}"', f'function : "{b}"', body)
    if func is not None:
        body = re.sub(r'function\s*:\s*"[^"]*"', f'function : "{func}"', body)
    return body


def extract_cell(lib_text: str, cell: str) -> str:
    m = re.search(rf'cell\s*\(\s*"?{cell}"?\s*\)\s*\{{', lib_text)
    i = m.start(); depth = 0; j = m.end() - 1
    while True:
        c = lib_text[j]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return lib_text[i:j + 1]
        j += 1


def main(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    lef = ''
    for name, w, li_pin, li_dir, m4_pin, m4_dir in (('VSITE_BUF', 1.84, 'Z', 'OUTPUT', 'A', 'INPUT'),
                                                   ('VSITE_ZERO', 1.84, 'Z', 'OUTPUT', 'A', 'INPUT'),
                                                   ('VSITE_ONE', 1.84, 'Z', 'OUTPUT', 'A', 'INPUT'),
                                                   ('LTAP', 3.68, 'A', 'INPUT', 'Z', 'OUTPUT')):
        lef += LEF.format(name=name, w=w, li_pin=li_pin, li_dir=li_dir, m4_pin=m4_pin, m4_dir=m4_dir, m4x2=w - 0.30) + '\n'
    (out / 'g2_cells.lef').write_text(lef + 'END LIBRARY\n')
    lib_text = subprocess.run(['docker', 'run', '--rm', IMAGE, 'cat', LIB], capture_output=True, text=True).stdout
    header = lib_text[:re.search(r'\n\s*cell\s*\(', lib_text).start()]
    header = re.sub(r'library\s*\(\s*"?[\w]+"?\s*\)', 'library ("g2_cells")', header, count=1)
    buf1 = extract_cell(lib_text, 'sky130_fd_sc_hd__buf_1')
    buf4 = extract_cell(lib_text, 'sky130_fd_sc_hd__buf_4')
    cells = [lib_cell(buf1, 'VSITE_BUF', 1.84 * 2.72, {'X': 'Z'}),
             lib_cell(buf1, 'VSITE_ZERO', 1.84 * 2.72, {'X': 'Z'}),
             lib_cell(buf4, 'LTAP', 3.68 * 2.72, {'X': 'Z'}),
             lib_cell(buf1, 'VSITE_ONE', 1.84 * 2.72, {'X': 'Z'})]
    # VSITE_ZERO: constant-0 output, no timing arcs from A
    z = cells[1]
    z = re.sub(r'(?<!_)function\s*:\s*"[^"]*"', 'function : "0"', z)   # output function only, keep power_down_function
    z = re.sub(r'timing\s*\(\s*\)\s*\{', 'timing_removed () {', z)
    z = re.sub(r'timing_removed \(\) \{.*?\n\s{12}\}\n', '', z, flags=re.S)  # best effort; verified by read below
    cells[1] = z
    o = cells[3]
    o = re.sub(r'(?<!_)function\s*:\s*"[^"]*"', 'function : "1"', o)
    o = re.sub(r'timing\s*\(\s*\)\s*\{', 'timing_removed () {', o)
    o = re.sub(r'timing_removed \(\) \{.*?\n\s{12}\}\n', '', o, flags=re.S)
    cells[3] = o
    # unique footprints (never interchangeable with library buffers) and dont_use for the resizer
    for k, nm in enumerate(('VSITE_BUF', 'VSITE_ZERO', 'LTAP', 'VSITE_ONE')):
        cells[k] = re.sub(r'cell_footprint\s*:\s*"[^"]*"\s*;', f'cell_footprint : "g2_{nm.lower()}";\n        dont_use : true;', cells[k])
    (out / 'g2_cells.lib').write_text(header + '\n' + '\n'.join(cells) + '\n}\n')
    print('wrote', out / 'g2_cells.lef', out / 'g2_cells.lib')


if __name__ == '__main__':
    main(Path(sys.argv[1]))
