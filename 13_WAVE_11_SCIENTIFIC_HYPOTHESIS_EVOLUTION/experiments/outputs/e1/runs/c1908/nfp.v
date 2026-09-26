// Benchmark "/r/12_WAVE_10_EXPERIMENTAL_DISCOVERY/experiments/inputs/c1/c2/c1908" written by ABC on Sat Sep 26 00:07:36 2026

module \/r/12_WAVE_10_EXPERIMENTAL_DISCOVERY/experiments/inputs/c1/c2/c1908  ( 
    pi00, pi01, pi02, pi03, pi04, pi05, pi06, pi07, pi08, pi09, pi10, pi11,
    pi12, pi13, pi14, pi15, pi16, pi17, pi18, pi19, pi20, pi21, pi22, pi23,
    pi24, pi25, pi26, pi27, pi28, pi29, pi30, pi31, pi32,
    po00, po01, po02, po03, po04, po05, po06, po07, po08, po09, po10, po11,
    po12, po13, po14, po15, po16, po17, po18, po19, po20, po21, po22, po23,
    po24  );
  input  pi00, pi01, pi02, pi03, pi04, pi05, pi06, pi07, pi08, pi09,
    pi10, pi11, pi12, pi13, pi14, pi15, pi16, pi17, pi18, pi19, pi20, pi21,
    pi22, pi23, pi24, pi25, pi26, pi27, pi28, pi29, pi30, pi31, pi32;
  output po00, po01, po02, po03, po04, po05, po06, po07, po08, po09, po10,
    po11, po12, po13, po14, po15, po16, po17, po18, po19, po20, po21, po22,
    po23, po24;
  wire new_n59, new_n60, new_n61, new_n62, new_n63, new_n64, new_n65,
    new_n66, new_n67, new_n68, new_n69, new_n70, new_n71, new_n72, new_n73,
    new_n74, new_n75, new_n76, new_n77, new_n78, new_n79, new_n80, new_n81,
    new_n82, new_n83, new_n84, new_n85, new_n86, new_n87, new_n88, new_n89,
    new_n90, new_n91, new_n92, new_n93, new_n94, new_n95, new_n96, new_n97,
    new_n98, new_n99, new_n100, new_n101, new_n102, new_n103, new_n104,
    new_n105, new_n106, new_n107, new_n108, new_n109, new_n110, new_n111,
    new_n112, new_n113, new_n114, new_n115, new_n116, new_n117, new_n118,
    new_n119, new_n120, new_n121, new_n122, new_n123, new_n124, new_n125,
    new_n126, new_n127, new_n128, new_n129, new_n130, new_n131, new_n132,
    new_n133, new_n134, new_n135, new_n136, new_n137, new_n138, new_n139,
    new_n140, new_n141, new_n142, new_n143, new_n144, new_n145, new_n146,
    new_n147, new_n148, new_n149, new_n150, new_n151, new_n152, new_n153,
    new_n154, new_n155, new_n156, new_n157, new_n158, new_n159, new_n160,
    new_n161, new_n162, new_n163, new_n164, new_n165, new_n166, new_n167,
    new_n168, new_n169, new_n170, new_n171, new_n172, new_n173, new_n174,
    new_n175, new_n176, new_n177, new_n178, new_n179, new_n180, new_n181,
    new_n182, new_n183, new_n184, new_n185, new_n186, new_n187, new_n188,
    new_n189, new_n190, new_n191, new_n192, new_n193, new_n195, new_n196,
    new_n197, new_n198, new_n199, new_n200, new_n201, new_n202, new_n203,
    new_n204, new_n205, new_n211, new_n215, new_n216, new_n221, new_n225,
    new_n226, new_n227, new_n228, new_n229, new_n231, new_n232, new_n233,
    new_n235, new_n236, new_n238, new_n239, new_n241, new_n242, new_n244,
    new_n245, new_n247, new_n248, new_n249, new_n250, new_n251, new_n252,
    new_n253, new_n255, new_n256, new_n257, new_n258, new_n259, new_n260,
    new_n261, new_n262, new_n264, new_n265;
  INVx1_ASAP7_75t_R    g000(.A(pi00), .Y(new_n59));
  INVx1_ASAP7_75t_R    g001(.A(pi01), .Y(new_n60));
  INVx1_ASAP7_75t_R    g002(.A(pi02), .Y(new_n61));
  INVx1_ASAP7_75t_R    g003(.A(pi03), .Y(new_n62));
  INVx1_ASAP7_75t_R    g004(.A(pi05), .Y(new_n63));
  INVx1_ASAP7_75t_R    g005(.A(pi10), .Y(new_n64));
  INVx1_ASAP7_75t_R    g006(.A(pi18), .Y(new_n65));
  INVx1_ASAP7_75t_R    g007(.A(pi19), .Y(new_n66));
  INVx1_ASAP7_75t_R    g008(.A(pi21), .Y(new_n67));
  INVx1_ASAP7_75t_R    g009(.A(pi26), .Y(new_n68));
  INVx1_ASAP7_75t_R    g010(.A(pi30), .Y(new_n69));
  OA211x2_ASAP7_75t_R  g011(.A1(pi00), .A2(new_n60), .B(new_n61), .C(new_n63), .Y(new_n70));
  NOR2x1_ASAP7_75t_R   g012(.A(pi02), .B(pi04), .Y(new_n71));
  INVx1_ASAP7_75t_R    g013(.A(new_n71), .Y(new_n72));
  OA21x2_ASAP7_75t_R   g014(.A1(new_n60), .A2(pi00), .B(new_n62), .Y(new_n73));
  AO21x1_ASAP7_75t_R   g015(.A1(new_n71), .A2(new_n73), .B(new_n70), .Y(new_n74));
  XNOR2x2_ASAP7_75t_R  g016(.A(pi09), .B(pi18), .Y(new_n75));
  XNOR2x2_ASAP7_75t_R  g017(.A(pi06), .B(pi19), .Y(new_n76));
  XOR2x2_ASAP7_75t_R   g018(.A(new_n76), .B(pi20), .Y(new_n77));
  NOR2x1_ASAP7_75t_R   g019(.A(pi01), .B(pi02), .Y(new_n78));
  XOR2x2_ASAP7_75t_R   g020(.A(pi14), .B(pi15), .Y(new_n79));
  NOR2x1_ASAP7_75t_R   g021(.A(pi16), .B(new_n79), .Y(new_n80));
  AND2x2_ASAP7_75t_R   g022(.A(new_n79), .B(pi16), .Y(new_n81));
  OA211x2_ASAP7_75t_R  g023(.A1(new_n80), .A2(new_n81), .B(pi17), .C(new_n78), .Y(new_n82));
  AOI211x1_ASAP7_75t_R g024(.A1(pi17), .A2(new_n78), .B(new_n80), .C(new_n81), .Y(new_n83));
  OAI21x1_ASAP7_75t_R  g025(.A1(new_n83), .A2(new_n82), .B(new_n77), .Y(new_n84));
  OR3x1_ASAP7_75t_R    g026(.A(new_n82), .B(new_n83), .C(new_n77), .Y(new_n85));
  AND3x1_ASAP7_75t_R   g027(.A(new_n85), .B(new_n84), .C(new_n75), .Y(new_n86));
  NAND3x1_ASAP7_75t_R  g028(.A(new_n85), .B(new_n84), .C(new_n75), .Y(new_n87));
  AOI21x1_ASAP7_75t_R  g029(.A1(new_n84), .A2(new_n85), .B(new_n75), .Y(new_n88));
  AO21x1_ASAP7_75t_R   g030(.A1(new_n85), .A2(new_n84), .B(new_n75), .Y(new_n89));
  NAND2x1_ASAP7_75t_R  g031(.A(new_n89), .B(new_n87), .Y(new_n90));
  OR4x2_ASAP7_75t_R    g032(.A(new_n86), .B(new_n88), .C(pi03), .D(pi21), .Y(new_n91));
  AO31x2_ASAP7_75t_R   g033(.A1(new_n62), .A2(new_n87), .A3(new_n89), .B(new_n67), .Y(new_n92));
  XOR2x2_ASAP7_75t_R   g034(.A(pi09), .B(pi10), .Y(new_n93));
  AND3x1_ASAP7_75t_R   g035(.A(new_n59), .B(new_n61), .C(pi12), .Y(new_n94));
  XNOR2x2_ASAP7_75t_R  g036(.A(pi06), .B(pi07), .Y(new_n95));
  XOR2x2_ASAP7_75t_R   g037(.A(pi08), .B(pi11), .Y(new_n96));
  XOR2x2_ASAP7_75t_R   g038(.A(new_n95), .B(new_n96), .Y(new_n97));
  XOR2x2_ASAP7_75t_R   g039(.A(new_n97), .B(new_n94), .Y(new_n98));
  XOR2x2_ASAP7_75t_R   g040(.A(new_n98), .B(new_n93), .Y(new_n99));
  OR3x1_ASAP7_75t_R    g041(.A(new_n99), .B(pi13), .C(pi03), .Y(new_n100));
  OAI21x1_ASAP7_75t_R  g042(.A1(pi03), .A2(new_n99), .B(pi13), .Y(new_n101));
  AND4x2_ASAP7_75t_R   g043(.A(new_n100), .B(new_n101), .C(new_n91), .D(new_n92), .Y(new_n102));
  AND5x1_ASAP7_75t_R   g044(.A(new_n100), .B(new_n101), .C(new_n74), .D(new_n91), .E(new_n92), .Y(new_n103));
  INVx1_ASAP7_75t_R    g045(.A(new_n103), .Y(new_n104));
  OA21x2_ASAP7_75t_R   g046(.A1(pi01), .A2(pi03), .B(pi27), .Y(new_n105));
  INVx1_ASAP7_75t_R    g047(.A(new_n105), .Y(new_n106));
  NAND2x1_ASAP7_75t_R  g048(.A(pi31), .B(new_n61), .Y(new_n107));
  XOR2x2_ASAP7_75t_R   g049(.A(new_n107), .B(pi14), .Y(new_n108));
  XOR2x2_ASAP7_75t_R   g050(.A(pi09), .B(pi16), .Y(new_n109));
  OR2x4_ASAP7_75t_R    g051(.A(new_n64), .B(new_n109), .Y(new_n110));
  NAND2x1_ASAP7_75t_R  g052(.A(new_n64), .B(new_n109), .Y(new_n111));
  AND2x2_ASAP7_75t_R   g053(.A(new_n110), .B(new_n111), .Y(new_n112));
  XOR2x2_ASAP7_75t_R   g054(.A(pi06), .B(pi23), .Y(new_n113));
  INVx1_ASAP7_75t_R    g055(.A(new_n113), .Y(new_n114));
  XNOR2x2_ASAP7_75t_R  g056(.A(pi07), .B(pi22), .Y(new_n115));
  XOR2x2_ASAP7_75t_R   g057(.A(pi07), .B(pi22), .Y(new_n116));
  NOR2x1_ASAP7_75t_R   g058(.A(new_n66), .B(new_n116), .Y(new_n117));
  NAND2x1_ASAP7_75t_R  g059(.A(pi19), .B(new_n115), .Y(new_n118));
  AND2x2_ASAP7_75t_R   g060(.A(new_n116), .B(new_n66), .Y(new_n119));
  NAND2x1_ASAP7_75t_R  g061(.A(new_n66), .B(new_n116), .Y(new_n120));
  XOR2x2_ASAP7_75t_R   g062(.A(new_n116), .B(pi19), .Y(new_n121));
  XNOR2x2_ASAP7_75t_R  g063(.A(pi08), .B(pi20), .Y(new_n122));
  XOR2x2_ASAP7_75t_R   g064(.A(pi08), .B(pi20), .Y(new_n123));
  NOR2x1_ASAP7_75t_R   g065(.A(new_n68), .B(new_n123), .Y(new_n124));
  NAND2x1_ASAP7_75t_R  g066(.A(pi26), .B(new_n122), .Y(new_n125));
  AND2x2_ASAP7_75t_R   g067(.A(new_n123), .B(new_n68), .Y(new_n126));
  NAND2x1_ASAP7_75t_R  g068(.A(new_n68), .B(new_n123), .Y(new_n127));
  XOR2x2_ASAP7_75t_R   g069(.A(new_n123), .B(pi26), .Y(new_n128));
  AO211x2_ASAP7_75t_R  g070(.A1(new_n127), .A2(new_n125), .B(new_n119), .C(new_n117), .Y(new_n129));
  AO211x2_ASAP7_75t_R  g071(.A1(new_n120), .A2(new_n118), .B(new_n126), .C(new_n124), .Y(new_n130));
  AND3x1_ASAP7_75t_R   g072(.A(new_n129), .B(new_n130), .C(new_n114), .Y(new_n131));
  AOI21x1_ASAP7_75t_R  g073(.A1(new_n129), .A2(new_n130), .B(new_n114), .Y(new_n132));
  OAI21x1_ASAP7_75t_R  g074(.A1(new_n132), .A2(new_n131), .B(new_n112), .Y(new_n133));
  AO211x2_ASAP7_75t_R  g075(.A1(new_n110), .A2(new_n111), .B(new_n132), .C(new_n131), .Y(new_n134));
  AND3x1_ASAP7_75t_R   g076(.A(new_n134), .B(new_n133), .C(new_n108), .Y(new_n135));
  NAND3x1_ASAP7_75t_R  g077(.A(new_n134), .B(new_n133), .C(new_n108), .Y(new_n136));
  AOI21x1_ASAP7_75t_R  g078(.A1(new_n133), .A2(new_n134), .B(new_n108), .Y(new_n137));
  AO21x1_ASAP7_75t_R   g079(.A1(new_n134), .A2(new_n133), .B(new_n108), .Y(new_n138));
  NOR2x1_ASAP7_75t_R   g080(.A(new_n137), .B(new_n135), .Y(new_n139));
  OR4x2_ASAP7_75t_R    g081(.A(new_n135), .B(new_n137), .C(pi03), .D(new_n105), .Y(new_n140));
  AO31x2_ASAP7_75t_R   g082(.A1(new_n62), .A2(new_n136), .A3(new_n138), .B(new_n106), .Y(new_n141));
  NAND2x1_ASAP7_75t_R  g083(.A(new_n141), .B(new_n140), .Y(new_n142));
  INVx1_ASAP7_75t_R    g084(.A(new_n142), .Y(new_n143));
  XNOR2x2_ASAP7_75t_R  g085(.A(pi10), .B(pi22), .Y(new_n144));
  AND3x1_ASAP7_75t_R   g086(.A(new_n59), .B(new_n61), .C(pi24), .Y(new_n145));
  XOR2x2_ASAP7_75t_R   g087(.A(new_n145), .B(pi25), .Y(new_n146));
  OAI21x1_ASAP7_75t_R  g088(.A1(new_n81), .A2(new_n80), .B(pi23), .Y(new_n147));
  OR3x1_ASAP7_75t_R    g089(.A(new_n80), .B(new_n81), .C(pi23), .Y(new_n148));
  AO21x1_ASAP7_75t_R   g090(.A1(new_n148), .A2(new_n147), .B(new_n146), .Y(new_n149));
  NAND3x1_ASAP7_75t_R  g091(.A(new_n148), .B(new_n147), .C(new_n146), .Y(new_n150));
  AND3x1_ASAP7_75t_R   g092(.A(new_n150), .B(new_n149), .C(new_n144), .Y(new_n151));
  AOI21x1_ASAP7_75t_R  g093(.A1(new_n149), .A2(new_n150), .B(new_n144), .Y(new_n152));
  NOR2x1_ASAP7_75t_R   g094(.A(new_n152), .B(new_n151), .Y(new_n153));
  OAI21x1_ASAP7_75t_R  g095(.A1(new_n152), .A2(new_n151), .B(new_n62), .Y(new_n154));
  OA21x2_ASAP7_75t_R   g096(.A1(pi00), .A2(pi03), .B(pi12), .Y(new_n155));
  XOR2x2_ASAP7_75t_R   g097(.A(new_n121), .B(pi26), .Y(new_n156));
  XNOR2x2_ASAP7_75t_R  g098(.A(pi11), .B(pi25), .Y(new_n157));
  XOR2x2_ASAP7_75t_R   g099(.A(pi11), .B(pi25), .Y(new_n158));
  NAND2x1_ASAP7_75t_R  g100(.A(pi18), .B(new_n158), .Y(new_n159));
  NAND2x1_ASAP7_75t_R  g101(.A(new_n65), .B(new_n157), .Y(new_n160));
  AND4x2_ASAP7_75t_R   g102(.A(new_n110), .B(new_n160), .C(new_n159), .D(new_n111), .Y(new_n161));
  AOI22x1_ASAP7_75t_R  g103(.A1(new_n110), .A2(new_n111), .B1(new_n160), .B2(new_n159), .Y(new_n162));
  OR2x4_ASAP7_75t_R    g104(.A(new_n162), .B(new_n161), .Y(new_n163));
  AND3x1_ASAP7_75t_R   g105(.A(new_n60), .B(new_n61), .C(pi27), .Y(new_n164));
  OAI21x1_ASAP7_75t_R  g106(.A1(new_n162), .A2(new_n161), .B(new_n164), .Y(new_n165));
  OR3x1_ASAP7_75t_R    g107(.A(new_n161), .B(new_n162), .C(new_n164), .Y(new_n166));
  AND3x1_ASAP7_75t_R   g108(.A(new_n166), .B(new_n165), .C(new_n156), .Y(new_n167));
  AOI21x1_ASAP7_75t_R  g109(.A1(new_n165), .A2(new_n166), .B(new_n156), .Y(new_n168));
  OR2x4_ASAP7_75t_R    g110(.A(new_n168), .B(new_n167), .Y(new_n169));
  OAI21x1_ASAP7_75t_R  g111(.A1(new_n168), .A2(new_n167), .B(new_n62), .Y(new_n170));
  OA22x2_ASAP7_75t_R   g112(.A1(pi28), .A2(new_n170), .B1(new_n154), .B2(new_n155), .Y(new_n171));
  AOI22x1_ASAP7_75t_R  g113(.A1(new_n170), .A2(pi28), .B1(new_n154), .B2(new_n155), .Y(new_n172));
  AND2x2_ASAP7_75t_R   g114(.A(new_n171), .B(new_n172), .Y(new_n173));
  NAND2x1_ASAP7_75t_R  g115(.A(new_n172), .B(new_n171), .Y(new_n174));
  OA21x2_ASAP7_75t_R   g116(.A1(pi00), .A2(pi03), .B(pi24), .Y(new_n175));
  INVx1_ASAP7_75t_R    g117(.A(new_n175), .Y(new_n176));
  AND2x2_ASAP7_75t_R   g118(.A(new_n61), .B(pi29), .Y(new_n177));
  XOR2x2_ASAP7_75t_R   g119(.A(new_n128), .B(new_n177), .Y(new_n178));
  XNOR2x2_ASAP7_75t_R  g120(.A(pi15), .B(pi23), .Y(new_n179));
  OR3x1_ASAP7_75t_R    g121(.A(new_n161), .B(new_n162), .C(new_n179), .Y(new_n180));
  OAI21x1_ASAP7_75t_R  g122(.A1(new_n162), .A2(new_n161), .B(new_n179), .Y(new_n181));
  AND3x1_ASAP7_75t_R   g123(.A(new_n180), .B(new_n181), .C(new_n178), .Y(new_n182));
  AOI21x1_ASAP7_75t_R  g124(.A1(new_n181), .A2(new_n180), .B(new_n178), .Y(new_n183));
  OR2x4_ASAP7_75t_R    g125(.A(new_n183), .B(new_n182), .Y(new_n184));
  OA21x2_ASAP7_75t_R   g126(.A1(new_n182), .A2(new_n183), .B(new_n62), .Y(new_n185));
  NAND2x1_ASAP7_75t_R  g127(.A(new_n69), .B(new_n185), .Y(new_n186));
  AO21x1_ASAP7_75t_R   g128(.A1(new_n184), .A2(new_n62), .B(new_n69), .Y(new_n187));
  AND2x2_ASAP7_75t_R   g129(.A(new_n187), .B(new_n186), .Y(new_n188));
  XOR2x2_ASAP7_75t_R   g130(.A(new_n185), .B(pi30), .Y(new_n189));
  AO21x1_ASAP7_75t_R   g131(.A1(new_n187), .A2(new_n186), .B(new_n176), .Y(new_n190));
  OAI21x1_ASAP7_75t_R  g132(.A1(pi01), .A2(pi03), .B(pi17), .Y(new_n191));
  AOI211x1_ASAP7_75t_R g133(.A1(new_n175), .A2(new_n189), .B(new_n174), .C(new_n191), .Y(new_n192));
  NAND3x1_ASAP7_75t_R  g134(.A(new_n192), .B(new_n143), .C(new_n103), .Y(new_n193));
  XOR2x2_ASAP7_75t_R   g135(.A(new_n193), .B(pi15), .Y(po00));
  NOR2x1_ASAP7_75t_R   g136(.A(pi02), .B(pi32), .Y(new_n195));
  OR2x4_ASAP7_75t_R    g137(.A(pi02), .B(pi32), .Y(new_n196));
  AO21x1_ASAP7_75t_R   g138(.A1(new_n73), .A2(new_n195), .B(new_n70), .Y(new_n197));
  AND5x1_ASAP7_75t_R   g139(.A(new_n100), .B(new_n101), .C(new_n197), .D(new_n91), .E(new_n92), .Y(new_n198));
  INVx1_ASAP7_75t_R    g140(.A(new_n198), .Y(new_n199));
  AOI21x1_ASAP7_75t_R  g141(.A1(new_n141), .A2(new_n140), .B(new_n191), .Y(new_n200));
  AO21x1_ASAP7_75t_R   g142(.A1(new_n140), .A2(new_n141), .B(new_n191), .Y(new_n201));
  NOR2x1_ASAP7_75t_R   g143(.A(new_n174), .B(new_n200), .Y(new_n202));
  AOI211x1_ASAP7_75t_R g144(.A1(new_n175), .A2(new_n189), .B(new_n200), .C(new_n174), .Y(new_n203));
  AO211x2_ASAP7_75t_R  g145(.A1(new_n175), .A2(new_n189), .B(new_n174), .C(new_n200), .Y(new_n204));
  AND4x2_ASAP7_75t_R   g146(.A(new_n201), .B(new_n198), .C(new_n190), .D(new_n173), .Y(new_n205));
  XOR2x2_ASAP7_75t_R   g147(.A(new_n205), .B(new_n68), .Y(po01));
  XNOR2x2_ASAP7_75t_R  g148(.A(pi20), .B(new_n205), .Y(po02));
  XOR2x2_ASAP7_75t_R   g149(.A(new_n193), .B(pi25), .Y(po03));
  XNOR2x2_ASAP7_75t_R  g150(.A(pi08), .B(new_n205), .Y(po04));
  XNOR2x2_ASAP7_75t_R  g151(.A(pi23), .B(new_n205), .Y(po05));
  AND4x2_ASAP7_75t_R   g152(.A(new_n201), .B(new_n190), .C(new_n173), .D(new_n103), .Y(new_n211));
  XOR2x2_ASAP7_75t_R   g153(.A(new_n211), .B(new_n64), .Y(po06));
  XNOR2x2_ASAP7_75t_R  g154(.A(pi09), .B(new_n211), .Y(po07));
  XNOR2x2_ASAP7_75t_R  g155(.A(pi16), .B(new_n211), .Y(po08));
  AND3x1_ASAP7_75t_R   g156(.A(new_n187), .B(new_n186), .C(new_n175), .Y(new_n215));
  AND3x1_ASAP7_75t_R   g157(.A(new_n202), .B(new_n215), .C(new_n198), .Y(new_n216));
  XOR2x2_ASAP7_75t_R   g158(.A(new_n216), .B(new_n66), .Y(po09));
  XNOR2x2_ASAP7_75t_R  g159(.A(pi07), .B(new_n216), .Y(po10));
  XNOR2x2_ASAP7_75t_R  g160(.A(pi22), .B(new_n216), .Y(po11));
  XNOR2x2_ASAP7_75t_R  g161(.A(pi06), .B(new_n216), .Y(po12));
  AND3x1_ASAP7_75t_R   g162(.A(new_n202), .B(new_n215), .C(new_n103), .Y(new_n221));
  XNOR2x2_ASAP7_75t_R  g163(.A(pi14), .B(new_n221), .Y(po13));
  XOR2x2_ASAP7_75t_R   g164(.A(new_n193), .B(pi18), .Y(po14));
  XOR2x2_ASAP7_75t_R   g165(.A(new_n193), .B(pi11), .Y(po15));
  OA21x2_ASAP7_75t_R   g166(.A1(new_n103), .A2(new_n198), .B(new_n203), .Y(new_n225));
  AO32x1_ASAP7_75t_R   g167(.A1(new_n173), .A2(new_n201), .A3(new_n215), .B1(new_n143), .B2(new_n192), .Y(new_n226));
  AND2x2_ASAP7_75t_R   g168(.A(new_n102), .B(new_n70), .Y(new_n227));
  AO21x1_ASAP7_75t_R   g169(.A1(new_n226), .A2(new_n227), .B(new_n225), .Y(new_n228));
  AND5x1_ASAP7_75t_R   g170(.A(new_n188), .B(new_n173), .C(new_n102), .D(new_n176), .E(new_n191), .Y(new_n229));
  AO221x2_ASAP7_75t_R  g171(.A1(new_n143), .A2(new_n229), .B1(pi05), .B2(new_n228), .C(pi02), .Y(po16));
  AOI211x1_ASAP7_75t_R g172(.A1(new_n104), .A2(new_n199), .B(new_n204), .C(pi03), .Y(new_n231));
  AOI21x1_ASAP7_75t_R  g173(.A1(new_n105), .A2(new_n231), .B(new_n139), .Y(new_n232));
  AO32x1_ASAP7_75t_R   g174(.A1(new_n105), .A2(new_n231), .A3(new_n139), .B1(new_n61), .B2(new_n63), .Y(new_n233));
  NOR2x1_ASAP7_75t_R   g175(.A(new_n232), .B(new_n233), .Y(po17));
  AOI21x1_ASAP7_75t_R  g176(.A1(pi30), .A2(new_n231), .B(new_n184), .Y(new_n235));
  AO32x1_ASAP7_75t_R   g177(.A1(pi30), .A2(new_n231), .A3(new_n184), .B1(new_n61), .B2(new_n63), .Y(new_n236));
  NOR2x1_ASAP7_75t_R   g178(.A(new_n235), .B(new_n236), .Y(po18));
  AOI21x1_ASAP7_75t_R  g179(.A1(pi21), .A2(new_n231), .B(new_n90), .Y(new_n238));
  AO32x1_ASAP7_75t_R   g180(.A1(pi21), .A2(new_n231), .A3(new_n90), .B1(new_n61), .B2(new_n63), .Y(new_n239));
  NOR2x1_ASAP7_75t_R   g181(.A(new_n238), .B(new_n239), .Y(po19));
  AOI21x1_ASAP7_75t_R  g182(.A1(pi13), .A2(new_n231), .B(new_n99), .Y(new_n241));
  AO32x1_ASAP7_75t_R   g183(.A1(pi13), .A2(new_n231), .A3(new_n99), .B1(new_n61), .B2(new_n63), .Y(new_n242));
  NOR2x1_ASAP7_75t_R   g184(.A(new_n241), .B(new_n242), .Y(po20));
  AOI21x1_ASAP7_75t_R  g185(.A1(new_n155), .A2(new_n231), .B(new_n153), .Y(new_n244));
  AO32x1_ASAP7_75t_R   g186(.A1(new_n153), .A2(new_n231), .A3(new_n155), .B1(new_n61), .B2(new_n63), .Y(new_n245));
  NOR2x1_ASAP7_75t_R   g187(.A(new_n244), .B(new_n245), .Y(po21));
  OR3x1_ASAP7_75t_R    g188(.A(new_n131), .B(new_n132), .C(new_n195), .Y(new_n247));
  AND4x2_ASAP7_75t_R   g189(.A(new_n203), .B(new_n247), .C(new_n61), .D(new_n198), .Y(new_n248));
  AOI21x1_ASAP7_75t_R  g190(.A1(new_n61), .A2(new_n205), .B(new_n247), .Y(new_n249));
  OR2x4_ASAP7_75t_R    g191(.A(pi02), .B(pi31), .Y(new_n250));
  AO21x1_ASAP7_75t_R   g192(.A1(pi31), .A2(pi32), .B(pi02), .Y(new_n251));
  AO211x2_ASAP7_75t_R  g193(.A1(new_n196), .A2(new_n250), .B(new_n249), .C(new_n248), .Y(new_n252));
  OAI21x1_ASAP7_75t_R  g194(.A1(new_n249), .A2(new_n248), .B(new_n251), .Y(new_n253));
  NAND2x1_ASAP7_75t_R  g195(.A(new_n253), .B(new_n252), .Y(po22));
  AOI21x1_ASAP7_75t_R  g196(.A1(new_n79), .A2(new_n163), .B(new_n71), .Y(new_n255));
  OAI21x1_ASAP7_75t_R  g197(.A1(new_n79), .A2(new_n163), .B(new_n255), .Y(new_n256));
  AND4x2_ASAP7_75t_R   g198(.A(new_n203), .B(new_n256), .C(new_n61), .D(new_n103), .Y(new_n257));
  AOI21x1_ASAP7_75t_R  g199(.A1(new_n61), .A2(new_n211), .B(new_n256), .Y(new_n258));
  OR2x4_ASAP7_75t_R    g200(.A(pi02), .B(pi29), .Y(new_n259));
  AO21x1_ASAP7_75t_R   g201(.A1(pi04), .A2(pi29), .B(pi02), .Y(new_n260));
  AO211x2_ASAP7_75t_R  g202(.A1(new_n72), .A2(new_n259), .B(new_n258), .C(new_n257), .Y(new_n261));
  OAI21x1_ASAP7_75t_R  g203(.A1(new_n258), .A2(new_n257), .B(new_n260), .Y(new_n262));
  NAND2x1_ASAP7_75t_R  g204(.A(new_n262), .B(new_n261), .Y(po23));
  AOI21x1_ASAP7_75t_R  g205(.A1(pi28), .A2(new_n231), .B(new_n169), .Y(new_n264));
  AO32x1_ASAP7_75t_R   g206(.A1(pi28), .A2(new_n231), .A3(new_n169), .B1(new_n61), .B2(new_n63), .Y(new_n265));
  NOR2x1_ASAP7_75t_R   g207(.A(new_n264), .B(new_n265), .Y(po24));
endmodule


