module top(input [11:0] a, input [11:0] b, input [23:0] c, output [24:0] y);
  assign y = a * b + c;
endmodule
