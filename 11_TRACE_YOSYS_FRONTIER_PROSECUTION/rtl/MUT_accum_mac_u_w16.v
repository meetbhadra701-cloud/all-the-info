module top(input [15:0] a, input [15:0] b, input [31:0] c, output [32:0] y);
  wire [31:0] s = a * b + c;
  assign y = {1'b0, s};
endmodule
