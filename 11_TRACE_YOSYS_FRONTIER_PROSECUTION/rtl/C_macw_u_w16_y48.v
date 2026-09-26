module top(input [15:0] a, input [15:0] b, input [47:0] c, output [47:0] y);
  assign y = a * b + c;
endmodule
