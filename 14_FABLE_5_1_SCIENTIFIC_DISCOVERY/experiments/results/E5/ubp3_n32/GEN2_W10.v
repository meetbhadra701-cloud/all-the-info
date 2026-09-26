module GEN2_W10(input [15:0] x, output [39:0] y);
  wire signed [7:0] i0 = x[7:0];
  wire signed [7:0] i1 = x[15:8];
  wire signed [9:0] p2 = i0 - i1;
  wire signed [9:0] p3 = i0 + i1;
  wire signed [9:0] o0 = i1;
  assign y[9:0] = o0;
  wire signed [9:0] o1 = i0;
  assign y[19:10] = o1;
  wire signed [9:0] o2 = p2;
  assign y[29:20] = o2;
  wire signed [9:0] o3 = p3;
  assign y[39:30] = o3;
endmodule
