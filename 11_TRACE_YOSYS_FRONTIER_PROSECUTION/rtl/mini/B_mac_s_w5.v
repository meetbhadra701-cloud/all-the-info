module top(input signed [4:0] a, input signed [4:0] b, input signed [9:0] c, output signed [10:0] y);
  assign y = a * b + c;
endmodule
