"""Single point of reuse of the validated research code (experiments/scripts).

The generator does not re-implement components that produced the validated R3 result: module RTL generators,
Yosys module synthesis, the independent AIGER simulators, the custom-cell LEF/Liberty builders, the R3 cell text
and placer TCL are imported from the historical scripts unchanged. Anything the generator adds (the W-independent
base top emitter, access expansion, plans, configs) is golden-tested against the historical outputs.
"""
from __future__ import annotations

import sys
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parent                                   # 14_FABLE_5_1_SCIENTIFIC_DISCOVERY
SCRIPTS = ROOT / 'experiments' / 'scripts'
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import e5_build  # noqa: E402
import e6_build  # noqa: E402
import g2_cells  # noqa: E402
import g3_build  # noqa: E402
import r3_build  # noqa: E402
import g2_struct  # noqa: E402

IMAGE = e5_build.IMAGE
LIB = e5_build.LIB
PLAT = e5_build.PLAT
XMAX = e5_build.XMAX
width = e5_build.width
canon_patterns = e5_build.canon_patterns
dock = e5_build.dock
dont_use_cells = e5_build.dont_use_cells

# bit-serial modules (E6): UBP generator, line negator, registered serial adder tree
gen_rtl = e6_build.gen_rtl
negline_rtl = e6_build.negline_rtl
tree_rtl = e6_build.tree_rtl
synth_seq = e6_build.synth_seq
read_aag_seq = e6_build.read_aag_seq
sim_seq = e6_build.sim_seq

# bit-plane popcount modules (G3, P2 = pc2)
ctrl_rtl = g3_build.ctrl_rtl
pline_rtl = g3_build.pline_rtl
prow_rtl = g3_build.prow_rtl
sim_bitplane = g3_build.sim_bitplane

# custom cells (G2 via sites / taps, R3 two-site tap) and the R3 placer
CELL_LEF = g2_cells.LEF
lib_cell = g2_cells.lib_cell
extract_cell = g2_cells.extract_cell
g2_cells_main = g2_cells.main
LTAP2_LEF = r3_build.LTAP2_LEF
DONT_TOUCH_R3 = r3_build.DONT_TOUCH
R3_PLACER = r3_build.PLACER
R2_PLACER = g2_struct.PLACER
