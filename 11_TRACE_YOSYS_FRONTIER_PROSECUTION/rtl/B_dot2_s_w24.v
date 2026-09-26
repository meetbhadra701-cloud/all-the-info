module top(input signed [23:0] a, input signed [23:0] b, input signed [23:0] c, input signed [23:0] d, output signed [48:0] y);
  assign y = a * b + c * d;
endmodule
