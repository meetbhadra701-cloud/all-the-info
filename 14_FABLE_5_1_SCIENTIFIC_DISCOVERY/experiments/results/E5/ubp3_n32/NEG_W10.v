module NEG_W10(input [9:0] x, output [9:0] y);
  wire signed [9:0] s = -$signed(x);
  assign y = s;
endmodule
