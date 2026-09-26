module top(input [23:0] a, input [23:0] b, output [47:0] y);
  assign y = (a * b) ^ ({48{1'b0}} | ((a[0] & b[23]) << 5));
endmodule
