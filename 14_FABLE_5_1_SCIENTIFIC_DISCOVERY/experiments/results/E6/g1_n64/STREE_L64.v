module STREE_L64(input clk, input start, input [63:0] x, output y);
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
  reg s11, c11; wire z11 = start ? 1'b0 : c11;
  always @(posedge clk) begin s11 <= x[22] ^ x[23] ^ z11; c11 <= (x[22] & x[23]) | (x[22] & z11) | (x[23] & z11); end
  reg s12, c12; wire z12 = start ? 1'b0 : c12;
  always @(posedge clk) begin s12 <= x[24] ^ x[25] ^ z12; c12 <= (x[24] & x[25]) | (x[24] & z12) | (x[25] & z12); end
  reg s13, c13; wire z13 = start ? 1'b0 : c13;
  always @(posedge clk) begin s13 <= x[26] ^ x[27] ^ z13; c13 <= (x[26] & x[27]) | (x[26] & z13) | (x[27] & z13); end
  reg s14, c14; wire z14 = start ? 1'b0 : c14;
  always @(posedge clk) begin s14 <= x[28] ^ x[29] ^ z14; c14 <= (x[28] & x[29]) | (x[28] & z14) | (x[29] & z14); end
  reg s15, c15; wire z15 = start ? 1'b0 : c15;
  always @(posedge clk) begin s15 <= x[30] ^ x[31] ^ z15; c15 <= (x[30] & x[31]) | (x[30] & z15) | (x[31] & z15); end
  reg s16, c16; wire z16 = start ? 1'b0 : c16;
  always @(posedge clk) begin s16 <= x[32] ^ x[33] ^ z16; c16 <= (x[32] & x[33]) | (x[32] & z16) | (x[33] & z16); end
  reg s17, c17; wire z17 = start ? 1'b0 : c17;
  always @(posedge clk) begin s17 <= x[34] ^ x[35] ^ z17; c17 <= (x[34] & x[35]) | (x[34] & z17) | (x[35] & z17); end
  reg s18, c18; wire z18 = start ? 1'b0 : c18;
  always @(posedge clk) begin s18 <= x[36] ^ x[37] ^ z18; c18 <= (x[36] & x[37]) | (x[36] & z18) | (x[37] & z18); end
  reg s19, c19; wire z19 = start ? 1'b0 : c19;
  always @(posedge clk) begin s19 <= x[38] ^ x[39] ^ z19; c19 <= (x[38] & x[39]) | (x[38] & z19) | (x[39] & z19); end
  reg s20, c20; wire z20 = start ? 1'b0 : c20;
  always @(posedge clk) begin s20 <= x[40] ^ x[41] ^ z20; c20 <= (x[40] & x[41]) | (x[40] & z20) | (x[41] & z20); end
  reg s21, c21; wire z21 = start ? 1'b0 : c21;
  always @(posedge clk) begin s21 <= x[42] ^ x[43] ^ z21; c21 <= (x[42] & x[43]) | (x[42] & z21) | (x[43] & z21); end
  reg s22, c22; wire z22 = start ? 1'b0 : c22;
  always @(posedge clk) begin s22 <= x[44] ^ x[45] ^ z22; c22 <= (x[44] & x[45]) | (x[44] & z22) | (x[45] & z22); end
  reg s23, c23; wire z23 = start ? 1'b0 : c23;
  always @(posedge clk) begin s23 <= x[46] ^ x[47] ^ z23; c23 <= (x[46] & x[47]) | (x[46] & z23) | (x[47] & z23); end
  reg s24, c24; wire z24 = start ? 1'b0 : c24;
  always @(posedge clk) begin s24 <= x[48] ^ x[49] ^ z24; c24 <= (x[48] & x[49]) | (x[48] & z24) | (x[49] & z24); end
  reg s25, c25; wire z25 = start ? 1'b0 : c25;
  always @(posedge clk) begin s25 <= x[50] ^ x[51] ^ z25; c25 <= (x[50] & x[51]) | (x[50] & z25) | (x[51] & z25); end
  reg s26, c26; wire z26 = start ? 1'b0 : c26;
  always @(posedge clk) begin s26 <= x[52] ^ x[53] ^ z26; c26 <= (x[52] & x[53]) | (x[52] & z26) | (x[53] & z26); end
  reg s27, c27; wire z27 = start ? 1'b0 : c27;
  always @(posedge clk) begin s27 <= x[54] ^ x[55] ^ z27; c27 <= (x[54] & x[55]) | (x[54] & z27) | (x[55] & z27); end
  reg s28, c28; wire z28 = start ? 1'b0 : c28;
  always @(posedge clk) begin s28 <= x[56] ^ x[57] ^ z28; c28 <= (x[56] & x[57]) | (x[56] & z28) | (x[57] & z28); end
  reg s29, c29; wire z29 = start ? 1'b0 : c29;
  always @(posedge clk) begin s29 <= x[58] ^ x[59] ^ z29; c29 <= (x[58] & x[59]) | (x[58] & z29) | (x[59] & z29); end
  reg s30, c30; wire z30 = start ? 1'b0 : c30;
  always @(posedge clk) begin s30 <= x[60] ^ x[61] ^ z30; c30 <= (x[60] & x[61]) | (x[60] & z30) | (x[61] & z30); end
  reg s31, c31; wire z31 = start ? 1'b0 : c31;
  always @(posedge clk) begin s31 <= x[62] ^ x[63] ^ z31; c31 <= (x[62] & x[63]) | (x[62] & z31) | (x[63] & z31); end
  reg st2; always @(posedge clk) st2 <= start;
  reg s32, c32; wire z32 = st2 ? 1'b0 : c32;
  always @(posedge clk) begin s32 <= s0 ^ s1 ^ z32; c32 <= (s0 & s1) | (s0 & z32) | (s1 & z32); end
  reg s33, c33; wire z33 = st2 ? 1'b0 : c33;
  always @(posedge clk) begin s33 <= s2 ^ s3 ^ z33; c33 <= (s2 & s3) | (s2 & z33) | (s3 & z33); end
  reg s34, c34; wire z34 = st2 ? 1'b0 : c34;
  always @(posedge clk) begin s34 <= s4 ^ s5 ^ z34; c34 <= (s4 & s5) | (s4 & z34) | (s5 & z34); end
  reg s35, c35; wire z35 = st2 ? 1'b0 : c35;
  always @(posedge clk) begin s35 <= s6 ^ s7 ^ z35; c35 <= (s6 & s7) | (s6 & z35) | (s7 & z35); end
  reg s36, c36; wire z36 = st2 ? 1'b0 : c36;
  always @(posedge clk) begin s36 <= s8 ^ s9 ^ z36; c36 <= (s8 & s9) | (s8 & z36) | (s9 & z36); end
  reg s37, c37; wire z37 = st2 ? 1'b0 : c37;
  always @(posedge clk) begin s37 <= s10 ^ s11 ^ z37; c37 <= (s10 & s11) | (s10 & z37) | (s11 & z37); end
  reg s38, c38; wire z38 = st2 ? 1'b0 : c38;
  always @(posedge clk) begin s38 <= s12 ^ s13 ^ z38; c38 <= (s12 & s13) | (s12 & z38) | (s13 & z38); end
  reg s39, c39; wire z39 = st2 ? 1'b0 : c39;
  always @(posedge clk) begin s39 <= s14 ^ s15 ^ z39; c39 <= (s14 & s15) | (s14 & z39) | (s15 & z39); end
  reg s40, c40; wire z40 = st2 ? 1'b0 : c40;
  always @(posedge clk) begin s40 <= s16 ^ s17 ^ z40; c40 <= (s16 & s17) | (s16 & z40) | (s17 & z40); end
  reg s41, c41; wire z41 = st2 ? 1'b0 : c41;
  always @(posedge clk) begin s41 <= s18 ^ s19 ^ z41; c41 <= (s18 & s19) | (s18 & z41) | (s19 & z41); end
  reg s42, c42; wire z42 = st2 ? 1'b0 : c42;
  always @(posedge clk) begin s42 <= s20 ^ s21 ^ z42; c42 <= (s20 & s21) | (s20 & z42) | (s21 & z42); end
  reg s43, c43; wire z43 = st2 ? 1'b0 : c43;
  always @(posedge clk) begin s43 <= s22 ^ s23 ^ z43; c43 <= (s22 & s23) | (s22 & z43) | (s23 & z43); end
  reg s44, c44; wire z44 = st2 ? 1'b0 : c44;
  always @(posedge clk) begin s44 <= s24 ^ s25 ^ z44; c44 <= (s24 & s25) | (s24 & z44) | (s25 & z44); end
  reg s45, c45; wire z45 = st2 ? 1'b0 : c45;
  always @(posedge clk) begin s45 <= s26 ^ s27 ^ z45; c45 <= (s26 & s27) | (s26 & z45) | (s27 & z45); end
  reg s46, c46; wire z46 = st2 ? 1'b0 : c46;
  always @(posedge clk) begin s46 <= s28 ^ s29 ^ z46; c46 <= (s28 & s29) | (s28 & z46) | (s29 & z46); end
  reg s47, c47; wire z47 = st2 ? 1'b0 : c47;
  always @(posedge clk) begin s47 <= s30 ^ s31 ^ z47; c47 <= (s30 & s31) | (s30 & z47) | (s31 & z47); end
  reg st3; always @(posedge clk) st3 <= st2;
  reg s48, c48; wire z48 = st3 ? 1'b0 : c48;
  always @(posedge clk) begin s48 <= s32 ^ s33 ^ z48; c48 <= (s32 & s33) | (s32 & z48) | (s33 & z48); end
  reg s49, c49; wire z49 = st3 ? 1'b0 : c49;
  always @(posedge clk) begin s49 <= s34 ^ s35 ^ z49; c49 <= (s34 & s35) | (s34 & z49) | (s35 & z49); end
  reg s50, c50; wire z50 = st3 ? 1'b0 : c50;
  always @(posedge clk) begin s50 <= s36 ^ s37 ^ z50; c50 <= (s36 & s37) | (s36 & z50) | (s37 & z50); end
  reg s51, c51; wire z51 = st3 ? 1'b0 : c51;
  always @(posedge clk) begin s51 <= s38 ^ s39 ^ z51; c51 <= (s38 & s39) | (s38 & z51) | (s39 & z51); end
  reg s52, c52; wire z52 = st3 ? 1'b0 : c52;
  always @(posedge clk) begin s52 <= s40 ^ s41 ^ z52; c52 <= (s40 & s41) | (s40 & z52) | (s41 & z52); end
  reg s53, c53; wire z53 = st3 ? 1'b0 : c53;
  always @(posedge clk) begin s53 <= s42 ^ s43 ^ z53; c53 <= (s42 & s43) | (s42 & z53) | (s43 & z53); end
  reg s54, c54; wire z54 = st3 ? 1'b0 : c54;
  always @(posedge clk) begin s54 <= s44 ^ s45 ^ z54; c54 <= (s44 & s45) | (s44 & z54) | (s45 & z54); end
  reg s55, c55; wire z55 = st3 ? 1'b0 : c55;
  always @(posedge clk) begin s55 <= s46 ^ s47 ^ z55; c55 <= (s46 & s47) | (s46 & z55) | (s47 & z55); end
  reg st4; always @(posedge clk) st4 <= st3;
  reg s56, c56; wire z56 = st4 ? 1'b0 : c56;
  always @(posedge clk) begin s56 <= s48 ^ s49 ^ z56; c56 <= (s48 & s49) | (s48 & z56) | (s49 & z56); end
  reg s57, c57; wire z57 = st4 ? 1'b0 : c57;
  always @(posedge clk) begin s57 <= s50 ^ s51 ^ z57; c57 <= (s50 & s51) | (s50 & z57) | (s51 & z57); end
  reg s58, c58; wire z58 = st4 ? 1'b0 : c58;
  always @(posedge clk) begin s58 <= s52 ^ s53 ^ z58; c58 <= (s52 & s53) | (s52 & z58) | (s53 & z58); end
  reg s59, c59; wire z59 = st4 ? 1'b0 : c59;
  always @(posedge clk) begin s59 <= s54 ^ s55 ^ z59; c59 <= (s54 & s55) | (s54 & z59) | (s55 & z59); end
  reg st5; always @(posedge clk) st5 <= st4;
  reg s60, c60; wire z60 = st5 ? 1'b0 : c60;
  always @(posedge clk) begin s60 <= s56 ^ s57 ^ z60; c60 <= (s56 & s57) | (s56 & z60) | (s57 & z60); end
  reg s61, c61; wire z61 = st5 ? 1'b0 : c61;
  always @(posedge clk) begin s61 <= s58 ^ s59 ^ z61; c61 <= (s58 & s59) | (s58 & z61) | (s59 & z61); end
  reg st6; always @(posedge clk) st6 <= st5;
  reg s62, c62; wire z62 = st6 ? 1'b0 : c62;
  always @(posedge clk) begin s62 <= s60 ^ s61 ^ z62; c62 <= (s60 & s61) | (s60 & z62) | (s61 & z62); end
  assign y = s62;
endmodule
