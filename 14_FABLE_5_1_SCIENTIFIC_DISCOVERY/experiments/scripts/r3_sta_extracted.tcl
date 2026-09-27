# R3 timing with routed parasitics (rigor check of the pre-registered placement-parasitic model):
#   base nets  : the base's own extracted SPEF (ORFS 6_final.spef, OpenRCX on the routed met1-met3 base)
#   program    : lumped RC from each programmable net's ROUTED met4/met5 geometry (r3_prog_spef.py)
# env: BASE_ODB, BASE_SDC, BASE_SPEF, PROG_TCL, PROG_SPEF
read_liberty /OpenROAD-flow-scripts/flow/platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
read_liberty /work/cells/g2_cells.lib
read_liberty /work/cells/g2r3_cells.lib
read_db $::env(BASE_ODB)
set blk [ord::get_db_block]
foreach inst [$blk getInsts] { if {[$inst isDoNotTouch]} { $inst setDoNotTouch 0 } }
source $::env(PROG_TCL)
g2_apply_program
read_sdc $::env(BASE_SDC)
set_propagated_clock [all_clocks]
read_spef $::env(BASE_SPEF)
read_spef $::env(PROG_SPEF)
puts "R3X_TIMING setup_ws=[sta::worst_slack_cmd max] hold_ws=[sta::worst_slack_cmd min]"
set tp [get_pins -of_objects [get_cells -filter "ref_name =~ LTAP*"] -filter "direction == output"]
set pe [find_timing_paths -through $tp -path_delay max]
if {[llength $pe]} { puts "R3X_PROG_WS setup=[[lindex $pe 0] slack]" }
report_checks -through $tp -path_delay max -fields {cap slew} -digits 3
exit
