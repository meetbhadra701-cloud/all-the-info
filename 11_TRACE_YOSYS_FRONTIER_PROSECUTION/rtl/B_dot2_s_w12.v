module top(input signed [11:0] a, input signed [11:0] b, input signed [11:0] c, input signed [11:0] d, output signed [24:0] y);
  assign y = a * b + c * d;
endmodule
