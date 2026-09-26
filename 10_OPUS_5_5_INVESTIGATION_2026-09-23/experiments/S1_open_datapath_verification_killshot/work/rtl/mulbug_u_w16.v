module top(input [15:0] a, input [15:0] b, output [31:0] y);
  assign y = (a * b) ^ ({32{1'b0}} | ((a[0] & b[15]) << 5));
endmodule
