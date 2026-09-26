module top(input signed [5:0] a, input signed [5:0] b, input signed [11:0] c, output signed [12:0] y);
  assign y = a * b + c;
endmodule
