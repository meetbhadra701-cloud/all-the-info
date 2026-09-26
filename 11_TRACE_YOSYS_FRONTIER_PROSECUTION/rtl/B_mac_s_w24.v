module top(input signed [23:0] a, input signed [23:0] b, input signed [47:0] c, output signed [48:0] y);
  assign y = a * b + c;
endmodule
