// Benchmark "/r/12_WAVE_10_EXPERIMENTAL_DISCOVERY/experiments/inputs/c1/c2/ctrl" written by ABC on Fri Sep 25 23:16:57 2026

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
    new_n42, new_n43, new_n44, new_n45, new_n46, new_n48, new_n49, new_n50,
    new_n51, new_n52, new_n54, new_n55, new_n56, new_n58, new_n59, new_n61,
    new_n62, new_n63, new_n64, new_n65, new_n66, new_n67, new_n70, new_n71,
    new_n72, new_n74, new_n76, new_n78, new_n80, new_n81, new_n82, new_n84,
    new_n86, new_n87, new_n88, new_n93, new_n98, new_n99, new_n100,
    new_n102, new_n104, new_n106, new_n107, new_n109;
  INVx1_ASAP7_75t_R    g00(.A(pi0), .Y(new_n35));
  INVx1_ASAP7_75t_R    g01(.A(pi1), .Y(new_n36));
  INVx1_ASAP7_75t_R    g02(.A(pi2), .Y(new_n37));
  INVx1_ASAP7_75t_R    g03(.A(pi3), .Y(new_n38));
  INVx1_ASAP7_75t_R    g04(.A(pi4), .Y(new_n39));
  INVx1_ASAP7_75t_R    g05(.A(pi5), .Y(new_n40));
  INVx1_ASAP7_75t_R    g06(.A(pi6), .Y(new_n41));
  AND2x2_ASAP7_75t_R   g07(.A(pi3), .B(pi4), .Y(new_n42));
  NAND2x1_ASAP7_75t_R  g08(.A(pi3), .B(pi4), .Y(new_n43));
  OA21x2_ASAP7_75t_R   g09(.A1(pi0), .A2(pi1), .B(new_n42), .Y(new_n44));
  NOR2x1_ASAP7_75t_R   g10(.A(pi3), .B(pi4), .Y(new_n45));
  AO21x1_ASAP7_75t_R   g11(.A1(new_n45), .A2(pi1), .B(new_n42), .Y(new_n46));
  AO21x1_ASAP7_75t_R   g12(.A1(new_n46), .A2(pi2), .B(new_n44), .Y(po00));
  NAND2x1_ASAP7_75t_R  g13(.A(pi4), .B(new_n38), .Y(new_n48));
  AO21x1_ASAP7_75t_R   g14(.A1(new_n38), .A2(pi4), .B(new_n36), .Y(new_n49));
  AND3x1_ASAP7_75t_R   g15(.A(new_n35), .B(pi3), .C(pi4), .Y(new_n50));
  OA21x2_ASAP7_75t_R   g16(.A1(new_n50), .A2(pi1), .B(new_n49), .Y(new_n51));
  AO21x1_ASAP7_75t_R   g17(.A1(new_n45), .A2(pi1), .B(new_n37), .Y(new_n52));
  OA21x2_ASAP7_75t_R   g18(.A1(new_n51), .A2(pi2), .B(new_n52), .Y(po01));
  OAI21x1_ASAP7_75t_R  g19(.A1(pi0), .A2(new_n48), .B(pi1), .Y(new_n54));
  AND2x2_ASAP7_75t_R   g20(.A(new_n39), .B(pi3), .Y(new_n55));
  OA21x2_ASAP7_75t_R   g21(.A1(new_n50), .A2(pi1), .B(new_n37), .Y(new_n56));
  OA21x2_ASAP7_75t_R   g22(.A1(new_n54), .A2(new_n55), .B(new_n56), .Y(po02));
  NOR2x1_ASAP7_75t_R   g23(.A(pi1), .B(pi2), .Y(new_n58));
  NOR2x1_ASAP7_75t_R   g24(.A(new_n38), .B(new_n58), .Y(new_n59));
  AOI211x1_ASAP7_75t_R g25(.A1(pi0), .A2(new_n42), .B(new_n59), .C(new_n45), .Y(po03));
  OA21x2_ASAP7_75t_R   g26(.A1(new_n39), .A2(pi6), .B(pi3), .Y(new_n61));
  NAND2x1_ASAP7_75t_R  g27(.A(pi4), .B(new_n40), .Y(new_n62));
  OA211x2_ASAP7_75t_R  g28(.A1(new_n41), .A2(new_n62), .B(new_n61), .C(pi0), .Y(new_n63));
  AND4x2_ASAP7_75t_R   g29(.A(new_n35), .B(pi3), .C(pi4), .D(pi5), .Y(new_n64));
  OAI21x1_ASAP7_75t_R  g30(.A1(new_n64), .A2(new_n63), .B(pi1), .Y(new_n65));
  AO21x1_ASAP7_75t_R   g31(.A1(new_n38), .A2(pi4), .B(new_n37), .Y(new_n66));
  OA21x2_ASAP7_75t_R   g32(.A1(new_n48), .A2(new_n35), .B(pi2), .Y(new_n67));
  AOI21x1_ASAP7_75t_R  g33(.A1(new_n37), .A2(new_n65), .B(new_n67), .Y(po04));
  OA211x2_ASAP7_75t_R  g34(.A1(pi2), .A2(new_n61), .B(new_n66), .C(pi1), .Y(po05));
  AND2x2_ASAP7_75t_R   g35(.A(pi0), .B(pi1), .Y(new_n70));
  OR3x1_ASAP7_75t_R    g36(.A(new_n43), .B(new_n70), .C(pi2), .Y(new_n71));
  AO21x1_ASAP7_75t_R   g37(.A1(pi3), .A2(pi4), .B(new_n37), .Y(new_n72));
  OA211x2_ASAP7_75t_R  g38(.A1(pi3), .A2(pi4), .B(new_n71), .C(new_n72), .Y(po06));
  AO22x1_ASAP7_75t_R   g39(.A1(new_n45), .A2(pi1), .B1(pi0), .B2(new_n42), .Y(new_n74));
  AO22x1_ASAP7_75t_R   g40(.A1(new_n74), .A2(pi2), .B1(new_n50), .B2(new_n58), .Y(po07));
  OA21x2_ASAP7_75t_R   g41(.A1(new_n72), .A2(new_n45), .B(pi1), .Y(new_n76));
  OA21x2_ASAP7_75t_R   g42(.A1(new_n54), .A2(pi2), .B(new_n76), .Y(po08));
  NAND2x1_ASAP7_75t_R  g43(.A(new_n43), .B(new_n58), .Y(new_n78));
  OA211x2_ASAP7_75t_R  g44(.A1(new_n54), .A2(pi2), .B(new_n52), .C(new_n78), .Y(po09));
  OA21x2_ASAP7_75t_R   g45(.A1(new_n39), .A2(pi1), .B(pi3), .Y(new_n80));
  OA211x2_ASAP7_75t_R  g46(.A1(pi0), .A2(new_n36), .B(new_n38), .C(pi4), .Y(new_n81));
  OR3x1_ASAP7_75t_R    g47(.A(new_n81), .B(new_n80), .C(pi2), .Y(new_n82));
  AND2x2_ASAP7_75t_R   g48(.A(new_n82), .B(new_n66), .Y(po10));
  OR5x1_ASAP7_75t_R    g49(.A(pi0), .B(pi1), .C(pi2), .D(pi3), .E(pi4), .Y(new_n84));
  INVx1_ASAP7_75t_R    g50(.A(new_n84), .Y(po11));
  OA21x2_ASAP7_75t_R   g51(.A1(pi0), .A2(pi1), .B(pi4), .Y(new_n86));
  OA21x2_ASAP7_75t_R   g52(.A1(new_n86), .A2(pi3), .B(new_n37), .Y(new_n87));
  AO21x1_ASAP7_75t_R   g53(.A1(new_n38), .A2(pi1), .B(pi4), .Y(new_n88));
  AO21x1_ASAP7_75t_R   g54(.A1(pi2), .A2(new_n88), .B(new_n87), .Y(po12));
  AND3x1_ASAP7_75t_R   g55(.A(new_n38), .B(new_n39), .C(pi2), .Y(po19));
  AND3x1_ASAP7_75t_R   g56(.A(new_n45), .B(pi2), .C(pi0), .Y(po13));
  AND3x1_ASAP7_75t_R   g57(.A(new_n45), .B(pi2), .C(new_n35), .Y(po14));
  AND3x1_ASAP7_75t_R   g58(.A(new_n36), .B(new_n39), .C(pi3), .Y(new_n93));
  AND3x1_ASAP7_75t_R   g59(.A(new_n93), .B(pi2), .C(new_n35), .Y(po15));
  AND3x1_ASAP7_75t_R   g60(.A(new_n93), .B(pi2), .C(pi0), .Y(po16));
  AND3x1_ASAP7_75t_R   g61(.A(new_n55), .B(new_n70), .C(pi2), .Y(po17));
  AND5x1_ASAP7_75t_R   g62(.A(new_n35), .B(new_n39), .C(pi3), .D(pi2), .E(pi1), .Y(po18));
  OAI21x1_ASAP7_75t_R  g63(.A1(new_n70), .A2(new_n43), .B(pi2), .Y(new_n98));
  AND3x1_ASAP7_75t_R   g64(.A(new_n62), .B(new_n70), .C(pi3), .Y(new_n99));
  AO21x1_ASAP7_75t_R   g65(.A1(new_n93), .A2(pi0), .B(pi2), .Y(new_n100));
  OA21x2_ASAP7_75t_R   g66(.A1(new_n99), .A2(new_n100), .B(new_n98), .Y(po20));
  AND5x1_ASAP7_75t_R   g67(.A(new_n41), .B(pi4), .C(pi3), .D(pi1), .E(pi5), .Y(new_n102));
  OA211x2_ASAP7_75t_R  g68(.A1(new_n102), .A2(new_n93), .B(new_n37), .C(pi0), .Y(po21));
  OA211x2_ASAP7_75t_R  g69(.A1(new_n41), .A2(new_n62), .B(new_n61), .C(new_n70), .Y(new_n104));
  OA21x2_ASAP7_75t_R   g70(.A1(new_n104), .A2(pi2), .B(new_n98), .Y(po22));
  XOR2x2_ASAP7_75t_R   g71(.A(pi0), .B(pi1), .Y(new_n106));
  OR3x1_ASAP7_75t_R    g72(.A(new_n48), .B(new_n106), .C(pi2), .Y(new_n107));
  INVx1_ASAP7_75t_R    g73(.A(new_n107), .Y(po24));
  OR5x1_ASAP7_75t_R    g74(.A(new_n35), .B(new_n39), .C(pi3), .D(pi2), .E(pi1), .Y(new_n109));
  INVx1_ASAP7_75t_R    g75(.A(new_n109), .Y(po25));
  assign               po23 = 1'b1;
endmodule


