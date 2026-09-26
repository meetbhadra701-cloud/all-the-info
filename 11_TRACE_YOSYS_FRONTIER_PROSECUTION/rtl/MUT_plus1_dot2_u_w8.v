module top(input [7:0] a, input [7:0] b, input [7:0] c, input [7:0] d, output [16:0] y);
  assign y = a * b + c * d + 1;
endmodule
