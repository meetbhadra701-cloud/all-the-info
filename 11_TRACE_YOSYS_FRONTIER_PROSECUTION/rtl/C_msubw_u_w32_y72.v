module top(input [31:0] a, input [31:0] b, input [71:0] c, output [71:0] y);
  assign y = c - a * b;
endmodule
