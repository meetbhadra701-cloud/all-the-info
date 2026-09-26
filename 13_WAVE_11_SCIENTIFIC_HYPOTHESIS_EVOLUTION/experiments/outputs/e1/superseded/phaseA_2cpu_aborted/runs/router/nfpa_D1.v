// Benchmark "/r/12_WAVE_10_EXPERIMENTAL_DISCOVERY/experiments/inputs/c1/c2/router" written by ABC on Fri Sep 25 23:11:03 2026

module \/r/12_WAVE_10_EXPERIMENTAL_DISCOVERY/experiments/inputs/c1/c2/router  ( 
    pi00, pi01, pi02, pi03, pi04, pi05, pi06, pi07, pi08, pi09, pi10, pi11,
    pi12, pi13, pi14, pi15, pi16, pi17, pi18, pi19, pi20, pi21, pi22, pi23,
    pi24, pi25, pi26, pi27, pi28, pi29, pi30, pi31, pi32, pi33, pi34, pi35,
    pi36, pi37, pi38, pi39, pi40, pi41, pi42, pi43, pi44, pi45, pi46, pi47,
    pi48, pi49, pi50, pi51, pi52, pi53, pi54, pi55, pi56, pi57, pi58, pi59,
    po00, po01, po02, po03, po04, po05, po06, po07, po08, po09, po10, po11,
    po12, po13, po14, po15, po16, po17, po18, po19, po20, po21, po22, po23,
    po24, po25, po26, po27, po28, po29  );
  input  pi00, pi01, pi02, pi03, pi04, pi05, pi06, pi07, pi08, pi09,
    pi10, pi11, pi12, pi13, pi14, pi15, pi16, pi17, pi18, pi19, pi20, pi21,
    pi22, pi23, pi24, pi25, pi26, pi27, pi28, pi29, pi30, pi31, pi32, pi33,
    pi34, pi35, pi36, pi37, pi38, pi39, pi40, pi41, pi42, pi43, pi44, pi45,
    pi46, pi47, pi48, pi49, pi50, pi51, pi52, pi53, pi54, pi55, pi56, pi57,
    pi58, pi59;
  output po00, po01, po02, po03, po04, po05, po06, po07, po08, po09, po10,
    po11, po12, po13, po14, po15, po16, po17, po18, po19, po20, po21, po22,
    po23, po24, po25, po26, po27, po28, po29;
  wire new_n92, new_n93, new_n94, new_n95, new_n96, new_n97, new_n98,
    new_n99, new_n100, new_n101, new_n102, new_n103, new_n104, new_n105,
    new_n106, new_n107, new_n108, new_n109, new_n110, new_n111, new_n112,
    new_n113, new_n114, new_n115, new_n116, new_n117, new_n118, new_n119,
    new_n120, new_n121, new_n122, new_n123, new_n124, new_n125, new_n126,
    new_n127, new_n128, new_n129, new_n130, new_n131, new_n132, new_n133,
    new_n134, new_n135, new_n136, new_n137, new_n138, new_n139, new_n140,
    new_n141, new_n142, new_n143, new_n144, new_n145, new_n146, new_n147,
    new_n148, new_n149, new_n150, new_n151, new_n152, new_n153, new_n155,
    new_n156, new_n157, new_n158, new_n159, new_n160, new_n161, new_n162,
    new_n163, new_n164, new_n165, new_n166, new_n167, new_n168, new_n169,
    new_n170, new_n171, new_n172, new_n173, new_n174, new_n175, new_n176,
    new_n177, new_n178, new_n179, new_n180, new_n181, new_n182, new_n183,
    new_n184, new_n185, new_n186, new_n187, new_n188, new_n189, new_n190,
    new_n191, new_n192, new_n193, new_n194, new_n195, new_n196, new_n197,
    new_n198, new_n200, new_n201;
  INVx1_ASAP7_75t_R    g000(.A(pi09), .Y(new_n92));
  INVx1_ASAP7_75t_R    g001(.A(pi14), .Y(new_n93));
  INVx1_ASAP7_75t_R    g002(.A(pi15), .Y(new_n94));
  INVx1_ASAP7_75t_R    g003(.A(pi16), .Y(new_n95));
  INVx1_ASAP7_75t_R    g004(.A(pi17), .Y(new_n96));
  INVx1_ASAP7_75t_R    g005(.A(pi18), .Y(new_n97));
  INVx1_ASAP7_75t_R    g006(.A(pi19), .Y(new_n98));
  INVx1_ASAP7_75t_R    g007(.A(pi20), .Y(new_n99));
  INVx1_ASAP7_75t_R    g008(.A(pi23), .Y(new_n100));
  INVx1_ASAP7_75t_R    g009(.A(pi39), .Y(new_n101));
  INVx1_ASAP7_75t_R    g010(.A(pi40), .Y(new_n102));
  INVx1_ASAP7_75t_R    g011(.A(pi41), .Y(new_n103));
  INVx1_ASAP7_75t_R    g012(.A(pi44), .Y(new_n104));
  INVx1_ASAP7_75t_R    g013(.A(pi48), .Y(new_n105));
  INVx1_ASAP7_75t_R    g014(.A(pi52), .Y(new_n106));
  INVx1_ASAP7_75t_R    g015(.A(pi56), .Y(new_n107));
  INVx1_ASAP7_75t_R    g016(.A(pi57), .Y(new_n108));
  AND3x1_ASAP7_75t_R   g017(.A(pi27), .B(pi28), .C(pi29), .Y(new_n109));
  INVx1_ASAP7_75t_R    g018(.A(new_n109), .Y(new_n110));
  NOR2x1_ASAP7_75t_R   g019(.A(pi09), .B(pi10), .Y(new_n111));
  OAI21x1_ASAP7_75t_R  g020(.A1(pi09), .A2(pi10), .B(pi11), .Y(new_n112));
  NOR2x1_ASAP7_75t_R   g021(.A(pi12), .B(pi13), .Y(new_n113));
  AOI21x1_ASAP7_75t_R  g022(.A1(new_n112), .A2(new_n113), .B(new_n93), .Y(new_n114));
  AO211x2_ASAP7_75t_R  g023(.A1(new_n112), .A2(new_n113), .B(new_n93), .C(new_n94), .Y(new_n115));
  AOI21x1_ASAP7_75t_R  g024(.A1(new_n95), .A2(new_n115), .B(new_n96), .Y(new_n116));
  INVx1_ASAP7_75t_R    g025(.A(new_n116), .Y(new_n117));
  OA21x2_ASAP7_75t_R   g026(.A1(new_n116), .A2(pi18), .B(pi19), .Y(new_n118));
  OA211x2_ASAP7_75t_R  g027(.A1(new_n116), .A2(pi18), .B(pi19), .C(pi20), .Y(new_n119));
  NOR2x1_ASAP7_75t_R   g028(.A(pi21), .B(new_n119), .Y(new_n120));
  NAND2x1_ASAP7_75t_R  g029(.A(pi24), .B(pi25), .Y(new_n121));
  AND3x1_ASAP7_75t_R   g030(.A(pi23), .B(pi24), .C(pi25), .Y(new_n122));
  OA31x2_ASAP7_75t_R   g031(.A1(pi21), .A2(new_n119), .A3(pi22), .B1(new_n122), .Y(new_n123));
  OA21x2_ASAP7_75t_R   g032(.A1(new_n123), .A2(pi26), .B(new_n109), .Y(new_n124));
  OAI21x1_ASAP7_75t_R  g033(.A1(pi26), .A2(new_n123), .B(new_n109), .Y(new_n125));
  XOR2x2_ASAP7_75t_R   g034(.A(new_n114), .B(pi15), .Y(new_n126));
  AND3x1_ASAP7_75t_R   g035(.A(new_n114), .B(pi16), .C(pi15), .Y(new_n127));
  OR4x2_ASAP7_75t_R    g036(.A(pi03), .B(pi04), .C(pi05), .D(pi06), .Y(new_n128));
  OR5x1_ASAP7_75t_R    g037(.A(new_n128), .B(new_n92), .C(pi08), .D(pi07), .E(pi10), .Y(new_n129));
  OR3x1_ASAP7_75t_R    g038(.A(new_n100), .B(pi26), .C(pi22), .Y(new_n130));
  OR5x1_ASAP7_75t_R    g039(.A(new_n130), .B(pi18), .C(new_n93), .D(pi13), .E(new_n98), .Y(new_n131));
  NAND2x1_ASAP7_75t_R  g040(.A(pi12), .B(new_n111), .Y(new_n132));
  OR3x1_ASAP7_75t_R    g041(.A(new_n121), .B(pi02), .C(pi01), .Y(new_n133));
  AO221x2_ASAP7_75t_R  g042(.A1(pi11), .A2(pi12), .B1(new_n112), .B2(new_n132), .C(new_n133), .Y(new_n134));
  OR5x1_ASAP7_75t_R    g043(.A(new_n126), .B(new_n127), .C(new_n129), .D(new_n134), .E(new_n131), .Y(new_n135));
  OR3x1_ASAP7_75t_R    g044(.A(new_n120), .B(new_n135), .C(new_n117), .Y(new_n136));
  XOR2x2_ASAP7_75t_R   g045(.A(new_n118), .B(pi20), .Y(new_n137));
  AO21x1_ASAP7_75t_R   g046(.A1(pi21), .A2(new_n119), .B(new_n137), .Y(new_n138));
  OA21x2_ASAP7_75t_R   g047(.A1(new_n138), .A2(new_n136), .B(new_n124), .Y(new_n139));
  AND3x1_ASAP7_75t_R   g048(.A(new_n115), .B(new_n96), .C(new_n95), .Y(new_n140));
  OR5x1_ASAP7_75t_R    g049(.A(new_n130), .B(new_n110), .C(pi21), .D(new_n99), .E(new_n121), .Y(new_n141));
  AND4x2_ASAP7_75t_R   g050(.A(pi02), .B(pi03), .C(pi04), .D(pi05), .Y(new_n142));
  AND4x2_ASAP7_75t_R   g051(.A(new_n142), .B(new_n111), .C(pi01), .D(pi00), .Y(new_n143));
  AND4x2_ASAP7_75t_R   g052(.A(pi06), .B(pi07), .C(pi08), .D(pi11), .Y(new_n144));
  AND4x2_ASAP7_75t_R   g053(.A(new_n144), .B(new_n113), .C(new_n95), .D(pi15), .Y(new_n145));
  NAND2x1_ASAP7_75t_R  g054(.A(new_n143), .B(new_n145), .Y(new_n146));
  AND3x1_ASAP7_75t_R   g055(.A(new_n113), .B(new_n112), .C(new_n93), .Y(new_n147));
  OR2x4_ASAP7_75t_R    g056(.A(new_n114), .B(new_n147), .Y(new_n148));
  OR5x1_ASAP7_75t_R    g057(.A(new_n148), .B(new_n146), .C(new_n140), .D(new_n116), .E(new_n141), .Y(new_n149));
  AND3x1_ASAP7_75t_R   g058(.A(new_n117), .B(new_n98), .C(new_n97), .Y(new_n150));
  XOR2x2_ASAP7_75t_R   g059(.A(new_n116), .B(pi18), .Y(new_n151));
  OR4x2_ASAP7_75t_R    g060(.A(new_n149), .B(new_n150), .C(new_n151), .D(new_n118), .Y(new_n152));
  NAND2x1_ASAP7_75t_R  g061(.A(new_n125), .B(new_n152), .Y(new_n153));
  AO21x1_ASAP7_75t_R   g062(.A1(new_n125), .A2(new_n152), .B(new_n139), .Y(po00));
  OA21x2_ASAP7_75t_R   g063(.A1(pi39), .A2(pi40), .B(pi41), .Y(new_n155));
  OR3x1_ASAP7_75t_R    g064(.A(new_n155), .B(pi43), .C(pi42), .Y(new_n156));
  INVx1_ASAP7_75t_R    g065(.A(new_n156), .Y(new_n157));
  AND2x2_ASAP7_75t_R   g066(.A(pi44), .B(pi45), .Y(new_n158));
  NAND2x1_ASAP7_75t_R  g067(.A(pi44), .B(pi45), .Y(new_n159));
  OA31x2_ASAP7_75t_R   g068(.A1(pi42), .A2(new_n155), .A3(pi43), .B1(new_n158), .Y(new_n160));
  OA21x2_ASAP7_75t_R   g069(.A1(new_n160), .A2(pi46), .B(pi47), .Y(new_n161));
  INVx1_ASAP7_75t_R    g070(.A(new_n161), .Y(new_n162));
  NOR2x1_ASAP7_75t_R   g071(.A(pi48), .B(new_n161), .Y(new_n163));
  OA211x2_ASAP7_75t_R  g072(.A1(new_n161), .A2(pi48), .B(pi49), .C(pi50), .Y(new_n164));
  OR2x4_ASAP7_75t_R    g073(.A(pi51), .B(pi52), .Y(new_n165));
  NAND2x1_ASAP7_75t_R  g074(.A(pi54), .B(pi55), .Y(new_n166));
  AND3x1_ASAP7_75t_R   g075(.A(pi53), .B(pi54), .C(pi55), .Y(new_n167));
  OA21x2_ASAP7_75t_R   g076(.A1(new_n164), .A2(new_n165), .B(new_n167), .Y(new_n168));
  AND3x1_ASAP7_75t_R   g077(.A(pi57), .B(pi58), .C(pi59), .Y(new_n169));
  OAI21x1_ASAP7_75t_R  g078(.A1(pi56), .A2(new_n168), .B(new_n169), .Y(new_n170));
  INVx1_ASAP7_75t_R    g079(.A(new_n170), .Y(new_n171));
  OR3x1_ASAP7_75t_R    g080(.A(new_n160), .B(new_n105), .C(pi46), .Y(new_n172));
  AND2x2_ASAP7_75t_R   g081(.A(new_n162), .B(new_n172), .Y(new_n173));
  OR4x2_ASAP7_75t_R    g082(.A(new_n108), .B(pi56), .C(pi51), .D(pi46), .Y(new_n174));
  OR4x2_ASAP7_75t_R    g083(.A(new_n101), .B(pi40), .C(pi37), .D(pi38), .Y(new_n175));
  OR5x1_ASAP7_75t_R    g084(.A(new_n174), .B(new_n175), .C(new_n103), .D(pi43), .E(new_n159), .Y(new_n176));
  AND4x2_ASAP7_75t_R   g085(.A(new_n106), .B(pi53), .C(pi49), .D(pi50), .Y(new_n177));
  INVx1_ASAP7_75t_R    g086(.A(new_n177), .Y(new_n178));
  AO21x1_ASAP7_75t_R   g087(.A1(pi47), .A2(pi48), .B(new_n178), .Y(new_n179));
  OR3x1_ASAP7_75t_R    g088(.A(new_n166), .B(pi32), .C(pi31), .Y(new_n180));
  OR5x1_ASAP7_75t_R    g089(.A(new_n180), .B(pi35), .C(pi34), .D(pi33), .E(pi36), .Y(new_n181));
  XNOR2x2_ASAP7_75t_R  g090(.A(pi42), .B(new_n155), .Y(new_n182));
  OR3x1_ASAP7_75t_R    g091(.A(new_n181), .B(new_n182), .C(new_n179), .Y(new_n183));
  OR3x1_ASAP7_75t_R    g092(.A(new_n183), .B(new_n176), .C(new_n173), .Y(new_n184));
  OR5x1_ASAP7_75t_R    g093(.A(new_n183), .B(new_n173), .C(pi30), .D(pi00), .E(new_n176), .Y(new_n185));
  OAI21x1_ASAP7_75t_R  g094(.A1(pi00), .A2(pi51), .B(new_n170), .Y(new_n186));
  AO21x1_ASAP7_75t_R   g095(.A1(new_n106), .A2(pi53), .B(new_n164), .Y(new_n187));
  AO21x1_ASAP7_75t_R   g096(.A1(new_n160), .A2(pi46), .B(pi47), .Y(new_n188));
  AND4x2_ASAP7_75t_R   g097(.A(new_n155), .B(new_n104), .C(pi43), .D(pi42), .Y(new_n189));
  AO21x1_ASAP7_75t_R   g098(.A1(new_n157), .A2(pi44), .B(new_n189), .Y(new_n190));
  AND4x2_ASAP7_75t_R   g099(.A(new_n107), .B(pi55), .C(pi54), .D(pi50), .Y(new_n191));
  AND4x2_ASAP7_75t_R   g100(.A(pi34), .B(pi35), .C(pi36), .D(pi37), .Y(new_n192));
  AND5x1_ASAP7_75t_R   g101(.A(new_n192), .B(pi32), .C(pi31), .D(pi30), .E(pi33), .Y(new_n193));
  AND5x1_ASAP7_75t_R   g102(.A(new_n169), .B(pi45), .C(pi41), .D(pi38), .E(new_n105), .Y(new_n194));
  AND5x1_ASAP7_75t_R   g103(.A(new_n193), .B(new_n194), .C(new_n101), .D(new_n102), .E(new_n191), .Y(new_n195));
  AND5x1_ASAP7_75t_R   g104(.A(new_n187), .B(new_n188), .C(new_n190), .D(new_n195), .E(new_n162), .Y(new_n196));
  XNOR2x2_ASAP7_75t_R  g105(.A(pi49), .B(new_n163), .Y(new_n197));
  AO32x1_ASAP7_75t_R   g106(.A1(new_n197), .A2(new_n186), .A3(new_n196), .B1(new_n185), .B2(new_n171), .Y(new_n198));
  AOI21x1_ASAP7_75t_R  g107(.A1(new_n153), .A2(new_n198), .B(new_n139), .Y(po01));
  AND2x2_ASAP7_75t_R   g108(.A(pi00), .B(pi30), .Y(new_n200));
  OAI21x1_ASAP7_75t_R  g109(.A1(new_n184), .A2(new_n200), .B(new_n171), .Y(new_n201));
  AOI211x1_ASAP7_75t_R g110(.A1(new_n125), .A2(new_n152), .B(new_n139), .C(new_n201), .Y(po02));
  assign               po03 = 1'b0;
  assign               po04 = 1'b0;
  assign               po05 = 1'b0;
  assign               po06 = 1'b0;
  assign               po07 = 1'b0;
  assign               po08 = 1'b0;
  assign               po09 = 1'b0;
  assign               po10 = 1'b0;
  assign               po11 = 1'b0;
  assign               po12 = 1'b0;
  assign               po13 = 1'b0;
  assign               po14 = 1'b0;
  assign               po15 = 1'b0;
  assign               po16 = 1'b0;
  assign               po17 = 1'b0;
  assign               po18 = 1'b0;
  assign               po19 = 1'b0;
  assign               po20 = 1'b0;
  assign               po21 = 1'b0;
  assign               po22 = 1'b0;
  assign               po23 = 1'b0;
  assign               po24 = 1'b0;
  assign               po25 = 1'b0;
  assign               po26 = 1'b0;
  assign               po27 = 1'b0;
  assign               po28 = 1'b0;
  assign               po29 = 1'b0;
endmodule


