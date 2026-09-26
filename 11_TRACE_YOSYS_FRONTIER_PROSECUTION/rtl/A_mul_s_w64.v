module top(input signed [63:0] a, input signed [63:0] b, output signed [127:0] y);
  assign y = a * b;
endmodule
