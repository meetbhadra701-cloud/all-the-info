# 04 — Cheap evaluators (phase B8)

Part 1 is the **pre-registration**. It was committed before any evaluator was run; `harness.prereg.audit` checks the order from git. Part 2 (results) is appended afterwards. Deviations are logged there, never edited into Part 1.

UBP lessons applied (`14_FABLE_5_1_SCIENTIFIC_DISCOVERY/24_LESSONS_FOR_NEXT_THESIS.md`):
- **Lesson 1:** the strongest baseline, implemented through the same evaluator.
- **Lesson 2:** full physical cost (real cells, flow sizing, extraction, the slow corner).
- **Lesson 3:** the limiting path is reported for every design.
- **Lesson 4:** a headroom class is declared.
- **Lesson 6:** pre-registration.
- **Lesson 7:** independent oracle and mutation controls.
- **Lesson 11:** config → record pipeline.
- **Lesson 12:** no rescue.

---

# Part 1 — Pre-registration

## XACC-E1 — width bound and order sensitivity (numerics)

**E1a. Width derivation (DERIVED, checked by enumeration).**
- **Formats:**
  - NVFP4 (E2M1, 16-element blocks, UE4M3 scale);
  - NVFP4 with UE5M3 scales;
  - MXFP4 (E2M1, 32, E8M0);
  - MXFP8-E4M3 (32, E8M0);
  - FP8-E4M3 and FP8-E5M2 with per-tensor scale;
  - FP16;
  - BF16.
- **Method.** Enumerate every element product and every scale-pair (significand, exponent) to get the exact range of a block contribution as an integer times 2^t. Then W(K) = the bits for |Σ| ≤ (K / block) · max|contribution|, for K ∈ {4096, 16384, 65536}.
- **Prediction** (recorded now): W(NVFP4-UE4M3, 65536) = 60 bits.
- **Consequence.** A bound above 64 bits does not kill anything by itself; E2 decides cost. But the discrepancy is reported as a failed prediction.

**E1b. Order sensitivity (MEASURED).**
- **Data:**
  - A (64×K) and B (K×64), K ∈ {4096, 16384};
  - three distributions: Gaussian N(0,1); Student-t with ν = 3; activations with 1% outlier channels ×20;
  - a fixed seed per setting.
- **Quantisation** with the published NVFP4 recipe:
  - per-tensor scale s_t = amax / (6 · 448);
  - block scale = round-to-nearest-even to UE4M3 of (block amax / 6) / s_t;
  - elements = RNE to E2M1 of x / (s_b · s_t), saturating at ±6.
- **Orders (8):**
  - sequential over blocks;
  - split-K ∈ {2, 4, 8, 16, 32}, sequential inside each split, partials combined sequentially;
  - a pairwise tree;
  - one random permutation of the block order.
- **FP32 path.** numpy float32 (IEEE RNE) accumulation of the block contributions. Each is exactly representable in FP32 because |P| < 2^20. The per-tensor scale product is applied in FP32 at the end.
- **Exact path.** Python integer accumulation, one exact RNE rounding to FP32 at the end, then the scale.
- **Metrics:**
  - the fraction of outputs whose FP32 bits differ between at least two orders;
  - the max ULP spread;
  - the FP32-vs-exact relative error;
  - the same fraction for the exact path.
- **Problem-premise check (pre-registered).** If FP32 outputs are order-invariant for **> 99%** of outputs in **every** setting, the problem does not exist for NVFP4, and XACC's importance claim is killed.
- **Mechanism check.** Exact outputs must be identical across all orders, 100%.
- **Mutation control.** The same check must *fail* on an exact path whose accumulator wraps at W − 12 bits, on the heavy-tailed K = 16384 setting. This shows the check can detect an accumulator that is too narrow.

## XACC-E2 — physical cost at the PE level (decisive)

**Designs.** Verilog-2005, one parameterised source. All share the same NVFP4 block front end and pipeline boundaries, and all accept one 16-element block pair per cycle (16 MACs per cycle).
- **Stage 0:** input registers — a[63:0], b[63:0] (16 E2M1 each), sa[7:0], sb[7:0] (UE4M3; the NaN code 0x7F is excluded by assumption), clr.
- **Stage A1:**
  - 16 E2M1×E2M1 products, in quarter-units, and their adder tree → S (13-bit signed);
  - the scale significand product M_ab (8 bits) and the shift s = E'_a + E'_b − 2 ∈ [0, 28];
  - registered.
- **Stage A2:** P = S · M_ab (21-bit signed), then the variant's pre-loop step, registered:
  - EXACT: X = P << s (49 bits);
  - FP32 variants: exact int→FP32 conversion of P · 2^(s−20).
- **Stage B (the accumulation loop), one of:**
  - `EXACT`: acc60 ← (clr ? 0 : acc60) + X;
  - `FP32_RNE1`: acc32 ← fp32add_RNE(clr ? 0 : acc32, F), in one cycle;
  - `FP32_RZ1`: the same with truncation (RZ);
  - `FP32_RNE_I2`: a two-stage pipelined RNE adder (align+add | normalise+round) with two interleaved accumulators. Even and odd cycles belong to two different outputs; this is the throughput-optimal FP32 structure.
- **Readout** (EXACT only; a separate module, registered in and out): 60-bit two's complement → FP32 (RNE) of value · 2^-20.

**Functional validity.** Required for every design point used.
- **Path.** The post-route `6_final.v` goes through Yosys with the sky130 Liberty functions, to AIGER, and into our own simulator, independent of the RTL.
- **Vectors:**
  - at least 20,000 random block sequences of length 1–256 with random clr;
  - plus directed cases: maximum magnitudes, exact cancellation, and RNE ties for FP32.
