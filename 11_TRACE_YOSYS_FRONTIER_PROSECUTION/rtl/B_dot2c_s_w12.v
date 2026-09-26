module top(input signed [11:0] a, input signed [11:0] b, input signed [11:0] c, input signed [11:0] d, input signed [23:0] e, output signed [25:0] y);
  assign y = a * b + c * d + e;
endmodule
