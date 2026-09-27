# Gate 2: program a FIXED base with one weight matrix and route ONLY the programmable layers.
# env: BASE_ODB (routed base, all base wiring <= met3), PROG_TCL (defines g2_apply_program), OUT (prefix), MODE (route|sta)
# MODE route : every base net is deleted (its wires are all <= met3 by construction, cells/placement untouched),
#              the via program creates the programmable nets, and they are routed on met4-met5 only.
# MODE sta   : the program is applied to the intact base; placement-parasitic STA at the base SDC clock (MODELED
#              timing), then the complete programmed netlist is written for functional verification.
read_db $::env(BASE_ODB)
set blk [ord::get_db_block]
# dont_touch protected the via sites / line taps during the base flow; programming = exactly the operations it blocks
# (connecting programmable pins, swapping to the identical-footprint ZERO/ONE master). Nothing is moved or resized.
foreach inst [$blk getInsts] { if {[$inst isDoNotTouch]} { $inst setDoNotTouch 0 } }
foreach net [$blk getNets] { if {[$net isDoNotTouch]} { $net setDoNotTouch 0 } }
source $::env(PROG_TCL)
if {$::env(MODE) eq "route" || $::env(MODE) eq "grt"} {
  set gone 0
  foreach net [$blk getNets] {
    set t [$net getSigType]
    if {$t ne "POWER" && $t ne "GROUND"} { odb::dbNet_destroy $net; incr gone }
  }
  puts "G2: removed $gone base nets (all base wiring is at or below met3)"
  g2_apply_program
  set np 0; set nterm 0
  foreach net [$blk getNets] { if {[string match pgm_* [$net getName]]} { incr np; incr nterm [llength [$net getITerms]] } }
  puts "G2: programmable nets $np, pins $nterm"
  set_routing_layers -signal met4-met5 -clock met4-met5   ;# both ranges, or GRT's min layer stays at met2
  global_route -congestion_iterations 30 -verbose -allow_congestion -congestion_report_file $::env(OUT)_congestion.rpt
  if {$::env(MODE) eq "grt"} { puts "G2_GRT done"; exit }
  detailed_route -output_drc $::env(OUT)_drc.rpt -droute_end_iter $::env(DRT_ITERS) -verbose 1
  set drc [detailed_route_num_drvs]
  puts "G2_RESULT drc=$drc"
  write_def $::env(OUT)_program.def
  check_antennas -report_file $::env(OUT)_antenna.rpt
} else {
  read_liberty /OpenROAD-flow-scripts/flow/platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
  read_liberty /work/cells/g2_cells.lib
  g2_apply_program
  read_sdc $::env(BASE_SDC)
  source /OpenROAD-flow-scripts/flow/platforms/sky130hd/setRC.tcl
  set_propagated_clock [all_clocks]
  estimate_parasitics -placement
  puts "G2_TIMING setup_ws=[sta::worst_slack_cmd max] hold_ws=[sta::worst_slack_cmd min]"
  if {[info exists ::env(REPORT_PATHS)] && $::env(REPORT_PATHS)} {
    report_checks -path_delay max -fields {slew cap fanout} -digits 3
    report_net -digits 3 [get_nets -of_objects [get_pins -of_objects [get_cells -filter "ref_name == LTAP"] -filter "direction == output"]] > $::env(OUT)_ltap_nets.rpt
  }
  set phys {}
  foreach lib [[ord::get_db] getLibs] { foreach m [$lib getMasters] {
    set sig 0; foreach mt [$m getMTerms] { if {[$mt getSigType] ne "POWER" && [$mt getSigType] ne "GROUND"} { set sig 1 } }
    if {!$sig} { lappend phys [$m getName] } } }
  write_verilog -remove_cells $phys $::env(OUT)_programmed.v
}
exit
