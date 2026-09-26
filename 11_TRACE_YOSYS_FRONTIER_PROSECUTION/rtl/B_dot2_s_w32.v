module top(input signed [31:0] a, input signed [31:0] b, input signed [31:0] c, input signed [31:0] d, output signed [64:0] y);
  assign y = a * b + c * d;
endmodule
