module top(input signed [13:0] a, input signed [13:0] b, output signed [27:0] y);
  assign y = a * b;
endmodule
