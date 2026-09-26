module top(input [39:0] a, input [39:0] b, input [79:0] c, output [80:0] y);
  assign y = a * b + c;
endmodule
