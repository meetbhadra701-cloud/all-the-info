// Benchmark "/r/12_WAVE_10_EXPERIMENTAL_DISCOVERY/experiments/inputs/c1/c2/c880" written by ABC on Fri Sep 25 23:42:19 2026

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
    new_n94, new_n95, new_n96, new_n97, new_n98, new_n99, new_n101,
    new_n103, new_n106, new_n107, new_n115, new_n117, new_n118, new_n120,
    new_n123, new_n124, new_n125, new_n126, new_n127, new_n128, new_n129,
    new_n130, new_n132, new_n133, new_n134, new_n135, new_n136, new_n137,
    new_n138, new_n139, new_n141, new_n142, new_n143, new_n144, new_n145,
    new_n146, new_n147, new_n148, new_n149, new_n150, new_n151, new_n152,
    new_n153, new_n154, new_n155, new_n156, new_n157, new_n158, new_n159,
    new_n160, new_n161, new_n162, new_n163, new_n164, new_n165, new_n166,
    new_n167, new_n168, new_n169, new_n170, new_n171, new_n172, new_n173,
    new_n175, new_n176, new_n177, new_n178, new_n179, new_n180, new_n181,
    new_n182, new_n183, new_n184, new_n185, new_n186, new_n187, new_n188,
    new_n189, new_n190, new_n191, new_n192, new_n193, new_n194, new_n195,
    new_n196, new_n197, new_n198, new_n199, new_n200, new_n201, new_n203,
    new_n204, new_n205, new_n206, new_n207, new_n208, new_n209, new_n211,
    new_n212, new_n213, new_n214, new_n215, new_n216, new_n218, new_n219,
    new_n220, new_n221, new_n222, new_n223, new_n224, new_n225, new_n226,
    new_n227, new_n228, new_n229, new_n230, new_n231, new_n232, new_n233,
    new_n234, new_n235, new_n236, new_n237, new_n238, new_n239, new_n240,
    new_n241, new_n242, new_n243, new_n244, new_n245, new_n246, new_n248,
    new_n249, new_n250, new_n251, new_n252, new_n253, new_n255, new_n256,
    new_n257, new_n258, new_n259, new_n260, new_n261, new_n263, new_n264,
    new_n265, new_n266, new_n267, new_n268, new_n270, new_n271, new_n272,
    new_n273, new_n274, new_n275;
  INVx1_ASAP7_75t_R    g000(.A(pi00), .Y(new_n87));
  INVx1_ASAP7_75t_R    g001(.A(pi07), .Y(new_n88));
  INVx1_ASAP7_75t_R    g002(.A(pi10), .Y(new_n89));
  INVx1_ASAP7_75t_R    g003(.A(pi28), .Y(new_n90));
  INVx1_ASAP7_75t_R    g004(.A(pi29), .Y(new_n91));
  INVx1_ASAP7_75t_R    g005(.A(pi31), .Y(new_n92));
  INVx1_ASAP7_75t_R    g006(.A(pi37), .Y(new_n93));
  INVx1_ASAP7_75t_R    g007(.A(pi38), .Y(new_n94));
  INVx1_ASAP7_75t_R    g008(.A(pi45), .Y(new_n95));
  INVx1_ASAP7_75t_R    g009(.A(pi48), .Y(new_n96));
  INVx1_ASAP7_75t_R    g010(.A(pi51), .Y(new_n97));
  INVx1_ASAP7_75t_R    g011(.A(pi52), .Y(new_n98));
  AND3x1_ASAP7_75t_R   g012(.A(pi00), .B(pi01), .C(pi02), .Y(new_n99));
  INVx1_ASAP7_75t_R    g013(.A(new_n99), .Y(po00));
  AND3x1_ASAP7_75t_R   g014(.A(pi02), .B(pi03), .C(pi04), .Y(new_n101));
  INVx1_ASAP7_75t_R    g015(.A(new_n101), .Y(po01));
  AND3x1_ASAP7_75t_R   g016(.A(pi00), .B(pi02), .C(pi04), .Y(new_n103));
  INVx1_ASAP7_75t_R    g017(.A(new_n103), .Y(po02));
  NAND2x1_ASAP7_75t_R  g018(.A(pi05), .B(pi06), .Y(po03));
  NAND2x1_ASAP7_75t_R  g019(.A(pi09), .B(pi10), .Y(new_n106));
  AND4x2_ASAP7_75t_R   g020(.A(pi07), .B(pi08), .C(pi09), .D(pi10), .Y(new_n107));
  INVx1_ASAP7_75t_R    g021(.A(new_n107), .Y(po04));
  AND5x1_ASAP7_75t_R   g022(.A(po02), .B(pi10), .C(pi08), .D(pi07), .E(pi11), .Y(po05));
  AND3x1_ASAP7_75t_R   g023(.A(pi01), .B(pi03), .C(pi12), .Y(po06));
  AND3x1_ASAP7_75t_R   g024(.A(pi03), .B(pi04), .C(pi12), .Y(po07));
  AND3x1_ASAP7_75t_R   g025(.A(pi00), .B(pi04), .C(pi12), .Y(po08));
  OAI21x1_ASAP7_75t_R  g026(.A1(pi14), .A2(pi15), .B(pi13), .Y(po09));
  AND5x1_ASAP7_75t_R   g027(.A(new_n103), .B(pi10), .C(pi08), .D(pi07), .E(pi11), .Y(po10));
  AND3x1_ASAP7_75t_R   g028(.A(pi10), .B(pi11), .C(pi16), .Y(new_n115));
  INVx1_ASAP7_75t_R    g029(.A(new_n115), .Y(po11));
  AND4x2_ASAP7_75t_R   g030(.A(pi08), .B(pi09), .C(pi10), .D(pi17), .Y(new_n117));
  AND3x1_ASAP7_75t_R   g031(.A(new_n117), .B(pi18), .C(pi02), .Y(new_n118));
  INVx1_ASAP7_75t_R    g032(.A(new_n118), .Y(po12));
  AND3x1_ASAP7_75t_R   g033(.A(new_n117), .B(pi18), .C(pi12), .Y(new_n120));
  NAND2x1_ASAP7_75t_R  g034(.A(pi19), .B(new_n120), .Y(po13));
  OAI21x1_ASAP7_75t_R  g035(.A1(pi14), .A2(pi15), .B(pi20), .Y(po14));
  XOR2x2_ASAP7_75t_R   g036(.A(pi22), .B(pi23), .Y(new_n123));
  XOR2x2_ASAP7_75t_R   g037(.A(new_n123), .B(pi21), .Y(new_n124));
  XNOR2x2_ASAP7_75t_R  g038(.A(pi28), .B(pi29), .Y(new_n125));
  XOR2x2_ASAP7_75t_R   g039(.A(new_n124), .B(new_n125), .Y(new_n126));
  XOR2x2_ASAP7_75t_R   g040(.A(pi26), .B(pi27), .Y(new_n127));
  XOR2x2_ASAP7_75t_R   g041(.A(new_n127), .B(pi30), .Y(new_n128));
  XOR2x2_ASAP7_75t_R   g042(.A(pi24), .B(pi25), .Y(new_n129));
  XOR2x2_ASAP7_75t_R   g043(.A(new_n128), .B(new_n129), .Y(new_n130));
  XOR2x2_ASAP7_75t_R   g044(.A(new_n126), .B(new_n130), .Y(po15));
  XOR2x2_ASAP7_75t_R   g045(.A(pi31), .B(pi32), .Y(new_n132));
  XOR2x2_ASAP7_75t_R   g046(.A(new_n132), .B(pi21), .Y(new_n133));
  XNOR2x2_ASAP7_75t_R  g047(.A(pi37), .B(pi38), .Y(new_n134));
  XOR2x2_ASAP7_75t_R   g048(.A(new_n133), .B(new_n134), .Y(new_n135));
  XOR2x2_ASAP7_75t_R   g049(.A(pi35), .B(pi36), .Y(new_n136));
  XOR2x2_ASAP7_75t_R   g050(.A(new_n136), .B(pi39), .Y(new_n137));
  XOR2x2_ASAP7_75t_R   g051(.A(pi33), .B(pi34), .Y(new_n138));
  XOR2x2_ASAP7_75t_R   g052(.A(new_n137), .B(new_n138), .Y(new_n139));
  XOR2x2_ASAP7_75t_R   g053(.A(new_n135), .B(new_n139), .Y(po16));
  NOR2x1_ASAP7_75t_R   g054(.A(pi00), .B(pi07), .Y(new_n141));
  OR2x4_ASAP7_75t_R    g055(.A(pi00), .B(pi07), .Y(new_n142));
  AND2x2_ASAP7_75t_R   g056(.A(pi12), .B(pi47), .Y(new_n143));
  NAND2x1_ASAP7_75t_R  g057(.A(pi12), .B(pi47), .Y(new_n144));
  NAND2x1_ASAP7_75t_R  g058(.A(pi00), .B(pi07), .Y(new_n145));
  OA21x2_ASAP7_75t_R   g059(.A1(new_n87), .A2(new_n88), .B(new_n143), .Y(new_n146));
  OAI21x1_ASAP7_75t_R  g060(.A1(new_n87), .A2(new_n88), .B(new_n143), .Y(new_n147));
  AND4x2_ASAP7_75t_R   g061(.A(new_n115), .B(new_n142), .C(new_n143), .D(new_n145), .Y(new_n148));
  AND3x1_ASAP7_75t_R   g062(.A(pi00), .B(pi01), .C(pi12), .Y(new_n149));
  NAND3x1_ASAP7_75t_R  g063(.A(pi00), .B(pi01), .C(pi12), .Y(new_n150));
  NAND2x1_ASAP7_75t_R  g064(.A(pi07), .B(pi16), .Y(new_n151));
  AND4x2_ASAP7_75t_R   g065(.A(pi07), .B(pi09), .C(pi10), .D(pi16), .Y(new_n152));
  AND2x2_ASAP7_75t_R   g066(.A(new_n150), .B(new_n152), .Y(new_n153));
  OA33x2_ASAP7_75t_R   g067(.A1(new_n106), .A2(new_n149), .A3(new_n151), .B1(new_n141), .B2(new_n147), .B3(po11), .Y(new_n154));
  AO32x1_ASAP7_75t_R   g068(.A1(new_n115), .A2(new_n146), .A3(new_n142), .B1(new_n152), .B2(new_n150), .Y(new_n155));
  OAI21x1_ASAP7_75t_R  g069(.A1(new_n153), .A2(new_n148), .B(pi29), .Y(new_n156));
  AO31x2_ASAP7_75t_R   g070(.A1(pi07), .A2(new_n115), .A3(new_n144), .B(new_n89), .Y(new_n157));
  AND3x1_ASAP7_75t_R   g071(.A(pi01), .B(pi02), .C(pi03), .Y(new_n158));
  AND2x2_ASAP7_75t_R   g072(.A(new_n115), .B(new_n158), .Y(new_n159));
  AND2x2_ASAP7_75t_R   g073(.A(new_n95), .B(pi17), .Y(new_n160));
  AND3x1_ASAP7_75t_R   g074(.A(new_n160), .B(new_n158), .C(new_n115), .Y(new_n161));
  AOI22x1_ASAP7_75t_R  g075(.A1(new_n159), .A2(new_n160), .B1(new_n157), .B2(pi46), .Y(new_n162));
  OA21x2_ASAP7_75t_R   g076(.A1(new_n91), .A2(new_n154), .B(new_n162), .Y(new_n163));
  NAND2x1_ASAP7_75t_R  g077(.A(new_n162), .B(new_n156), .Y(new_n164));
  AO21x1_ASAP7_75t_R   g078(.A1(new_n156), .A2(new_n162), .B(new_n94), .Y(new_n165));
  XOR2x2_ASAP7_75t_R   g079(.A(new_n163), .B(pi38), .Y(new_n166));
  OA21x2_ASAP7_75t_R   g080(.A1(new_n164), .A2(pi38), .B(pi52), .Y(new_n167));
  AO31x2_ASAP7_75t_R   g081(.A1(new_n94), .A2(new_n156), .A3(new_n162), .B(new_n98), .Y(new_n168));
  AO221x2_ASAP7_75t_R  g082(.A1(new_n165), .A2(new_n167), .B1(new_n98), .B2(new_n166), .C(new_n97), .Y(new_n169));
  AO21x1_ASAP7_75t_R   g083(.A1(pi38), .A2(pi49), .B(pi44), .Y(new_n170));
  AND4x2_ASAP7_75t_R   g084(.A(new_n120), .B(pi41), .C(pi40), .D(pi00), .Y(new_n171));
  AO222x2_ASAP7_75t_R  g085(.A1(pi42), .A2(pi43), .B1(pi50), .B2(pi28), .C1(pi38), .C2(new_n171), .Y(new_n172));
  AOI21x1_ASAP7_75t_R  g086(.A1(new_n164), .A2(new_n170), .B(new_n172), .Y(new_n173));
  OA211x2_ASAP7_75t_R  g087(.A1(new_n96), .A2(new_n166), .B(new_n169), .C(new_n173), .Y(po17));
  AO221x2_ASAP7_75t_R  g088(.A1(pi53), .A2(new_n157), .B1(pi26), .B2(new_n155), .C(new_n161), .Y(new_n175));
  NOR2x1_ASAP7_75t_R   g089(.A(pi35), .B(new_n175), .Y(new_n176));
  OR2x4_ASAP7_75t_R    g090(.A(pi35), .B(new_n175), .Y(new_n177));
  AND2x2_ASAP7_75t_R   g091(.A(new_n175), .B(pi35), .Y(new_n178));
  OR2x4_ASAP7_75t_R    g092(.A(new_n178), .B(new_n176), .Y(new_n179));
  AO221x2_ASAP7_75t_R  g093(.A1(pi55), .A2(new_n157), .B1(pi27), .B2(new_n155), .C(new_n161), .Y(new_n180));
  NAND2x1_ASAP7_75t_R  g094(.A(pi36), .B(new_n180), .Y(new_n181));
  NOR2x1_ASAP7_75t_R   g095(.A(pi36), .B(new_n180), .Y(new_n182));
  OR2x4_ASAP7_75t_R    g096(.A(pi36), .B(new_n180), .Y(new_n183));
  NAND2x1_ASAP7_75t_R  g097(.A(pi28), .B(new_n155), .Y(new_n184));
  AOI22x1_ASAP7_75t_R  g098(.A1(new_n159), .A2(new_n160), .B1(new_n157), .B2(pi54), .Y(new_n185));
  OA21x2_ASAP7_75t_R   g099(.A1(new_n90), .A2(new_n154), .B(new_n185), .Y(new_n186));
  NAND2x1_ASAP7_75t_R  g100(.A(new_n185), .B(new_n184), .Y(new_n187));
  AOI21x1_ASAP7_75t_R  g101(.A1(new_n185), .A2(new_n184), .B(new_n93), .Y(new_n188));
  OA211x2_ASAP7_75t_R  g102(.A1(new_n90), .A2(new_n154), .B(new_n185), .C(new_n93), .Y(new_n189));
  NAND2x1_ASAP7_75t_R  g103(.A(new_n93), .B(new_n186), .Y(new_n190));
  OAI21x1_ASAP7_75t_R  g104(.A1(new_n94), .A2(new_n163), .B(new_n168), .Y(new_n191));
  AOI21x1_ASAP7_75t_R  g105(.A1(new_n165), .A2(new_n168), .B(new_n189), .Y(new_n192));
  AOI21x1_ASAP7_75t_R  g106(.A1(new_n190), .A2(new_n191), .B(new_n188), .Y(new_n193));
  OAI21x1_ASAP7_75t_R  g107(.A1(new_n188), .A2(new_n192), .B(new_n183), .Y(new_n194));
  AND2x2_ASAP7_75t_R   g108(.A(new_n194), .B(new_n181), .Y(new_n195));
  OAI21x1_ASAP7_75t_R  g109(.A1(new_n182), .A2(new_n193), .B(new_n181), .Y(new_n196));
  OAI21x1_ASAP7_75t_R  g110(.A1(new_n179), .A2(new_n195), .B(pi51), .Y(new_n197));
  AO21x1_ASAP7_75t_R   g111(.A1(new_n179), .A2(new_n195), .B(new_n197), .Y(new_n198));
  AO21x1_ASAP7_75t_R   g112(.A1(pi35), .A2(pi49), .B(pi44), .Y(new_n199));
  AO222x2_ASAP7_75t_R  g113(.A1(pi25), .A2(pi50), .B1(new_n171), .B2(pi35), .C1(new_n199), .C2(new_n175), .Y(new_n200));
  INVx1_ASAP7_75t_R    g114(.A(new_n200), .Y(new_n201));
  OA211x2_ASAP7_75t_R  g115(.A1(new_n96), .A2(new_n179), .B(new_n198), .C(new_n201), .Y(po18));
  AND2x2_ASAP7_75t_R   g116(.A(new_n183), .B(new_n181), .Y(new_n203));
  INVx1_ASAP7_75t_R    g117(.A(new_n203), .Y(new_n204));
  OAI21x1_ASAP7_75t_R  g118(.A1(new_n193), .A2(new_n204), .B(pi51), .Y(new_n205));
  AO21x1_ASAP7_75t_R   g119(.A1(new_n193), .A2(new_n204), .B(new_n205), .Y(new_n206));
  AO21x1_ASAP7_75t_R   g120(.A1(pi36), .A2(pi49), .B(pi44), .Y(new_n207));
  AO222x2_ASAP7_75t_R  g121(.A1(pi26), .A2(pi50), .B1(pi56), .B2(pi42), .C1(pi36), .C2(new_n171), .Y(new_n208));
  AOI21x1_ASAP7_75t_R  g122(.A1(new_n180), .A2(new_n207), .B(new_n208), .Y(new_n209));
  OA211x2_ASAP7_75t_R  g123(.A1(new_n96), .A2(new_n204), .B(new_n206), .C(new_n209), .Y(po19));
  NOR2x1_ASAP7_75t_R   g124(.A(new_n189), .B(new_n188), .Y(new_n211));
  NAND2x1_ASAP7_75t_R  g125(.A(new_n191), .B(new_n211), .Y(new_n212));
  OA21x2_ASAP7_75t_R   g126(.A1(new_n211), .A2(new_n191), .B(pi51), .Y(new_n213));
  AO21x1_ASAP7_75t_R   g127(.A1(pi37), .A2(pi49), .B(pi44), .Y(new_n214));
  AO222x2_ASAP7_75t_R  g128(.A1(pi27), .A2(pi50), .B1(pi57), .B2(pi42), .C1(pi37), .C2(new_n171), .Y(new_n215));
  AO21x1_ASAP7_75t_R   g129(.A1(new_n187), .A2(new_n214), .B(new_n215), .Y(new_n216));
  AOI221x1_ASAP7_75t_R g130(.A1(pi48), .A2(new_n211), .B1(new_n213), .B2(new_n212), .C(new_n216), .Y(po20));
  AND3x1_ASAP7_75t_R   g131(.A(new_n115), .B(new_n144), .C(pi17), .Y(new_n218));
  AND3x1_ASAP7_75t_R   g132(.A(new_n159), .B(new_n95), .C(pi07), .Y(new_n219));
  AO221x2_ASAP7_75t_R  g133(.A1(pi09), .A2(pi58), .B1(new_n218), .B2(pi53), .C(new_n219), .Y(new_n220));
  AO21x1_ASAP7_75t_R   g134(.A1(pi22), .A2(new_n155), .B(new_n220), .Y(new_n221));
  INVx1_ASAP7_75t_R    g135(.A(new_n221), .Y(new_n222));
  AO221x2_ASAP7_75t_R  g136(.A1(pi16), .A2(pi58), .B1(new_n218), .B2(pi55), .C(new_n219), .Y(new_n223));
  AO21x1_ASAP7_75t_R   g137(.A1(pi23), .A2(new_n155), .B(new_n223), .Y(new_n224));
  NAND2x1_ASAP7_75t_R  g138(.A(pi32), .B(new_n224), .Y(new_n225));
  NOR2x1_ASAP7_75t_R   g139(.A(pi32), .B(new_n224), .Y(new_n226));
  INVx1_ASAP7_75t_R    g140(.A(new_n226), .Y(new_n227));
  AO221x2_ASAP7_75t_R  g141(.A1(pi07), .A2(pi58), .B1(new_n218), .B2(pi54), .C(new_n219), .Y(new_n228));
  AO21x1_ASAP7_75t_R   g142(.A1(pi24), .A2(new_n155), .B(new_n228), .Y(new_n229));
  AND2x2_ASAP7_75t_R   g143(.A(new_n229), .B(pi33), .Y(new_n230));
  NOR2x1_ASAP7_75t_R   g144(.A(pi33), .B(new_n229), .Y(new_n231));
  OR2x4_ASAP7_75t_R    g145(.A(pi33), .B(new_n229), .Y(new_n232));
  AO221x2_ASAP7_75t_R  g146(.A1(pi58), .A2(pi59), .B1(new_n218), .B2(pi46), .C(new_n219), .Y(new_n233));
  AO21x1_ASAP7_75t_R   g147(.A1(pi25), .A2(new_n155), .B(new_n233), .Y(new_n234));
  NAND2x1_ASAP7_75t_R  g148(.A(pi34), .B(new_n234), .Y(new_n235));
  NOR2x1_ASAP7_75t_R   g149(.A(pi34), .B(new_n234), .Y(new_n236));
  OR2x4_ASAP7_75t_R    g150(.A(pi34), .B(new_n234), .Y(new_n237));
  AOI21x1_ASAP7_75t_R  g151(.A1(new_n181), .A2(new_n194), .B(new_n176), .Y(new_n238));
  AOI21x1_ASAP7_75t_R  g152(.A1(new_n177), .A2(new_n196), .B(new_n178), .Y(new_n239));
  OAI21x1_ASAP7_75t_R  g153(.A1(new_n178), .A2(new_n238), .B(new_n237), .Y(new_n240));
  AND2x2_ASAP7_75t_R   g154(.A(new_n240), .B(new_n235), .Y(new_n241));
  OAI21x1_ASAP7_75t_R  g155(.A1(new_n236), .A2(new_n239), .B(new_n235), .Y(new_n242));
  AOI21x1_ASAP7_75t_R  g156(.A1(new_n235), .A2(new_n240), .B(new_n231), .Y(new_n243));
  AOI21x1_ASAP7_75t_R  g157(.A1(new_n232), .A2(new_n242), .B(new_n230), .Y(new_n244));
  OAI21x1_ASAP7_75t_R  g158(.A1(new_n230), .A2(new_n243), .B(new_n227), .Y(new_n245));
  OA21x2_ASAP7_75t_R   g159(.A1(new_n244), .A2(new_n226), .B(new_n225), .Y(new_n246));
  MAJx2_ASAP7_75t_R    g160(.A(new_n246), .B(new_n222), .C(new_n92), .Y(po21));
  NAND2x1_ASAP7_75t_R  g161(.A(new_n235), .B(new_n237), .Y(new_n248));
  OAI21x1_ASAP7_75t_R  g162(.A1(new_n248), .A2(new_n239), .B(pi51), .Y(new_n249));
  AO21x1_ASAP7_75t_R   g163(.A1(new_n239), .A2(new_n248), .B(new_n249), .Y(new_n250));
  AO21x1_ASAP7_75t_R   g164(.A1(pi34), .A2(pi49), .B(pi44), .Y(new_n251));
  AO222x2_ASAP7_75t_R  g165(.A1(pi24), .A2(pi50), .B1(new_n171), .B2(pi34), .C1(new_n251), .C2(new_n234), .Y(new_n252));
  INVx1_ASAP7_75t_R    g166(.A(new_n252), .Y(new_n253));
  OA211x2_ASAP7_75t_R  g167(.A1(new_n96), .A2(new_n248), .B(new_n250), .C(new_n253), .Y(po22));
  XOR2x2_ASAP7_75t_R   g168(.A(new_n221), .B(new_n92), .Y(new_n255));
  INVx1_ASAP7_75t_R    g169(.A(new_n255), .Y(new_n256));
  OA211x2_ASAP7_75t_R  g170(.A1(new_n244), .A2(new_n226), .B(new_n225), .C(new_n255), .Y(new_n257));
  AOI21x1_ASAP7_75t_R  g171(.A1(new_n225), .A2(new_n245), .B(new_n255), .Y(new_n258));
  AO21x1_ASAP7_75t_R   g172(.A1(pi31), .A2(pi49), .B(pi44), .Y(new_n259));
  AO222x2_ASAP7_75t_R  g173(.A1(pi45), .A2(pi50), .B1(new_n171), .B2(pi31), .C1(new_n259), .C2(new_n221), .Y(new_n260));
  AOI21x1_ASAP7_75t_R  g174(.A1(pi48), .A2(new_n256), .B(new_n260), .Y(new_n261));
  OA31x2_ASAP7_75t_R   g175(.A1(new_n97), .A2(new_n257), .A3(new_n258), .B1(new_n261), .Y(po23));
  NAND2x1_ASAP7_75t_R  g176(.A(new_n225), .B(new_n227), .Y(new_n263));
  INVx1_ASAP7_75t_R    g177(.A(new_n263), .Y(new_n264));
  OR3x1_ASAP7_75t_R    g178(.A(new_n243), .B(new_n264), .C(new_n230), .Y(new_n265));
  OA21x2_ASAP7_75t_R   g179(.A1(new_n244), .A2(new_n263), .B(pi51), .Y(new_n266));
  AO21x1_ASAP7_75t_R   g180(.A1(pi32), .A2(pi49), .B(pi44), .Y(new_n267));
  AO222x2_ASAP7_75t_R  g181(.A1(pi22), .A2(pi50), .B1(new_n171), .B2(pi32), .C1(new_n267), .C2(new_n224), .Y(new_n268));
  AOI221x1_ASAP7_75t_R g182(.A1(pi48), .A2(new_n264), .B1(new_n265), .B2(new_n266), .C(new_n268), .Y(po24));
  OR2x4_ASAP7_75t_R    g183(.A(new_n230), .B(new_n231), .Y(new_n270));
  INVx1_ASAP7_75t_R    g184(.A(new_n270), .Y(new_n271));
  NAND2x1_ASAP7_75t_R  g185(.A(new_n270), .B(new_n241), .Y(new_n272));
  OA21x2_ASAP7_75t_R   g186(.A1(new_n241), .A2(new_n270), .B(pi51), .Y(new_n273));
  AO21x1_ASAP7_75t_R   g187(.A1(pi33), .A2(pi49), .B(pi44), .Y(new_n274));
  AO222x2_ASAP7_75t_R  g188(.A1(pi23), .A2(pi50), .B1(new_n171), .B2(pi33), .C1(new_n274), .C2(new_n229), .Y(new_n275));
  AOI221x1_ASAP7_75t_R g189(.A1(pi48), .A2(new_n271), .B1(new_n273), .B2(new_n272), .C(new_n275), .Y(po25));
endmodule


