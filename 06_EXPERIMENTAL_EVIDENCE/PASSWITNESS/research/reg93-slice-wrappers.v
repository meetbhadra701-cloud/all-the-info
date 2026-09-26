module gold_reg93_slice(y, clk, wire0, wire1, wire2, wire3);
  output [14:0] y;
  input clk;
  input [14:0] wire0;
  input [8:0] wire1;
  input signed [18:0] wire2;
  input [16:0] wire3;
  wire [300:0] full_y;
  gold_top gold(.y(full_y), .clk(clk), .wire0(wire0), .wire1(wire1), .wire2(wire2), .wire3(wire3));
  assign y = full_y[254:240];
endmodule

module gate_reg93_slice(y, clk, wire0, wire1, wire2, wire3);
  output [14:0] y;
  input clk;
  input [14:0] wire0;
  input [8:0] wire1;
  input signed [18:0] wire2;
  input [16:0] wire3;
  wire [300:0] full_y;
  gate_top gate(.y(full_y), .clk(clk), .wire0(wire0), .wire1(wire1), .wire2(wire2), .wire3(wire3));
  assign y = full_y[254:240];
endmodule
