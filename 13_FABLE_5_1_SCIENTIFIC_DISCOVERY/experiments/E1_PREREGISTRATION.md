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

(empty at registration)
