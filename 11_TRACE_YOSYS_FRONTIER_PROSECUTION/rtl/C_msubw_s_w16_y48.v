module top(input signed [15:0] a, input signed [15:0] b, input signed [47:0] c, output signed [47:0] y);
  assign y = c - a * b;
endmodule
