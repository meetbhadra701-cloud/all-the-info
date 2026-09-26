module top(input [63:0] a, input [63:0] b, input [127:0] c, output [128:0] y);
  assign y = a * b + c;
endmodule
