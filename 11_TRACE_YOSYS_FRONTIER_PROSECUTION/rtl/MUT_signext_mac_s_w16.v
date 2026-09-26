module top(input signed [15:0] a, input signed [15:0] b, input signed [31:0] c, output signed [32:0] y);
  wire [31:0] p = a * b;
  assign y = {1'b0, p} + c;
endmodule
