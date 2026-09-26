module top(input [15:0] a, input [15:0] b, input [39:0] c, output [39:0] y);
  assign y = c - a * b;
endmodule
