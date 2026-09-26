module top(input signed [31:0] a, input signed [31:0] b, output signed [63:0] y);
  assign y = a * b;
endmodule
