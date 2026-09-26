module top(input [9:0] x, output [10:0] y);
  wire signed [10:0] s = -$signed(x);
  assign y = s;
endmodule
