module top(input [15:0] a, input [15:0] b, input [15:0] c, input [15:0] d, output [32:0] y);
  assign y = a * b + c * d + 1;
endmodule
