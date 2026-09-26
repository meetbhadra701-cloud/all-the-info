module top(input signed [11:0] a, input signed [11:0] b, output signed [23:0] y);
  assign y = a * b;
endmodule
