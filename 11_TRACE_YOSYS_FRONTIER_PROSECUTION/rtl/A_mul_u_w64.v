module top(input [63:0] a, input [63:0] b, output [127:0] y);
  assign y = a * b;
endmodule
