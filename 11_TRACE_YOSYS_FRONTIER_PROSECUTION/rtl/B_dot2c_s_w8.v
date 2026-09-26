module top(input signed [7:0] a, input signed [7:0] b, input signed [7:0] c, input signed [7:0] d, input signed [15:0] e, output signed [17:0] y);
  assign y = a * b + c * d + e;
endmodule
