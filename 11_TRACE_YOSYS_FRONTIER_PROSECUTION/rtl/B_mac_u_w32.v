module top(input [31:0] a, input [31:0] b, input [63:0] c, output [64:0] y);
  assign y = a * b + c;
endmodule
