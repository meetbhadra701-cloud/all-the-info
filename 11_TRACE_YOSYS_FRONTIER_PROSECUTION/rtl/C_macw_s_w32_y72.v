module top(input signed [31:0] a, input signed [31:0] b, input signed [71:0] c, output signed [71:0] y);
  assign y = a * b + c;
endmodule
