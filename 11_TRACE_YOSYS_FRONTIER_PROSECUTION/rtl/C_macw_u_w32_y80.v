module top(input [31:0] a, input [31:0] b, input [79:0] c, output [79:0] y);
  assign y = a * b + c;
endmodule
