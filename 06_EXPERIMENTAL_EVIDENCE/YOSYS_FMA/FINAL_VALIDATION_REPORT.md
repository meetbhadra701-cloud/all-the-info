# Experiment 6 — Yosys signed-FMA fix final validation

## Final disposition

**C. PATCH CORRECT FOR TESTED CASES, BUT IMPORTANT VALIDATION GAPS REMAIN.**

The defect reproduces in a clean current Yosys main build. The local patch
corrects the reproduced signed wide-accumulation path and passes the completed
bounded validation, including a bit-level model, current-main functional
miters, documented compressor/final-adder options, and the existing relevant
tests. It is not marked ready for maintainer review because two matrix proofs
timed out, the full original FIR4 W16 proof remains inconclusive, mixed RTL
signedness does not exercise the affected `$macc_v2` path, and the full Yosys
suite was not run.

No GitHub issue, pull request, push, or upstream commit was created.

## Environment and provenance

The clean current-main checkout is Yosys commit
`e8db64c609c7ae4574e66bbd475f5f10f36d7a31`, dated `2026-09-21T16:08:28Z`,
with ABC submodule `d93d356216e3547770631ec26e71463e35196507`. It was built in
Docker Desktop's Linux engine using Ubuntu 24.04, Clang 18.1.3, CMake 3.28.3,
Ninja, and two build jobs. The exact identity and image IDs are in
`current_upstream/SOURCE_IDENTITY.md`; the build logs are in `logs/`.

The patched worktree is local branch `exp6-fma-fix`, based directly on current
main. The only source change is `kernel/compressor_tree.cc` in
`CompressorTree::generate_partial_products()`. The patch uses a `long long`
intermediate for `width_a + width_b - 1` to remove theoretical signed-int
overflow before the range check.

## Current-main reproduction

| Test | Clean current main | Patched current main |
|---|---:|---:|
| FIR4 W4, normal | PASS | PASS |
| FIR4 W4, `-arith_tree` | FAIL | PASS |
| FIR4 W4, `-no-fma` | PASS | PASS |
| FIR4 W8, normal | PASS | PASS |
| FIR4 W8, `-arith_tree` | FAIL | PASS |
| FIR4 W8, `-no-fma` | PASS | PASS |
| Minimized two-product W4 | FAIL | PASS |
| Minimized two-product W8 | FAIL | PASS |
| Minimized two-product W16 | FAIL | PASS |
| Original FIR4 W16 | NOT RUN on current clean main | INCONCLUSIVE at 300 s |

The clean current-main minimized tests produce real SAT counterexamples, not
process-only failures. The direct W4 regression
`tests/signed_fma_regression_w4.ys` fails clean and passes patched. One clean
matrix witness is `a0=6, a1=8, b0=0, b1=0` for the signed-constant W4/B3/Y16
configuration.

Detailed per-case evidence is in `results/current_main_comparison.csv` and the
referenced logs.

## Independent arithmetic review

For product width `P = width_a + width_b` and accumulation width `W`, the old
term is `C_old = 2^(P-1)` when the bit is in range. The patch emits

```text
C_new = sum(i=P-1..W-1) 2^i = 2^W - 2^(P-1).
```

Thus `C_old - C_new = 2^P (mod 2^W)`, or equivalently the patched result is
the old result minus the native product modulus. This matches the observed
wide-accumulation error. At `W=P`, the two terms are identical. For `W<P`,
the source guard emits neither final correction term, so this change preserves
the old correction behavior under truncation; that observation does not prove
all other truncated partial products correct.

The identity check covered 360 `(P,W)` rows with zero mismatches. A separate
bit-for-bit model exhaustively tested all inputs for operand widths 1--4,
target widths 1--9, and both signedness flags. For the equal-signedness
domain accepted by `$macc_v2`, the patched model had zero failures in 576
configuration rows; the old model failed only signed cases with `W>P`.
Unsigned cases passed before and after. Mixed-signedness diagnostics are
recorded but are not part of the `$macc_v2` Baugh--Wooley domain because
`Macc::from_cell()` asserts equal A/B signedness per product.

The full argument and model outputs are in
`mathematical_review/CORRECTION_PROOF.md` and `results/baugh_wooley_model.csv`.

## Bounded formal matrix

The patched build completed 44 functional SAT configurations:

| Signedness/form | Completed PASS | Timeout | Counterexample |
|---|---:|---:|---:|
| Signed × signed | 26 | 2 | 0 |
| Unsigned × unsigned | 8 | 0 | 0 |
| Signed × unsigned | 4 | 0 | 0 |
| Unsigned × signed | 4 | 0 | 0 |
| **Total** | **42** | **2** | **0** |

The matrix covers result widths below/equal to/above native product width,
positive/negative/zero constants, two and three products, asymmetric widths,
explicit extension before multiplication, and explicit extension after
multiplication. The two inconclusive cases are larger SAT instances, not
passes: signed A8/B4/Y20 and signed three-product A8/B3/Y24.

