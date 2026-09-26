# E1 — pre-registration (written before any E1 data was generated)

**Date:** 2026-09-26.

**Tested hypothesis family:** Problem A — area-optimal hardwired (fixed-weight) linear layers. See `../03_HYPOTHESIS_REGISTER.md`.

## Mechanism under test (OURS)

**Universal block-pattern fabric (UBP-g).** Split the n inputs into blocks of g. For every block, a weight-independent generator computes all (3^g − 1)/2 nonzero signed subset sums of its g inputs, up to sign. Every row then adds or subtracts one generator output per nonzero block.

- The base layers (generator adders and the row adder trees) do not depend on W.
- W enters only through which generator line each row-block connects to (a via/metal choice) and through the add/sub sign.
- g = 1 is the existing per-input scheme: ternary add/sub/skip (Ankhdjet-style), and "Multiply-Select-Add" (Taalas-style) for multi-bit weights.

## Baselines

1. **g = 1 (per-input sharing; the existing universal scheme):** Σ_rows (nnz_i − 1) add/sub.
2. **da4ml 0.6.0 `cmvm.solve` defaults:** weight-specific common-subexpression CMVM, the strongest open CMVM method (TRETS 2025, integrated in hls4ml). It is NOT universal: its adder DAG depends on W.
3. **Weight-specific block patterns (CBP-g):** generate only the used patterns and their parent closure. Included to separate "block sharing" from "universality".

## Inputs

- i.i.d. ternary W with P(0) = p0 ∈ {0.33, 0.50} and P(+1) = P(−1). Sizes m = n ∈ {64, 128, 256, 512, 1024, 2048, 4096}. Three seeds per size.
- Limitation, declared now: real BitNet checkpoints cannot be fetched (the huggingface.co host is blocked by the environment's egress policy).

## Measures

- **U:** unit-cost adder count (one add/sub = 1).
- **B:** bit-weighted cost, Σ over adders of the result width in bits. Inputs are 8-bit signed and widths come from exact value ranges; this is a ripple-adder area proxy.
- Solver wall time.

## Correctness (independent)

- Every UBP/CBP construction is emitted as an explicit op list.
- da4ml solutions are executed by our own interpreter, not da4ml's.
- Every result is checked against numpy `W @ x` on 64 random 8-bit input vectors. A mismatch invalidates the data point.

## Kill and advance conditions (fixed now)

| ID | Condition | Classification |
|---|---|---|
| K1 (mechanism) | Median U(g=1)/U(UBP-g*) < 1.5 for ternary at m = n ≥ 1024 | block patterns give no material reduction → MECHANISM FALSIFIED |
| K2 (universality price) | At sizes where da4ml finishes in ≤ 600 s, median U(UBP-g*)/U(da4ml) > 1.5 | universal fabrics lose too much against weight-specific CSE; the thesis narrows to "full-custom only", which is occupied by CSE (da4ml) → NOVELTY OCCUPIED for the universal claim |
| A1 (advance) | U(g=1)/U(UBP-g*) ≥ 2 at m = n ≥ 1024 AND U(UBP-g*)/U(da4ml) ≤ 1.25 where da4ml finishes | proceed to E2 (gate-level synthesis) |

- g* is the g that minimizes U, chosen per size by exhaustive search over g ∈ {1..8}. This is reported, not tuned per seed.
- The bit-weighted cost B is reported alongside U. If U and B disagree on K1/K2, the more conservative reading is taken.

## Deviation log

**D1 — before any E1 data.** The independent checker exposed two problems during smoke tests:
- **(a) da4ml 0.6.0 input-layout hazard.** `solve` treats an F-ordered array as its transpose and raises no error (`../evidence/da4ml_layout_hazard.txt`). All E1 da4ml calls use `np.ascontiguousarray`, and they assert `pipe.kernel == K`.
- **(b) A bug in our own integer evaluator.** It ignored operand shifts. It was fixed and re-validated with 4 negative controls: flipped op sign, flipped output sign, and two shift/polarity mutations of da4ml circuits, all rejected.

**D2 — during the run.** The da4ml 256×256 (p0 = 0.33, seed 0) instance hit the 600 s cap. It did so while a native ABC build (`make -j3`) shared the 4-core machine, so the timeout is **not a clean runtime measurement**.
- By the registered rule, da4ml was then skipped for the remaining seeds and larger sizes at that p0.
- A supplementary idle-machine da4ml run at 256 with a longer cap is reported separately, if run, and is not used for K2.

**D3 — analysis, post hoc (declared; it does not change the registered test).** The registered "g = 1" cost Σ_i(nnz_i − 1) is the **full-custom** cost: zeros are skipped.
- In a via-programmable fabric the base layers cannot know where zeros are, so the universal g = 1 fabric needs m(n − 1) adders.
- The registered UBP cost uses a universal generator with row trees over nonzero blocks only. That is a hybrid between the two regimes.
- `e1_analyze.py` therefore also prints exact regime-correct closed forms (V: g1_V = m(n−1) vs UBP_V with full trees), plus a counting lower bound.
- The registered K1/K2/A1 are evaluated exactly as registered, on the registered quantities.

**D4 — sizes ≥ 2048.**
- g = 1 is costed in cost-only mode: the same code path without op storage, with its closed form asserted.
- UBP is built explicitly and checked with a batch of 4 when the generator has ≤ 6 M entries; otherwise it is costed only.
- All constructions were explicitly checked at n ≤ 1024.

**D5 — stopped at the end of the session (declared).**
- The sweep was stopped with n = 4096, p0 = 0.50 at 2 of 3 seeds; every other cell has 3 seeds.
- The remaining instance is a regime-(F), unhashed cost-only row, a comparison superseded by E1-hashed (see E3_PREREGISTRATION.md).

**Registered verdicts (from `results/E1_summary.md`):**
- **K1 not triggered.** The median over n ≥ 1024 of min(U, B) g1/UBP* is 2.47, so A1's size clause is met, *but against the unhashed per-input baseline, later shown to be weak*.
- **K2 not triggered.** The median UBP*/da4ml is 1.34.
- **A1's advance condition was NOT met,** because its da4ml clause (≤ 1.25) failed.

The thesis's advance rests on E3 (regime V), which was pre-registered separately.
