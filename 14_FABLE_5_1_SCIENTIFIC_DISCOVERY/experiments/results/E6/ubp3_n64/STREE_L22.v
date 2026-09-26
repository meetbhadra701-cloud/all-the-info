module STREE_L22(input clk, input start, input [21:0] x, output y);
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
  reg s8, c8; wire z8 = start ? 1'b0 : c8;
  always @(posedge clk) begin s8 <= x[16] ^ x[17] ^ z8; c8 <= (x[16] & x[17]) | (x[16] & z8) | (x[17] & z8); end
  reg s9, c9; wire z9 = start ? 1'b0 : c9;
  always @(posedge clk) begin s9 <= x[18] ^ x[19] ^ z9; c9 <= (x[18] & x[19]) | (x[18] & z9) | (x[19] & z9); end
  reg s10, c10; wire z10 = start ? 1'b0 : c10;
  always @(posedge clk) begin s10 <= x[20] ^ x[21] ^ z10; c10 <= (x[20] & x[21]) | (x[20] & z10) | (x[21] & z10); end
  reg st2; always @(posedge clk) st2 <= start;
  reg s11, c11; wire z11 = st2 ? 1'b0 : c11;
  always @(posedge clk) begin s11 <= s0 ^ s1 ^ z11; c11 <= (s0 & s1) | (s0 & z11) | (s1 & z11); end
  reg s12, c12; wire z12 = st2 ? 1'b0 : c12;
  always @(posedge clk) begin s12 <= s2 ^ s3 ^ z12; c12 <= (s2 & s3) | (s2 & z12) | (s3 & z12); end
  reg s13, c13; wire z13 = st2 ? 1'b0 : c13;
  always @(posedge clk) begin s13 <= s4 ^ s5 ^ z13; c13 <= (s4 & s5) | (s4 & z13) | (s5 & z13); end
  reg s14, c14; wire z14 = st2 ? 1'b0 : c14;
  always @(posedge clk) begin s14 <= s6 ^ s7 ^ z14; c14 <= (s6 & s7) | (s6 & z14) | (s7 & z14); end
  reg s15, c15; wire z15 = st2 ? 1'b0 : c15;
  always @(posedge clk) begin s15 <= s8 ^ s9 ^ z15; c15 <= (s8 & s9) | (s8 & z15) | (s9 & z15); end
  reg d16; always @(posedge clk) d16 <= s10;
  reg st3; always @(posedge clk) st3 <= st2;
  reg s17, c17; wire z17 = st3 ? 1'b0 : c17;
  always @(posedge clk) begin s17 <= s11 ^ s12 ^ z17; c17 <= (s11 & s12) | (s11 & z17) | (s12 & z17); end
  reg s18, c18; wire z18 = st3 ? 1'b0 : c18;
  always @(posedge clk) begin s18 <= s13 ^ s14 ^ z18; c18 <= (s13 & s14) | (s13 & z18) | (s14 & z18); end
  reg s19, c19; wire z19 = st3 ? 1'b0 : c19;
  always @(posedge clk) begin s19 <= s15 ^ d16 ^ z19; c19 <= (s15 & d16) | (s15 & z19) | (d16 & z19); end
  reg st4; always @(posedge clk) st4 <= st3;
  reg s20, c20; wire z20 = st4 ? 1'b0 : c20;
  always @(posedge clk) begin s20 <= s17 ^ s18 ^ z20; c20 <= (s17 & s18) | (s17 & z20) | (s18 & z20); end
  reg d21; always @(posedge clk) d21 <= s19;
  reg st5; always @(posedge clk) st5 <= st4;
  reg s22, c22; wire z22 = st5 ? 1'b0 : c22;
  always @(posedge clk) begin s22 <= s20 ^ d21 ^ z22; c22 <= (s20 & d21) | (s20 & z22) | (d21 & z22); end
  assign y = s22;
endmodule
