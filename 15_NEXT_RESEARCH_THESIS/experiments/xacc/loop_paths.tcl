# XACC-E2 diagnostic (pre-registered as reported, never decisive): worst setup slack of paths ending at the
# accumulator registers (the loop stage), at one corner. env: ODB, LIBS, SDC, SPEF, CORNER
read_db $::env(ODB)
foreach lib $::env(LIBS) { read_liberty $lib }
read_sdc $::env(SDC)
set_propagated_clock [all_clocks]
read_spef $::env(SPEF)
set regs [get_cells -quiet {*acc*}]
set d [get_pins -quiet -of_objects $regs -filter "direction == input"]
set pe [lindex [find_timing_paths -to $d -path_delay max -group_path_count 1] 0]
if {$pe ne ""} { puts "LOOP_WS corner=$::env(CORNER) setup=[$pe slack] regs=[llength $regs]" } else { puts "LOOP_WS none" }
set all [lindex [find_timing_paths -path_delay max -group_path_count 1] 0]
puts "ALL_WS corner=$::env(CORNER) setup=[$all slack]"
exit
