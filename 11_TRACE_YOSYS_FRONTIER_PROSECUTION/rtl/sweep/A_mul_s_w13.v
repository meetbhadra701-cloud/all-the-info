module top(input signed [12:0] a, input signed [12:0] b, output signed [25:0] y);
  assign y = a * b;
endmodule
