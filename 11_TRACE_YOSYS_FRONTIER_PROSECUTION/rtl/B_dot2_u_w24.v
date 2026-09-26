module top(input [23:0] a, input [23:0] b, input [23:0] c, input [23:0] d, output [48:0] y);
  assign y = a * b + c * d;
endmodule
