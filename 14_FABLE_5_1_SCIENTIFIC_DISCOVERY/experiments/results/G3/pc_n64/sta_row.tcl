read_lef /OpenROAD-flow-scripts/flow/platforms/sky130hd/lef/sky130_fd_sc_hd.tlef
read_lef /OpenROAD-flow-scripts/flow/platforms/sky130hd/lef/sky130_fd_sc_hd_merged.lef
read_liberty /OpenROAD-flow-scripts/flow/platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
read_verilog PROW_pc_L64_gl.v
link_design PROW_pc_L64
create_clock -name clk -period 3.0 [get_ports clk]
set_input_delay 0 -clock clk [delete_from_list [all_inputs] [get_ports clk]]
set_output_delay 0 -clock clk [all_outputs]
set_load 0.005 [all_outputs]
puts "WS_all [sta::worst_slack_cmd max]"
report_checks -path_delay max -group_path_count 3 -format end
report_checks -from [all_inputs] -path_delay max -format end
report_checks -from [all_registers -clock_pins] -to [all_registers -data_pins] -path_delay max -format end
exit
