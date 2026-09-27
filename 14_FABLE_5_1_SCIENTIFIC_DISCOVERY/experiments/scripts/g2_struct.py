"""Gate 2 revision R2: a STRUCTURED (crossbar) W-blind base placement.

python3 g2_struct.py G2_DIR DESIGN UTIL [UTIL ...]
  writes G2_DIR/cells/struct_DESIGN.tcl (the plan + placer) and G2_DIR/DESIGN/config_sUTIL.mk (ORFS config, nickname
  g2s_DESIGN_uUTIL). The base NETLIST is the unchanged G2 base; only the placement of the programmable-pin cells is fixed
  before global placement (ORFS POST_PDN_TCL hook, i.e. after tapcells and PDN, before 3_1 global placement):
  * one vertical band per line group: UBP3 = one per 3-input block (22 bands, 26 line taps each; last block 2);
    per-input fabrics (pc2, g1s) = one per input (64 bands, 2 line taps each);
  * the via site of (row i, band k) at the band's centre, at height (i + 0.5)/64 of the core (one site per row per band);
  * the band's line taps inside the band, spread evenly over the core height: tap t of T at height (t + 0.5)/T.
  Every coordinate is a function of (row, band, tap index) only: the plan is identical for every W. The cells are set
  FIRM (global and detailed placement treat them as fixed); every other cell is placed by ORFS from base connectivity.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

LINE_UBP = re.compile(r'p([pn])(\d+)_(\d+)$')     # UBP3 line: polarity, block, pattern
LINE_PI = re.compile(r'l([pn])(\d+)$')            # per-input line: polarity, input


def plan(g2: Path, design: str) -> tuple[int, list[tuple[str, int, float, str]]]:
    m = json.loads((g2 / design / 'mapping.json').read_text())
    n_rows = 64
    entries = []
    bands: dict[int, list[tuple[int, int, str]]] = {}
    for L in m['lines']:
        u = LINE_UBP.match(L) if design == 'ubp3s' else LINE_PI.match(L)
        assert u, L
        if design == 'ubp3s':
            pol, k, q = u.group(1), int(u.group(2)), int(u.group(3))
            bands.setdefault(k, []).append((q, 0 if pol == 'p' else 1, L))
        else:
            pol, k = u.group(1), int(u.group(2))
            bands.setdefault(k, []).append((0, 0 if pol == 'p' else 1, L))
    nb = len(bands)
    for k, ls in bands.items():
        ls.sort()
        for t, (_, _, L) in enumerate(ls):
            entries.append((f'lt_{L}', k, (t + 0.5) / len(ls), 'tap'))
    net = (g2 / design / 'netlist_base.v').read_text()
    for i, k in re.findall(r'VSITE_BUF vs_(\d+)_(\d+) ', net):
        entries.append((f'vs_{i}_{k}', int(k), (int(i) + 0.5) / n_rows, 'site'))
    return nb, entries


PLACER = r'''
# ---- R2 structured placement of the programmable-pin cells (W-blind; see g2_struct.py) ----
set blk [ord::get_db_block]
set core [$blk getCoreArea]
set dbu [$blk getDbUnitsPerMicron]
set cx0 [$core xMin]; set cy0 [$core yMin]; set cx1 [$core xMax]; set cy1 [$core yMax]
set rows {}
foreach r [$blk getRows] { lappend rows [list [lindex [$r getOrigin] 1] $r] }
set rows [lsort -integer -index 0 $rows]
set occ [dict create]
foreach inst [$blk getInsts] {
  if {[$inst getPlacementStatus] eq "NONE" || [$inst getPlacementStatus] eq "UNPLACED"} { continue }
  set bb [$inst getBBox]
  dict lappend occ [$bb yMin] [list [$bb xMin] [$bb xMax]]
}
proc g2_free {occ y xa xb} {
  if {![dict exists $occ $y]} { return 1 }
  foreach iv [dict get $occ $y] { if {$xa < [lindex $iv 1] && [lindex $iv 0] < $xb} { return 0 } }
  return 1
}
set placed 0
foreach e $g2_plan {
  lassign $e name band yf kind
  set inst [$blk findInst $name]
  if {$inst eq "NULL"} { error "R2: instance $name not found" }
  set w [[$inst getMaster] getWidth]
  set bw [expr {double($cx1 - $cx0) / $g2_nb}]
  set xc [expr {$cx0 + ($band + 0.5) * $bw}]
  # taps sit immediately right of the band's via-site column (site width 1.84 um + one 0.46 um site gap)
  if {$kind eq "tap"} { set xc [expr {$xc + 0.92 * $dbu + $w / 2.0 + 0.46 * $dbu}] }
  set yt [expr {$cy0 + $yf * ($cy1 - $cy0)}]
  # nearest row, then the nearest free site-aligned span (search outward, then neighbouring rows)
  set best -1; set bd 1e18
  for {set j 0} {$j < [llength $rows]} {incr j} {
    set d [expr {abs([lindex $rows $j 0] - $yt)}]
    if {$d < $bd} { set bd $d; set best $j }
  }
  set done 0
  foreach dj {0 1 -1 2 -2 3 -3} {
    set j [expr {$best + $dj}]
    if {$j < 0 || $j >= [llength $rows]} { continue }
    set r [lindex $rows $j 1]
    set ry [lindex [$r getOrigin] 1]; set rx [lindex [$r getOrigin] 0]
    set sw [[$r getSite] getWidth]; set nsite [$r getSiteCount]
    set s0 [expr {int(round(($xc - $w / 2.0 - $rx) / $sw))}]
    for {set ds 0} {$ds < 200} {incr ds} {
      foreach s [list [expr {$s0 + $ds}] [expr {$s0 - $ds}]] {
        set xa [expr {$rx + $s * $sw}]; set xb [expr {$xa + $w}]
        if {$s < 0 || $xb > $rx + $nsite * $sw} { continue }
        if {[g2_free $occ $ry $xa $xb]} {
          $inst setOrient [$r getOrient]
          $inst setLocation $xa $ry
          $inst setPlacementStatus FIRM
          dict lappend occ $ry [list $xa $xb]
          set done 1; break
        }
      }
      if {$done} { break }
    }
    if {$done} { break }
  }
  if {!$done} { error "R2: no legal slot for $name" }
  incr placed
}
puts "R2: placed $placed programmable-pin cells FIRM in $g2_nb bands"
'''


def main(g2: Path, design: str, utils: list[int]):
    nb, entries = plan(g2, design)
    tcl = [f'# generated by g2_struct.py for {design}: {nb} bands, {len(entries)} cells', f'set g2_nb {nb}', 'set g2_plan {']
    tcl += [f'  {{{n} {k} {yf:.6f} {kind}}}' for n, k, yf, kind in entries]
    tcl += ['}', PLACER]
    (g2 / 'cells' / f'struct_{design}.tcl').write_text('\n'.join(tcl) + '\n')
    src = (g2 / design / 'config_u60.mk').read_text()
    for u in utils:
        cfg = re.sub(r'DESIGN_NICKNAME = g2_\w+', f'DESIGN_NICKNAME = g2s_{design}_u{u}', src)
        cfg = re.sub(r'CORE_UTILIZATION = \d+', f'CORE_UTILIZATION = {u}', cfg)
        cfg += f'export POST_PDN_TCL = /work/cells/struct_{design}.tcl\n'
        (g2 / design / f'config_s{u}.mk').write_text(cfg)
    print(json.dumps({'design': design, 'bands': nb, 'cells': len(entries),
                      'taps': sum(1 for e in entries if e[3] == 'tap'), 'sites': sum(1 for e in entries if e[3] == 'site'),
                      'configs': [f'config_s{u}.mk' for u in utils]}))


if __name__ == '__main__':
    main(Path(sys.argv[1]), sys.argv[2], [int(u) for u in sys.argv[3:]])
