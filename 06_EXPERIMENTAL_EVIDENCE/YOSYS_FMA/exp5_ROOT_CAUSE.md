# Root cause: signed FMA partial-product correction is not sign-extended

## Reproduced source

The clean build is Yosys commit `9ff27d29c672cc5274ce69106145a8aed7c9ba3d`,
with ABC submodule commit `d3f10b3724553d1cf6628fb86e496028c2868bb8`.
The relevant implementation is `kernel/compressor_tree.cc`, function
`CompressorTree::generate_partial_products()`.

## Mechanism

The FMA path converts a signed `$macc_v2` product term into Baugh–Wooley
partial products. Before the patch, the signed correction was emitted as one
constant bit at:

```text
width_a + width_b - 1
```

That is sufficient when the arithmetic result is retained at the native
product width. It is not sufficient when the product is embedded in a wider
FMA accumulation. The generated rows are zero-extended to the accumulation
width, so the native product sign extension is absent. The single correction
bit therefore becomes an unconditional positive offset instead of the
required sign extension through the wider result.

The local repair emits a constant with ones from the product sign bit through
the target accumulation width. At the native product width this is the same
single-bit correction modulo the result width. At a wider accumulation width it
provides the required two's-complement sign extension.

## RTLIL evidence

The W4 pre-`arith_tree` `$macc_v2` records signed product terms with:

```text
Y_WIDTH  = 20
A_WIDTHS = 262148  (packed 16-bit entries: 4, 4)
B_WIDTHS = 262147  (packed 16-bit entries: 3, 4)
A_SIGNED = 2'b11
B_SIGNED = 2'b11
```

The W8 corresponding records use `Y_WIDTH=24`, `A_WIDTHS` entries `8,8`,
and `B_WIDTHS` entries `3,4`. These parameters are preserved in the saved
pre-transformation RTLIL artifacts and are consumed by `Macc::from_cell()`.

## Counterexample arithmetic

The minimized failing family is a two-product signed FMA with explicit
sign-extension into a wider output. The W4 witness is `a=6`, `b=3` for the
minimized test; the original FIR4 witness is `x0=7`, `x1=12`, `x2=9`,
`x3=6`.

For the original W4 FIR4 witness, the first two signed product widths are
`4x3` and `4x4`. The one-bit correction is placed at the product sign-bit
positions (`m+n-1`), and the resulting wide-accumulation error is one power of
two higher for each positive product:

```text
2^(4+3) + 2^(4+4) = 0x080 + 0x100 = 0x180
```

This equals the observed formal error `gate_y=0x180` versus `gold_y=0x00000`.
The match is an explanatory source-level identity, not a cell-count
inference. The W8 original witness similarly fails with `gate_y=0x1986`
versus `gold_y=0x0186`; its difference is `0x1800`.

## Scope of the change

Only the signed correction constant in `kernel/compressor_tree.cc` was
changed. FMA expansion remains enabled. The patch does not special-case the
FIR4 inputs, widths, coefficients, compressor strategy, or final adder.

## Validation status

The patched build formally proves the original FIR4 W4 and W8 cases and the
minimized two-product cases at W4, W8, and W16. The full original FIR4 W16
formal proof timed out at the bounded 300-second harness limit and is recorded
as inconclusive, not as a pass. Independent Icarus replay passes for the
original W4/W8 vectors. All 13 checked-in `tests/arith_tree/*.ys` scripts pass
in both clean and patched builds.

The explanation is specific to this implementation and source commit. It is
not a claim of full Yosys correctness or of upstream acceptance.
