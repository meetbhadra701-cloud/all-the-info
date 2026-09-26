module top(input [7:0] a, input [7:0] b, input [31:0] c, output [31:0] y);
  assign y = c - a * b;
endmodule
