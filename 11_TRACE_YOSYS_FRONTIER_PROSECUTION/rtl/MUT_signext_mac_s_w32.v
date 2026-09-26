module top(input signed [31:0] a, input signed [31:0] b, input signed [63:0] c, output signed [64:0] y);
  wire [63:0] p = a * b;
  assign y = {1'b0, p} + c;
endmodule
