// Benchmark "/r/12_WAVE_10_EXPERIMENTAL_DISCOVERY/experiments/inputs/c1/c2/int2float" written by ABC on Fri Sep 25 23:42:08 2026

module \/r/12_WAVE_10_EXPERIMENTAL_DISCOVERY/experiments/inputs/c1/c2/int2float  ( 
    pi00, pi01, pi02, pi03, pi04, pi05, pi06, pi07, pi08, pi09, pi10,
    po0, po1, po2, po3, po4, po5, po6  );
  input  pi00, pi01, pi02, pi03, pi04, pi05, pi06, pi07, pi08, pi09,
    pi10;
  output po0, po1, po2, po3, po4, po5, po6;
  wire new_n19, new_n20, new_n21, new_n22, new_n23, new_n24, new_n25,
    new_n26, new_n27, new_n28, new_n29, new_n30, new_n31, new_n32, new_n33,
    new_n34, new_n35, new_n36, new_n37, new_n38, new_n39, new_n40, new_n41,
    new_n42, new_n43, new_n44, new_n45, new_n46, new_n47, new_n48, new_n49,
    new_n50, new_n51, new_n52, new_n53, new_n54, new_n55, new_n56, new_n57,
    new_n58, new_n60, new_n61, new_n62, new_n63, new_n64, new_n65, new_n66,
    new_n67, new_n68, new_n69, new_n70, new_n71, new_n72, new_n73, new_n74,
    new_n75, new_n76, new_n77, new_n78, new_n79, new_n80, new_n81, new_n82,
    new_n83, new_n84, new_n85, new_n86, new_n87, new_n88, new_n90, new_n91,
    new_n92, new_n93, new_n94, new_n95, new_n96, new_n97, new_n98, new_n99,
    new_n100, new_n101, new_n102, new_n103, new_n104, new_n105, new_n106,
    new_n107, new_n108, new_n109, new_n110, new_n111, new_n112, new_n113,
    new_n114, new_n115, new_n116, new_n117, new_n119, new_n120, new_n121,
    new_n122, new_n124, new_n125, new_n126, new_n127, new_n128, new_n129,
    new_n130, new_n131, new_n132, new_n133, new_n134, new_n135, new_n136,
    new_n138, new_n139, new_n140, new_n141, new_n142, new_n143, new_n144;
  INVx1_ASAP7_75t_R    g000(.A(pi01), .Y(new_n19));
  INVx1_ASAP7_75t_R    g001(.A(pi02), .Y(new_n20));
  INVx1_ASAP7_75t_R    g002(.A(pi03), .Y(new_n21));
  INVx1_ASAP7_75t_R    g003(.A(pi04), .Y(new_n22));
  INVx1_ASAP7_75t_R    g004(.A(pi05), .Y(new_n23));
  INVx1_ASAP7_75t_R    g005(.A(pi06), .Y(new_n24));
  INVx1_ASAP7_75t_R    g006(.A(pi07), .Y(new_n25));
  INVx1_ASAP7_75t_R    g007(.A(pi08), .Y(new_n26));
  INVx1_ASAP7_75t_R    g008(.A(pi09), .Y(new_n27));
  INVx1_ASAP7_75t_R    g009(.A(pi10), .Y(new_n28));
  NAND2x1_ASAP7_75t_R  g010(.A(pi04), .B(pi08), .Y(new_n29));
  AND2x2_ASAP7_75t_R   g011(.A(pi01), .B(pi04), .Y(new_n30));
  AO21x1_ASAP7_75t_R   g012(.A1(new_n22), .A2(pi08), .B(new_n30), .Y(new_n31));
  NOR2x1_ASAP7_75t_R   g013(.A(pi06), .B(pi07), .Y(new_n32));
  OAI21x1_ASAP7_75t_R  g014(.A1(pi00), .A2(new_n30), .B(new_n32), .Y(new_n33));
  AO21x1_ASAP7_75t_R   g015(.A1(new_n31), .A2(pi00), .B(new_n33), .Y(new_n34));
  NAND2x1_ASAP7_75t_R  g016(.A(new_n29), .B(new_n34), .Y(new_n35));
  NOR2x1_ASAP7_75t_R   g017(.A(pi02), .B(pi07), .Y(new_n36));
  AO32x1_ASAP7_75t_R   g018(.A1(pi01), .A2(new_n36), .A3(pi05), .B1(new_n22), .B2(pi07), .Y(new_n37));
  AND3x1_ASAP7_75t_R   g019(.A(new_n21), .B(pi04), .C(pi07), .Y(new_n38));
  AO21x1_ASAP7_75t_R   g020(.A1(new_n37), .A2(pi03), .B(new_n38), .Y(new_n39));
  AND3x1_ASAP7_75t_R   g021(.A(new_n22), .B(pi05), .C(pi08), .Y(new_n40));
  AO221x2_ASAP7_75t_R  g022(.A1(new_n26), .A2(new_n39), .B1(new_n23), .B2(new_n35), .C(new_n40), .Y(new_n41));
  AND3x1_ASAP7_75t_R   g023(.A(new_n23), .B(pi06), .C(pi09), .Y(new_n42));
  AND2x2_ASAP7_75t_R   g024(.A(new_n24), .B(pi05), .Y(new_n43));
  OA211x2_ASAP7_75t_R  g025(.A1(pi04), .A2(new_n25), .B(new_n20), .C(pi01), .Y(new_n44));
  AND2x2_ASAP7_75t_R   g026(.A(pi03), .B(pi04), .Y(new_n45));
  NAND2x1_ASAP7_75t_R  g027(.A(pi03), .B(pi04), .Y(new_n46));
  AND3x1_ASAP7_75t_R   g028(.A(new_n44), .B(new_n46), .C(new_n29), .Y(new_n47));
  NOR2x1_ASAP7_75t_R   g029(.A(pi07), .B(pi08), .Y(new_n48));
  AND3x1_ASAP7_75t_R   g030(.A(new_n48), .B(pi02), .C(new_n19), .Y(new_n49));
  OR3x1_ASAP7_75t_R    g031(.A(new_n47), .B(new_n49), .C(pi09), .Y(new_n50));
  AO221x2_ASAP7_75t_R  g032(.A1(new_n43), .A2(new_n50), .B1(new_n27), .B2(new_n41), .C(new_n42), .Y(new_n51));
  AND2x2_ASAP7_75t_R   g033(.A(new_n24), .B(pi07), .Y(new_n52));
  XOR2x2_ASAP7_75t_R   g034(.A(pi02), .B(pi03), .Y(new_n53));
  NOR2x1_ASAP7_75t_R   g035(.A(pi08), .B(pi09), .Y(new_n54));
  INVx1_ASAP7_75t_R    g036(.A(new_n54), .Y(new_n55));
  AO21x1_ASAP7_75t_R   g037(.A1(new_n53), .A2(new_n54), .B(pi10), .Y(new_n56));
  AO32x1_ASAP7_75t_R   g038(.A1(pi08), .A2(pi09), .A3(pi10), .B1(new_n25), .B2(new_n56), .Y(new_n57));
  AO22x1_ASAP7_75t_R   g039(.A1(new_n57), .A2(pi06), .B1(pi10), .B2(new_n52), .Y(new_n58));
  AO21x1_ASAP7_75t_R   g040(.A1(new_n51), .A2(new_n28), .B(new_n58), .Y(po0));
  OAI21x1_ASAP7_75t_R  g041(.A1(new_n19), .A2(new_n20), .B(pi00), .Y(new_n60));
  OA211x2_ASAP7_75t_R  g042(.A1(pi00), .A2(new_n20), .B(new_n25), .C(pi04), .Y(new_n61));
  AO21x1_ASAP7_75t_R   g043(.A1(new_n22), .A2(new_n27), .B(new_n36), .Y(new_n62));
  AO222x2_ASAP7_75t_R  g044(.A1(pi08), .A2(new_n27), .B1(new_n62), .B2(new_n19), .C1(new_n60), .C2(new_n61), .Y(new_n63));
  NAND2x1_ASAP7_75t_R  g045(.A(pi09), .B(new_n25), .Y(new_n64));
  AND3x1_ASAP7_75t_R   g046(.A(new_n54), .B(new_n46), .C(pi07), .Y(new_n65));
  AO221x2_ASAP7_75t_R  g047(.A1(new_n25), .A2(pi09), .B1(new_n24), .B2(new_n63), .C(new_n65), .Y(new_n66));
  NOR2x1_ASAP7_75t_R   g048(.A(pi04), .B(pi06), .Y(new_n67));
  AND3x1_ASAP7_75t_R   g049(.A(new_n25), .B(pi02), .C(pi01), .Y(new_n68));
  AO21x1_ASAP7_75t_R   g050(.A1(pi01), .A2(pi02), .B(pi07), .Y(new_n69));
  AO32x1_ASAP7_75t_R   g051(.A1(pi04), .A2(new_n54), .A3(new_n69), .B1(new_n67), .B2(new_n68), .Y(new_n70));
  OA21x2_ASAP7_75t_R   g052(.A1(pi04), .A2(pi09), .B(new_n64), .Y(new_n71));
  AO32x1_ASAP7_75t_R   g053(.A1(pi06), .A2(new_n55), .A3(new_n71), .B1(pi03), .B2(new_n70), .Y(new_n72));
  OR3x1_ASAP7_75t_R    g054(.A(new_n26), .B(pi09), .C(pi04), .Y(new_n73));
  AOI21x1_ASAP7_75t_R  g055(.A1(new_n64), .A2(new_n73), .B(pi06), .Y(new_n74));
  AO21x1_ASAP7_75t_R   g056(.A1(new_n72), .A2(pi05), .B(new_n74), .Y(new_n75));
  AOI21x1_ASAP7_75t_R  g057(.A1(new_n23), .A2(new_n66), .B(new_n75), .Y(new_n76));
  NAND2x1_ASAP7_75t_R  g058(.A(pi06), .B(pi07), .Y(new_n77));
  AND5x1_ASAP7_75t_R   g059(.A(new_n27), .B(pi10), .C(pi06), .D(pi07), .E(pi08), .Y(new_n78));
  INVx1_ASAP7_75t_R    g060(.A(new_n78), .Y(new_n79));
  OR3x1_ASAP7_75t_R    g061(.A(new_n24), .B(pi09), .C(pi04), .Y(new_n80));
  OR3x1_ASAP7_75t_R    g062(.A(new_n23), .B(pi06), .C(pi01), .Y(new_n81));
  AO21x1_ASAP7_75t_R   g063(.A1(new_n80), .A2(new_n81), .B(pi03), .Y(new_n82));
  OR3x1_ASAP7_75t_R    g064(.A(new_n23), .B(pi06), .C(pi03), .Y(new_n83));
  AO21x1_ASAP7_75t_R   g065(.A1(new_n80), .A2(new_n83), .B(pi02), .Y(new_n84));
  OR5x1_ASAP7_75t_R    g066(.A(new_n20), .B(new_n21), .C(new_n22), .D(new_n24), .E(pi09), .Y(new_n85));
  AND2x2_ASAP7_75t_R   g067(.A(new_n84), .B(new_n85), .Y(new_n86));
  AO21x1_ASAP7_75t_R   g068(.A1(new_n86), .A2(new_n82), .B(pi07), .Y(new_n87));
  AO221x2_ASAP7_75t_R  g069(.A1(pi06), .A2(pi07), .B1(new_n28), .B2(new_n87), .C(pi08), .Y(new_n88));
  OA211x2_ASAP7_75t_R  g070(.A1(new_n76), .A2(pi10), .B(new_n88), .C(new_n79), .Y(po1));
  AND3x1_ASAP7_75t_R   g071(.A(new_n22), .B(pi05), .C(pi03), .Y(new_n90));
  AND4x2_ASAP7_75t_R   g072(.A(new_n21), .B(new_n24), .C(pi04), .D(pi00), .Y(new_n91));
  OA21x2_ASAP7_75t_R   g073(.A1(new_n91), .A2(new_n90), .B(pi01), .Y(new_n92));
  NAND2x1_ASAP7_75t_R  g074(.A(pi00), .B(pi01), .Y(new_n93));
  AO21x1_ASAP7_75t_R   g075(.A1(new_n93), .A2(new_n45), .B(new_n67), .Y(new_n94));
  AO21x1_ASAP7_75t_R   g076(.A1(new_n23), .A2(new_n94), .B(new_n92), .Y(new_n95));
  AND3x1_ASAP7_75t_R   g077(.A(new_n20), .B(new_n24), .C(pi03), .Y(new_n96));
  AO21x1_ASAP7_75t_R   g078(.A1(new_n21), .A2(pi05), .B(new_n96), .Y(new_n97));
  AOI22x1_ASAP7_75t_R  g079(.A1(pi04), .A2(new_n97), .B1(new_n95), .B2(pi02), .Y(new_n98));
  NAND2x1_ASAP7_75t_R  g080(.A(pi05), .B(pi06), .Y(new_n99));
  OR3x1_ASAP7_75t_R    g081(.A(new_n20), .B(new_n24), .C(pi05), .Y(new_n100));
  AO21x1_ASAP7_75t_R   g082(.A1(new_n100), .A2(new_n81), .B(new_n46), .Y(new_n101));
  OA21x2_ASAP7_75t_R   g083(.A1(new_n45), .A2(new_n99), .B(new_n101), .Y(new_n102));
  OA21x2_ASAP7_75t_R   g084(.A1(new_n98), .A2(pi07), .B(new_n102), .Y(new_n103));
  AO21x1_ASAP7_75t_R   g085(.A1(pi04), .A2(pi05), .B(new_n77), .Y(new_n104));
  AND2x2_ASAP7_75t_R   g086(.A(new_n25), .B(pi06), .Y(new_n105));
  AO22x1_ASAP7_75t_R   g087(.A1(new_n105), .A2(new_n20), .B1(new_n52), .B2(pi03), .Y(new_n106));
  AND3x1_ASAP7_75t_R   g088(.A(new_n106), .B(pi05), .C(pi04), .Y(new_n107));
  INVx1_ASAP7_75t_R    g089(.A(new_n107), .Y(new_n108));
  OA211x2_ASAP7_75t_R  g090(.A1(new_n103), .A2(pi08), .B(new_n108), .C(new_n104), .Y(new_n109));
  AND3x1_ASAP7_75t_R   g091(.A(new_n105), .B(pi05), .C(pi04), .Y(new_n110));
  OAI21x1_ASAP7_75t_R  g092(.A1(new_n52), .A2(new_n110), .B(pi08), .Y(new_n111));
  OAI21x1_ASAP7_75t_R  g093(.A1(pi09), .A2(new_n109), .B(new_n111), .Y(new_n112));
  AND3x1_ASAP7_75t_R   g094(.A(new_n26), .B(pi09), .C(pi05), .Y(new_n113));
  AO21x1_ASAP7_75t_R   g095(.A1(pi08), .A2(pi10), .B(new_n113), .Y(new_n114));
  NAND2x1_ASAP7_75t_R  g096(.A(pi05), .B(pi07), .Y(new_n115));
  AO21x1_ASAP7_75t_R   g097(.A1(new_n115), .A2(pi08), .B(pi10), .Y(new_n116));
  AO32x1_ASAP7_75t_R   g098(.A1(pi06), .A2(new_n114), .A3(pi07), .B1(pi09), .B2(new_n116), .Y(new_n117));
  AO21x1_ASAP7_75t_R   g099(.A1(new_n112), .A2(new_n28), .B(new_n117), .Y(po2));
  AND3x1_ASAP7_75t_R   g100(.A(pi05), .B(pi06), .C(pi07), .Y(new_n119));
  INVx1_ASAP7_75t_R    g101(.A(new_n119), .Y(new_n120));
  OR3x1_ASAP7_75t_R    g102(.A(pi04), .B(pi07), .C(pi08), .Y(new_n121));
  OA33x2_ASAP7_75t_R   g103(.A1(pi05), .A2(pi06), .A3(new_n121), .B1(new_n29), .B2(new_n120), .B3(pi02), .Y(new_n122));
  OR4x2_ASAP7_75t_R    g104(.A(new_n122), .B(pi10), .C(pi09), .D(pi03), .Y(po3));
  AO21x1_ASAP7_75t_R   g105(.A1(pi05), .A2(pi06), .B(new_n68), .Y(new_n124));
  NOR2x1_ASAP7_75t_R   g106(.A(pi05), .B(pi07), .Y(new_n125));
  AO21x1_ASAP7_75t_R   g107(.A1(new_n124), .A2(pi03), .B(new_n125), .Y(new_n126));
  AO21x1_ASAP7_75t_R   g108(.A1(new_n126), .A2(pi04), .B(new_n105), .Y(new_n127));
  AND4x2_ASAP7_75t_R   g109(.A(new_n23), .B(new_n24), .C(pi00), .D(pi01), .Y(new_n128));
  OA211x2_ASAP7_75t_R  g110(.A1(new_n110), .A2(new_n128), .B(pi02), .C(pi03), .Y(new_n129));
  INVx1_ASAP7_75t_R    g111(.A(new_n129), .Y(new_n130));
  AO21x1_ASAP7_75t_R   g112(.A1(new_n127), .A2(new_n130), .B(pi08), .Y(new_n131));
  AO21x1_ASAP7_75t_R   g113(.A1(new_n119), .A2(pi08), .B(new_n27), .Y(new_n132));
  NAND2x1_ASAP7_75t_R  g114(.A(pi03), .B(pi08), .Y(new_n133));
  OA21x2_ASAP7_75t_R   g115(.A1(new_n20), .A2(pi03), .B(new_n133), .Y(new_n134));
  OR5x1_ASAP7_75t_R    g116(.A(new_n22), .B(new_n23), .C(new_n24), .D(new_n25), .E(pi09), .Y(new_n135));
  OA21x2_ASAP7_75t_R   g117(.A1(new_n135), .A2(new_n134), .B(new_n132), .Y(new_n136));
  AO21x1_ASAP7_75t_R   g118(.A1(new_n131), .A2(new_n136), .B(pi10), .Y(po4));
  AND5x1_ASAP7_75t_R   g119(.A(new_n125), .B(pi03), .C(pi01), .D(pi00), .E(new_n26), .Y(new_n138));
  AO21x1_ASAP7_75t_R   g120(.A1(pi08), .A2(new_n119), .B(new_n138), .Y(new_n139));
  AO32x1_ASAP7_75t_R   g121(.A1(pi03), .A2(pi08), .A3(new_n119), .B1(pi02), .B2(new_n139), .Y(new_n140));
  AND5x1_ASAP7_75t_R   g122(.A(pi02), .B(pi03), .C(pi04), .D(pi05), .E(pi06), .Y(new_n141));
  INVx1_ASAP7_75t_R    g123(.A(new_n141), .Y(new_n142));
  OA211x2_ASAP7_75t_R  g124(.A1(pi05), .A2(pi06), .B(new_n142), .C(new_n48), .Y(new_n143));
  OR3x1_ASAP7_75t_R    g125(.A(new_n143), .B(pi10), .C(pi09), .Y(new_n144));
  AO21x1_ASAP7_75t_R   g126(.A1(pi04), .A2(new_n140), .B(new_n144), .Y(po5));
  OR5x1_ASAP7_75t_R    g127(.A(new_n141), .B(pi09), .C(pi08), .D(pi07), .E(pi10), .Y(po6));
endmodule