The selected clean current-main comparison contains 12 cases: 11 PASS and one
real FAIL at signed constant A4/B3/Y16. The clean build was not expected to
fail every matrix configuration.

Results and scripts:

* `results/width_signedness_matrix.csv`
* `formal/scripts/run_width_signedness_matrix.py`
* `formal/logs/width_signedness_matrix/`

## Compressor and final-adder prosecution

The installed current build documents `-strategy fa|42`, `-final
auto|ripple|prefix`, and `-no-fma`. On the W4 signed-FMA miter:

| Build | `fa/ripple` | `42/ripple` | `42/prefix` | `fa/prefix` | `-no-fma` |
|---|---:|---:|---:|---:|---:|
| Current clean | FAIL | FAIL | FAIL | FAIL | PASS |
| Patched | PASS | PASS | PASS | PASS | PASS |

This indicates the defect is not specific to one compressor strategy or final
adder. The source-level correction remains local to the signed partial-product
construction.

## Existing tests

All 13 current `tests/arith_tree/*.ys` scripts passed on both clean and
patched current-main builds: 26/26 runs. Two relevant current `tests/alumacc`
MACC tests also passed on both builds: 4/4 runs. These suites are not claimed
to be the full Yosys test suite, and their clean passes demonstrate that the
old tests did not catch this functional wide-FMA defect.

Results: `results/upstream_test_results.csv` and
`results/relevant_extra_tests.csv`.

## Performance sanity check

This is generic synthesis only, not physical area or timing. The bounded FIR4
comparison used the same current-main toolchain and flow:

| W | Current tree cells | Patched tree cells | Difference | Current tree seconds | Patched tree seconds |
|---:|---:|---:|---:|---:|---:|
| 4 | 151 | 146 | -5 | 0.886 | 0.883 |
| 8 | 330 | 331 | +1 | 1.005 | 1.063 |
| 16 | 716 | 723 | +7 | 1.124 | 1.111 |

Normal and `-no-fma` cell counts were unchanged at 145/270/518. The patch
does not disable FMA globally. No Liberty mapping, physical area, placement,
routing, or timing claim is made.

## Current upstream and prior-art check

Current main still contains the old one-bit correction; no upstream fix for
this defect was found in the checked-out source. Yosys [PR #6178](https://github.com/YosysHQ/yosys/pull/6178) concerns
multiply-add reassociation and `$macc` formation for DSP inference. It is not
the partial-product correction repair and was not treated as one.

## Required answers

1. **Does the defect reproduce on current Yosys main?** Yes, at FIR4 W4/W8
   and minimized W4/W8/W16.
2. **Has upstream already fixed it?** No in tested current main.
3. **Is the correction mathematically valid for wider accumulation?** Yes for
   the reviewed correction term and supported equal-signedness product path;
   the independent identity and bit model found no supported-domain failure.
4. **What happens at native product width?** `W=P` makes the mask one bit, so
   behavior is preserved.
5. **What happens under output truncation?** For `W<P`, the new guard emits no
   final correction, matching the old code. Other truncation logic remains
   outside this term-only proof.
6. **Do mixed signedness configurations remain correct?** The completed RTL
   mixed cases pass, but they generally do not exercise `$macc_v2`'s equal-
   signedness Baugh--Wooley path; this remains a boundary, not a universal
   claim.
7. **Which new configurations were proved?** 42 completed patched matrix
   proofs, plus the original/minimized cases, four FMA option variants, 13
   arithmetic-tree tests, and two MACC tests.
8. **Did any new counterexamples appear?** No completed patched case produced
   one. Two larger cases timed out.
9. **Do relevant upstream tests pass?** Yes, 26/26 arithmetic-tree and 4/4
   extra MACC runs.
10. **Is original FIR4 W16 still inconclusive?** Yes, the patched current-main
    proof timed out at 300 seconds. The corresponding current clean-main W16
    run was not executed; the earlier Experiment 5 clean-W16 failure was on the
    historical `9ff27d29...` checkout, not current main.
11. **Can a smaller/compositional proof establish the operation?** Yes: the
    minimized two-product W16 proof and the direct functional W4 regression
    pass. They do not prove the full FIR4 W16 design.
12. **Does the patch preserve FMA functionality?** Yes for completed tests;
    FMA-enabled variants pass and `-no-fma` remains a control.
13. **Were performance regressions observed?** Small generic cell-count
    changes were observed; no stable runtime regression or physical PPA result
    was established.
14. **What remains unverified?** The full FIR4 W16 proof, two larger matrix
    proofs, all `$macc_v2` parameter combinations, a direct kernel unit proof,
    full-suite coverage, and physical implementation.
15. **Is this patch ready for maintainer review?** No. Disposition C is the
    evidence-supported answer.

## Strongest remaining risk

The patch is a mechanism-based correction with strong bounded evidence, but
the strongest hostile-review objection is still uncovered interaction among
`$macc_v2` width/truncation combinations, surrounding Baugh--Wooley terms, and
compressor construction. The two timeouts and full FIR4 W16 timeout must not
be silently converted into PASS results.
