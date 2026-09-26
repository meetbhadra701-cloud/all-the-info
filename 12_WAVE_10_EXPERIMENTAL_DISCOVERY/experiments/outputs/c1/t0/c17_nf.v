// Benchmark "/w/experiments/inputs/c1/c2/c17" written by ABC on Fri Sep 25 09:01:11 2026

module \/w/experiments/inputs/c1/c2/c17  ( 
    pi0, pi1, pi2, pi3, pi4,
    po0, po1  );
  input  pi0, pi1, pi2, pi3, pi4;
  output po0, po1;
  wire new_n8, new_n9, new_n10, new_n11;
  INVx1_ASAP7_75t_R    g0(.A(pi2), .Y(new_n8));
  INVx1_ASAP7_75t_R    g1(.A(pi4), .Y(new_n9));
  NAND2x1_ASAP7_75t_R  g2(.A(pi0), .B(pi1), .Y(new_n10));
  AND2x2_ASAP7_75t_R   g3(.A(pi1), .B(pi3), .Y(new_n11));
  OAI21x1_ASAP7_75t_R  g4(.A1(new_n8), .A2(new_n11), .B(new_n10), .Y(po0));
  AOI22x1_ASAP7_75t_R  g5(.A1(pi1), .A2(pi3), .B1(new_n9), .B2(new_n8), .Y(po1));
endmodule


