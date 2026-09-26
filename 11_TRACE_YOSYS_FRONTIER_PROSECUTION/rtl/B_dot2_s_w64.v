module top(input signed [63:0] a, input signed [63:0] b, input signed [63:0] c, input signed [63:0] d, output signed [128:0] y);
  assign y = a * b + c * d;
endmodule
