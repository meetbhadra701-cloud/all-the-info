module top(input signed [1:0] a, input signed [1:0] b, input signed [3:0] c, output signed [4:0] y);
  assign y = a * b + c;
endmodule
