module top(input [15:0] a, input [15:0] b, output [31:0] y);
  wire [30:0] p = a * b;
  assign y = {1'b0, p};
endmodule
