# Post-hoc fairness sensitivity (D-R3.4; NOT pre-registered, changes no classification): the same MODELED timing
# as the pre-registered STA (placement parasitics, 3.0 ns, programmed netlist), then one W-independent base change
# applied identically to every design: each spine-root driver (the instance driving a base net that feeds an LTAP*
# tap) is upsized to the drive-4 member of its own family. STA-only what-if: nothing is re-placed or re-routed.
# env: BASE_ODB, BASE_SDC, PROG_TCL
read_db $::env(BASE_ODB)
set blk [ord::get_db_block]
foreach inst [$blk getInsts] { if {[$inst isDoNotTouch]} { $inst setDoNotTouch 0 } }
foreach net [$blk getNets] { if {[$net isDoNotTouch]} { $net setDoNotTouch 0 } }
read_liberty /OpenROAD-flow-scripts/flow/platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
read_liberty /work/cells/g2_cells.lib
read_liberty /work/cells/g2r3_cells.lib
source $::env(PROG_TCL)
g2_apply_program
read_sdc $::env(BASE_SDC)
source /OpenROAD-flow-scripts/flow/platforms/sky130hd/setRC.tcl
set_propagated_clock [all_clocks]
estimate_parasitics -placement
set tp [get_pins -of_objects [get_cells -filter "ref_name =~ LTAP*"] -filter "direction == output"]
proc prog_ws {tp} {
  set pe [find_timing_paths -through $tp -path_delay max]
  if {[llength $pe]} { return [[lindex $pe 0] slack] } else { return none }
}
puts "WHATIF_BEFORE setup_ws=[sta::worst_slack_cmd max] hold_ws=[sta::worst_slack_cmd min] prog_ws=[prog_ws $tp]"
# spine roots: drivers of every net that has an LTAP* input pin
set roots [dict create]
foreach inst [$blk getInsts] {
  if {![string match LTAP* [[$inst getMaster] getName]]} { continue }
  foreach it [$inst getITerms] {
    if {[[$it getMTerm] getIoType] ne "INPUT"} { continue }
    set net [$it getNet]
    if {$net eq "NULL"} { continue }
    foreach d [$net getITerms] {
      if {[$d isOutputSignal]} { dict set roots [[$d getInst] getName] [[[$d getInst] getMaster] getName] }
    }
  }
}
set hist [dict create]; set darea 0.0; set n 0
dict for {name master} $roots {
  dict incr hist $master
  if {[regexp {^(sky130_fd_sc_hd__(?:dfxtp|clkinv|inv|buf|clkbuf))_(\d+)$} $master -> fam drive] && $drive < 4} {
    set new ${fam}_4
    set a0 [get_property [get_lib_cells */$master] area]
    set a1 [get_property [get_lib_cells */$new] area]
    replace_cell [get_cells $name] [get_lib_cells */$new]
    set darea [expr {$darea + $a1 - $a0}]; incr n
  }
}
puts "WHATIF_ROOTS n_roots=[dict size $roots] upsized=$n delta_area_um2=[format %.4f $darea] masters=$hist"
estimate_parasitics -placement
puts "WHATIF_AFTER setup_ws=[sta::worst_slack_cmd max] hold_ws=[sta::worst_slack_cmd min] prog_ws=[prog_ws $tp]"
report_checks -path_delay max -fields {cap slew fanout} -digits 3
exit
