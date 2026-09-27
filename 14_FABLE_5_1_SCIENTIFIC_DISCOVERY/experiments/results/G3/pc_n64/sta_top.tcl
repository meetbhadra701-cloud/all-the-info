read_lef /OpenROAD-flow-scripts/flow/platforms/sky130hd/lef/sky130_fd_sc_hd.tlef
read_lef /OpenROAD-flow-scripts/flow/platforms/sky130hd/lef/sky130_fd_sc_hd_merged.lef
read_liberty /OpenROAD-flow-scripts/flow/platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
read_verilog netlist.v
link_design top
create_clock -name clk -period 3.0 [get_ports clk]
set_input_delay 0 -clock clk [delete_from_list [all_inputs] [get_ports clk]]
set_output_delay 0 -clock clk [all_outputs]
set_load 0.005 [all_outputs]
puts "WS [sta::worst_slack_cmd max]"
report_checks -path_delay max -group_path_count 1 -format end
report_checks -path_delay max -fields {fanout} -digits 2 > crit.rpt
puts "AREA [rsz::design_area]"
exit
