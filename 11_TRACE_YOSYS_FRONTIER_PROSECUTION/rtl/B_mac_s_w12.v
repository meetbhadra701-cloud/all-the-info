module top(input signed [11:0] a, input signed [11:0] b, input signed [23:0] c, output signed [24:0] y);
  assign y = a * b + c;
endmodule
