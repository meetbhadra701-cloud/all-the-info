# 03 — Proximity, reflection, debate, evolution and ranking (phases B6–B7)

Written before any experiment was run; the results are in 04.

For each candidate:
- **generation:** where it came from;
- **proximity:** the closest known work and the distance to it;
- **reflection:** the weakest assumption;
- **evolution:** at most one bounded change, declared here, before data.

---

## XACC — exact, order-free accumulation for bounded-scale block formats

**Generation.** It is the intersection of the one 2026 cost regime with a hardware-shaped cause (01 §1.4) and the property of the formats now being standardised (01 §1.5): their block scales have a bounded exponent range.

**Proximity:**

| Nearest work | What it does | Distance to XACC |
|---|---|---|
| Kulisch / long accumulators; FloPoCo FPGA long accumulator | Exact fixed-point accumulation of floats over a window | **Same ingredient.** XACC's content is the *format-specific width bound* (a small window because the block scale is bounded) and the *cost claim* against FP32 at the physical level. Without those it is the known principle |
| Per-tensor shared exponents: INT8 GEMM, Flexpoint, BFP accelerators | One scale per tensor makes products integers, so accumulation is exact (INT32) | Per-*block* scales break that, because every block has its own exponent. XACC shows a bounded block-scale range costs only the scale-exponent span in extra bits |
| HiFloat4 [S] | Changes the *format* (hierarchical power-of-two micro-exponents) so a 64-element group stays integer; FP afterwards | XACC keeps NVFP4 unchanged and makes the *cross-block* accumulation exact over all of K |
| "FP8 is All You Need" hardware [S] | Exact INT64 positional accumulation in INT8 tensor cores, for FP64 emulation (Ozaki-II) | Different inputs (integer slices), a different purpose (FP64 accuracy), no block-scale analysis. **Closest hardware proposal, with a different mechanism target** |
| `nvfp4-dotprod-formal-dv` [G] | Exact fixed-point BF16 accumulation *inside* a bounded window; out-of-window operands become NaN | Not exact for all inputs; no cost or system claim |
| Software determinism (batch-invariant kernels, TBIK, fused-upcast) [S] | Fix the order | XACC removes the need to fix the order, for the GEMM part only |
| Qualcomm FP8 vs INT8 [S] | Argues FP accumulators beat Kulisch for FP8-E4 | That is per-product accumulation. XACC's causal claim is per-*block* amortisation plus a scale-bounded window. **The direct opposing expert opinion; E2 decides** |

**Reflection — weakest assumptions, most dangerous first:**
1. **Cost.**
   - 60 bits of state plus a 5-level shifter plus a 60-bit adder must not exceed int→FP conversion plus FP32 align/add/normalise/round plus 32 bits of state.
   - The state doubling is the real risk. In a GPU the accumulators live in tensor memory, so 64-bit accumulators halve the resident tile.
   - The PE-level evaluator measures the arithmetic and the PE-local state. The TMEM effect is **not** measured, and any positive result must say so.
2. **Scope of importance.**
   - RL rollouts today are mostly BF16, where exactness costs about 550 bits (not free).
   - XACC helps where NVFP4 / FP8 GEMMs are used (FP4/FP8 inference, NVFP4 training), which is a growing but not total share.
   - It fixes GEMM determinism only; attention and norms remain software's job.
3. **The problem premise per format.** If FP32 accumulation of NVFP4 block contributions were almost always order-invariant in practice (few rounding events), there would be nothing to fix. E1 tests this.

**Bounded evolution.** None declared for XACC. The three-target clock sweep in E2 is part of the protocol, not an evolution. If E2 kills it, it is killed.

---

## XABFT — threshold-free SDC detection

**Generation.** A consequence of XACC's exactness, applied to the SDC problem (01 §1.6).

**Proximity:**
- ABFT (1984) is the ingredient.
- Exact integer ABFT exists for INT GEMMs [S: 2609.19743].
- FP-Sketch reaches zero false positives in software [S: 2609.19758].
- Freivalds-style exact verification is textbook.

XABFT's only distinct content is exactness *for block-scaled float formats*, which comes entirely from XACC.

