module top(input [8:0] x, output [9:0] y);
  wire signed [9:0] s = -$signed(x);
  assign y = s;
endmodule
