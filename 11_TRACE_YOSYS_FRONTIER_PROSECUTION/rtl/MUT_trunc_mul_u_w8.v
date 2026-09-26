module top(input [7:0] a, input [7:0] b, output [15:0] y);
  wire [14:0] p = a * b;
  assign y = {1'b0, p};
endmodule
