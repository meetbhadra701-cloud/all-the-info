# Experiment 5 — Yosys signed-FMA `arith_tree` correctness repair

## Disposition

**C. Clean upstream defect confirmed; local patch developed but not fully
validated.**

The defect reproduces in a clean official-source build at commit
`9ff27d29c672cc5274ce69106145a8aed7c9ba3d`. A narrowly scoped local patch
passes the original W4/W8 cases, a minimized W4/W8/W16 family, independent
simulation replay, and all 13 checked-in arithmetic-tree scripts. The full
original FIR4 W16 formal proof timed out at 300 seconds, and broader
signedness/width combinations and current-main testing remain incomplete.

No issue or pull request was submitted.

## Environment and provenance

The clean build used Docker Desktop 29.8.0 with an Ubuntu 24.04 build image,
Clang 18.1.3, CMake 3.28.3, Ninja, Yosys commit
`9ff27d29c672cc5274ce69106145a8aed7c9ba3d`, and ABC 1.01 from submodule
`d3f10b3724553d1cf6628fb86e496028c2868bb8`. The Docker daemon was verified
working. The source checkout is on local branch `exp5-fma-correctness-repair`.

The exact environment capture is in `logs/environment_exp5.txt`; clean and
patched build logs are in `logs/docker_build.log` and
`logs/docker_build_patched.log`.

## Clean reproduction

| Design/configuration | W4 | W8 |
|---|---|---|
| Normal synthesis vs RTL | PASS | PASS |
| `synth -arith_tree` vs RTL | FAIL, `0x180` vs `0x00000` | FAIL, `0x1986` vs `0x0186` |
| FMA disabled | PASS | PASS |

The formal harness classified results from the SAT proof text, not only the
process return code. The original W4 witness is `x0=7, x1=12, x2=9, x3=6`.
The W8 witness is `x0=234, x1=22, x2=100, x3=0`. The detailed logs are under
`formal/logs/clean_reproduction/`.

## Minimization

The smallest retained trigger is a two-product signed FMA with explicit
sign-extension into a wider result. A single signed product does not enter the
FMA expansion path and passes; two products fail.

| Minimized miter | Clean upstream | Patched build |
|---|---|---|
| W4 | FAIL | PASS |
| W8 | FAIL | PASS |
| W16 | FAIL | PASS |

The minimized RTL and logs are in `work/minimize/`, with the summarized CSVs
in `results/minimization.csv` and `results/minimization_patched.csv`.

## Root cause

`CompressorTree::generate_partial_products()` in
`upstream/source/kernel/compressor_tree.cc` emits signed Baugh–Wooley
correction constants. Before the patch, the final correction was one bit at
`width_a + width_b - 1`. That is adequate at the native product width, but
incorrect when the product is embedded in a wider FMA accumulation: the
partial-product rows are zero-extended, so the correction is not sign-extended
through the target width.

For the original W4 witness, the first two FMA product widths are 4×3 and 4×4.
The old correction is placed at product sign-bit positions `m+n-1`; in the
wider accumulation the resulting error is one power of two higher per positive
product. Thus the observed total is
`2^(4+3) + 2^(4+4) = 0x080 + 0x100 = 0x180`, matching the formal result.
The exact RTLIL-level relationship is preserved in
`source_analysis/ROOT_CAUSE.md`; the minimized two-product reproducer is the
cleanest causal evidence.

The local fix emits ones from the product sign-bit position through the full
accumulation width. The patch is saved at `patch/arith_tree_fix.patch`.
FMA remains enabled; the repair does not special-case the FIR4 coefficients or
disable the optimization.

## Formal and independent validation

- Original FIR4 W4/W8: clean fails only with default `arith_tree`; patched
  build passes normal, `arith_tree`, and `-no-fma` checks.
- Minimized signed-FMA W4/W8/W16: clean fails; patched build formally passes.
- Deliberately incorrect coefficient: detected as a real SAT counterexample at
  W4 and W8 (`results/negative_control.csv`).
