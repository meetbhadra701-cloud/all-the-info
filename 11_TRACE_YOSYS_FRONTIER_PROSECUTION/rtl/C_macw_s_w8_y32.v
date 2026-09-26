module top(input signed [7:0] a, input signed [7:0] b, input signed [31:0] c, output signed [31:0] y);
  assign y = a * b + c;
endmodule
