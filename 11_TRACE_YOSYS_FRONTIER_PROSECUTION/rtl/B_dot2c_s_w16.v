module top(input signed [15:0] a, input signed [15:0] b, input signed [15:0] c, input signed [15:0] d, input signed [31:0] e, output signed [33:0] y);
  assign y = a * b + c * d + e;
endmodule
