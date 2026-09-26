module top(input signed [9:0] a, input signed [9:0] b, output signed [19:0] y);
  assign y = a * b;
endmodule