**Reflection.**
- Weakest assumption: the faults a tolerance must let through are consequential, not noise-level.
- Second: the wider checksum lane (B's column sums are not NVFP4) has a cost that the model-level check does not measure.

**Debate outcome.** XABFT is not an independent thesis. If XACC fails on cost, XABFT's case reduces to "pay for exactness to get detection", which dual-lane integer designs and software sketches already offer.

**Bounded evolution (declared now, the one allowed): merge XABFT into XACC** as its secondary claim C2. Its evaluator runs as XACC-E3 and decides only whether C2 is material.

---

## MR-SIGNOFF — oracle-free metamorphic validation of the open sign-off stack

**Generation.** The archive's hardware-gated C-2 ("open-flow sign-off vs silicon") asked for an oracle the open world lacks. Metamorphic relations need no oracle.

**Proximity.**
- Metamorphic testing is a mature method in compilers (EMI), SMT (YinYang) and databases.
- Equivalence-based fuzzing exists for synthesis (Verismith).
- Summaries show no metamorphic testing of extraction or STA [S], which is absence in summaries only.

**Reflection.**
- Weakest assumption: that the tools violate an exact invariance at all. They may be carefully deterministic.
- Second, a classification risk: findings are defects, which the kill database says are not contributions by themselves. The research claim must be the *method's* power (violations found that tests miss), not any single bug.

**Bounded evolution.** None.

---

## LIN-CEC — linear-algebraic CEC for XOR-dominated logic

**Generation.** From the DAC'26 best-paper area (01 §1.1).

**Proximity: occupied.**
- Gaussian elimination in XOR-dense regions for circuit equivalence checking is reported [S].
- CryptoMiniSat's Gauss–Jordan solves XOR-heavy instances in seconds [S].
- BDDs represent parity in linear size.

**Reflection.** Even if ABC's CDCL-based `&cec` fails on such miters, the fix is a known technique integrated into a known tool. That is **engineering** (kill-database pattern: "known principle + new implementation").

**Decision at proximity: KILLED (occupied).** It is not selected for an evaluator. A 60-second-per-instance ABC screen is recorded in 04 only as supporting evidence of the tool behaviour, not as a thesis test.

---

## Comparative debate and ranking (B7)

Readiness is judged on:
- importance;
- mechanism precision;
- a cheap, decisive falsifier;
- structural headroom;
- distance to prior art (distinct content, not ingredients);
- independence from other candidates.

No numeric scores are assigned; they would be false precision.

| Rank | Candidate | For | Against | Selected for B8 |
|---|---|---|---|---|
| 1 | **XACC** | 2026-hot problem with a hardware-shaped cause; a precise, format-specific mechanism; a falsifier of hours with the strongest baselines named; categorical benefit | The ingredient is known, so novelty rests on the width bound plus the physical cost claim; state doubling; scope limited to bounded-scale formats | **Yes** (E1 numerics, E2 physical) |
| 2 | **MR-SIGNOFF** | Independent of XACC; cheap; oracle-free and categorical | Moderate importance; likely engineering classification | **Yes** |
| 3 | **XABFT** (merged into XACC as C2) | Categorical detection | Dependent; value depends on small-fault consequence | **Yes, as XACC-E3** (model-level) |
| 4 | LIN-CEC | — | Occupied; engineering | No (killed) |

**The debate's one strong disagreement, recorded.**
- **Prosecution:** XACC is "Kulisch applied to NVFP4", an obvious composition in a crowded year.
- **Defence:** the obviousness of *using* a long accumulator is conceded. What is not established anywhere found is:
  - (a) that two-level scaling makes the window about 60 bits;
  - (b) that at this width exactness is *cheaper* than the FP32 accumulation the format specifies, which contradicts the published expert expectation for FP8;
  - (c) that the scale format (UE4M3 / UE5M3 vs E8M0) therefore decides whether hardware determinism is free.

  If (b) is measured, the composition has a non-obvious, quantitative interaction effect (lesson 8 in `14_…/24`). If (b) fails, the defence collapses and the prosecution wins.
- **Resolution:** E2 is the arbiter. Its criterion is fixed in 04 before any data.
