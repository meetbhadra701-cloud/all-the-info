module PLINE(input clk, input a, output pos, output neg);
  reg q; always @(posedge clk) q <= a;
  assign pos = q; assign neg = ~q;
endmodule
