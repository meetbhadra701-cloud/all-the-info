module top(input [31:0] a0, input [31:0] b0, input [31:0] a1, input [31:0] b1, output [64:0] y);
  assign y = a0 * b0 + a1 * b1;
endmodule
