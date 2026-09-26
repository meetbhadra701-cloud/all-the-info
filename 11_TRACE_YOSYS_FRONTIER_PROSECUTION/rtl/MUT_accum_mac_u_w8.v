module top(input [7:0] a, input [7:0] b, input [15:0] c, output [16:0] y);
  wire [15:0] s = a * b + c;
  assign y = {1'b0, s};
endmodule
