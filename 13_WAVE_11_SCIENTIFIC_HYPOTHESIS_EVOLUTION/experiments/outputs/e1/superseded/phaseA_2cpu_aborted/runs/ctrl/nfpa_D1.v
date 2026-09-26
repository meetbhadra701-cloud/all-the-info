// Benchmark "/r/12_WAVE_10_EXPERIMENTAL_DISCOVERY/experiments/inputs/c1/c2/ctrl" written by ABC on Fri Sep 25 23:10:58 2026

module \/r/12_WAVE_10_EXPERIMENTAL_DISCOVERY/experiments/inputs/c1/c2/ctrl  ( 
    pi0, pi1, pi2, pi3, pi4, pi5, pi6,
    po00, po01, po02, po03, po04, po05, po06, po07, po08, po09, po10, po11,
    po12, po13, po14, po15, po16, po17, po18, po19, po20, po21, po22, po23,
    po24, po25  );
  input  pi0, pi1, pi2, pi3, pi4, pi5, pi6;
  output po00, po01, po02, po03, po04, po05, po06, po07, po08, po09, po10,
    po11, po12, po13, po14, po15, po16, po17, po18, po19, po20, po21, po22,
    po23, po24, po25;
  wire new_n35, new_n36, new_n37, new_n38, new_n39, new_n40, new_n41,
    new_n42, new_n43, new_n44, new_n46, new_n47, new_n48, new_n49, new_n50,
    new_n51, new_n53, new_n54, new_n56, new_n57, new_n59, new_n60, new_n61,
    new_n62, new_n63, new_n64, new_n65, new_n68, new_n69, new_n70, new_n72,
    new_n74, new_n77, new_n78, new_n79, new_n81, new_n83, new_n84, new_n85,
    new_n90, new_n95, new_n96, new_n97, new_n99, new_n101, new_n104;
  INVx1_ASAP7_75t_R    g00(.A(pi0), .Y(new_n35));
  INVx1_ASAP7_75t_R    g01(.A(pi2), .Y(new_n36));
  INVx1_ASAP7_75t_R    g02(.A(pi3), .Y(new_n37));
  INVx1_ASAP7_75t_R    g03(.A(pi4), .Y(new_n38));
  INVx1_ASAP7_75t_R    g04(.A(pi6), .Y(new_n39));
  AND2x2_ASAP7_75t_R   g05(.A(pi3), .B(pi4), .Y(new_n40));
  NAND2x1_ASAP7_75t_R  g06(.A(pi3), .B(pi4), .Y(new_n41));
  NOR2x1_ASAP7_75t_R   g07(.A(pi0), .B(pi1), .Y(new_n42));
  NOR2x1_ASAP7_75t_R   g08(.A(pi3), .B(pi4), .Y(new_n43));
  AOI21x1_ASAP7_75t_R  g09(.A1(pi1), .A2(new_n43), .B(new_n40), .Y(new_n44));
  OAI22x1_ASAP7_75t_R  g10(.A1(new_n41), .A2(new_n42), .B1(new_n44), .B2(new_n36), .Y(po00));
  AND2x2_ASAP7_75t_R   g11(.A(new_n37), .B(pi4), .Y(new_n46));
  NAND2x1_ASAP7_75t_R  g12(.A(pi4), .B(new_n37), .Y(new_n47));
  AND3x1_ASAP7_75t_R   g13(.A(new_n35), .B(pi3), .C(pi4), .Y(new_n48));
  NOR2x1_ASAP7_75t_R   g14(.A(pi1), .B(new_n48), .Y(new_n49));
  AOI21x1_ASAP7_75t_R  g15(.A1(pi1), .A2(new_n47), .B(new_n49), .Y(new_n50));
  AO21x1_ASAP7_75t_R   g16(.A1(new_n43), .A2(pi1), .B(new_n36), .Y(new_n51));
  OA21x2_ASAP7_75t_R   g17(.A1(new_n50), .A2(pi2), .B(new_n51), .Y(po01));
  OA21x2_ASAP7_75t_R   g18(.A1(new_n47), .A2(pi0), .B(pi1), .Y(new_n53));
  NAND2x1_ASAP7_75t_R  g19(.A(pi3), .B(new_n38), .Y(new_n54));
  AOI211x1_ASAP7_75t_R g20(.A1(new_n53), .A2(new_n54), .B(new_n49), .C(pi2), .Y(po02));
  NOR2x1_ASAP7_75t_R   g21(.A(pi1), .B(pi2), .Y(new_n56));
  OR2x4_ASAP7_75t_R    g22(.A(pi1), .B(pi2), .Y(new_n57));
  AOI221x1_ASAP7_75t_R g23(.A1(pi0), .A2(new_n40), .B1(pi3), .B2(new_n57), .C(new_n43), .Y(po03));
  OA21x2_ASAP7_75t_R   g24(.A1(new_n38), .A2(pi6), .B(pi3), .Y(new_n59));
  OR2x4_ASAP7_75t_R    g25(.A(pi5), .B(new_n38), .Y(new_n60));
  OA211x2_ASAP7_75t_R  g26(.A1(new_n60), .A2(new_n39), .B(pi0), .C(new_n59), .Y(new_n61));
  AND2x2_ASAP7_75t_R   g27(.A(new_n48), .B(pi5), .Y(new_n62));
  OA21x2_ASAP7_75t_R   g28(.A1(new_n61), .A2(new_n62), .B(pi1), .Y(new_n63));
  AO21x1_ASAP7_75t_R   g29(.A1(new_n37), .A2(pi4), .B(new_n36), .Y(new_n64));
  AO21x1_ASAP7_75t_R   g30(.A1(new_n46), .A2(pi0), .B(new_n36), .Y(new_n65));
  OA21x2_ASAP7_75t_R   g31(.A1(new_n63), .A2(pi2), .B(new_n65), .Y(po04));
  OA211x2_ASAP7_75t_R  g32(.A1(pi2), .A2(new_n59), .B(new_n64), .C(pi1), .Y(po05));
  AND2x2_ASAP7_75t_R   g33(.A(pi0), .B(pi1), .Y(new_n68));
  OR3x1_ASAP7_75t_R    g34(.A(new_n41), .B(new_n68), .C(pi2), .Y(new_n69));
  AO21x1_ASAP7_75t_R   g35(.A1(pi3), .A2(pi4), .B(new_n36), .Y(new_n70));
  OA211x2_ASAP7_75t_R  g36(.A1(pi3), .A2(pi4), .B(new_n69), .C(new_n70), .Y(po06));
  AO22x1_ASAP7_75t_R   g37(.A1(new_n43), .A2(pi1), .B1(pi0), .B2(new_n40), .Y(new_n72));
  AO22x1_ASAP7_75t_R   g38(.A1(new_n72), .A2(pi2), .B1(new_n48), .B2(new_n56), .Y(po07));
  NAND2x1_ASAP7_75t_R  g39(.A(new_n36), .B(new_n53), .Y(new_n74));
  OA211x2_ASAP7_75t_R  g40(.A1(new_n43), .A2(new_n70), .B(new_n74), .C(pi1), .Y(po08));
  OA211x2_ASAP7_75t_R  g41(.A1(new_n40), .A2(new_n57), .B(new_n74), .C(new_n51), .Y(po09));
  OA21x2_ASAP7_75t_R   g42(.A1(new_n38), .A2(pi1), .B(pi3), .Y(new_n77));
  NAND2x1_ASAP7_75t_R  g43(.A(pi1), .B(new_n35), .Y(new_n78));
  AO21x1_ASAP7_75t_R   g44(.A1(new_n46), .A2(new_n78), .B(pi2), .Y(new_n79));
  OA21x2_ASAP7_75t_R   g45(.A1(new_n79), .A2(new_n77), .B(new_n64), .Y(po10));
  OR5x1_ASAP7_75t_R    g46(.A(pi0), .B(pi1), .C(pi2), .D(pi3), .E(pi4), .Y(new_n81));
  INVx1_ASAP7_75t_R    g47(.A(new_n81), .Y(po11));
  NOR2x1_ASAP7_75t_R   g48(.A(new_n38), .B(new_n42), .Y(new_n83));
  OA21x2_ASAP7_75t_R   g49(.A1(new_n83), .A2(pi3), .B(new_n36), .Y(new_n84));
  AO21x1_ASAP7_75t_R   g50(.A1(new_n37), .A2(pi1), .B(pi4), .Y(new_n85));
  AO21x1_ASAP7_75t_R   g51(.A1(pi2), .A2(new_n85), .B(new_n84), .Y(po12));
  AND3x1_ASAP7_75t_R   g52(.A(new_n37), .B(new_n38), .C(pi2), .Y(po19));
  AND3x1_ASAP7_75t_R   g53(.A(new_n43), .B(pi2), .C(pi0), .Y(po13));
  AND3x1_ASAP7_75t_R   g54(.A(new_n43), .B(pi2), .C(new_n35), .Y(po14));
  NOR2x1_ASAP7_75t_R   g55(.A(pi1), .B(new_n54), .Y(new_n90));
  AND3x1_ASAP7_75t_R   g56(.A(new_n90), .B(pi2), .C(new_n35), .Y(po15));
  AND3x1_ASAP7_75t_R   g57(.A(new_n90), .B(pi2), .C(pi0), .Y(po16));
  AND5x1_ASAP7_75t_R   g58(.A(new_n38), .B(pi2), .C(pi1), .D(pi0), .E(pi3), .Y(po17));
  AND5x1_ASAP7_75t_R   g59(.A(new_n35), .B(new_n38), .C(pi3), .D(pi2), .E(pi1), .Y(po18));
  OAI21x1_ASAP7_75t_R  g60(.A1(new_n68), .A2(new_n41), .B(pi2), .Y(new_n95));
  AND3x1_ASAP7_75t_R   g61(.A(new_n60), .B(new_n68), .C(pi3), .Y(new_n96));
  AO21x1_ASAP7_75t_R   g62(.A1(new_n90), .A2(pi0), .B(pi2), .Y(new_n97));
  OA21x2_ASAP7_75t_R   g63(.A1(new_n97), .A2(new_n96), .B(new_n95), .Y(po20));
  AND5x1_ASAP7_75t_R   g64(.A(new_n39), .B(pi4), .C(pi3), .D(pi1), .E(pi5), .Y(new_n99));
  OA211x2_ASAP7_75t_R  g65(.A1(new_n90), .A2(new_n99), .B(pi0), .C(new_n36), .Y(po21));
  OA211x2_ASAP7_75t_R  g66(.A1(new_n60), .A2(new_n39), .B(new_n59), .C(new_n68), .Y(new_n101));
  OA21x2_ASAP7_75t_R   g67(.A1(new_n101), .A2(pi2), .B(new_n95), .Y(po22));
  OA211x2_ASAP7_75t_R  g68(.A1(new_n42), .A2(new_n68), .B(new_n46), .C(new_n36), .Y(po24));
  OR5x1_ASAP7_75t_R    g69(.A(new_n35), .B(new_n38), .C(pi3), .D(pi2), .E(pi1), .Y(new_n104));
  INVx1_ASAP7_75t_R    g70(.A(new_n104), .Y(po25));
  assign               po23 = 1'b1;
endmodule


