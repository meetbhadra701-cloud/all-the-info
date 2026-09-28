# research_harness: OpenRCX extraction with the platform rules (process corner index 0), exactly as the ORFS final
# report does. Origin: ubpgen/resources/signoff_extract.tcl (the program-net count is optional here).
# env: ODB, or LEFS (space-separated) + DEF;  RCX_RULES, OUT_SPEF, OUT_ODB;  optional NET_PREFIX (nets to count)
if {[info exists ::env(ODB)] && $::env(ODB) ne ""} {
  read_db $::env(ODB)
} else {
  foreach lef $::env(LEFS) { read_lef $lef }
  read_def $::env(DEF)
}
define_process_corner -ext_model_index 0 X
set_extraction_rules_file $::env(RCX_RULES)
extract_parasitics
write_spef $::env(OUT_SPEF)
write_db $::env(OUT_ODB)
set blk [ord::get_db_block]
set pfx [expr {[info exists ::env(NET_PREFIX)] ? $::env(NET_PREFIX) : ""}]
set nw 0; set np 0
foreach net [$blk getNets] {
  if {[$net getWire] ne "NULL"} { incr nw }
  if {$pfx ne "" && [string match ${pfx}* [$net getName]]} { incr np }
}
puts "SIGNOFF_EXTRACT nets_with_wires=$nw pgm_nets=$np insts=[llength [$blk getInsts]]"
exit
