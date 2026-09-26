// Benchmark "/r/12_WAVE_10_EXPERIMENTAL_DISCOVERY/experiments/inputs/c1/c2/c880" written by ABC on Fri Sep 25 23:42:20 2026

module \/r/12_WAVE_10_EXPERIMENTAL_DISCOVERY/experiments/inputs/c1/c2/c880  ( 
    pi00, pi01, pi02, pi03, pi04, pi05, pi06, pi07, pi08, pi09, pi10, pi11,
    pi12, pi13, pi14, pi15, pi16, pi17, pi18, pi19, pi20, pi21, pi22, pi23,
    pi24, pi25, pi26, pi27, pi28, pi29, pi30, pi31, pi32, pi33, pi34, pi35,
    pi36, pi37, pi38, pi39, pi40, pi41, pi42, pi43, pi44, pi45, pi46, pi47,
    pi48, pi49, pi50, pi51, pi52, pi53, pi54, pi55, pi56, pi57, pi58, pi59,
    po00, po01, po02, po03, po04, po05, po06, po07, po08, po09, po10, po11,
    po12, po13, po14, po15, po16, po17, po18, po19, po20, po21, po22, po23,
    po24, po25  );
  input  pi00, pi01, pi02, pi03, pi04, pi05, pi06, pi07, pi08, pi09,
    pi10, pi11, pi12, pi13, pi14, pi15, pi16, pi17, pi18, pi19, pi20, pi21,
    pi22, pi23, pi24, pi25, pi26, pi27, pi28, pi29, pi30, pi31, pi32, pi33,
    pi34, pi35, pi36, pi37, pi38, pi39, pi40, pi41, pi42, pi43, pi44, pi45,
    pi46, pi47, pi48, pi49, pi50, pi51, pi52, pi53, pi54, pi55, pi56, pi57,
    pi58, pi59;
  output po00, po01, po02, po03, po04, po05, po06, po07, po08, po09, po10,
    po11, po12, po13, po14, po15, po16, po17, po18, po19, po20, po21, po22,
    po23, po24, po25;
  wire new_n87, new_n88, new_n89, new_n90, new_n91, new_n92, new_n93,
    new_n95, new_n97, new_n100, new_n103, new_n109, new_n111, new_n112,
    new_n114, new_n117, new_n118, new_n119, new_n120, new_n121, new_n122,
    new_n123, new_n124, new_n126, new_n127, new_n128, new_n129, new_n130,
    new_n131, new_n132, new_n133, new_n135, new_n136, new_n137, new_n138,
    new_n139, new_n140, new_n141, new_n142, new_n143, new_n144, new_n145,
    new_n146, new_n147, new_n148, new_n149, new_n150, new_n151, new_n152,
    new_n153, new_n154, new_n155, new_n156, new_n157, new_n158, new_n159,
    new_n160, new_n161, new_n163, new_n164, new_n165, new_n166, new_n167,
    new_n168, new_n169, new_n170, new_n171, new_n172, new_n173, new_n174,
    new_n175, new_n176, new_n177, new_n178, new_n179, new_n180, new_n181,
    new_n183, new_n184, new_n185, new_n186, new_n187, new_n188, new_n190,
    new_n191, new_n192, new_n193, new_n194, new_n195, new_n197, new_n198,
    new_n199, new_n200, new_n201, new_n202, new_n203, new_n204, new_n205,
    new_n206, new_n207, new_n208, new_n209, new_n210, new_n211, new_n212,
    new_n213, new_n214, new_n215, new_n216, new_n217, new_n218, new_n220,
    new_n221, new_n222, new_n223, new_n224, new_n226, new_n227, new_n228,
    new_n229, new_n230, new_n231, new_n233, new_n234, new_n235, new_n236,
    new_n237, new_n238, new_n240, new_n241, new_n242, new_n243, new_n244,
    new_n245;
  INVx1_ASAP7_75t_R    g000(.A(pi00), .Y(new_n87));
  INVx1_ASAP7_75t_R    g001(.A(pi10), .Y(new_n88));
  INVx1_ASAP7_75t_R    g002(.A(pi31), .Y(new_n89));
  INVx1_ASAP7_75t_R    g003(.A(pi45), .Y(new_n90));
  INVx1_ASAP7_75t_R    g004(.A(pi48), .Y(new_n91));
  INVx1_ASAP7_75t_R    g005(.A(pi51), .Y(new_n92));
  AND3x1_ASAP7_75t_R   g006(.A(pi00), .B(pi01), .C(pi02), .Y(new_n93));
  INVx1_ASAP7_75t_R    g007(.A(new_n93), .Y(po00));
  AND3x1_ASAP7_75t_R   g008(.A(pi02), .B(pi03), .C(pi04), .Y(new_n95));
  INVx1_ASAP7_75t_R    g009(.A(new_n95), .Y(po01));
  AND3x1_ASAP7_75t_R   g010(.A(pi00), .B(pi02), .C(pi04), .Y(new_n97));
  INVx1_ASAP7_75t_R    g011(.A(new_n97), .Y(po02));
  NAND2x1_ASAP7_75t_R  g012(.A(pi05), .B(pi06), .Y(po03));
  AND4x2_ASAP7_75t_R   g013(.A(pi07), .B(pi08), .C(pi09), .D(pi10), .Y(new_n100));
  INVx1_ASAP7_75t_R    g014(.A(new_n100), .Y(po04));
  AND5x1_ASAP7_75t_R   g015(.A(po02), .B(pi10), .C(pi08), .D(pi07), .E(pi11), .Y(po05));
  NAND2x1_ASAP7_75t_R  g016(.A(pi01), .B(pi12), .Y(new_n103));
  AND3x1_ASAP7_75t_R   g017(.A(pi01), .B(pi03), .C(pi12), .Y(po06));
  AND3x1_ASAP7_75t_R   g018(.A(pi03), .B(pi04), .C(pi12), .Y(po07));
  AND3x1_ASAP7_75t_R   g019(.A(pi00), .B(pi04), .C(pi12), .Y(po08));
  OAI21x1_ASAP7_75t_R  g020(.A1(pi14), .A2(pi15), .B(pi13), .Y(po09));
  AND5x1_ASAP7_75t_R   g021(.A(new_n97), .B(pi10), .C(pi08), .D(pi07), .E(pi11), .Y(po10));
  AND3x1_ASAP7_75t_R   g022(.A(pi10), .B(pi11), .C(pi16), .Y(new_n109));
  INVx1_ASAP7_75t_R    g023(.A(new_n109), .Y(po11));
  AND4x2_ASAP7_75t_R   g024(.A(pi08), .B(pi09), .C(pi10), .D(pi17), .Y(new_n111));
  AND3x1_ASAP7_75t_R   g025(.A(new_n111), .B(pi18), .C(pi02), .Y(new_n112));
  INVx1_ASAP7_75t_R    g026(.A(new_n112), .Y(po12));
  AND3x1_ASAP7_75t_R   g027(.A(new_n111), .B(pi18), .C(pi12), .Y(new_n114));
  NAND2x1_ASAP7_75t_R  g028(.A(pi19), .B(new_n114), .Y(po13));
  OAI21x1_ASAP7_75t_R  g029(.A1(pi14), .A2(pi15), .B(pi20), .Y(po14));
  XOR2x2_ASAP7_75t_R   g030(.A(pi22), .B(pi23), .Y(new_n117));
  XOR2x2_ASAP7_75t_R   g031(.A(new_n117), .B(pi21), .Y(new_n118));
  XNOR2x2_ASAP7_75t_R  g032(.A(pi28), .B(pi29), .Y(new_n119));
  XOR2x2_ASAP7_75t_R   g033(.A(new_n118), .B(new_n119), .Y(new_n120));
  XOR2x2_ASAP7_75t_R   g034(.A(pi26), .B(pi27), .Y(new_n121));
  XOR2x2_ASAP7_75t_R   g035(.A(new_n121), .B(pi30), .Y(new_n122));
  XOR2x2_ASAP7_75t_R   g036(.A(pi24), .B(pi25), .Y(new_n123));
  XOR2x2_ASAP7_75t_R   g037(.A(new_n122), .B(new_n123), .Y(new_n124));
  XOR2x2_ASAP7_75t_R   g038(.A(new_n120), .B(new_n124), .Y(po15));
  XOR2x2_ASAP7_75t_R   g039(.A(pi31), .B(pi32), .Y(new_n126));
  XOR2x2_ASAP7_75t_R   g040(.A(new_n126), .B(pi21), .Y(new_n127));
  XNOR2x2_ASAP7_75t_R  g041(.A(pi37), .B(pi38), .Y(new_n128));
  XOR2x2_ASAP7_75t_R   g042(.A(new_n127), .B(new_n128), .Y(new_n129));
  XOR2x2_ASAP7_75t_R   g043(.A(pi35), .B(pi36), .Y(new_n130));
  XOR2x2_ASAP7_75t_R   g044(.A(new_n130), .B(pi39), .Y(new_n131));
  XOR2x2_ASAP7_75t_R   g045(.A(pi33), .B(pi34), .Y(new_n132));
  XOR2x2_ASAP7_75t_R   g046(.A(new_n131), .B(new_n132), .Y(new_n133));
  XOR2x2_ASAP7_75t_R   g047(.A(new_n129), .B(new_n133), .Y(po16));
  OR2x4_ASAP7_75t_R    g048(.A(pi00), .B(pi07), .Y(new_n135));
  AND2x2_ASAP7_75t_R   g049(.A(pi12), .B(pi47), .Y(new_n136));
  NAND2x1_ASAP7_75t_R  g050(.A(pi12), .B(pi47), .Y(new_n137));
  NAND2x1_ASAP7_75t_R  g051(.A(pi00), .B(pi07), .Y(new_n138));
  AOI21x1_ASAP7_75t_R  g052(.A1(pi00), .A2(pi07), .B(new_n137), .Y(new_n139));
  AND4x2_ASAP7_75t_R   g053(.A(new_n109), .B(new_n135), .C(new_n136), .D(new_n138), .Y(new_n140));
  AND3x1_ASAP7_75t_R   g054(.A(pi00), .B(pi01), .C(pi12), .Y(new_n141));
  INVx1_ASAP7_75t_R    g055(.A(new_n141), .Y(new_n142));
  AND4x2_ASAP7_75t_R   g056(.A(pi07), .B(pi09), .C(pi10), .D(pi16), .Y(new_n143));
  OA21x2_ASAP7_75t_R   g057(.A1(new_n87), .A2(new_n103), .B(new_n143), .Y(new_n144));
  AO32x1_ASAP7_75t_R   g058(.A1(new_n109), .A2(new_n139), .A3(new_n135), .B1(new_n143), .B2(new_n142), .Y(new_n145));
  OA21x2_ASAP7_75t_R   g059(.A1(new_n140), .A2(new_n144), .B(pi29), .Y(new_n146));
  AO31x2_ASAP7_75t_R   g060(.A1(pi07), .A2(new_n109), .A3(new_n137), .B(new_n88), .Y(new_n147));
  AND3x1_ASAP7_75t_R   g061(.A(pi01), .B(pi02), .C(pi03), .Y(new_n148));
  AND4x2_ASAP7_75t_R   g062(.A(new_n109), .B(new_n148), .C(pi17), .D(new_n90), .Y(new_n149));
  AO21x1_ASAP7_75t_R   g063(.A1(pi46), .A2(new_n147), .B(new_n149), .Y(new_n150));
  AO21x1_ASAP7_75t_R   g064(.A1(pi29), .A2(new_n145), .B(new_n150), .Y(new_n151));
  OA21x2_ASAP7_75t_R   g065(.A1(new_n146), .A2(new_n150), .B(pi38), .Y(new_n152));
  AO211x2_ASAP7_75t_R  g066(.A1(pi29), .A2(new_n145), .B(pi38), .C(new_n150), .Y(new_n153));
  XOR2x2_ASAP7_75t_R   g067(.A(new_n151), .B(pi38), .Y(new_n154));
  NAND2x1_ASAP7_75t_R  g068(.A(pi52), .B(new_n153), .Y(new_n155));
  OA21x2_ASAP7_75t_R   g069(.A1(new_n155), .A2(new_n152), .B(pi51), .Y(new_n156));
  OA21x2_ASAP7_75t_R   g070(.A1(pi52), .A2(new_n154), .B(new_n156), .Y(new_n157));
  AO21x1_ASAP7_75t_R   g071(.A1(pi38), .A2(pi49), .B(pi44), .Y(new_n158));
  AND4x2_ASAP7_75t_R   g072(.A(new_n114), .B(pi41), .C(pi40), .D(pi00), .Y(new_n159));
  AO222x2_ASAP7_75t_R  g073(.A1(pi42), .A2(pi43), .B1(pi50), .B2(pi28), .C1(pi38), .C2(new_n159), .Y(new_n160));
  AO221x2_ASAP7_75t_R  g074(.A1(new_n151), .A2(new_n158), .B1(pi48), .B2(new_n154), .C(new_n160), .Y(new_n161));
  NOR2x1_ASAP7_75t_R   g075(.A(new_n161), .B(new_n157), .Y(po17));
  AO221x2_ASAP7_75t_R  g076(.A1(pi53), .A2(new_n147), .B1(pi26), .B2(new_n145), .C(new_n149), .Y(new_n163));
  NOR2x1_ASAP7_75t_R   g077(.A(pi35), .B(new_n163), .Y(new_n164));
  NAND2x1_ASAP7_75t_R  g078(.A(pi35), .B(new_n163), .Y(new_n165));
  XNOR2x2_ASAP7_75t_R  g079(.A(pi35), .B(new_n163), .Y(new_n166));
  AO221x2_ASAP7_75t_R  g080(.A1(pi55), .A2(new_n147), .B1(pi27), .B2(new_n145), .C(new_n149), .Y(new_n167));
  AND2x2_ASAP7_75t_R   g081(.A(new_n167), .B(pi36), .Y(new_n168));
  OR2x4_ASAP7_75t_R    g082(.A(pi36), .B(new_n167), .Y(new_n169));
  AO221x2_ASAP7_75t_R  g083(.A1(pi54), .A2(new_n147), .B1(pi28), .B2(new_n145), .C(new_n149), .Y(new_n170));
  NAND2x1_ASAP7_75t_R  g084(.A(pi37), .B(new_n170), .Y(new_n171));
  NOR2x1_ASAP7_75t_R   g085(.A(pi37), .B(new_n170), .Y(new_n172));
  AOI21x1_ASAP7_75t_R  g086(.A1(pi52), .A2(new_n153), .B(new_n152), .Y(new_n173));
  AO21x1_ASAP7_75t_R   g087(.A1(new_n153), .A2(pi52), .B(new_n152), .Y(new_n174));
  OAI21x1_ASAP7_75t_R  g088(.A1(new_n172), .A2(new_n173), .B(new_n171), .Y(new_n175));
  AOI21x1_ASAP7_75t_R  g089(.A1(new_n169), .A2(new_n175), .B(new_n168), .Y(new_n176));
  OAI21x1_ASAP7_75t_R  g090(.A1(new_n166), .A2(new_n176), .B(pi51), .Y(new_n177));
  AO21x1_ASAP7_75t_R   g091(.A1(new_n166), .A2(new_n176), .B(new_n177), .Y(new_n178));
  AO21x1_ASAP7_75t_R   g092(.A1(pi35), .A2(pi49), .B(pi44), .Y(new_n179));
  AO222x2_ASAP7_75t_R  g093(.A1(pi25), .A2(pi50), .B1(new_n159), .B2(pi35), .C1(new_n179), .C2(new_n163), .Y(new_n180));
  INVx1_ASAP7_75t_R    g094(.A(new_n180), .Y(new_n181));
  OA211x2_ASAP7_75t_R  g095(.A1(new_n91), .A2(new_n166), .B(new_n178), .C(new_n181), .Y(po18));
  XOR2x2_ASAP7_75t_R   g096(.A(new_n167), .B(pi36), .Y(new_n183));
  AOI21x1_ASAP7_75t_R  g097(.A1(new_n183), .A2(new_n175), .B(new_n92), .Y(new_n184));
  OA21x2_ASAP7_75t_R   g098(.A1(new_n175), .A2(new_n183), .B(new_n184), .Y(new_n185));
  AO21x1_ASAP7_75t_R   g099(.A1(pi36), .A2(pi49), .B(pi44), .Y(new_n186));
  AO222x2_ASAP7_75t_R  g100(.A1(pi26), .A2(pi50), .B1(pi56), .B2(pi42), .C1(pi36), .C2(new_n159), .Y(new_n187));
  AO221x2_ASAP7_75t_R  g101(.A1(new_n167), .A2(new_n186), .B1(pi48), .B2(new_n183), .C(new_n187), .Y(new_n188));
  NOR2x1_ASAP7_75t_R   g102(.A(new_n188), .B(new_n185), .Y(po19));
  XOR2x2_ASAP7_75t_R   g103(.A(new_n170), .B(pi37), .Y(new_n190));
  NAND2x1_ASAP7_75t_R  g104(.A(new_n174), .B(new_n190), .Y(new_n191));
  OA21x2_ASAP7_75t_R   g105(.A1(new_n190), .A2(new_n174), .B(pi51), .Y(new_n192));
  AO21x1_ASAP7_75t_R   g106(.A1(pi37), .A2(pi49), .B(pi44), .Y(new_n193));
  AO222x2_ASAP7_75t_R  g107(.A1(pi27), .A2(pi50), .B1(pi57), .B2(pi42), .C1(pi37), .C2(new_n159), .Y(new_n194));
  AO221x2_ASAP7_75t_R  g108(.A1(new_n170), .A2(new_n193), .B1(pi48), .B2(new_n190), .C(new_n194), .Y(new_n195));
  AOI21x1_ASAP7_75t_R  g109(.A1(new_n191), .A2(new_n192), .B(new_n195), .Y(po20));
  AND3x1_ASAP7_75t_R   g110(.A(new_n109), .B(new_n137), .C(pi17), .Y(new_n197));
  AND4x2_ASAP7_75t_R   g111(.A(new_n109), .B(new_n148), .C(pi07), .D(new_n90), .Y(new_n198));
  AO221x2_ASAP7_75t_R  g112(.A1(pi09), .A2(pi58), .B1(new_n197), .B2(pi53), .C(new_n198), .Y(new_n199));
  AO21x1_ASAP7_75t_R   g113(.A1(pi22), .A2(new_n145), .B(new_n199), .Y(new_n200));
  INVx1_ASAP7_75t_R    g114(.A(new_n200), .Y(new_n201));
  AO221x2_ASAP7_75t_R  g115(.A1(pi16), .A2(pi58), .B1(new_n197), .B2(pi55), .C(new_n198), .Y(new_n202));
  AO21x1_ASAP7_75t_R   g116(.A1(pi23), .A2(new_n145), .B(new_n202), .Y(new_n203));
  AND2x2_ASAP7_75t_R   g117(.A(new_n203), .B(pi32), .Y(new_n204));
  OR2x4_ASAP7_75t_R    g118(.A(pi32), .B(new_n203), .Y(new_n205));
  AO221x2_ASAP7_75t_R  g119(.A1(pi07), .A2(pi58), .B1(new_n197), .B2(pi54), .C(new_n198), .Y(new_n206));
  AO21x1_ASAP7_75t_R   g120(.A1(pi24), .A2(new_n145), .B(new_n206), .Y(new_n207));
  NAND2x1_ASAP7_75t_R  g121(.A(pi33), .B(new_n207), .Y(new_n208));
  NOR2x1_ASAP7_75t_R   g122(.A(pi33), .B(new_n207), .Y(new_n209));
  AO221x2_ASAP7_75t_R  g123(.A1(pi58), .A2(pi59), .B1(new_n197), .B2(pi46), .C(new_n198), .Y(new_n210));
  AO21x1_ASAP7_75t_R   g124(.A1(pi25), .A2(new_n145), .B(new_n210), .Y(new_n211));
  AND2x2_ASAP7_75t_R   g125(.A(new_n211), .B(pi34), .Y(new_n212));
  OR2x4_ASAP7_75t_R    g126(.A(pi34), .B(new_n211), .Y(new_n213));
  OAI21x1_ASAP7_75t_R  g127(.A1(new_n164), .A2(new_n176), .B(new_n165), .Y(new_n214));
  AOI21x1_ASAP7_75t_R  g128(.A1(new_n213), .A2(new_n214), .B(new_n212), .Y(new_n215));
  OA21x2_ASAP7_75t_R   g129(.A1(new_n215), .A2(new_n209), .B(new_n208), .Y(new_n216));
  OAI21x1_ASAP7_75t_R  g130(.A1(new_n209), .A2(new_n215), .B(new_n208), .Y(new_n217));
  AOI21x1_ASAP7_75t_R  g131(.A1(new_n205), .A2(new_n217), .B(new_n204), .Y(new_n218));
  MAJx2_ASAP7_75t_R    g132(.A(new_n218), .B(new_n201), .C(new_n89), .Y(po21));
  XOR2x2_ASAP7_75t_R   g133(.A(new_n211), .B(pi34), .Y(new_n220));
  AOI21x1_ASAP7_75t_R  g134(.A1(new_n220), .A2(new_n214), .B(new_n92), .Y(new_n221));
  OA21x2_ASAP7_75t_R   g135(.A1(new_n214), .A2(new_n220), .B(new_n221), .Y(new_n222));
  AO21x1_ASAP7_75t_R   g136(.A1(pi34), .A2(pi49), .B(pi44), .Y(new_n223));
  AO222x2_ASAP7_75t_R  g137(.A1(pi24), .A2(pi50), .B1(new_n159), .B2(pi34), .C1(new_n223), .C2(new_n211), .Y(new_n224));
  AOI211x1_ASAP7_75t_R g138(.A1(pi48), .A2(new_n220), .B(new_n222), .C(new_n224), .Y(po22));
  XOR2x2_ASAP7_75t_R   g139(.A(new_n200), .B(new_n89), .Y(new_n226));
  INVx1_ASAP7_75t_R    g140(.A(new_n226), .Y(new_n227));
  NAND2x1_ASAP7_75t_R  g141(.A(new_n226), .B(new_n218), .Y(new_n228));
  OA21x2_ASAP7_75t_R   g142(.A1(new_n218), .A2(new_n226), .B(pi51), .Y(new_n229));
  AO21x1_ASAP7_75t_R   g143(.A1(pi31), .A2(pi49), .B(pi44), .Y(new_n230));
  AO222x2_ASAP7_75t_R  g144(.A1(pi45), .A2(pi50), .B1(new_n159), .B2(pi31), .C1(new_n230), .C2(new_n200), .Y(new_n231));
  AOI221x1_ASAP7_75t_R g145(.A1(pi48), .A2(new_n227), .B1(new_n229), .B2(new_n228), .C(new_n231), .Y(po23));
  XNOR2x2_ASAP7_75t_R  g146(.A(pi32), .B(new_n203), .Y(new_n233));
  OAI21x1_ASAP7_75t_R  g147(.A1(new_n233), .A2(new_n216), .B(pi51), .Y(new_n234));
  AO21x1_ASAP7_75t_R   g148(.A1(new_n216), .A2(new_n233), .B(new_n234), .Y(new_n235));
  AO21x1_ASAP7_75t_R   g149(.A1(pi32), .A2(pi49), .B(pi44), .Y(new_n236));
  AO22x1_ASAP7_75t_R   g150(.A1(new_n159), .A2(pi32), .B1(pi22), .B2(pi50), .Y(new_n237));
  AOI21x1_ASAP7_75t_R  g151(.A1(new_n203), .A2(new_n236), .B(new_n237), .Y(new_n238));
  OA211x2_ASAP7_75t_R  g152(.A1(new_n91), .A2(new_n233), .B(new_n235), .C(new_n238), .Y(po24));
  XNOR2x2_ASAP7_75t_R  g153(.A(pi33), .B(new_n207), .Y(new_n240));
  OAI21x1_ASAP7_75t_R  g154(.A1(new_n240), .A2(new_n215), .B(pi51), .Y(new_n241));
  AO21x1_ASAP7_75t_R   g155(.A1(new_n215), .A2(new_n240), .B(new_n241), .Y(new_n242));
  AO21x1_ASAP7_75t_R   g156(.A1(pi33), .A2(pi49), .B(pi44), .Y(new_n243));
  AO222x2_ASAP7_75t_R  g157(.A1(pi23), .A2(pi50), .B1(new_n159), .B2(pi33), .C1(new_n243), .C2(new_n207), .Y(new_n244));
  INVx1_ASAP7_75t_R    g158(.A(new_n244), .Y(new_n245));
  OA211x2_ASAP7_75t_R  g159(.A1(new_n91), .A2(new_n240), .B(new_n242), .C(new_n245), .Y(po25));
endmodule


