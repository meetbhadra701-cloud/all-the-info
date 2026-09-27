"""R3 (final layout revision): segmented line taps for the weight-independent UBP3-serial fixed base.

Only the PHYSICAL access structure changes; the logic (SGEN3/SNEG/STREE, via-site selection) is the R2/G2 base
netlist unchanged.
  * every line L gets K = 4 line taps lt_L_s0..s3 (new 2-site cell LTAP2) on the SAME base net L. The base routes
    the line as a W-independent spine (met1-met3) from its driver to its four taps;
  * rows are split into four equal segments (rows 16s .. 16s+15); a program connects a site in segment s only to the
    tap of its line in segment s, so no programmable net spans more than one quarter of the band;
  * LTAP2 = 2 sites (0.92 x 2.72 um) with a single-track met4 pad; 4 x 2 sites = the 8 sites of R2's one LTAP, so the
    base cell area is identical (169,952 um^2);
  * placement (W-blind, FIRM before global placement, POST_PDN_TCL): 22 bands; the band's 64 via sites in one column
    at the band centre (row i at height (i + 0.5)/64), track-aligned; tap (line t of T, segment s) at height
    (s + (t + 0.5)/T)/4 and at the line's home x = band_left + (t + 0.5)/T x band_width, track-aligned
    (pad centre on a met4 track).
Everything depends only on (row, band, line index, segment): the same base serves every W.

python3 r3_build.py cells    G2_DIR              # cells/g2r3_cells.lef/.lib (LTAP2), cells/dont_touch_r3.tcl
python3 r3_build.py base     G2_DIR U [U ...]    # ubp3r3/: netlist_base.v, mapping.json, sdc, W copies, configs; cells/struct_ubp3r3.tcl
python3 r3_build.py programs G2_DIR TAG [...]    # ubp3r3/prog_TAG.{json,tcl} from the G2 ubp3s programs (same W)
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from g2_cells import IMAGE, LIB, extract_cell, lib_cell  # noqa: E402
from g2_build import leaf_source  # noqa: E402

K = 4
N = 64
DESIGNS = {'ubp3s': ('ubp3r3', re.compile(r'p([pn])(\d+)_(\d+)$'), 'config_u52s.mk'),
           'pc2': ('pc2r3', re.compile(r'l([pn])(\d+)()$'), 'config_u67s.mk')}
SRC, DST, LINE, CFG = 'ubp3s', *DESIGNS['ubp3s']

LTAP2_LEF = """VERSION 5.7 ;
BUSBITCHARS "[]" ;
DIVIDERCHAR "/" ;

MACRO LTAP2
  CLASS CORE ;
  ORIGIN 0 0 ;
  FOREIGN LTAP2 0 0 ;
  SIZE 0.92 BY 2.72 ;
  SYMMETRY X Y R90 ;
  SITE unithd ;
  PIN A
    DIRECTION INPUT ;
    USE SIGNAL ;
    PORT
      LAYER li1 ;
        RECT 0.085 1.015 0.345 1.665 ;
    END
  END A
  PIN Z
    DIRECTION OUTPUT ;
    USE SIGNAL ;
    PORT
      LAYER met4 ;
        RECT 0.15 0.80 0.77 1.92 ;
    END
  END Z
  PIN VPWR
    DIRECTION INOUT ;
    USE POWER ;
    PORT
      LAYER met1 ;
        RECT 0.00 2.480 0.92 2.960 ;
    END
  END VPWR
  PIN VGND
    DIRECTION INOUT ;
    USE GROUND ;
    PORT
      LAYER met1 ;
        RECT 0.00 -0.240 0.92 0.240 ;
    END
  END VGND
  OBS
    LAYER met1 ;
      RECT 0.52 0.90 0.84 1.80 ;
    LAYER met2 ;
      RECT 0.52 0.90 0.84 1.80 ;
    LAYER met3 ;
      RECT 0.45 0.80 0.87 1.90 ;
  END
