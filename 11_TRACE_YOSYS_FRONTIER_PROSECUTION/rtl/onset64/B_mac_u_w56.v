module top(input [55:0] a, input [55:0] b, input [111:0] c, output [112:0] y);
  assign y = a * b + c;
endmodule
