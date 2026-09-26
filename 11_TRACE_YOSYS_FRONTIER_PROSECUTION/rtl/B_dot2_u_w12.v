module top(input [11:0] a, input [11:0] b, input [11:0] c, input [11:0] d, output [24:0] y);
  assign y = a * b + c * d;
endmodule
