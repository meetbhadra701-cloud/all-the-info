module top(input signed [31:0] a, input signed [31:0] b, input signed [63:0] c, output signed [64:0] y);
  assign y = a * b + c;
endmodule
