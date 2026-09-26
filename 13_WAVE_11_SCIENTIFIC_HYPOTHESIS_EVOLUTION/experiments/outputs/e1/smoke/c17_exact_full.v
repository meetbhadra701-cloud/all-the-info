module top( x0 , x1 , x2 , x3 , x4 , y0 , y1 );
  input x0 , x1 , x2 , x3 , x4 ;
  output y0 , y1 ;
  INVx1_ASAP7_75t_R g0 ( .A (x2), .Y (xn2) );
  INVx1_ASAP7_75t_R g1 ( .A (x4), .Y (xn4) );
  NAND2x1_ASAP7_75t_R g2 ( .A (x0), .B (x1), .Y (n6_1) );
  AND2x2_ASAP7_75t_R g3 ( .A (x1), .B (x3), .Y (n7_0) );
  OAI21x1_ASAP7_75t_R g4 ( .A1 (xn2), .A2 (n7_0), .B (n6_1), .Y (n9_1) );
  AOI22x1_ASAP7_75t_R g5 ( .A1 (x3), .A2 (x1), .B1 (xn4), .B2 (xn2), .Y (n11_1) );
  assign y0 = n9_1;
  assign y1 = n11_1;
endmodule
