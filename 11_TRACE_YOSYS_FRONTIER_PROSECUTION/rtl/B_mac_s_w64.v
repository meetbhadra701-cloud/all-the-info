module top(input signed [63:0] a, input signed [63:0] b, input signed [127:0] c, output signed [128:0] y);
  assign y = a * b + c;
endmodule
