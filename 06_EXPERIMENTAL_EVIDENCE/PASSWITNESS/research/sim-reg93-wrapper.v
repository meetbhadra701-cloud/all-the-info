module simtop(gold_y, gate_y, gold_slice, gate_slice);
  output wire [300:0] gold_y;
  output wire [300:0] gate_y;
  output wire [14:0] gold_slice;
  output wire [14:0] gate_slice;
  wire clk = 1'b0;
  wire [14:0] wire0 = 15'b0;
  wire [8:0] wire1 = 9'b0;
  wire signed [18:0] wire2 = 19'b0;
  wire [16:0] wire3 = 17'b0;
  gold_top gold(gold_y, clk, wire0, wire1, wire2, wire3);
  gate_top gate(gate_y, clk, wire0, wire1, wire2, wire3);
  assign gold_slice = gold_y[254:240];
  assign gate_slice = gate_y[254:240];
endmodule