- **Goldens:**
  - exact Python integers (EXACT);
  - exact-integer RNE / RZ FP32 models, the RNE model also cross-checked against numpy float32.
- **Mutation controls** (each must be *detected*, that is, it must fail):
  - a design mutant with the shift amount off by one;
  - the EXACT golden with a 59-bit wrap;
  - the FP32_RNE1 golden computed with RZ.

**Physical implementation (the research harness).**
- **Flow:** ORFS sky130hd, image `openroad/orfs:latest` (sha256:69df744e…), default flow, CORE_UTILIZATION 50%.
- **Clock targets:** T_clk ∈ {3.0, 5.0, 8.0} ns for every design; each design gets its best point.
- **Sign-off:** OpenRCX extraction of `6_final.odb`, then OpenSTA at tt / ss / ff with the pinned libraries. T_c = T_clk − WS_setup,c.
- **Area A:** the standard-cell area of `6_final.def` excluding fill and well taps, using the harness area table. It includes every buffer and resize the flow made.
- **Validity of a point:**
  - functionally valid;
  - 0 detailed-routing violations;
  - hold slack ≥ 0 at every corner.

  Invalid points are excluded. A design with no valid point makes the decision INCOMPLETE; it is fixed and rerun, not decided.

**Decisive metric.** A×T per block at the conservative corner, ss:

  A_EXACT,eff = A_EXACT + A_readout / N_share, with **N_share = 16** (decisive; 1 and 64 reported)

  **R_cost = min over T_clk of A×T_ss(EXACT_eff) / min over FP32 designs and T_clk of A×T_ss(FP32)**

**Decision:**
- **R_cost > 1.10:** **KILL** (exactness is not free at the PE level).
- **R_cost ≤ 1.10:** **PASS** (cost parity).
- **R_cost ≤ 0.90:** PASS **with structural headroom** (exact is cheaper by at least 10%).

**Reported, never decisive:**
- tt and ff ratios;
- the area-only ratio;
- the loop-stage critical path of every design;
- N_share = 1 and 64;
- the RZ-only comparison;
- the limiting path at ss for every design.

**Scope note, fixed now.** E2 measures PE-local accumulators, as in output-stationary arrays. The GPU tensor-memory capacity effect of 60-bit accumulators is *not* measured. Any PASS is stated with that limit.

## XACC-E3 (XABFT, merged as C2) — does exactness buy material detection?

- **Tile and data.** An NVFP4 GEMM tile, M = N = 32, K = 4096, with the three E1 distributions.
- **Exact path.**
  - Row checksum: Σ_j C_ij in exact integers, against the exact dot product of A's row with B's exact column sums.
  - Detection is inequality.
- **FP32 path.**
  - Standard ABFT: an appended checksum column, B_cs = Σ_j B_kj computed in float64 then used as an FP32 operand, pushed through the same FP32 accumulation.
  - Detection is |Σ_j C_ij − C_i,cs| > τ.
  - τ is the tightest threshold giving zero false positives over 10,000 fault-free rows (the maximum observed difference).
- **Faults.** 10,000 single-bit flips, each at a random output, block step and state bit (60 bits for exact, 32 for FP32).
- **Metrics:**
  - detection rates;
  - for FP32 misses, the output error relative to that output's FP32 accumulation error, measured against exact.
- **Decision.** **KILL C2** if every FP32-missed fault has an error ≤ 10× the FP32 accumulation error of its output (only noise-level faults escape). Otherwise C2 is **material**, and the distribution is reported.

## MR-SIGNOFF — metamorphic invariance of OpenRCX + OpenSTA

- **Designs:**
  - D1: the frozen UBP B60 base (`6_final.def`, on disk, regenerable);
  - D2: ORFS sky130hd `gcd`, built with ORFS defaults.
- **Per variant:**
  - LEF + DEF → OpenRCX (harness `extract.tcl`, DEF input) → SPEF;
  - OpenSTA at tt (harness `sta_corner.tcl`) with the design's SDC and the SPEF.
- **Relations:**
  - **MR0:** run twice on identical input. SPEF must be identical except for its header date.
  - **MR1:** DEF COMPONENTS and NETS sections permuted (seed 1).
  - **MR2:** a consistent bijective renaming of all nets and instances (ports kept).
  - **MR3:** a mirror about the vertical axis x' = x_min + x_max − x of every component and routing shape, with orientations N↔FN and S↔FS. Optional: done only if implementable within about an hour; otherwise reported as not done.
- **Violation.** Any net's total C or R differing by more than 1e-9 relative, or any worst slack differing by more than 1e-4 ns, after mapping names back.
- **Decision.**
  - **PASS** (the method finds something): at least one reproducible violation of MR1–MR3 not explained by a documented legitimate dependence.
  - **KILL:** every relation invariant on both designs.
- **If MR0 itself fails,** that is a finding (nondeterminism) and is reported first. The MR comparisons then use a tolerance of the MR0 spread.

## LIN-CEC screen (evidence for the proximity kill only; not a thesis test)

- **Pairs.** Parallel CRC-32 over D ∈ {64, 256, 1024} data bits, in flat-matrix form against LFSR-unrolled form, both through Yosys + ABC.
- **Check.** ABC `&cec` with a 60 s limit each.
- **Reported:** solved or unsolved, and time. The kill (occupied) stands either way.

## What happens after Part 2

- **B9:** prior-art prosecution of the surviving mechanism(s), in `05_PRIOR_ART_PROSECUTION.md`.
- **B10:** primary and reserve, in 06 / 07.
- If XACC-E2 kills XACC, no rescue: the answer may be **NO NEW THESIS READY**.
