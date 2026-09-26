module top(input [47:0] a, input [47:0] b, input [47:0] c, input [47:0] d, output [96:0] y);
  assign y = a * b + c * d;
endmodule
