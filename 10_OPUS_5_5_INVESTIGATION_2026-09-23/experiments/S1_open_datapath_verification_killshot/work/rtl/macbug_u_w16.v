module top(input [15:0] a, input [15:0] b, input [31:0] c, output [32:0] y);
  assign y = (a * b + c) ^ ({33{1'b0}} | ((a[0] & b[15]) << 5));
endmodule
