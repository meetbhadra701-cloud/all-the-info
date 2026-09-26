module top(input [31:0] a, input [31:0] b, input [31:0] c, input [31:0] d, output [64:0] y);
  assign y = a * b + c * d + 1;
endmodule
