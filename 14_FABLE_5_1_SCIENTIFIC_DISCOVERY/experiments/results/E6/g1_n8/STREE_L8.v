module STREE_L8(input clk, input start, input [7:0] x, output y);
  reg s0, c0; wire z0 = start ? 1'b0 : c0;
  always @(posedge clk) begin s0 <= x[0] ^ x[1] ^ z0; c0 <= (x[0] & x[1]) | (x[0] & z0) | (x[1] & z0); end
  reg s1, c1; wire z1 = start ? 1'b0 : c1;
  always @(posedge clk) begin s1 <= x[2] ^ x[3] ^ z1; c1 <= (x[2] & x[3]) | (x[2] & z1) | (x[3] & z1); end
  reg s2, c2; wire z2 = start ? 1'b0 : c2;
  always @(posedge clk) begin s2 <= x[4] ^ x[5] ^ z2; c2 <= (x[4] & x[5]) | (x[4] & z2) | (x[5] & z2); end
  reg s3, c3; wire z3 = start ? 1'b0 : c3;
  always @(posedge clk) begin s3 <= x[6] ^ x[7] ^ z3; c3 <= (x[6] & x[7]) | (x[6] & z3) | (x[7] & z3); end
  reg st2; always @(posedge clk) st2 <= start;
  reg s4, c4; wire z4 = st2 ? 1'b0 : c4;
  always @(posedge clk) begin s4 <= s0 ^ s1 ^ z4; c4 <= (s0 & s1) | (s0 & z4) | (s1 & z4); end
  reg s5, c5; wire z5 = st2 ? 1'b0 : c5;
  always @(posedge clk) begin s5 <= s2 ^ s3 ^ z5; c5 <= (s2 & s3) | (s2 & z5) | (s3 & z5); end
  reg st3; always @(posedge clk) st3 <= st2;
  reg s6, c6; wire z6 = st3 ? 1'b0 : c6;
  always @(posedge clk) begin s6 <= s4 ^ s5 ^ z6; c6 <= (s4 & s5) | (s4 & z6) | (s5 & z6); end
  assign y = s6;
endmodule
