module top(input [23:0] a0, input [23:0] b0, input [23:0] a1, input [23:0] b1, output [48:0] y);
  assign y = a0 * b0 + a1 * b1;
endmodule
