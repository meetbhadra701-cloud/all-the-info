module top(input signed [7:0] a, input signed [7:0] b, input signed [7:0] c, input signed [7:0] d, output signed [16:0] y);
  assign y = a * b + c * d;
endmodule
