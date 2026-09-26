module top(input [31:0] a, input [31:0] b, input [63:0] c, output [64:0] y);
  wire [63:0] s = a * b + c;
  assign y = {1'b0, s};
endmodule
