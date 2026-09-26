module SNEG(input clk, input start, input a, output pos, output neg);
  reg p, n, c; wire z = start ? 1'b1 : c; wire na = ~a;
  always @(posedge clk) begin p <= a; n <= na ^ z; c <= na & z; end
  assign pos = p; assign neg = n;
endmodule
