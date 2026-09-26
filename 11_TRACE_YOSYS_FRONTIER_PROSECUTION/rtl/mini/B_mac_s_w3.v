module top(input signed [2:0] a, input signed [2:0] b, input signed [5:0] c, output signed [6:0] y);
  assign y = a * b + c;
endmodule
