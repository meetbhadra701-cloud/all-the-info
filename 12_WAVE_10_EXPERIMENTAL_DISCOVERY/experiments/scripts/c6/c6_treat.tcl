# Wave 10 / C6: apply one post-placement timing treatment to the ORFS 3_place.odb and measure it.
# Env: C6_MODE = none | resynth | annealing | genetic | repair_timing | annealing_repair
#      C6_SEED (annealing/genetic), C6_ITERS (optional), C6_OUT (output dir, absolute)
# Metrics use the placement parasitics estimate (estimate_parasitics -placement), the setting the rmp docs name for these commands.
source $::env(SCRIPTS_DIR)/load.tcl
# C6_STAGE=unplaced loads the synthesized netlist with ideal wires (the blog example's setting, Amendment 1)
set unplaced [expr {[info exists ::env(C6_STAGE)] && $::env(C6_STAGE) eq "unplaced"}]
if {$unplaced} { load_design 1_synth.v 1_synth.sdc } else { load_design 3_place.odb 3_place.sdc }
set out $::env(C6_OUT)
file mkdir $out
set mode $::env(C6_MODE)
set seed [expr {[info exists ::env(C6_SEED)] ? $::env(C6_SEED) : 1}]

proc c6_metrics {tag} {
  global unplaced
  if {!$unplaced} { estimate_parasitics -placement }
  set wns [sta::worst_slack -max]
  set tns [sta::total_negative_slack -max]
  set area [expr {[rsz::design_area] * 1e12}]
  set ninst [llength [get_cells *]]
  return [format "\"%s_wns\": %.4f, \"%s_tns\": %.4f, \"%s_area\": %.6f, \"%s_inst\": %d" $tag $wns $tag $tns $tag $area $tag $ninst]
}

set m0 [c6_metrics before]
write_verilog $out/before.v
set t0 [clock milliseconds]
switch -- $mode {
  none          { }
  resynth       { resynth }
  annealing     { if {[info exists ::env(C6_ITERS)]} { resynth_annealing -seed $seed -iters $::env(C6_ITERS) } else { resynth_annealing -seed $seed } }
  genetic       { if {[info exists ::env(C6_ITERS)]} { resynth_genetic -seed $seed -iters $::env(C6_ITERS) } else { resynth_genetic -seed $seed } }
  repair_timing { repair_timing -setup }
  annealing_repair { resynth_annealing -seed $seed; estimate_parasitics -placement; repair_timing -setup }
  default       { error "unknown C6_MODE $mode" }
}
set dt [expr {([clock milliseconds] - $t0) / 1000.0}]
set m1 [c6_metrics after]
write_verilog $out/after.v
write_db $out/after.odb
set fh [open $out/metrics.json w]
puts $fh [format "{\"mode\": \"%s\", \"seed\": %s, %s, %s, \"seconds\": %.3f}" $mode $seed $m0 $m1 $dt]
close $fh
puts "C6_DONE [format {mode=%s seed=%s} $mode $seed]"
