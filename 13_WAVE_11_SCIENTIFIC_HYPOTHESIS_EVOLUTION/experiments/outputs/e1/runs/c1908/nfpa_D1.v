// Benchmark "/r/12_WAVE_10_EXPERIMENTAL_DISCOVERY/experiments/inputs/c1/c2/c1908" written by ABC on Sat Sep 26 00:07:38 2026

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
    new_n189, new_n190, new_n191, new_n192, new_n194, new_n195, new_n196,
    new_n197, new_n198, new_n199, new_n205, new_n209, new_n210, new_n215,
    new_n219, new_n220, new_n221, new_n222, new_n223, new_n224, new_n226,
    new_n227, new_n228, new_n230, new_n231, new_n232, new_n234, new_n235,
    new_n236, new_n238, new_n239, new_n241, new_n242, new_n243, new_n245,
    new_n246, new_n247, new_n248, new_n250, new_n251, new_n252, new_n253,
    new_n254, new_n256, new_n257, new_n258;
  INVx1_ASAP7_75t_R    g000(.A(pi00), .Y(new_n59));
  INVx1_ASAP7_75t_R    g001(.A(pi01), .Y(new_n60));
  INVx1_ASAP7_75t_R    g002(.A(pi02), .Y(new_n61));
  INVx1_ASAP7_75t_R    g003(.A(pi03), .Y(new_n62));
  INVx1_ASAP7_75t_R    g004(.A(pi19), .Y(new_n63));
  INVx1_ASAP7_75t_R    g005(.A(pi21), .Y(new_n64));
  INVx1_ASAP7_75t_R    g006(.A(pi26), .Y(new_n65));
  INVx1_ASAP7_75t_R    g007(.A(pi30), .Y(new_n66));
  NOR2x1_ASAP7_75t_R   g008(.A(pi02), .B(pi05), .Y(new_n67));
  OA21x2_ASAP7_75t_R   g009(.A1(pi00), .A2(new_n60), .B(new_n67), .Y(new_n68));
  NOR2x1_ASAP7_75t_R   g010(.A(pi02), .B(pi04), .Y(new_n69));
  OA21x2_ASAP7_75t_R   g011(.A1(new_n60), .A2(pi00), .B(new_n62), .Y(new_n70));
  AO21x1_ASAP7_75t_R   g012(.A1(new_n69), .A2(new_n70), .B(new_n68), .Y(new_n71));
  XNOR2x2_ASAP7_75t_R  g013(.A(pi09), .B(pi18), .Y(new_n72));
  XNOR2x2_ASAP7_75t_R  g014(.A(pi06), .B(pi19), .Y(new_n73));
  XOR2x2_ASAP7_75t_R   g015(.A(new_n73), .B(pi20), .Y(new_n74));
  NOR2x1_ASAP7_75t_R   g016(.A(pi01), .B(pi02), .Y(new_n75));
  OR2x4_ASAP7_75t_R    g017(.A(pi14), .B(pi15), .Y(new_n76));
  NAND2x1_ASAP7_75t_R  g018(.A(pi14), .B(pi15), .Y(new_n77));
  AND2x2_ASAP7_75t_R   g019(.A(new_n76), .B(new_n77), .Y(new_n78));
  AOI21x1_ASAP7_75t_R  g020(.A1(new_n77), .A2(new_n76), .B(pi16), .Y(new_n79));
  AND3x1_ASAP7_75t_R   g021(.A(new_n76), .B(new_n77), .C(pi16), .Y(new_n80));
  OA211x2_ASAP7_75t_R  g022(.A1(new_n80), .A2(new_n79), .B(new_n75), .C(pi17), .Y(new_n81));
  AOI211x1_ASAP7_75t_R g023(.A1(pi17), .A2(new_n75), .B(new_n80), .C(new_n79), .Y(new_n82));
  OAI21x1_ASAP7_75t_R  g024(.A1(new_n82), .A2(new_n81), .B(new_n74), .Y(new_n83));
  OR3x1_ASAP7_75t_R    g025(.A(new_n81), .B(new_n82), .C(new_n74), .Y(new_n84));
  AND3x1_ASAP7_75t_R   g026(.A(new_n84), .B(new_n83), .C(new_n72), .Y(new_n85));
  NAND3x1_ASAP7_75t_R  g027(.A(new_n84), .B(new_n83), .C(new_n72), .Y(new_n86));
  AOI21x1_ASAP7_75t_R  g028(.A1(new_n83), .A2(new_n84), .B(new_n72), .Y(new_n87));
  AO21x1_ASAP7_75t_R   g029(.A1(new_n84), .A2(new_n83), .B(new_n72), .Y(new_n88));
  NAND2x1_ASAP7_75t_R  g030(.A(new_n88), .B(new_n86), .Y(new_n89));
  OR4x2_ASAP7_75t_R    g031(.A(new_n85), .B(new_n87), .C(pi03), .D(pi21), .Y(new_n90));
  AO31x2_ASAP7_75t_R   g032(.A1(new_n62), .A2(new_n86), .A3(new_n88), .B(new_n64), .Y(new_n91));
  XNOR2x2_ASAP7_75t_R  g033(.A(pi09), .B(pi10), .Y(new_n92));
  INVx1_ASAP7_75t_R    g034(.A(new_n92), .Y(new_n93));
  NOR2x1_ASAP7_75t_R   g035(.A(pi00), .B(pi02), .Y(new_n94));
  AND3x1_ASAP7_75t_R   g036(.A(new_n59), .B(new_n61), .C(pi12), .Y(new_n95));
  XOR2x2_ASAP7_75t_R   g037(.A(pi06), .B(pi07), .Y(new_n96));
  XNOR2x2_ASAP7_75t_R  g038(.A(pi08), .B(pi11), .Y(new_n97));
  AND2x2_ASAP7_75t_R   g039(.A(new_n97), .B(new_n96), .Y(new_n98));
  NOR2x1_ASAP7_75t_R   g040(.A(new_n96), .B(new_n97), .Y(new_n99));
  OAI21x1_ASAP7_75t_R  g041(.A1(new_n98), .A2(new_n99), .B(new_n95), .Y(new_n100));
  AO211x2_ASAP7_75t_R  g042(.A1(pi12), .A2(new_n94), .B(new_n98), .C(new_n99), .Y(new_n101));
  AND3x1_ASAP7_75t_R   g043(.A(new_n101), .B(new_n100), .C(new_n93), .Y(new_n102));
  AOI21x1_ASAP7_75t_R  g044(.A1(new_n100), .A2(new_n101), .B(new_n93), .Y(new_n103));
  OR2x4_ASAP7_75t_R    g045(.A(new_n103), .B(new_n102), .Y(new_n104));
  OR3x1_ASAP7_75t_R    g046(.A(new_n104), .B(pi13), .C(pi03), .Y(new_n105));
  OAI21x1_ASAP7_75t_R  g047(.A1(pi03), .A2(new_n104), .B(pi13), .Y(new_n106));
  AND4x2_ASAP7_75t_R   g048(.A(new_n105), .B(new_n106), .C(new_n90), .D(new_n91), .Y(new_n107));
  AND5x1_ASAP7_75t_R   g049(.A(new_n105), .B(new_n106), .C(new_n90), .D(new_n91), .E(new_n71), .Y(new_n108));
  NAND2x1_ASAP7_75t_R  g050(.A(new_n71), .B(new_n107), .Y(new_n109));
  OA21x2_ASAP7_75t_R   g051(.A1(pi01), .A2(pi03), .B(pi27), .Y(new_n110));
  INVx1_ASAP7_75t_R    g052(.A(new_n110), .Y(new_n111));
  NAND2x1_ASAP7_75t_R  g053(.A(pi31), .B(new_n61), .Y(new_n112));
  XOR2x2_ASAP7_75t_R   g054(.A(new_n112), .B(pi14), .Y(new_n113));
  XNOR2x2_ASAP7_75t_R  g055(.A(pi09), .B(pi16), .Y(new_n114));
  NAND2x1_ASAP7_75t_R  g056(.A(pi10), .B(new_n114), .Y(new_n115));
  OR2x4_ASAP7_75t_R    g057(.A(pi10), .B(new_n114), .Y(new_n116));
  AND2x2_ASAP7_75t_R   g058(.A(new_n116), .B(new_n115), .Y(new_n117));
  XOR2x2_ASAP7_75t_R   g059(.A(pi06), .B(pi23), .Y(new_n118));
  INVx1_ASAP7_75t_R    g060(.A(new_n118), .Y(new_n119));
  XOR2x2_ASAP7_75t_R   g061(.A(pi07), .B(pi22), .Y(new_n120));
  NOR2x1_ASAP7_75t_R   g062(.A(new_n63), .B(new_n120), .Y(new_n121));
  OR2x4_ASAP7_75t_R    g063(.A(new_n63), .B(new_n120), .Y(new_n122));
  AND2x2_ASAP7_75t_R   g064(.A(new_n120), .B(new_n63), .Y(new_n123));
  NAND2x1_ASAP7_75t_R  g065(.A(new_n63), .B(new_n120), .Y(new_n124));
  XOR2x2_ASAP7_75t_R   g066(.A(pi08), .B(pi20), .Y(new_n125));
  NOR2x1_ASAP7_75t_R   g067(.A(new_n65), .B(new_n125), .Y(new_n126));
  OR2x4_ASAP7_75t_R    g068(.A(new_n65), .B(new_n125), .Y(new_n127));
  AND2x2_ASAP7_75t_R   g069(.A(new_n125), .B(new_n65), .Y(new_n128));
  NAND2x1_ASAP7_75t_R  g070(.A(new_n65), .B(new_n125), .Y(new_n129));
  NOR2x1_ASAP7_75t_R   g071(.A(new_n128), .B(new_n126), .Y(new_n130));
  AO211x2_ASAP7_75t_R  g072(.A1(new_n129), .A2(new_n127), .B(new_n123), .C(new_n121), .Y(new_n131));
  AO211x2_ASAP7_75t_R  g073(.A1(new_n124), .A2(new_n122), .B(new_n128), .C(new_n126), .Y(new_n132));
  AND3x1_ASAP7_75t_R   g074(.A(new_n131), .B(new_n132), .C(new_n119), .Y(new_n133));
  AOI21x1_ASAP7_75t_R  g075(.A1(new_n131), .A2(new_n132), .B(new_n119), .Y(new_n134));
  OAI21x1_ASAP7_75t_R  g076(.A1(new_n134), .A2(new_n133), .B(new_n117), .Y(new_n135));
  AO211x2_ASAP7_75t_R  g077(.A1(new_n115), .A2(new_n116), .B(new_n134), .C(new_n133), .Y(new_n136));
  AND3x1_ASAP7_75t_R   g078(.A(new_n136), .B(new_n135), .C(new_n113), .Y(new_n137));
  NAND3x1_ASAP7_75t_R  g079(.A(new_n136), .B(new_n135), .C(new_n113), .Y(new_n138));
  AOI21x1_ASAP7_75t_R  g080(.A1(new_n135), .A2(new_n136), .B(new_n113), .Y(new_n139));
  AO21x1_ASAP7_75t_R   g081(.A1(new_n136), .A2(new_n135), .B(new_n113), .Y(new_n140));
  NOR2x1_ASAP7_75t_R   g082(.A(new_n139), .B(new_n137), .Y(new_n141));
  AND4x2_ASAP7_75t_R   g083(.A(new_n138), .B(new_n140), .C(new_n62), .D(new_n111), .Y(new_n142));
  OA31x2_ASAP7_75t_R   g084(.A1(pi03), .A2(new_n137), .A3(new_n139), .B1(new_n110), .Y(new_n143));
  NOR2x1_ASAP7_75t_R   g085(.A(new_n143), .B(new_n142), .Y(new_n144));
  XNOR2x2_ASAP7_75t_R  g086(.A(pi10), .B(pi22), .Y(new_n145));
  AND3x1_ASAP7_75t_R   g087(.A(new_n59), .B(new_n61), .C(pi24), .Y(new_n146));
  XNOR2x2_ASAP7_75t_R  g088(.A(pi25), .B(new_n146), .Y(new_n147));
  OA21x2_ASAP7_75t_R   g089(.A1(new_n80), .A2(new_n79), .B(pi23), .Y(new_n148));
  NOR3x1_ASAP7_75t_R   g090(.A(new_n80), .B(new_n79), .C(pi23), .Y(new_n149));
  OAI21x1_ASAP7_75t_R  g091(.A1(new_n148), .A2(new_n149), .B(new_n147), .Y(new_n150));
  OR3x1_ASAP7_75t_R    g092(.A(new_n149), .B(new_n148), .C(new_n147), .Y(new_n151));
  AND3x1_ASAP7_75t_R   g093(.A(new_n151), .B(new_n150), .C(new_n145), .Y(new_n152));
  AOI21x1_ASAP7_75t_R  g094(.A1(new_n150), .A2(new_n151), .B(new_n145), .Y(new_n153));
  NOR2x1_ASAP7_75t_R   g095(.A(new_n153), .B(new_n152), .Y(new_n154));
  OAI21x1_ASAP7_75t_R  g096(.A1(new_n153), .A2(new_n152), .B(new_n62), .Y(new_n155));
  OA21x2_ASAP7_75t_R   g097(.A1(pi00), .A2(pi03), .B(pi12), .Y(new_n156));
  OR3x1_ASAP7_75t_R    g098(.A(new_n154), .B(new_n156), .C(pi03), .Y(new_n157));
  AO21x1_ASAP7_75t_R   g099(.A1(new_n122), .A2(new_n124), .B(new_n65), .Y(new_n158));
  OR3x1_ASAP7_75t_R    g100(.A(new_n121), .B(new_n123), .C(pi26), .Y(new_n159));
  NAND2x1_ASAP7_75t_R  g101(.A(new_n158), .B(new_n159), .Y(new_n160));
  XOR2x2_ASAP7_75t_R   g102(.A(pi11), .B(pi25), .Y(new_n161));
  NAND2x1_ASAP7_75t_R  g103(.A(pi18), .B(new_n161), .Y(new_n162));
  OR2x4_ASAP7_75t_R    g104(.A(pi18), .B(new_n161), .Y(new_n163));
  AND4x2_ASAP7_75t_R   g105(.A(new_n116), .B(new_n163), .C(new_n162), .D(new_n115), .Y(new_n164));
  AOI22x1_ASAP7_75t_R  g106(.A1(new_n163), .A2(new_n162), .B1(new_n116), .B2(new_n115), .Y(new_n165));
  OR2x4_ASAP7_75t_R    g107(.A(new_n165), .B(new_n164), .Y(new_n166));
  AND3x1_ASAP7_75t_R   g108(.A(new_n60), .B(new_n61), .C(pi27), .Y(new_n167));
  OA21x2_ASAP7_75t_R   g109(.A1(new_n164), .A2(new_n165), .B(new_n167), .Y(new_n168));
  AOI211x1_ASAP7_75t_R g110(.A1(pi27), .A2(new_n75), .B(new_n164), .C(new_n165), .Y(new_n169));
  OR3x1_ASAP7_75t_R    g111(.A(new_n169), .B(new_n168), .C(new_n160), .Y(new_n170));
  OAI21x1_ASAP7_75t_R  g112(.A1(new_n168), .A2(new_n169), .B(new_n160), .Y(new_n171));
  NAND2x1_ASAP7_75t_R  g113(.A(new_n171), .B(new_n170), .Y(new_n172));
  AO21x1_ASAP7_75t_R   g114(.A1(new_n170), .A2(new_n171), .B(pi03), .Y(new_n173));
  AOI22x1_ASAP7_75t_R  g115(.A1(new_n155), .A2(new_n156), .B1(new_n173), .B2(pi28), .Y(new_n174));
  OA211x2_ASAP7_75t_R  g116(.A1(pi28), .A2(new_n173), .B(new_n174), .C(new_n157), .Y(new_n175));
  OA21x2_ASAP7_75t_R   g117(.A1(pi00), .A2(pi03), .B(pi24), .Y(new_n176));
  NAND2x1_ASAP7_75t_R  g118(.A(pi29), .B(new_n61), .Y(new_n177));
  XOR2x2_ASAP7_75t_R   g119(.A(new_n130), .B(new_n177), .Y(new_n178));
  XNOR2x2_ASAP7_75t_R  g120(.A(pi15), .B(pi23), .Y(new_n179));
  OR3x1_ASAP7_75t_R    g121(.A(new_n164), .B(new_n165), .C(new_n179), .Y(new_n180));
  OAI21x1_ASAP7_75t_R  g122(.A1(new_n165), .A2(new_n164), .B(new_n179), .Y(new_n181));
  NAND3x1_ASAP7_75t_R  g123(.A(new_n178), .B(new_n180), .C(new_n181), .Y(new_n182));
  AO21x1_ASAP7_75t_R   g124(.A1(new_n180), .A2(new_n181), .B(new_n178), .Y(new_n183));
  NAND2x1_ASAP7_75t_R  g125(.A(new_n183), .B(new_n182), .Y(new_n184));
  AOI211x1_ASAP7_75t_R g126(.A1(new_n182), .A2(new_n183), .B(pi03), .C(pi30), .Y(new_n185));
  AOI21x1_ASAP7_75t_R  g127(.A1(new_n62), .A2(new_n184), .B(new_n66), .Y(new_n186));
  NOR2x1_ASAP7_75t_R   g128(.A(new_n185), .B(new_n186), .Y(new_n187));
  OAI21x1_ASAP7_75t_R  g129(.A1(new_n185), .A2(new_n186), .B(new_n176), .Y(new_n188));
  OA21x2_ASAP7_75t_R   g130(.A1(pi01), .A2(pi03), .B(pi17), .Y(new_n189));
  AND3x1_ASAP7_75t_R   g131(.A(new_n175), .B(new_n188), .C(new_n189), .Y(new_n190));
  NAND2x1_ASAP7_75t_R  g132(.A(new_n144), .B(new_n190), .Y(new_n191));
  OR2x4_ASAP7_75t_R    g133(.A(new_n109), .B(new_n191), .Y(new_n192));
  XOR2x2_ASAP7_75t_R   g134(.A(new_n192), .B(pi15), .Y(po00));
  NOR2x1_ASAP7_75t_R   g135(.A(pi02), .B(pi32), .Y(new_n194));
  AO21x1_ASAP7_75t_R   g136(.A1(new_n70), .A2(new_n194), .B(new_n68), .Y(new_n195));
  AND2x2_ASAP7_75t_R   g137(.A(new_n107), .B(new_n195), .Y(new_n196));
  OAI21x1_ASAP7_75t_R  g138(.A1(new_n143), .A2(new_n142), .B(new_n189), .Y(new_n197));
  AND2x2_ASAP7_75t_R   g139(.A(new_n175), .B(new_n197), .Y(new_n198));
  AND4x2_ASAP7_75t_R   g140(.A(new_n196), .B(new_n175), .C(new_n188), .D(new_n197), .Y(new_n199));
  XOR2x2_ASAP7_75t_R   g141(.A(new_n199), .B(new_n65), .Y(po01));
  XNOR2x2_ASAP7_75t_R  g142(.A(pi20), .B(new_n199), .Y(po02));
  XOR2x2_ASAP7_75t_R   g143(.A(new_n192), .B(pi25), .Y(po03));
  XNOR2x2_ASAP7_75t_R  g144(.A(pi08), .B(new_n199), .Y(po04));
  XNOR2x2_ASAP7_75t_R  g145(.A(pi23), .B(new_n199), .Y(po05));
  AND4x2_ASAP7_75t_R   g146(.A(new_n175), .B(new_n188), .C(new_n197), .D(new_n108), .Y(new_n205));
  XNOR2x2_ASAP7_75t_R  g147(.A(pi10), .B(new_n205), .Y(po06));
  XNOR2x2_ASAP7_75t_R  g148(.A(pi09), .B(new_n205), .Y(po07));
  XNOR2x2_ASAP7_75t_R  g149(.A(pi16), .B(new_n205), .Y(po08));
  NAND3x1_ASAP7_75t_R  g150(.A(new_n198), .B(new_n187), .C(new_n176), .Y(new_n209));
  AND5x1_ASAP7_75t_R   g151(.A(new_n187), .B(new_n196), .C(new_n175), .D(new_n197), .E(new_n176), .Y(new_n210));
  XOR2x2_ASAP7_75t_R   g152(.A(new_n210), .B(new_n63), .Y(po09));
  XNOR2x2_ASAP7_75t_R  g153(.A(pi07), .B(new_n210), .Y(po10));
  XNOR2x2_ASAP7_75t_R  g154(.A(pi22), .B(new_n210), .Y(po11));
  XNOR2x2_ASAP7_75t_R  g155(.A(pi06), .B(new_n210), .Y(po12));
  NOR2x1_ASAP7_75t_R   g156(.A(new_n109), .B(new_n209), .Y(new_n215));
  XNOR2x2_ASAP7_75t_R  g157(.A(pi14), .B(new_n215), .Y(po13));
  XOR2x2_ASAP7_75t_R   g158(.A(new_n192), .B(pi18), .Y(po14));
  XOR2x2_ASAP7_75t_R   g159(.A(new_n192), .B(pi11), .Y(po15));
  OA211x2_ASAP7_75t_R  g160(.A1(new_n108), .A2(new_n196), .B(new_n198), .C(new_n188), .Y(new_n219));
  NAND2x1_ASAP7_75t_R  g161(.A(new_n68), .B(new_n107), .Y(new_n220));
  AOI21x1_ASAP7_75t_R  g162(.A1(new_n191), .A2(new_n209), .B(new_n220), .Y(new_n221));
  OA21x2_ASAP7_75t_R   g163(.A1(new_n221), .A2(new_n219), .B(pi05), .Y(new_n222));
  NOR2x1_ASAP7_75t_R   g164(.A(new_n176), .B(new_n189), .Y(new_n223));
  AND5x1_ASAP7_75t_R   g165(.A(new_n144), .B(new_n187), .C(new_n175), .D(new_n107), .E(new_n223), .Y(new_n224));
  OR3x1_ASAP7_75t_R    g166(.A(new_n222), .B(new_n224), .C(pi02), .Y(po16));
  OA21x2_ASAP7_75t_R   g167(.A1(new_n199), .A2(new_n205), .B(new_n62), .Y(new_n226));
  AND2x2_ASAP7_75t_R   g168(.A(new_n226), .B(new_n110), .Y(new_n227));
  AOI21x1_ASAP7_75t_R  g169(.A1(new_n141), .A2(new_n227), .B(new_n67), .Y(new_n228));
  OA21x2_ASAP7_75t_R   g170(.A1(new_n141), .A2(new_n227), .B(new_n228), .Y(po17));
  AOI21x1_ASAP7_75t_R  g171(.A1(pi30), .A2(new_n226), .B(new_n184), .Y(new_n230));
  AND3x1_ASAP7_75t_R   g172(.A(new_n226), .B(new_n184), .C(pi30), .Y(new_n231));
  OR3x1_ASAP7_75t_R    g173(.A(new_n231), .B(new_n230), .C(new_n67), .Y(new_n232));
  INVx1_ASAP7_75t_R    g174(.A(new_n232), .Y(po18));
  AOI21x1_ASAP7_75t_R  g175(.A1(pi21), .A2(new_n226), .B(new_n89), .Y(new_n234));
  AND3x1_ASAP7_75t_R   g176(.A(new_n226), .B(new_n89), .C(pi21), .Y(new_n235));
  OR3x1_ASAP7_75t_R    g177(.A(new_n235), .B(new_n234), .C(new_n67), .Y(new_n236));
  INVx1_ASAP7_75t_R    g178(.A(new_n236), .Y(po19));
  AND2x2_ASAP7_75t_R   g179(.A(new_n226), .B(pi13), .Y(new_n238));
  AOI21x1_ASAP7_75t_R  g180(.A1(new_n104), .A2(new_n238), .B(new_n67), .Y(new_n239));
  OA21x2_ASAP7_75t_R   g181(.A1(new_n104), .A2(new_n238), .B(new_n239), .Y(po20));
  AOI21x1_ASAP7_75t_R  g182(.A1(new_n156), .A2(new_n226), .B(new_n154), .Y(new_n241));
  AND3x1_ASAP7_75t_R   g183(.A(new_n226), .B(new_n156), .C(new_n154), .Y(new_n242));
  OR3x1_ASAP7_75t_R    g184(.A(new_n242), .B(new_n241), .C(new_n67), .Y(new_n243));
  INVx1_ASAP7_75t_R    g185(.A(new_n243), .Y(po21));
  AND2x2_ASAP7_75t_R   g186(.A(new_n199), .B(new_n61), .Y(new_n245));
  OR3x1_ASAP7_75t_R    g187(.A(new_n133), .B(new_n134), .C(new_n194), .Y(new_n246));
  XOR2x2_ASAP7_75t_R   g188(.A(new_n245), .B(new_n246), .Y(new_n247));
  AO21x1_ASAP7_75t_R   g189(.A1(pi31), .A2(pi32), .B(pi02), .Y(new_n248));
  XOR2x2_ASAP7_75t_R   g190(.A(new_n247), .B(new_n248), .Y(po22));
  AND2x2_ASAP7_75t_R   g191(.A(new_n205), .B(new_n61), .Y(new_n250));
  AOI21x1_ASAP7_75t_R  g192(.A1(new_n78), .A2(new_n166), .B(new_n69), .Y(new_n251));
  OA21x2_ASAP7_75t_R   g193(.A1(new_n78), .A2(new_n166), .B(new_n251), .Y(new_n252));
  XOR2x2_ASAP7_75t_R   g194(.A(new_n250), .B(new_n252), .Y(new_n253));
  AO21x1_ASAP7_75t_R   g195(.A1(pi04), .A2(pi29), .B(pi02), .Y(new_n254));
  XNOR2x2_ASAP7_75t_R  g196(.A(new_n254), .B(new_n253), .Y(po23));
  AOI21x1_ASAP7_75t_R  g197(.A1(pi28), .A2(new_n226), .B(new_n172), .Y(new_n256));
  AND3x1_ASAP7_75t_R   g198(.A(new_n226), .B(new_n172), .C(pi28), .Y(new_n257));
  OR3x1_ASAP7_75t_R    g199(.A(new_n257), .B(new_n256), .C(new_n67), .Y(new_n258));
  INVx1_ASAP7_75t_R    g200(.A(new_n258), .Y(po24));
endmodule


