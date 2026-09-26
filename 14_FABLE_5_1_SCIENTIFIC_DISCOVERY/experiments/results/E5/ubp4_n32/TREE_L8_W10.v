module TREE_L8_W10(input [79:0] x, output [12:0] y);
  wire signed [9:0] l0 = x[9:0];
  wire signed [9:0] l1 = x[19:10];
  wire signed [9:0] l2 = x[29:20];
  wire signed [9:0] l3 = x[39:30];
  wire signed [9:0] l4 = x[49:40];
  wire signed [9:0] l5 = x[59:50];
  wire signed [9:0] l6 = x[69:60];
  wire signed [9:0] l7 = x[79:70];
  wire signed [12:0] t0 = l0 + l1;
  wire signed [12:0] t1 = l2 + l3;
  wire signed [12:0] t2 = l4 + l5;
  wire signed [12:0] t3 = l6 + l7;
  wire signed [12:0] t4 = t0 + t1;
  wire signed [12:0] t5 = t2 + t3;
  wire signed [12:0] t6 = t4 + t5;
  wire signed [12:0] s = t6;
  assign y = s;
endmodule
