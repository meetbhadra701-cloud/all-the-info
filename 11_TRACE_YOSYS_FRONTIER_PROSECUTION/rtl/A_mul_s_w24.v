module top(input signed [23:0] a, input signed [23:0] b, output signed [47:0] y);
  assign y = a * b;
endmodule
