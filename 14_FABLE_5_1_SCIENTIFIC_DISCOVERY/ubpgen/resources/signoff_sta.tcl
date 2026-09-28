# ubpgen sign-off, step 2: STA of the merged, extracted database at ONE corner.
# env: ODB, LIBS (space-separated, the corner's standard + custom libraries), SDC, SPEF, CORNER
read_db $::env(ODB)
foreach lib $::env(LIBS) { read_liberty $lib }
read_sdc $::env(SDC)
set_propagated_clock [all_clocks]
read_spef $::env(SPEF)
set c $::env(CORNER)
puts "SIGNOFF_WS corner=$c setup=[sta::worst_slack_cmd max] hold=[sta::worst_slack_cmd min]"
proc path_rows {pe} {
  set rows {}
  foreach pin [[$pe path] pins] { lappend rows [get_full_name $pin] }
  return $rows
}
# worst setup path (full report parsed in Python), worst hold path endpoint
puts "SIGNOFF_SETUP_PATH_BEGIN"
report_checks -path_delay max -group_path_count 1 -fields {cap slew fanout net} -digits 4
puts "SIGNOFF_SETUP_PATH_END"
puts "SIGNOFF_HOLD_PATH_BEGIN"
report_checks -path_delay min -group_path_count 1 -fields {net} -digits 4
puts "SIGNOFF_HOLD_PATH_END"
# worst setup slack through the programmable nets (tap outputs), and its path
set tz [get_pins -of_objects [get_cells -filter "ref_name =~ LTAP*"] -filter "direction == output"]
set pe [lindex [find_timing_paths -through $tz -path_delay max -group_path_count 1] 0]
if {$pe ne ""} {
  puts "SIGNOFF_PROG_WS setup=[$pe slack]"
  puts "SIGNOFF_PROG_PATH_BEGIN"
  report_checks -through $tz -path_delay max -group_path_count 1 -fields {cap slew fanout net} -digits 4
  puts "SIGNOFF_PROG_PATH_END"
} else { puts "SIGNOFF_PROG_WS setup=none" }
# transitions at the tap inputs (spine quality) and at the connected via-site inputs (programmable nets)
set ta [get_pins -of_objects [get_cells -filter "ref_name =~ LTAP*"] -filter "direction == input"]
set worst_ta 0.0; set worst_ta_pin ""
foreach p $ta { set s [get_property $p slew_max]; if {$s > $worst_ta} { set worst_ta $s; set worst_ta_pin [get_full_name $p] } }
set worst_va 0.0; set worst_va_pin ""
foreach p [get_pins -of_objects [get_cells -filter "ref_name == VSITE_BUF"] -filter "direction == input"] {
  if {[get_nets -quiet -of_objects $p] eq ""} { continue }
  set s [get_property $p slew_max]; if {$s > $worst_va} { set worst_va $s; set worst_va_pin [get_full_name $p] }
}
puts "SIGNOFF_SLEW tap_input_max=$worst_ta tap_input_pin=$worst_ta_pin site_input_max=$worst_va site_input_pin=$worst_va_pin"
# the spine drivers actually in the routed base (masters driving the tap inputs)
set hist [dict create]
foreach p $ta {
  set n [get_nets -of_objects $p]
  foreach d [get_pins -of_objects $n -filter "direction == output"] { dict incr hist [get_property [get_cells -of_objects $d] ref_name] }
}
puts "SIGNOFF_SPINE_DRIVERS [dict get $hist]"
exit
