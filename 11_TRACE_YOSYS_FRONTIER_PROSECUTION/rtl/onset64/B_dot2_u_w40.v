module top(input [39:0] a, input [39:0] b, input [39:0] c, input [39:0] d, output [80:0] y);
  assign y = a * b + c * d;
endmodule