END LTAP2
END LIBRARY
"""

DONT_TOUCH = """# POST_SYNTH hook (R3): via sites and line taps (LTAP, LTAP2) are part of the FIXED base
set cnt 0
foreach inst [[ord::get_db_block] getInsts] {
  set m [[$inst getMaster] getName]
  if {[string match VSITE_* $m] || [string match LTAP* $m]} { $inst setDoNotTouch 1; incr cnt }
}
puts "G2/R3: dont_touch set on $cnt via-site/line-tap instances"
"""

PLACER = r'''
# ---- R3 placement of the programmable-access cells (W-blind; see r3_build.py) ----
set blk [ord::get_db_block]
set dbu [$blk getDbUnitsPerMicron]
set core [$blk getCoreArea]
set cx0 [$core xMin]; set cy0 [$core yMin]; set cx1 [$core xMax]; set cy1 [$core yMax]
set trk [expr {int(round(0.92 * $dbu))}]
set rows {}
foreach r [$blk getRows] { lappend rows [list [lindex [$r getOrigin] 1] $r] }
set rows [lsort -integer -index 0 $rows]
set occ [dict create]
foreach inst [$blk getInsts] {
  if {[$inst getPlacementStatus] eq "NONE" || [$inst getPlacementStatus] eq "UNPLACED"} { continue }
  set bb [$inst getBBox]
  dict lappend occ [$bb yMin] [list [$bb xMin] [$bb xMax]]
}
proc r3_free {occ y xa xb} {
  if {![dict exists $occ $y]} { return 1 }
  foreach iv [dict get $occ $y] { if {$xa < [lindex $iv 1] && [lindex $iv 0] < $xb} { return 0 } }
  return 1
}
set placed 0; set moved 0
set bw [expr {double($cx1 - $cx0) / $r3_nb}]
foreach e $r3_plan {
  lassign $e name band xf yf
  set inst [$blk findInst $name]
  if {$inst eq "NULL"} { error "R3: instance $name not found" }
  set w [[$inst getMaster] getWidth]
  set xc [expr {$cx0 + ($band + $xf) * $bw}]
  set yt [expr {$cy0 + $yf * ($cy1 - $cy0)}]
  set best -1; set bd 1e18
  for {set j 0} {$j < [llength $rows]} {incr j} {
    set d [expr {abs([lindex $rows $j 0] - $yt)}]
    if {$d < $bd} { set bd $d; set best $j }
  }
  set done 0
  foreach dj {0 1 -1 2 -2 3 -3 4 -4} {
    set j [expr {$best + $dj}]
    if {$j < 0 || $j >= [llength $rows]} { continue }
    set r [lindex $rows $j 1]
    set ry [lindex [$r getOrigin] 1]; set rx [lindex [$r getOrigin] 0]
    set sw [[$r getSite] getWidth]; set nsite [$r getSiteCount]
    set s0 [expr {int(round(($xc - $w / 2.0 - $rx) / $sw))}]
    for {set ds 0} {$ds < 400} {incr ds} {
      foreach s [list [expr {$s0 + $ds}] [expr {$s0 - $ds}]] {
        set xa [expr {$rx + $s * $sw}]; set xb [expr {$xa + $w}]
        if {$s < 0 || $xb > $rx + $nsite * $sw} { continue }
        # track alignment: the cell origin on the 0.92 um grid puts the met4 pad centre (origin + 0.46 um) on a met4 track
        if {($xa % $trk) != 0} { continue }
        if {[r3_free $occ $ry $xa $xb]} {
          $inst setOrient [$r getOrient]
          $inst setLocation $xa $ry
          $inst setPlacementStatus FIRM
          dict lappend occ $ry [list $xa $xb]
          if {$dj != 0 || $ds > 2} { incr moved }
          set done 1; break
        }
      }
      if {$done} { break }
    }
    if {$done} { break }
  }
  if {!$done} { error "R3: no legal track-aligned slot for $name" }
  incr placed
}
puts "R3: placed $placed programmable-access cells FIRM in $r3_nb bands ($moved displaced from their target)"
'''


def cells(g2: Path):
    cdir = g2 / 'cells'
    (cdir / 'g2r3_cells.lef').write_text(LTAP2_LEF)
    lib_text = subprocess.run(['docker', 'run', '--rm', IMAGE, 'cat', LIB], capture_output=True, text=True).stdout
    header = lib_text[:re.search(r'\n\s*cell\s*\(', lib_text).start()]
    header = re.sub(r'library\s*\(\s*"?[\w]+"?\s*\)', 'library ("g2r3_cells")', header, count=1)
    cell = lib_cell(extract_cell(lib_text, 'sky130_fd_sc_hd__buf_4'), 'LTAP2', 0.92 * 2.72, {'X': 'Z'})
    cell = re.sub(r'cell_footprint\s*:\s*"[^"]*"\s*;', 'cell_footprint : "g2_ltap2";\n        dont_use : true;', cell)
    (cdir / 'g2r3_cells.lib').write_text(header + '\n' + cell + '\n}\n')
    (cdir / 'dont_touch_r3.tcl').write_text(DONT_TOUCH)
    print('wrote', cdir / 'g2r3_cells.lef', cdir / 'g2r3_cells.lib', cdir / 'dont_touch_r3.tcl')


def band_lines(mp_lines):
    bands: dict[int, list[tuple[int, int, str]]] = {}
    for L in mp_lines:
        m = LINE.match(L)
        bands.setdefault(int(m.group(2)), []).append((int(m.group(3) or 0), 0 if m.group(1) == 'p' else 1, L))
    return {b: [L for _, _, L in sorted(v)] for b, v in bands.items()}


def base(g2: Path, utils: list[int]):
    src, dst = g2 / SRC, g2 / DST
    dst.mkdir(exist_ok=True)
    net = (src / 'netlist_base.v').read_text()
    pat = re.compile(r'  LTAP (lt_(\w+)) \(\n    \.A\((\w+)\)\n  \);\n')
    n_old = len(pat.findall(net))

    def rep(m):
        return ''.join(f'  LTAP2 {m.group(1)}_s{s} (\n    .A({m.group(3)})\n  );\n' for s in range(K))
    net2 = pat.sub(rep, net)
    n_lines = len(json.loads((src / 'mapping.json').read_text())['lines'])
    assert n_old == n_lines and net2.count('LTAP2 lt_') == n_lines * K and ' LTAP lt_' not in net2, n_old
    (dst / 'netlist_base.v').write_text(net2)
    shutil.copy(src / 'constraint.sdc', dst / 'constraint.sdc')
    for f in src.glob('W_w*.npy'):
        shutil.copy(f, dst / f.name)
    mp = json.loads((src / 'mapping.json').read_text())
    bl = band_lines(mp['lines'])
    mp.update({'taps_per_line': K, 'segment_rows': N // K,
               'taps': {L: [f'lt_{L}_s{s}' for s in range(K)] for L in mp['lines']}})
    (dst / 'mapping.json').write_text(json.dumps(mp))
    # W-blind plan: (instance, band, x fraction within band, y fraction of core)
    plan = []
    for i, k in re.findall(r'VSITE_BUF vs_(\d+)_(\d+) ', net2):
        plan.append((f'vs_{i}_{k}', int(k), 0.5, (int(i) + 0.5) / N))
    for b, lines in bl.items():
        T = len(lines)
        for t, L in enumerate(lines):
            for s in range(K):
                plan.append((f'lt_{L}_s{s}', b, (t + 0.5) / T, (s + (t + 0.5) / T) / K))
    tcl = [f'# generated by r3_build.py: {len(bl)} bands, {len(plan)} cells (sites + {K} taps per line)',
           f'set r3_nb {len(bl)}', 'set r3_plan {']
    tcl += [f'  {{{n} {b} {xf:.6f} {yf:.6f}}}' for n, b, xf, yf in plan]
    tcl += ['}', PLACER]
    (g2 / 'cells' / f'struct_{DST}.tcl').write_text('\n'.join(tcl) + '\n')
    cfg0 = (src / CFG).read_text()
    for u in utils:
        cfg = cfg0.replace(f'/work/{SRC}/', f'/work/{DST}/')
        cfg = re.sub(r'DESIGN_NICKNAME = \S+', f'DESIGN_NICKNAME = g2r3_{DST}_u{u}', cfg)
        cfg = re.sub(r'CORE_UTILIZATION = \d+', f'CORE_UTILIZATION = {u}', cfg)
        cfg = cfg.replace('ADDITIONAL_LEFS = /work/cells/g2_cells.lef', 'ADDITIONAL_LEFS = /work/cells/g2_cells.lef /work/cells/g2r3_cells.lef')
        cfg = cfg.replace('ADDITIONAL_LIBS = /work/cells/g2_cells.lib', 'ADDITIONAL_LIBS = /work/cells/g2_cells.lib /work/cells/g2r3_cells.lib')
        cfg = cfg.replace('POST_SYNTH_TCL = /work/cells/dont_touch.tcl', 'POST_SYNTH_TCL = /work/cells/dont_touch_r3.tcl')
        cfg = cfg.replace(f'POST_PDN_TCL = /work/cells/struct_{SRC}.tcl', f'POST_PDN_TCL = /work/cells/struct_{DST}.tcl')
        assert cfg.count(f'/work/{DST}/') == 3 and 'g2r3_cells.lef' in cfg and f'struct_{DST}' in cfg and 'dont_touch_r3' in cfg
        (dst / f'config_u{u}r.mk').write_text(cfg)
    print(json.dumps({'design': DST, 'taps': n_lines * K, 'plan_cells': len(plan), 'configs': [f'config_u{u}r.mk' for u in utils]}))


def programs(g2: Path, tags: list[str]):
    src, dst = g2 / SRC, g2 / DST
    mp = json.loads((src / 'mapping.json').read_text())
    for tag in tags:
        old = json.loads((src / f'prog_{tag}.json').read_text())
        W = np.load(src / f'W_{tag}.npy')
        # independent re-derivation of every leaf's line from W (must equal the G2 program)
        check = {}
        for i in range(N):
            for k in range(mp['leaves_per_row']):
                L = leaf_source(SRC, W, i, k, N)
                if L is not None:
                    check.setdefault(L, []).append(f'vs_{i}_{k}')
        assert {L: sorted(v) for L, v in check.items()} == {L: sorted(v) for L, v in old['nets'].items()}, tag
        nets = {}
        for L, sites in old['nets'].items():
            for sname in sites:
                i = int(sname.split('_')[1])
                nets.setdefault(f'{L}_s{i // (N // K)}', []).append(sname)
        prog = dict(old)
        prog.update({'nets': nets, 'n_prog_nets': len(nets), 'n_prog_pins': sum(len(v) for v in nets.values()) + len(nets),
                     'derived_from': f'{SRC}/prog_{tag}.json (split by row segment)'})
        (dst / f'prog_{tag}.json').write_text(json.dumps(prog))
        T = ['proc g2_apply_program {} {', '  set blk [ord::get_db_block]', '  set db [ord::get_db]',
             '  set mz [$db findMaster VSITE_ZERO]', '  set mo [$db findMaster VSITE_ONE]']
        for z in old['zeros']:
            T.append(f'  [$blk findInst {z}] swapMaster $mz')
        for o in old.get('ones', []):
            T.append(f'  [$blk findInst {o}] swapMaster $mo')
        for srcn, sites in nets.items():
            T.append(f'  set net [odb::dbNet_create $blk pgm_{srcn}]')
            T.append(f'  [[$blk findInst lt_{srcn}] findITerm Z] connect $net')
            for s in sites:
                T.append(f'  [[$blk findInst {s}] findITerm A] connect $net')
        T.append('}')
        (dst / f'prog_{tag}.tcl').write_text('\n'.join(T) + '\n')
        print(tag, 'nets', len(nets), 'pins', prog['n_prog_pins'], 'zeros', len(old['zeros']))


if __name__ == '__main__':
    cmd, g2 = sys.argv[1], Path(sys.argv[2])
    if len(sys.argv) > 3 and sys.argv[-1] in DESIGNS and cmd != 'cells':   # optional trailing source design
        SRC = sys.argv.pop()
        DST, LINE, CFG = DESIGNS[SRC]
    if cmd == 'cells':
        cells(g2)
    elif cmd == 'base':
        base(g2, [int(u) for u in sys.argv[3:]])
    else:
        programs(g2, sys.argv[3:])
