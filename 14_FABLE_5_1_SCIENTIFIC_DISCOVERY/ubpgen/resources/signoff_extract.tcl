# ubpgen sign-off, step 1: the merged base + program database, extracted with OpenRCX exactly as the ORFS final report
# does (platform rules, process corner index 0). env: LEFS (space-separated), MERGED_DEF, RCX_RULES, OUT_SPEF, OUT_ODB
foreach lef $::env(LEFS) { read_lef $lef }
read_def $::env(MERGED_DEF)
define_process_corner -ext_model_index 0 X
set_extraction_rules_file $::env(RCX_RULES)
extract_parasitics
write_spef $::env(OUT_SPEF)
write_db $::env(OUT_ODB)
set blk [ord::get_db_block]
set nw 0; set np 0
foreach net [$blk getNets] {
  if {[$net getWire] ne "NULL"} { incr nw }
  if {[string match pgm_* [$net getName]]} { incr np }
}
puts "SIGNOFF_EXTRACT nets_with_wires=$nw pgm_nets=$np insts=[llength [$blk getInsts]]"
exit
