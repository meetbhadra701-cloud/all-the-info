module top(input [23:0] a, input [23:0] b, input [47:0] c, output [48:0] y);
  assign y = a * b + c;
endmodule
