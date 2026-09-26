module top(input [15:0] a0, input [15:0] b0, input [15:0] a1, input [15:0] b1, output [32:0] y);
  assign y = (a0 * b0 + a1 * b1) ^ ({33{1'b0}} | ((a0[0] & b1[15]) << 3));
endmodule
