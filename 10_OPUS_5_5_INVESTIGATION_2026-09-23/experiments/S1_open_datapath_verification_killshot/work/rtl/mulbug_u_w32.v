module top(input [31:0] a, input [31:0] b, output [63:0] y);
  assign y = (a * b) ^ ({64{1'b0}} | ((a[0] & b[31]) << 5));
endmodule
