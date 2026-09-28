# research_harness: STA of a placed/routed database at ONE corner (one session per corner, no MCMM state).
# Origin: ubpgen/resources/signoff_sta.tcl without the UBP tap/via-site probes; the output markers are unchanged, so
# harness.sta.parse_sta reads both.
# env: ODB, LIBS (space-separated: the corner's standard library + every custom library AT THAT CORNER), SDC, CORNER;
#      optional SPEF (extracted parasitics; without it: placement estimate with the platform setRC),
#      optional THROUGH (ref_name glob of a cell class, e.g. "LTAP*": worst setup path through its outputs)
read_db $::env(ODB)
foreach lib $::env(LIBS) { read_liberty $lib }
read_sdc $::env(SDC)
set_propagated_clock [all_clocks]
if {[info exists ::env(SPEF)] && $::env(SPEF) ne ""} {
  read_spef $::env(SPEF)
} else {
  source /OpenROAD-flow-scripts/flow/platforms/sky130hd/setRC.tcl
  estimate_parasitics -placement
}
set c $::env(CORNER)
puts "SIGNOFF_WS corner=$c setup=[sta::worst_slack_cmd max] hold=[sta::worst_slack_cmd min]"
puts "SIGNOFF_SETUP_PATH_BEGIN"
report_checks -path_delay max -group_path_count 1 -fields {cap slew fanout net} -digits 4
puts "SIGNOFF_SETUP_PATH_END"
puts "SIGNOFF_HOLD_PATH_BEGIN"
report_checks -path_delay min -group_path_count 1 -fields {net} -digits 4
puts "SIGNOFF_HOLD_PATH_END"
if {[info exists ::env(THROUGH)] && $::env(THROUGH) ne ""} {
  set tz [get_pins -quiet -of_objects [get_cells -quiet -filter "ref_name =~ $::env(THROUGH)"] -filter "direction == output"]
  set pe ""
  if {[llength $tz]} { set pe [lindex [find_timing_paths -through $tz -path_delay max -group_path_count 1] 0] }
  if {$pe ne ""} {
    puts "SIGNOFF_PROG_WS setup=[$pe slack]"
    puts "SIGNOFF_PROG_PATH_BEGIN"
    report_checks -through $tz -path_delay max -group_path_count 1 -fields {cap slew fanout net} -digits 4
    puts "SIGNOFF_PROG_PATH_END"
  } else { puts "SIGNOFF_PROG_WS setup=none" }
}
exit
