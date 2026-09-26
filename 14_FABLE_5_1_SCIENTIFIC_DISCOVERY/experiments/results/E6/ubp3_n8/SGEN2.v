module SGEN2(input clk, input start, input [1:0] x, output [3:0] y);
  reg x0_d1; always @(posedge clk) x0_d1 <= x[0];
  reg x1_d1; always @(posedge clk) x1_d1 <= x[1];
  reg st_d1; always @(posedge clk) st_d1 <= start;
  reg g0, gc0; wire gz0 = start ? 1'b1 : gc0; wire gn0 = ~x[1];
  always @(posedge clk) begin g0 <= x[0] ^ gn0 ^ gz0; gc0 <= (x[0] & gn0) | (x[0] & gz0) | (gn0 & gz0); end
  reg g1, gc1; wire gz1 = start ? 1'b0 : gc1;
  always @(posedge clk) begin g1 <= x[0] ^ x[1] ^ gz1; gc1 <= (x[0] & x[1]) | (x[0] & gz1) | (x[1] & gz1); end
  reg al0_0; always @(posedge clk) al0_0 <= x[1];
  assign y[0] = al0_0;
  reg al1_0; always @(posedge clk) al1_0 <= x[0];
  assign y[1] = al1_0;
  assign y[2] = g0;
  assign y[3] = g1;
endmodule
