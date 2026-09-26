module top(input signed [31:0] a, input signed [31:0] b, input signed [31:0] c, input signed [31:0] d, input signed [63:0] e, output signed [65:0] y);
  assign y = a * b + c * d + e;
endmodule
