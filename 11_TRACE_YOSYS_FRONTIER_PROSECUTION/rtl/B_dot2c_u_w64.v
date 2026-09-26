module top(input [63:0] a, input [63:0] b, input [63:0] c, input [63:0] d, input [127:0] e, output [129:0] y);
  assign y = a * b + c * d + e;
endmodule
