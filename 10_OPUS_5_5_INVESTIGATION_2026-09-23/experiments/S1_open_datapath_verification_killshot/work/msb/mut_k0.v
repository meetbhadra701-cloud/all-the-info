module top(input [7:0] a, input [7:0] b, input [15:0] c, output [16:0] y);
  wire [16:0] good = a * b + c;
  assign y = good ^ ((a[0] & b[7]) ? (17'd1 << 0) : 17'd0);
endmodule
