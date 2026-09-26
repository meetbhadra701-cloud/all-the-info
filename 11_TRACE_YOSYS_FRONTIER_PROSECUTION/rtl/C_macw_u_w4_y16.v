module top(input [3:0] a, input [3:0] b, input [15:0] c, output [15:0] y);
  assign y = a * b + c;
endmodule
