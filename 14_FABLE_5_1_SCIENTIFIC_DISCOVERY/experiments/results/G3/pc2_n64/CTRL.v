module CTRL(input clk, input start, output [7:0] ph);
  reg s1, s2; reg [7:0] r;
  always @(posedge clk) begin s1 <= start; s2 <= s1; r <= {r[6:0], s2}; end
  assign ph = r;
endmodule
