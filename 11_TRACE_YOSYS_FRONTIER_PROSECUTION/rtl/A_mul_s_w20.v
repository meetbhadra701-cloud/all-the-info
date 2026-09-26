module top(input signed [19:0] a, input signed [19:0] b, output signed [39:0] y);
  assign y = a * b;
endmodule
