module top(input signed [14:0] a, input signed [14:0] b, output signed [29:0] y);
  assign y = a * b;
endmodule
