module top(y, clk, wire4);
  input clk;
  input signed wire4;
  output [1:0] y;
  wire [1:0] reg10;
  reg \reg10_reg[0]  = 1'hx;
  always @(posedge clk)
    \reg10_reg[0]  <= wire4;
  assign reg10[0] = \reg10_reg[0] ;
  assign reg10[1] = reg10[0];
  assign y = {reg10[0], reg10[0]};
endmodule
