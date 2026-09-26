module STREE_L3(input clk, input start, input [2:0] x, output y);
  reg s0, c0; wire z0 = start ? 1'b0 : c0;
  always @(posedge clk) begin s0 <= x[0] ^ x[1] ^ z0; c0 <= (x[0] & x[1]) | (x[0] & z0) | (x[1] & z0); end
  reg d1; always @(posedge clk) d1 <= x[2];
  reg st2; always @(posedge clk) st2 <= start;
  reg s2, c2; wire z2 = st2 ? 1'b0 : c2;
  always @(posedge clk) begin s2 <= s0 ^ d1 ^ z2; c2 <= (s0 & d1) | (s0 & z2) | (d1 & z2); end
  assign y = s2;
endmodule
