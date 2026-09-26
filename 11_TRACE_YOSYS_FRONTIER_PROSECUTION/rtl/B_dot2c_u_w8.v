module top(input [7:0] a, input [7:0] b, input [7:0] c, input [7:0] d, input [15:0] e, output [17:0] y);
  assign y = a * b + c * d + e;
endmodule
