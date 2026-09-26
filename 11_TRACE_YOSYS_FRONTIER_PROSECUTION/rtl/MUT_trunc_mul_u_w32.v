module top(input [31:0] a, input [31:0] b, output [63:0] y);
  wire [62:0] p = a * b;
  assign y = {1'b0, p};
endmodule
