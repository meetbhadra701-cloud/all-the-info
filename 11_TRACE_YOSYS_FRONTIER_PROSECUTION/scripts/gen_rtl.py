#!/usr/bin/env python3
"""Generate RTL for Families A (multipliers), B (fused trees) and C (wide accumulators),
plus RTL-level semantic mutants, and write rtl/manifest.csv.

Port names are single letters a,b,c,d,e (alphabetical == declaration == operand order) and
output y, so AIGER input order is predictable; it is still verified from .map files later.
Each row carries an independent reference specification string understood by aigtool.py.
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RTL = os.path.join(HERE, '..', 'rtl')
os.makedirs(RTL, exist_ok=True)
rows = []


def decl(name, w, signed):
    return f"input {'signed ' if signed else ''}[{w-1}:0] {name}"


def emit(did, family, kind, signs, widths, yw, body, note='', expect='CORRECT', spec_override=None):
    names = 'abcde'[:len(widths)]
    ports = ', '.join(decl(n, w, s == 's') for n, w, s in zip(names, widths, signs))
    ysigned = 'signed ' if 's' in signs else ''
    src = f"module top({ports}, output {ysigned}[{yw-1}:0] y);\n{body}\nendmodule\n"
    open(os.path.join(RTL, did + '.v'), 'w').write(src)
    spec = spec_override or f"{kind}:{signs}:{','.join(map(str, widths))}:{yw}"
    rows.append({'design': did, 'family': family, 'kind': kind, 'signs': signs,
                 'widths': ','.join(map(str, widths)), 'yw': yw, 'spec': spec,
                 'rtl_expectation': expect, 'note': note})


# ---------------- Family A: multipliers y = a*b, natural width 2W
for W in (8, 12, 16, 20, 24, 32, 64):
    for sg in 'us':
        emit(f"A_mul_{sg}_w{W}", 'A', 'mul', sg * 2, [W, W], 2 * W, '  assign y = a * b;')

# ---------------- Family B: fused sums of products, natural widths
for W in (8, 12, 16, 24, 32, 64):
    for sg in 'us':
        emit(f"B_mac_{sg}_w{W}", 'B', 'mac', sg * 3, [W, W, 2 * W], 2 * W + 1, '  assign y = a * b + c;')
        emit(f"B_dot2_{sg}_w{W}", 'B', 'dot2', sg * 4, [W, W, W, W], 2 * W + 1, '  assign y = a * b + c * d;')
        emit(f"B_dot2c_{sg}_w{W}", 'B', 'dot2c', sg * 5, [W, W, W, W, 2 * W], 2 * W + 2, '  assign y = a * b + c * d + e;')

# ---------------- Family C: wide accumulators (Y > A+B), positive and negated products
for W in (4, 8, 16, 32):
    for extra in (8, 16):
        Y = 2 * W + extra
        for sg in 'us':
            emit(f"C_macw_{sg}_w{W}_y{Y}", 'C', 'mac', sg * 3, [W, W, Y], Y, '  assign y = a * b + c;',
                 note=f'Y_WIDTH={Y} > A+B={2*W}')
            emit(f"C_msubw_{sg}_w{W}_y{Y}", 'C', 'msub', sg * 3, [W, W, Y], Y, '  assign y = c - a * b;',
                 note=f'Y_WIDTH={Y} > A+B={2*W}; negated product')
    for sg in 'us':  # natural-width negated product (fits a MAC-shaped interface: a,b W; c 2W; y 2W+1)
        emit(f"C_msub_{sg}_w{W}", 'C', 'msub', sg * 3, [W, W, 2 * W], 2 * W + 1, '  assign y = c - a * b;',
             note='natural-width negated product')

# ---------------- RTL-level semantic mutants (expected INCORRECT w.r.t. the correct spec)
for W in (8, 16, 32):
    # incorrect sign extension: signed operands, product zero-extended into the accumulator
    emit(f"MUT_signext_mac_s_w{W}", 'MUT', 'mac', 'sss', [W, W, 2 * W], 2 * W + 1,
         f"  wire [{2*W-1}:0] p = a * b;\n  assign y = {{1'b0, p}} + c;",
         note='product zero-extended instead of sign-extended', expect='INCORRECT')
    # truncated product: product MSB dropped
    emit(f"MUT_trunc_mul_u_w{W}", 'MUT', 'mul', 'uu', [W, W], 2 * W,
         f"  wire [{2*W-2}:0] p = a * b;\n  assign y = {{1'b0, p}};",
         note='product truncated to 2W-1 bits', expect='INCORRECT')
    # incorrect accumulator arithmetic: carry out of the 2W-bit sum dropped
    emit(f"MUT_accum_mac_u_w{W}", 'MUT', 'mac', 'uuu', [W, W, 2 * W], 2 * W + 1,
         f"  wire [{2*W-1}:0] s = a * b + c;\n  assign y = {{1'b0, s}};",
         note='accumulator carry-out dropped', expect='INCORRECT')
    # incorrect accumulator arithmetic: off-by-one
    emit(f"MUT_plus1_dot2_u_w{W}", 'MUT', 'dot2', 'uuuu', [W, W, W, W], 2 * W + 1,
         '  assign y = a * b + c * d + 1;', note='accumulator off by one', expect='INCORRECT')

with open(os.path.join(RTL, 'manifest.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(len(rows), 'designs written to', os.path.abspath(RTL))
