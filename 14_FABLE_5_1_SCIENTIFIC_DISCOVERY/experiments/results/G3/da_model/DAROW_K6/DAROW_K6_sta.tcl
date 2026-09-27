read_lef /OpenROAD-flow-scripts/flow/platforms/sky130hd/lef/sky130_fd_sc_hd.tlef
read_lef /OpenROAD-flow-scripts/flow/platforms/sky130hd/lef/sky130_fd_sc_hd_merged.lef
read_liberty /OpenROAD-flow-scripts/flow/platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
read_verilog DAROW_K6_gl.v
link_design DAROW_K6
create_clock -name clk -period 100
set_input_delay 0 -clock clk [all_inputs]
set_output_delay 0 -clock clk [all_outputs]
set_load 0.005 [all_outputs]
puts "WS [sta::worst_slack_cmd max]"
puts "AREA [rsz::design_area]"
exit
