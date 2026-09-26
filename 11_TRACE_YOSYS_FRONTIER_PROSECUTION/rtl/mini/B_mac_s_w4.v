module top(input signed [3:0] a, input signed [3:0] b, input signed [7:0] c, output signed [8:0] y);
  assign y = a * b + c;
endmodule
