module top(input [7:0] a, input [7:0] b, output [15:0] y);
  assign y = (a * b) ^ ({16{1'b0}} | ((a[0] & b[7]) << 5));
endmodule
