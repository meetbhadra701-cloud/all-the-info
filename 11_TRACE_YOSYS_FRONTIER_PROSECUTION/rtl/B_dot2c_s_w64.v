module top(input signed [63:0] a, input signed [63:0] b, input signed [63:0] c, input signed [63:0] d, input signed [127:0] e, output signed [129:0] y);
  assign y = a * b + c * d + e;
endmodule
