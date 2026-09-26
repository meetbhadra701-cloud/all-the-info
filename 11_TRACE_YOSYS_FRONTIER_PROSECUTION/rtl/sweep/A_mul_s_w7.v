module top(input signed [6:0] a, input signed [6:0] b, output signed [13:0] y);
  assign y = a * b;
endmodule
