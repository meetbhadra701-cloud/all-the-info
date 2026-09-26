module top(input [47:0] a, input [47:0] b, input [95:0] c, output [96:0] y);
  assign y = a * b + c;
endmodule
