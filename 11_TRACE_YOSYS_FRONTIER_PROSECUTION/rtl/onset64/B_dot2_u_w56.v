module top(input [55:0] a, input [55:0] b, input [55:0] c, input [55:0] d, output [112:0] y);
  assign y = a * b + c * d;
endmodule
