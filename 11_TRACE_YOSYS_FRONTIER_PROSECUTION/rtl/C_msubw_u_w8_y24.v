module top(input [7:0] a, input [7:0] b, input [23:0] c, output [23:0] y);
  assign y = c - a * b;
endmodule
