module top(input signed [15:0] a, input signed [15:0] b, input signed [39:0] c, output signed [39:0] y);
  assign y = a * b + c;
endmodule
