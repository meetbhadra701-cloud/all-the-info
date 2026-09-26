module top(input signed [7:0] a, input signed [7:0] b, input signed [15:0] c, output signed [16:0] y);
  assign y = c - a * b;
endmodule
