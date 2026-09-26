module STREE_L16(input clk, input start, input [15:0] x, output y);
  reg s0, c0; wire z0 = start ? 1'b0 : c0;
  always @(posedge clk) begin s0 <= x[0] ^ x[1] ^ z0; c0 <= (x[0] & x[1]) | (x[0] & z0) | (x[1] & z0); end
  reg s1, c1; wire z1 = start ? 1'b0 : c1;
  always @(posedge clk) begin s1 <= x[2] ^ x[3] ^ z1; c1 <= (x[2] & x[3]) | (x[2] & z1) | (x[3] & z1); end
  reg s2, c2; wire z2 = start ? 1'b0 : c2;
  always @(posedge clk) begin s2 <= x[4] ^ x[5] ^ z2; c2 <= (x[4] & x[5]) | (x[4] & z2) | (x[5] & z2); end
  reg s3, c3; wire z3 = start ? 1'b0 : c3;
  always @(posedge clk) begin s3 <= x[6] ^ x[7] ^ z3; c3 <= (x[6] & x[7]) | (x[6] & z3) | (x[7] & z3); end
  reg s4, c4; wire z4 = start ? 1'b0 : c4;
  always @(posedge clk) begin s4 <= x[8] ^ x[9] ^ z4; c4 <= (x[8] & x[9]) | (x[8] & z4) | (x[9] & z4); end
  reg s5, c5; wire z5 = start ? 1'b0 : c5;
  always @(posedge clk) begin s5 <= x[10] ^ x[11] ^ z5; c5 <= (x[10] & x[11]) | (x[10] & z5) | (x[11] & z5); end
  reg s6, c6; wire z6 = start ? 1'b0 : c6;
  always @(posedge clk) begin s6 <= x[12] ^ x[13] ^ z6; c6 <= (x[12] & x[13]) | (x[12] & z6) | (x[13] & z6); end
  reg s7, c7; wire z7 = start ? 1'b0 : c7;
  always @(posedge clk) begin s7 <= x[14] ^ x[15] ^ z7; c7 <= (x[14] & x[15]) | (x[14] & z7) | (x[15] & z7); end
  reg st2; always @(posedge clk) st2 <= start;
  reg s8, c8; wire z8 = st2 ? 1'b0 : c8;
  always @(posedge clk) begin s8 <= s0 ^ s1 ^ z8; c8 <= (s0 & s1) | (s0 & z8) | (s1 & z8); end
  reg s9, c9; wire z9 = st2 ? 1'b0 : c9;
  always @(posedge clk) begin s9 <= s2 ^ s3 ^ z9; c9 <= (s2 & s3) | (s2 & z9) | (s3 & z9); end
  reg s10, c10; wire z10 = st2 ? 1'b0 : c10;
  always @(posedge clk) begin s10 <= s4 ^ s5 ^ z10; c10 <= (s4 & s5) | (s4 & z10) | (s5 & z10); end
  reg s11, c11; wire z11 = st2 ? 1'b0 : c11;
  always @(posedge clk) begin s11 <= s6 ^ s7 ^ z11; c11 <= (s6 & s7) | (s6 & z11) | (s7 & z11); end
  reg st3; always @(posedge clk) st3 <= st2;
  reg s12, c12; wire z12 = st3 ? 1'b0 : c12;
  always @(posedge clk) begin s12 <= s8 ^ s9 ^ z12; c12 <= (s8 & s9) | (s8 & z12) | (s9 & z12); end
  reg s13, c13; wire z13 = st3 ? 1'b0 : c13;
  always @(posedge clk) begin s13 <= s10 ^ s11 ^ z13; c13 <= (s10 & s11) | (s10 & z13) | (s11 & z13); end
  reg st4; always @(posedge clk) st4 <= st3;
  reg s14, c14; wire z14 = st4 ? 1'b0 : c14;
  always @(posedge clk) begin s14 <= s12 ^ s13 ^ z14; c14 <= (s12 & s13) | (s12 & z14) | (s13 & z14); end
  assign y = s14;
endmodule
