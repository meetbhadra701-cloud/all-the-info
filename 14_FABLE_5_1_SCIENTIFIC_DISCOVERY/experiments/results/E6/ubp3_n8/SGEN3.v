module SGEN3(input clk, input start, input [2:0] x, output [12:0] y);
  reg x0_d1; always @(posedge clk) x0_d1 <= x[0];
  reg x0_d2; always @(posedge clk) x0_d2 <= x0_d1;
  reg x1_d1; always @(posedge clk) x1_d1 <= x[1];
  reg x1_d2; always @(posedge clk) x1_d2 <= x1_d1;
  reg x2_d1; always @(posedge clk) x2_d1 <= x[2];
  reg x2_d2; always @(posedge clk) x2_d2 <= x2_d1;
  reg st_d1; always @(posedge clk) st_d1 <= start;
  reg st_d2; always @(posedge clk) st_d2 <= st_d1;
  reg g0, gc0; wire gz0 = start ? 1'b1 : gc0; wire gn0 = ~x[2];
  always @(posedge clk) begin g0 <= x[1] ^ gn0 ^ gz0; gc0 <= (x[1] & gn0) | (x[1] & gz0) | (gn0 & gz0); end
  reg g1, gc1; wire gz1 = start ? 1'b0 : gc1;
  always @(posedge clk) begin g1 <= x[1] ^ x[2] ^ gz1; gc1 <= (x[1] & x[2]) | (x[1] & gz1) | (x[2] & gz1); end
  reg g2, gc2; wire gz2 = start ? 1'b1 : gc2; wire gn2 = ~x[2];
  always @(posedge clk) begin g2 <= x[0] ^ gn2 ^ gz2; gc2 <= (x[0] & gn2) | (x[0] & gz2) | (gn2 & gz2); end
  reg g3, gc3; wire gz3 = start ? 1'b0 : gc3;
  always @(posedge clk) begin g3 <= x[0] ^ x[2] ^ gz3; gc3 <= (x[0] & x[2]) | (x[0] & gz3) | (x[2] & gz3); end
  reg g4, gc4; wire gz4 = start ? 1'b1 : gc4; wire gn4 = ~x[1];
  always @(posedge clk) begin g4 <= x[0] ^ gn4 ^ gz4; gc4 <= (x[0] & gn4) | (x[0] & gz4) | (gn4 & gz4); end
  reg g5, gc5; wire gz5 = start ? 1'b0 : gc5;
  always @(posedge clk) begin g5 <= x[0] ^ x[1] ^ gz5; gc5 <= (x[0] & x[1]) | (x[0] & gz5) | (x[1] & gz5); end
  reg g6, gc6; wire gz6 = st_d1 ? 1'b1 : gc6; wire gn6 = ~x2_d1;
  always @(posedge clk) begin g6 <= g4 ^ gn6 ^ gz6; gc6 <= (g4 & gn6) | (g4 & gz6) | (gn6 & gz6); end
  reg g7, gc7; wire gz7 = st_d1 ? 1'b0 : gc7;
  always @(posedge clk) begin g7 <= g4 ^ x2_d1 ^ gz7; gc7 <= (g4 & x2_d1) | (g4 & gz7) | (x2_d1 & gz7); end
  reg g8, gc8; wire gz8 = st_d1 ? 1'b1 : gc8; wire gn8 = ~x2_d1;
  always @(posedge clk) begin g8 <= g5 ^ gn8 ^ gz8; gc8 <= (g5 & gn8) | (g5 & gz8) | (gn8 & gz8); end
  reg g9, gc9; wire gz9 = st_d1 ? 1'b0 : gc9;
  always @(posedge clk) begin g9 <= g5 ^ x2_d1 ^ gz9; gc9 <= (g5 & x2_d1) | (g5 & gz9) | (x2_d1 & gz9); end
  reg al0_0; always @(posedge clk) al0_0 <= x[2];
  reg al0_1; always @(posedge clk) al0_1 <= al0_0;
  assign y[0] = al0_1;
  reg al1_0; always @(posedge clk) al1_0 <= x[1];
  reg al1_1; always @(posedge clk) al1_1 <= al1_0;
  assign y[1] = al1_1;
  reg al2_0; always @(posedge clk) al2_0 <= x[0];
  reg al2_1; always @(posedge clk) al2_1 <= al2_0;
  assign y[2] = al2_1;
  reg al3_1; always @(posedge clk) al3_1 <= g0;
  assign y[3] = al3_1;
  reg al4_1; always @(posedge clk) al4_1 <= g1;
  assign y[4] = al4_1;
  reg al5_1; always @(posedge clk) al5_1 <= g2;
  assign y[5] = al5_1;
  reg al6_1; always @(posedge clk) al6_1 <= g3;
  assign y[6] = al6_1;
  reg al7_1; always @(posedge clk) al7_1 <= g4;
  assign y[7] = al7_1;
  reg al8_1; always @(posedge clk) al8_1 <= g5;
  assign y[8] = al8_1;
  assign y[9] = g6;
  assign y[10] = g7;
  assign y[11] = g8;
  assign y[12] = g9;
endmodule
