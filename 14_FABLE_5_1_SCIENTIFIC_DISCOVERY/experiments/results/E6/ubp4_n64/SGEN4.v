module SGEN4(input clk, input start, input [3:0] x, output [39:0] y);
  reg x0_d1; always @(posedge clk) x0_d1 <= x[0];
  reg x0_d2; always @(posedge clk) x0_d2 <= x0_d1;
  reg x0_d3; always @(posedge clk) x0_d3 <= x0_d2;
  reg x1_d1; always @(posedge clk) x1_d1 <= x[1];
  reg x1_d2; always @(posedge clk) x1_d2 <= x1_d1;
  reg x1_d3; always @(posedge clk) x1_d3 <= x1_d2;
  reg x2_d1; always @(posedge clk) x2_d1 <= x[2];
  reg x2_d2; always @(posedge clk) x2_d2 <= x2_d1;
  reg x2_d3; always @(posedge clk) x2_d3 <= x2_d2;
  reg x3_d1; always @(posedge clk) x3_d1 <= x[3];
  reg x3_d2; always @(posedge clk) x3_d2 <= x3_d1;
  reg x3_d3; always @(posedge clk) x3_d3 <= x3_d2;
  reg st_d1; always @(posedge clk) st_d1 <= start;
  reg st_d2; always @(posedge clk) st_d2 <= st_d1;
  reg st_d3; always @(posedge clk) st_d3 <= st_d2;
  reg g0, gc0; wire gz0 = start ? 1'b1 : gc0; wire gn0 = ~x[3];
  always @(posedge clk) begin g0 <= x[2] ^ gn0 ^ gz0; gc0 <= (x[2] & gn0) | (x[2] & gz0) | (gn0 & gz0); end
  reg g1, gc1; wire gz1 = start ? 1'b0 : gc1;
  always @(posedge clk) begin g1 <= x[2] ^ x[3] ^ gz1; gc1 <= (x[2] & x[3]) | (x[2] & gz1) | (x[3] & gz1); end
  reg g2, gc2; wire gz2 = start ? 1'b1 : gc2; wire gn2 = ~x[3];
  always @(posedge clk) begin g2 <= x[1] ^ gn2 ^ gz2; gc2 <= (x[1] & gn2) | (x[1] & gz2) | (gn2 & gz2); end
  reg g3, gc3; wire gz3 = start ? 1'b0 : gc3;
  always @(posedge clk) begin g3 <= x[1] ^ x[3] ^ gz3; gc3 <= (x[1] & x[3]) | (x[1] & gz3) | (x[3] & gz3); end
  reg g4, gc4; wire gz4 = start ? 1'b1 : gc4; wire gn4 = ~x[2];
  always @(posedge clk) begin g4 <= x[1] ^ gn4 ^ gz4; gc4 <= (x[1] & gn4) | (x[1] & gz4) | (gn4 & gz4); end
  reg g5, gc5; wire gz5 = start ? 1'b0 : gc5;
  always @(posedge clk) begin g5 <= x[1] ^ x[2] ^ gz5; gc5 <= (x[1] & x[2]) | (x[1] & gz5) | (x[2] & gz5); end
  reg g6, gc6; wire gz6 = start ? 1'b1 : gc6; wire gn6 = ~x[3];
  always @(posedge clk) begin g6 <= x[0] ^ gn6 ^ gz6; gc6 <= (x[0] & gn6) | (x[0] & gz6) | (gn6 & gz6); end
  reg g7, gc7; wire gz7 = start ? 1'b0 : gc7;
  always @(posedge clk) begin g7 <= x[0] ^ x[3] ^ gz7; gc7 <= (x[0] & x[3]) | (x[0] & gz7) | (x[3] & gz7); end
  reg g8, gc8; wire gz8 = start ? 1'b1 : gc8; wire gn8 = ~x[2];
  always @(posedge clk) begin g8 <= x[0] ^ gn8 ^ gz8; gc8 <= (x[0] & gn8) | (x[0] & gz8) | (gn8 & gz8); end
  reg g9, gc9; wire gz9 = start ? 1'b0 : gc9;
  always @(posedge clk) begin g9 <= x[0] ^ x[2] ^ gz9; gc9 <= (x[0] & x[2]) | (x[0] & gz9) | (x[2] & gz9); end
  reg g10, gc10; wire gz10 = start ? 1'b1 : gc10; wire gn10 = ~x[1];
  always @(posedge clk) begin g10 <= x[0] ^ gn10 ^ gz10; gc10 <= (x[0] & gn10) | (x[0] & gz10) | (gn10 & gz10); end
  reg g11, gc11; wire gz11 = start ? 1'b0 : gc11;
  always @(posedge clk) begin g11 <= x[0] ^ x[1] ^ gz11; gc11 <= (x[0] & x[1]) | (x[0] & gz11) | (x[1] & gz11); end
  reg g12, gc12; wire gz12 = st_d1 ? 1'b1 : gc12; wire gn12 = ~x3_d1;
  always @(posedge clk) begin g12 <= g4 ^ gn12 ^ gz12; gc12 <= (g4 & gn12) | (g4 & gz12) | (gn12 & gz12); end
  reg g13, gc13; wire gz13 = st_d1 ? 1'b0 : gc13;
  always @(posedge clk) begin g13 <= g4 ^ x3_d1 ^ gz13; gc13 <= (g4 & x3_d1) | (g4 & gz13) | (x3_d1 & gz13); end
  reg g14, gc14; wire gz14 = st_d1 ? 1'b1 : gc14; wire gn14 = ~x3_d1;
  always @(posedge clk) begin g14 <= g5 ^ gn14 ^ gz14; gc14 <= (g5 & gn14) | (g5 & gz14) | (gn14 & gz14); end
  reg g15, gc15; wire gz15 = st_d1 ? 1'b0 : gc15;
  always @(posedge clk) begin g15 <= g5 ^ x3_d1 ^ gz15; gc15 <= (g5 & x3_d1) | (g5 & gz15) | (x3_d1 & gz15); end
  reg g16, gc16; wire gz16 = st_d1 ? 1'b1 : gc16; wire gn16 = ~x3_d1;
  always @(posedge clk) begin g16 <= g8 ^ gn16 ^ gz16; gc16 <= (g8 & gn16) | (g8 & gz16) | (gn16 & gz16); end
  reg g17, gc17; wire gz17 = st_d1 ? 1'b0 : gc17;
  always @(posedge clk) begin g17 <= g8 ^ x3_d1 ^ gz17; gc17 <= (g8 & x3_d1) | (g8 & gz17) | (x3_d1 & gz17); end
  reg g18, gc18; wire gz18 = st_d1 ? 1'b1 : gc18; wire gn18 = ~x3_d1;
  always @(posedge clk) begin g18 <= g9 ^ gn18 ^ gz18; gc18 <= (g9 & gn18) | (g9 & gz18) | (gn18 & gz18); end
  reg g19, gc19; wire gz19 = st_d1 ? 1'b0 : gc19;
  always @(posedge clk) begin g19 <= g9 ^ x3_d1 ^ gz19; gc19 <= (g9 & x3_d1) | (g9 & gz19) | (x3_d1 & gz19); end
  reg g20, gc20; wire gz20 = st_d1 ? 1'b1 : gc20; wire gn20 = ~x3_d1;
  always @(posedge clk) begin g20 <= g10 ^ gn20 ^ gz20; gc20 <= (g10 & gn20) | (g10 & gz20) | (gn20 & gz20); end
  reg g21, gc21; wire gz21 = st_d1 ? 1'b0 : gc21;
  always @(posedge clk) begin g21 <= g10 ^ x3_d1 ^ gz21; gc21 <= (g10 & x3_d1) | (g10 & gz21) | (x3_d1 & gz21); end
  reg g22, gc22; wire gz22 = st_d1 ? 1'b1 : gc22; wire gn22 = ~x3_d1;
  always @(posedge clk) begin g22 <= g11 ^ gn22 ^ gz22; gc22 <= (g11 & gn22) | (g11 & gz22) | (gn22 & gz22); end
  reg g23, gc23; wire gz23 = st_d1 ? 1'b0 : gc23;
  always @(posedge clk) begin g23 <= g11 ^ x3_d1 ^ gz23; gc23 <= (g11 & x3_d1) | (g11 & gz23) | (x3_d1 & gz23); end
  reg g24, gc24; wire gz24 = st_d1 ? 1'b1 : gc24; wire gn24 = ~x2_d1;
  always @(posedge clk) begin g24 <= g10 ^ gn24 ^ gz24; gc24 <= (g10 & gn24) | (g10 & gz24) | (gn24 & gz24); end
  reg g25, gc25; wire gz25 = st_d1 ? 1'b0 : gc25;
  always @(posedge clk) begin g25 <= g10 ^ x2_d1 ^ gz25; gc25 <= (g10 & x2_d1) | (g10 & gz25) | (x2_d1 & gz25); end
  reg g26, gc26; wire gz26 = st_d1 ? 1'b1 : gc26; wire gn26 = ~x2_d1;
  always @(posedge clk) begin g26 <= g11 ^ gn26 ^ gz26; gc26 <= (g11 & gn26) | (g11 & gz26) | (gn26 & gz26); end
  reg g27, gc27; wire gz27 = st_d1 ? 1'b0 : gc27;
  always @(posedge clk) begin g27 <= g11 ^ x2_d1 ^ gz27; gc27 <= (g11 & x2_d1) | (g11 & gz27) | (x2_d1 & gz27); end
  reg g28, gc28; wire gz28 = st_d2 ? 1'b1 : gc28; wire gn28 = ~x3_d2;
  always @(posedge clk) begin g28 <= g24 ^ gn28 ^ gz28; gc28 <= (g24 & gn28) | (g24 & gz28) | (gn28 & gz28); end
  reg g29, gc29; wire gz29 = st_d2 ? 1'b0 : gc29;
  always @(posedge clk) begin g29 <= g24 ^ x3_d2 ^ gz29; gc29 <= (g24 & x3_d2) | (g24 & gz29) | (x3_d2 & gz29); end
  reg g30, gc30; wire gz30 = st_d2 ? 1'b1 : gc30; wire gn30 = ~x3_d2;
  always @(posedge clk) begin g30 <= g25 ^ gn30 ^ gz30; gc30 <= (g25 & gn30) | (g25 & gz30) | (gn30 & gz30); end
  reg g31, gc31; wire gz31 = st_d2 ? 1'b0 : gc31;
  always @(posedge clk) begin g31 <= g25 ^ x3_d2 ^ gz31; gc31 <= (g25 & x3_d2) | (g25 & gz31) | (x3_d2 & gz31); end
  reg g32, gc32; wire gz32 = st_d2 ? 1'b1 : gc32; wire gn32 = ~x3_d2;
  always @(posedge clk) begin g32 <= g26 ^ gn32 ^ gz32; gc32 <= (g26 & gn32) | (g26 & gz32) | (gn32 & gz32); end
  reg g33, gc33; wire gz33 = st_d2 ? 1'b0 : gc33;
  always @(posedge clk) begin g33 <= g26 ^ x3_d2 ^ gz33; gc33 <= (g26 & x3_d2) | (g26 & gz33) | (x3_d2 & gz33); end
  reg g34, gc34; wire gz34 = st_d2 ? 1'b1 : gc34; wire gn34 = ~x3_d2;
  always @(posedge clk) begin g34 <= g27 ^ gn34 ^ gz34; gc34 <= (g27 & gn34) | (g27 & gz34) | (gn34 & gz34); end
  reg g35, gc35; wire gz35 = st_d2 ? 1'b0 : gc35;
  always @(posedge clk) begin g35 <= g27 ^ x3_d2 ^ gz35; gc35 <= (g27 & x3_d2) | (g27 & gz35) | (x3_d2 & gz35); end
  reg al0_0; always @(posedge clk) al0_0 <= x[3];
  reg al0_1; always @(posedge clk) al0_1 <= al0_0;
  reg al0_2; always @(posedge clk) al0_2 <= al0_1;
  assign y[0] = al0_2;
  reg al1_0; always @(posedge clk) al1_0 <= x[2];
  reg al1_1; always @(posedge clk) al1_1 <= al1_0;
  reg al1_2; always @(posedge clk) al1_2 <= al1_1;
  assign y[1] = al1_2;
  reg al2_0; always @(posedge clk) al2_0 <= x[1];
  reg al2_1; always @(posedge clk) al2_1 <= al2_0;
  reg al2_2; always @(posedge clk) al2_2 <= al2_1;
  assign y[2] = al2_2;
  reg al3_0; always @(posedge clk) al3_0 <= x[0];
  reg al3_1; always @(posedge clk) al3_1 <= al3_0;
  reg al3_2; always @(posedge clk) al3_2 <= al3_1;
  assign y[3] = al3_2;
  reg al4_1; always @(posedge clk) al4_1 <= g0;
  reg al4_2; always @(posedge clk) al4_2 <= al4_1;
  assign y[4] = al4_2;
  reg al5_1; always @(posedge clk) al5_1 <= g1;
  reg al5_2; always @(posedge clk) al5_2 <= al5_1;
  assign y[5] = al5_2;
  reg al6_1; always @(posedge clk) al6_1 <= g2;
  reg al6_2; always @(posedge clk) al6_2 <= al6_1;
  assign y[6] = al6_2;
  reg al7_1; always @(posedge clk) al7_1 <= g3;
  reg al7_2; always @(posedge clk) al7_2 <= al7_1;
  assign y[7] = al7_2;
  reg al8_1; always @(posedge clk) al8_1 <= g4;
  reg al8_2; always @(posedge clk) al8_2 <= al8_1;
  assign y[8] = al8_2;
  reg al9_1; always @(posedge clk) al9_1 <= g5;
  reg al9_2; always @(posedge clk) al9_2 <= al9_1;
  assign y[9] = al9_2;
  reg al10_1; always @(posedge clk) al10_1 <= g6;
  reg al10_2; always @(posedge clk) al10_2 <= al10_1;
  assign y[10] = al10_2;
  reg al11_1; always @(posedge clk) al11_1 <= g7;
  reg al11_2; always @(posedge clk) al11_2 <= al11_1;
  assign y[11] = al11_2;
  reg al12_1; always @(posedge clk) al12_1 <= g8;
  reg al12_2; always @(posedge clk) al12_2 <= al12_1;
  assign y[12] = al12_2;
  reg al13_1; always @(posedge clk) al13_1 <= g9;
  reg al13_2; always @(posedge clk) al13_2 <= al13_1;
  assign y[13] = al13_2;
  reg al14_1; always @(posedge clk) al14_1 <= g10;
  reg al14_2; always @(posedge clk) al14_2 <= al14_1;
  assign y[14] = al14_2;
  reg al15_1; always @(posedge clk) al15_1 <= g11;
  reg al15_2; always @(posedge clk) al15_2 <= al15_1;
  assign y[15] = al15_2;
  reg al16_2; always @(posedge clk) al16_2 <= g12;
  assign y[16] = al16_2;
  reg al17_2; always @(posedge clk) al17_2 <= g13;
  assign y[17] = al17_2;
  reg al18_2; always @(posedge clk) al18_2 <= g14;
  assign y[18] = al18_2;
  reg al19_2; always @(posedge clk) al19_2 <= g15;
  assign y[19] = al19_2;
  reg al20_2; always @(posedge clk) al20_2 <= g16;
  assign y[20] = al20_2;
  reg al21_2; always @(posedge clk) al21_2 <= g17;
  assign y[21] = al21_2;
  reg al22_2; always @(posedge clk) al22_2 <= g18;
  assign y[22] = al22_2;
  reg al23_2; always @(posedge clk) al23_2 <= g19;
  assign y[23] = al23_2;
  reg al24_2; always @(posedge clk) al24_2 <= g20;
  assign y[24] = al24_2;
  reg al25_2; always @(posedge clk) al25_2 <= g21;
  assign y[25] = al25_2;
  reg al26_2; always @(posedge clk) al26_2 <= g22;
  assign y[26] = al26_2;
  reg al27_2; always @(posedge clk) al27_2 <= g23;
  assign y[27] = al27_2;
  reg al28_2; always @(posedge clk) al28_2 <= g24;
  assign y[28] = al28_2;
  reg al29_2; always @(posedge clk) al29_2 <= g25;
  assign y[29] = al29_2;
  reg al30_2; always @(posedge clk) al30_2 <= g26;
  assign y[30] = al30_2;
  reg al31_2; always @(posedge clk) al31_2 <= g27;
  assign y[31] = al31_2;
  assign y[32] = g28;
  assign y[33] = g29;
  assign y[34] = g30;
  assign y[35] = g31;
  assign y[36] = g32;
  assign y[37] = g33;
  assign y[38] = g34;
  assign y[39] = g35;
endmodule