- Independent Icarus replay of the original W4/W8 vectors: normal and patched
  `arith_tree` candidates match the RTL reference (`results/replay_patched.csv`).
- Existing checked-in arithmetic-tree scripts: 13/13 pass in both clean and
  patched builds (`results/upstream_arith_tree_tests.csv`).
- Full original FIR4 W16 `arith_tree` proof: clean fails; patched proof timed
  out at 300 seconds. This is recorded as INCONCLUSIVE, not PASS.

The combined matrix is `results/regression_matrix.csv`.

## Performance check

This was a generic mapped-cell/runtime check only; no Liberty library,
OpenROAD, placement, routing, or physical timing was used.

| Width | Clean normal cells | Clean tree cells | Patched normal cells | Patched tree cells |
|---:|---:|---:|---:|---:|
| 4 | 145 | 151 | 145 | 146 |
| 8 | 270 | 330 | 270 | 331 |
| 16 | 518 | 716 | 518 | 723 |

The compressor-tree FA counts were unchanged at W4/W8/W16 (14/22/38 in the
bounded run); FMA was not globally disabled. The patch adds generic logic for
the sign-extension mask, so the bounded mapped-cell count increases. These
are not physical area measurements. Full data and commands are in
`results/performance_comparison.csv` and `formal/logs/performance/`.

## Upstream-status check

A bounded search of official Yosys issue/PR records found no exact match for
this minimized Baugh–Wooley wide-accumulation failure. Related arithmetic work
exists, including an open multiply-add reassociation PR, but that is not
evidence that this defect is fixed upstream. Current-main behavior was not
validated in this experiment, so “not found” is not “not known.” The local
submission draft is `upstream_submission/DRAFT_ISSUE_OR_PR.md`.

## Answers to the required questions

1. **Did the bug reproduce in clean upstream Yosys?** Yes, at W4 and W8 in the original FIR4 and at W4/W8/W16 in the minimized two-product family.
2. **Exact commit?** `9ff27d29c672cc5274ce69106145a8aed7c9ba3d`.
3. **Smallest failing RTL?** Two signed products added as a wider FMA result, in `tests/signed_fma_wide_source.v`.
4. **Root cause?** The signed Baugh–Wooley correction was not sign-extended to the wider accumulation width.
5. **Violated semantics?** Signed two’s-complement multiplication followed by signed addition and truncation/sign extension to the declared result width.
6. **C++ changed?** Only `kernel/compressor_tree.cc`, in `generate_partial_products()`; see `patch/arith_tree_fix.patch`.
7. **Why does it correct the mechanism?** It replaces the one-bit correction with the full-width two’s-complement sign-extension mask.
8. **Formal W4/W8/W16?** PASS for the minimized family at all three widths. Original FIR4 W4/W8 PASS after patch; original FIR4 W16 is INCONCLUSIVE due timeout.
9. **Existing regressions?** 13/13 checked-in arithmetic-tree scripts pass in both builds.
10. **Performance effect?** Generic mapped cell count increased for the tree flow by 1, 1, and 5 cells at W4/W8/W16; runtime variation was sub-second and noisy. No physical PPA result exists.
11. **Known/fixed upstream?** No exact match was found in the bounded official-record search; current main was not tested.
12. **Upstream-ready?** Not yet. The local patch is reviewable but validation is not complete enough to claim readiness.
13. **Remaining unverified?** Full FIR4 W16 proof, broad mixed signedness and truncation combinations, current-main behavior, full Yosys test suite, and physical effects.
14. **Strongest reason the patch could still be incorrect?** The correction formula was validated on the minimized family and selected regressions, not exhaustively across all `$macc_v2` width/sign combinations and compressor configurations.

## Final disposition

**C. Clean upstream defect confirmed; local patch developed but not fully
validated.** The defect is real and the local mechanism-based repair is
strongly supported, but the evidence does not justify claiming full compiler
correctness or upstream readiness.
