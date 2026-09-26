module top(input [3:0] a, input [3:0] b, input [23:0] c, output [23:0] y);
  assign y = c - a * b;
endmodule
