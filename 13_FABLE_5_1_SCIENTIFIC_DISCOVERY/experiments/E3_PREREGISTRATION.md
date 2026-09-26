# E3 — pre-registration: gate-level test of the regime-(V) claim

Written 2026-09-26 after E2's first delay-oriented results. No E3 data existed at this point.

## Why E3 exists (a finding, recorded before E3)

- **E2's design flaw.** E2 synthesizes a *specific* W with constants propagated. That is regime (F).
- **What that does to the baseline.** In (F), synthesis structural hashing (Yosys `opt_merge`, ABC `strash`) merges identical partial sums that recur across rows of the per-input balanced trees.
- **Measured size of the effect** (`scripts/hwlayer.py` op lists, hash-consed):
  - per-input adders at n = 128 drop from 10,929 to 5,884 (p0 = .33) and from 7,984 to 4,968 (p0 = .5);
  - UBP4 drops only from 5,074 to 5,040 and from 4,862 to 4,816.
- **Consequence.** E1's (F) comparison "per-input Σ(nnz − 1) vs UBP" used a baseline weaker than what a standard tool produces automatically. That is the Wave 10 weak-baseline error, caught here.
- **What it does not affect.** In regime (V) no such hashing is possible, because the base layers cannot depend on W. So E2 cannot test the (V) claim, and E3 does.

## Hypothesis

At iso-delay on SKY130, the cell area of a weight-independent (V) fabric built from universal block generators plus ⌈n/g⌉-leaf row trees is ≥ 1.5× smaller than the (V) per-input fabric with n-leaf row trees. Select wiring is excluded; it is handled by the wire model.

## Components (all weight-independent)

- **TREE(L, w):** L opaque w-bit signed leaves (the via-selected lines, modelled as primary inputs) summed by one multi-operand adder, written as a single Verilog sum. Yosys `alumacc` and ABC choose the structure.
- **GEN(g):** all (3^g − 1)/2 canonical signed subset sums of g 8-bit inputs, built parent + one input, as in `hwlayer.py`.
- **Polarity.** Both fabrics provide ± lines, so per-site polarity is a via choice. Negators are shared per line: n negators for g = 1 and ⌈n/g⌉·(3^g − 1)/2 for UBP. They are counted with a NEG(w) component.
- **Fabric areas:**
  - A_V(g1) = m·TREE(n, 8) + n·NEG(8)
  - A_V(UBP-g) = m·TREE(⌈n/g⌉, w_g) + ⌈n/g⌉·[GEN(g) + (3^g − 1)/2 · NEG(w_g)], with w_g = 8 + ⌈log2 g⌉.

## Sizes

- n = m ∈ {128, 1024}, g ∈ {2, 3, 4}.
- TREE(1024, 8) is the largest component, at about 1023 adders' worth of logic.

## Flow

- Yosys (YoWASP) → AIG; our AIGER simulator checks every component on 64 random vectors against Python integer arithmetic; native ABC `strash; dch; map` with SKY130 HD.
- **Iso-delay:**
  - D*(n) = max over designs of the delay-optimal critical path, where UBP's path is d(GEN) + d(TREE(⌈n/g⌉)).
  - g1's tree is re-mapped with `-D D*`.
  - UBP's tree is re-mapped with `-D (D* − d_GEN)`, with GEN at its delay-optimal mapping.
- ABC `cec` for every mapped component ("Networks are equivalent" only).

## Kill and advance conditions

| ID | Condition | Classification |
|---|---|---|
| K3 | min_g A_V(g1)/A_V(UBP-g) < 1.3 at both n | (V) advantage does not survive gate level → MECHANISM FALSIFIED in (V) |
| ADV3 | ≥ 1.5 at n = 1024 | (V) claim supported at cell level; wiring (PnR) is the remaining risk |

## Deviation log

(empty)
