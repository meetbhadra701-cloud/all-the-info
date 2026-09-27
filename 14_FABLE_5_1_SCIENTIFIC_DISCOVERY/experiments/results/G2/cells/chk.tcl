read_lef /OpenROAD-flow-scripts/flow/platforms/sky130hd/lef/sky130_fd_sc_hd.tlef
read_lef /OpenROAD-flow-scripts/flow/platforms/sky130hd/lef/sky130_fd_sc_hd_merged.lef
read_lef g2_cells.lef
read_liberty /OpenROAD-flow-scripts/flow/platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
read_liberty g2_cells.lib
puts "masters: [llength [[ord::get_db] getLibs]]"
foreach c {VSITE_BUF VSITE_ZERO LTAP} { set m [[ord::get_db] findMaster $c]; puts "$c [$m getWidth] [$m getHeight] pins=[llength [$m getMTerms]]" }
exit
