module CTRL(input clk, input start, output [7:0] ph);
  reg s1; reg [7:0] r;
  always @(posedge clk) begin s1 <= start;  r <= {r[6:0], s1}; end
  assign ph = r;
endmodule
