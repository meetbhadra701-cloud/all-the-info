module top(input [7:0] x, output [8:0] y);
  wire signed [8:0] s = -$signed(x);
  assign y = s;
endmodule
