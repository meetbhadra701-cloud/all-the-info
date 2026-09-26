module NEG_W8(input [7:0] x, output [7:0] y);
  wire signed [7:0] s = -$signed(x);
  assign y = s;
endmodule
