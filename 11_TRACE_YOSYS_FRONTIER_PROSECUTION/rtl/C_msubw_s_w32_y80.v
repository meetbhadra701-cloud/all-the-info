module top(input signed [31:0] a, input signed [31:0] b, input signed [79:0] c, output signed [79:0] y);
  assign y = c - a * b;
endmodule
