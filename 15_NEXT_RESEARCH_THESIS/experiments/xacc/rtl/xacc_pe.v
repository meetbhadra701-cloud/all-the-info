// XACC-E2 (04 Part 1): NVFP4 block dot-product-accumulate PEs. One 16-element block pair per cycle.
// Stage 0: input registers. Stage A1: 16 E2M1 products + balanced adder tree -> S (13b signed); scale significand
// product M_ab (8b); shift s = E'a + E'b - 2 (0..28). Stage A2: P = S * M_ab (20b signed) and the variant's pre-loop
// step (exact: X = P << s; FP32: exact int->FP32 of P * 2^(s-20)). Stage B: the accumulation loop.
// UE4M3 scale code 0x7F (NaN) is excluded by assumption; bit 7 of a scale byte is ignored (unsigned scales).

// ------------------------------------------------------------------------------------------ common front end
module e2m1_q (input [3:0] c, output signed [4:0] q);
  wire [3:0] mag = (c[2:1] == 2'd0) ? {3'b000, c[0]} :
                   (c[2:1] == 2'd1) ? {2'b00, 1'b1, c[0]} :
                   (c[2:1] == 2'd2) ? {1'b0, 1'b1, c[0], 1'b0} : {1'b1, c[0], 2'b00};
  assign q = c[3] ? -$signed({1'b0, mag}) : $signed({1'b0, mag});
endmodule

module front_a1 (input [63:0] a, input [63:0] b, input [7:0] sa, input [7:0] sb,
                 output signed [12:0] S, output [7:0] mab, output [4:0] s);
  wire signed [9:0] p [0:15];
  genvar i;
  generate for (i = 0; i < 16; i = i + 1) begin : g_mul
    wire signed [4:0] qa, qb;
    e2m1_q ua (.c(a[4*i+3:4*i]), .q(qa));
    e2m1_q ub (.c(b[4*i+3:4*i]), .q(qb));
    assign p[i] = qa * qb;
  end endgenerate
  // balanced adder tree (4 levels)
  wire signed [10:0] l1 [0:7];
  wire signed [11:0] l2 [0:3];
  wire signed [12:0] l3 [0:1];
  generate for (i = 0; i < 8; i = i + 1) begin : g_l1 assign l1[i] = p[2*i] + p[2*i+1]; end endgenerate
  generate for (i = 0; i < 4; i = i + 1) begin : g_l2 assign l2[i] = l1[2*i] + l1[2*i+1]; end endgenerate
  generate for (i = 0; i < 2; i = i + 1) begin : g_l3 assign l3[i] = l2[2*i] + l2[2*i+1]; end endgenerate
  assign S = l3[0] + l3[1];
  // UE4M3: e = [6:3], m = [2:0]; M = e ? 8+m : m; E' = e ? e : 1
  wire [3:0] ea = sa[6:3], eb = sb[6:3];
  wire [3:0] ma = (ea != 0) ? {1'b1, sa[2:0]} : {1'b0, sa[2:0]};
  wire [3:0] mb = (eb != 0) ? {1'b1, sb[2:0]} : {1'b0, sb[2:0]};
  wire [3:0] epa = (ea != 0) ? ea : 4'd1;
  wire [3:0] epb = (eb != 0) ? eb : 4'd1;
  assign mab = ma * mb;
  assign s = epa + epb - 5'd2;
endmodule

// P = S * M_ab, exact (|P| <= 2304 * 225 < 2^19)
module front_a2p (input signed [12:0] S, input [7:0] mab, output signed [19:0] P);
  wire signed [21:0] full = S * $signed({1'b0, mab});
  assign P = full[19:0];
endmodule

// exact int -> FP32 of P * 2^(s-20) (|P| < 2^19 fits the 24-bit significand: no rounding)
module int2fp32 (input signed [19:0] P, input [4:0] s, output [31:0] f);
  wire sign = P[19];
  wire [18:0] mag = sign ? -P[18:0] : P[18:0];
  reg [4:0] k;            // position of the leading one
  integer j;
  always @* begin
    k = 0;
    for (j = 0; j < 19; j = j + 1) if (mag[j]) k = j[4:0];
  end
  wire [41:0] sh = {23'd0, mag} << (5'd23 - k);
  wire [7:0] e = {3'd0, k} + {3'd0, s} + 8'd107;
  assign f = (mag == 0) ? 32'd0 : {sign, e, sh[22:0]};
endmodule

// ------------------------------------------------------------------------------------------ FP32 adder (two halves)
// Domain: operands are +0 or normal (no subnormals, infinities or NaNs can occur for these PEs).
module fpadd_s1 (input [31:0] x, input [31:0] y, output rs, output [7:0] re, output [27:0] sum);
  wire [7:0] ex = x[30:23], ey = y[30:23];
  wire [23:0] mx = (ex != 0) ? {1'b1, x[22:0]} : 24'd0;
  wire [23:0] my = (ey != 0) ? {1'b1, y[22:0]} : 24'd0;
  wire swap = {ey, my} > {ex, mx};
  wire sa = swap ? y[31] : x[31], sb = swap ? x[31] : y[31];
  wire [7:0] ea = swap ? ey : ex, eb = swap ? ex : ey;
  wire [23:0] ma = swap ? my : mx, mb = swap ? mx : my;
  wire [7:0] d = ea - eb;
  wire [26:0] mbx = {mb, 3'b000};
  wire [26:0] al = (d >= 8'd27) ? 27'd0 : (mbx >> d);
  wire [26:0] lost = (d >= 8'd27) ? mbx : (mbx & ~({27{1'b1}} << d));
  wire [26:0] als = {al[26:1], al[0] | (|lost)};
  wire [27:0] max = {1'b0, ma, 3'b000};
  assign sum = (sa ^ sb) ? (max - {1'b0, als}) : (max + {1'b0, als});
  assign rs = sa;
  assign re = ea;
endmodule

module fpadd_s2 #(parameter RNE = 1) (input rs, input [7:0] re, input [27:0] sum, output [31:0] z);
  reg [4:0] lz;
  integer j;
  always @* begin
    lz = 0;
    for (j = 0; j <= 26; j = j + 1) if (sum[j]) lz = 5'd26 - j[4:0];
  end
  wire [26:0] n_carry = {sum[27:2], sum[1] | sum[0]};
  wire [26:0] n_left = sum[26:0] << lz;
  wire [26:0] n = sum[27] ? n_carry : n_left;
  wire [7:0] e1 = sum[27] ? (re + 8'd1) : (re - {3'd0, lz});
  wire [22:0] mant = n[25:3];
  wire g = n[2], r = n[1], st = n[0];
  wire inc = RNE ? (g & (r | st | mant[0])) : 1'b0;
  wire [23:0] mr = {1'b0, mant} + {23'd0, inc};
  wire [7:0] e2 = mr[23] ? (e1 + 8'd1) : e1;
  wire [22:0] m2 = mr[23] ? 23'd0 : mr[22:0];
  assign z = (sum == 0) ? 32'd0 : {rs, e2, m2};
endmodule

module fpadd #(parameter RNE = 1) (input [31:0] x, input [31:0] y, output [31:0] z);
  wire rs; wire [7:0] re; wire [27:0] sum;
  fpadd_s1 u1 (.x(x), .y(y), .rs(rs), .re(re), .sum(sum));
  fpadd_s2 #(.RNE(RNE)) u2 (.rs(rs), .re(re), .sum(sum), .z(z));
endmodule

// ------------------------------------------------------------------------------------------ PE tops
module pe_exact (input clk, input clr, input [63:0] a, input [63:0] b, input [7:0] sa, input [7:0] sb,
                 output reg [59:0] acc);
  reg [63:0] ra, rb; reg [7:0] rsa, rsb; reg c0, c1, c2;
  reg signed [12:0] S1; reg [7:0] m1; reg [4:0] s1;
  reg signed [47:0] X2;
  wire signed [12:0] S; wire [7:0] mab; wire [4:0] s; wire signed [19:0] P;
  front_a1 fa (.a(ra), .b(rb), .sa(rsa), .sb(rsb), .S(S), .mab(mab), .s(s));
  front_a2p fp (.S(S1), .mab(m1), .P(P));
  wire signed [47:0] Pext = {{28{P[19]}}, P};
  always @(posedge clk) begin
    ra <= a; rb <= b; rsa <= sa; rsb <= sb; c0 <= clr;
    S1 <= S; m1 <= mab; s1 <= s; c1 <= c0;
    X2 <= Pext <<< s1; c2 <= c1;
    acc <= (c2 ? 60'd0 : acc) + {{12{X2[47]}}, X2};
  end
endmodule

module pe_fp32 #(parameter RNE = 1) (input clk, input clr, input [63:0] a, input [63:0] b, input [7:0] sa,
                                     input [7:0] sb, output reg [31:0] acc);
  reg [63:0] ra, rb; reg [7:0] rsa, rsb; reg c0, c1, c2;
  reg signed [12:0] S1; reg [7:0] m1; reg [4:0] s1;
  reg [31:0] F2;
  wire signed [12:0] S; wire [7:0] mab; wire [4:0] s; wire signed [19:0] P; wire [31:0] F; wire [31:0] z;
  front_a1 fa (.a(ra), .b(rb), .sa(rsa), .sb(rsb), .S(S), .mab(mab), .s(s));
  front_a2p fp (.S(S1), .mab(m1), .P(P));
  int2fp32 cv (.P(P), .s(s1), .f(F));
  fpadd #(.RNE(RNE)) ad (.x(c2 ? 32'd0 : acc), .y(F2), .z(z));
  always @(posedge clk) begin
    ra <= a; rb <= b; rsa <= sa; rsb <= sb; c0 <= clr;
    S1 <= S; m1 <= mab; s1 <= s; c1 <= c0;
    F2 <= F; c2 <= c1;
    acc <= z;
  end
endmodule

module pe_fp32_rne1 (input clk, input clr, input [63:0] a, input [63:0] b, input [7:0] sa, input [7:0] sb,
                     output [31:0] acc);
  pe_fp32 #(.RNE(1)) u (.clk(clk), .clr(clr), .a(a), .b(b), .sa(sa), .sb(sb), .acc(acc));
endmodule

module pe_fp32_rz1 (input clk, input clr, input [63:0] a, input [63:0] b, input [7:0] sa, input [7:0] sb,
                    output [31:0] acc);
  pe_fp32 #(.RNE(0)) u (.clk(clk), .clr(clr), .a(a), .b(b), .sa(sa), .sb(sb), .acc(acc));
endmodule

// Two-stage pipelined RNE accumulator, two interleaved accumulators: the block entering stage B in cycle t belongs
// to accumulator t mod 2 (ph). Stage B1 = align + add, stage B2 = normalise + round. acc_q[ph] holds the result of
// the block two cycles earlier when B1 reads it.
module pe_fp32_rne_i2 (input clk, input clr, input [63:0] a, input [63:0] b, input [7:0] sa, input [7:0] sb,
                       output [63:0] acc);
  reg [63:0] ra, rb; reg [7:0] rsa, rsb; reg c0, c1, c2;
  reg signed [12:0] S1; reg [7:0] m1; reg [4:0] s1;
  reg [31:0] F2;
  reg ph, ph3;
  reg [31:0] acc0, acc1;
  reg rs3; reg [7:0] re3; reg [27:0] sum3;
  wire signed [12:0] S; wire [7:0] mab; wire [4:0] s; wire signed [19:0] P; wire [31:0] F; wire [31:0] z;
  wire rs; wire [7:0] re; wire [27:0] sum;
  front_a1 fa (.a(ra), .b(rb), .sa(rsa), .sb(rsb), .S(S), .mab(mab), .s(s));
  front_a2p fp (.S(S1), .mab(m1), .P(P));
  int2fp32 cv (.P(P), .s(s1), .f(F));
  wire [31:0] cur = c2 ? 32'd0 : (ph ? acc1 : acc0);
  fpadd_s1 b1 (.x(cur), .y(F2), .rs(rs), .re(re), .sum(sum));
  fpadd_s2 #(.RNE(1)) b2 (.rs(rs3), .re(re3), .sum(sum3), .z(z));
  always @(posedge clk) begin
    ra <= a; rb <= b; rsa <= sa; rsb <= sb; c0 <= clr;
    S1 <= S; m1 <= mab; s1 <= s; c1 <= c0;
    F2 <= F; c2 <= c1;
    ph <= ~ph;
    rs3 <= rs; re3 <= re; sum3 <= sum; ph3 <= ph;
    if (ph3) acc1 <= z; else acc0 <= z;
  end
  assign acc = {acc1, acc0};
endmodule

// ------------------------------------------------------------------------------------------ exact readout
// 60-bit two's complement (LSB 2^-20) -> FP32, round to nearest even. Shared by a row/column of exact PEs.
module readout60 (input clk, input [59:0] v, output reg [31:0] f);
  reg [59:0] rv;
  wire sign = rv[59];
  wire [58:0] mag = sign ? -rv[58:0] : rv[58:0];
  reg [5:0] k;
  integer j;
  always @* begin
    k = 0;
    for (j = 0; j < 59; j = j + 1) if (mag[j]) k = j[5:0];
  end
  // align so the leading one is at bit 58: norm[58] = 1, significand = norm[58:35], guard = norm[34], sticky = |norm[33:0]
  wire [58:0] norm = mag << (6'd58 - k);
  wire [22:0] mant = norm[57:35];
  wire g = norm[34];
  wire st = |norm[33:0];
  wire inc = g & (st | mant[0]);
  wire [23:0] mr = {1'b0, mant} + {23'd0, inc};
  wire [7:0] e = {2'd0, k} + 8'd107 + {7'd0, mr[23]};
  wire [22:0] m2 = mr[23] ? 23'd0 : mr[22:0];
  always @(posedge clk) begin
    rv <= v;
    f <= (mag == 0) ? 32'd0 : {sign, e, m2};
  end
endmodule
