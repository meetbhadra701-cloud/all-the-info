module top(input [31:0] a, input [31:0] b, input [31:0] c, input [31:0] d, input [63:0] e, output [65:0] y);
  assign y = a * b + c * d + e;
endmodule
