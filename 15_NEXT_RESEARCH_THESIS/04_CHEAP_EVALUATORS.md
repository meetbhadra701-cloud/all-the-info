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

---

# Part 2 — Results (appended after the evaluators ran; Part 1 above is unchanged)

The pre-registration is commit `967661a`, pushed before any evaluator ran. Every number below comes from `experiments/*/results/`.

## XACC-E1a — width bound: prediction confirmed (DERIVED, enumerated)

`experiments/xacc/formats.py` → `results/e1a_widths.{md,json}`. Every element product and every scale pair was enumerated for the block formats. The closed form used for FP16/BF16 is checked against full enumeration for E2M1, E4M3 and E5M2.

| Format | W(K=4096) | W(16384) | W(65536) | Exponent span |
|---|---|---|---|---|
| **NVFP4 (E2M1, 16, UE4M3)** | 56 | 58 | **60** (predicted 60) | 28 |
| NVFP4 with UE5M3 scales | 88 | 90 | 92 | 60 |
| MXFP4 (E2M1, 32, E8M0) | 529 | 531 | 533 | 508 |
| MXFP8 (E4M3, 32, E8M0) | 557 | 559 | 561 | 508 |
| FP8-E4M3, per-tensor scale | 49 | 51 | 53 | 28 |
| FP8-E5M2, per-tensor scale | 77 | 79 | 81 | 58 |
| FP16 | 93 | 95 | 97 | 58 |
| BF16 | 535 | 537 | 539 | 506 |

The NVFP4 hardware encoding was checked exhaustively:
- |S| ≤ 2,304 (13-bit signed);
- |P| ≤ 518,400 (20-bit signed);
- shift s ∈ [0, 28];
- the shifted contribution fits 48-bit signed.

## XACC-E1b — order sensitivity: **the problem-premise kill condition is met**

`experiments/xacc/order_invariance.py` → `results/e1b_order_invariance.{md,json}`. The table covers 64×64 outputs, 8 reduction orders and the NVFP4 recipe, with FP32 IEEE (RNE) accumulation of block contributions.

| Data | K | FP32: outputs order-sensitive | FP32 max ULP spread | FP32 rel. error vs exact (median) | Exact: order-sensitive | Exact = independent element-level integer GEMM |
|---|---|---|---|---|---|---|
| Gaussian | 4096 | 0.0% | 0 | 2.1e-8 | 0.0% | yes |
| Student-t, ν=3 | 4096 | 0.0% | 0 | 2.1e-8 | 0.0% | yes |
| 1% outlier channels ×20 | 4096 | 0.0% | 0 | 2.1e-8 | 0.0% | yes |
| Gaussian | 16384 | 0.0% | 0 | 2.1e-8 | 0.0% | yes |
| Student-t, ν=3 | 16384 | 0.0% | 0 | 2.0e-8 | 0.0% | yes |
| 1% outlier channels ×20 | 16384 | **0.1%** | 1 | 2.1e-8 | 0.0% | yes |

**Decision (pre-registered).** FP32-accumulated outputs are order-invariant for at least 99.9% of outputs in every setting, more than the 99% the kill rule names. **XACC's importance claim is KILLED for NVFP4 on the pre-registered data regimes.**

The FP32 relative error equals the final rounding alone. IEEE FP32 accumulation of NVFP4 block contributions is effectively *exact* on these data, so there is nothing for an exact accumulator to fix.

The mechanism check passed: the exact path is 100% order-invariant, and its sums equal an independent element-level integer GEMM (no blocks, no shifts).

**Deviation D1 (mutation control).** The pre-registered control was "an accumulator wrapping at W − 12 bits must fail on the heavy-tailed K = 16384 setting". It was **not triggered there**: realistic sums reached only 40 bits there, below the 46-bit wrap. It was triggered on the Gaussian settings, where sums reached 48 bits, above the 44/46-bit wraps.

The control therefore demonstrated that the check can fail, but not on the setting named. The design error: the wrap width was set relative to the worst-case window W, not to realistic sum magnitudes. It changes no decision: the kill rests on the FP32 path, not the exact path.

## Post hoc (not pre-registered, not decisive): why the premise failed, and where it would hold

`experiments/xacc/posthoc_dynamic_range.py` → `results/posthoc_dynamic_range.json`. Gaussian data with a fraction of K-channels scaled by an outlier factor; FP32 accumulation over the same 8 orders.

| Outliers (factor, fraction) | K | Within-row shift span (median / max) | FP32 outputs order-sensitive | Max ULP spread | Sequential partial sums inexact |
|---|---|---|---|---|---|
| none | 16384 | 4 / 5 | 0.0% | 0 | 0.0% |
| ×20, 1% | 16384 | 7 / 9 | 0.05% | 1 | 0.01% |
| ×100, 0.1% | 16384 | 9 / 11 | 1.0% | 2 | 0.1% |
| **×1000, 0.1%** | 16384 | 12 / 14 | **97.5%** | 7,168 | 43% |
| ×10000, 0.05% | 16384 | 15 / 17 | 100% | 14,592 | 79% |
| none | 65536 | 4 / 5 | 0.07% | 1 | 0.01% |
| ×20, 1% | 65536 | 8 / 9 | 11.4% | 24 | 2.2% |
| ×100, 0.1% | 65536 | 9 / 11 | 27.5% | 1,024 | 5.8% |
| ×1000, 0.1% | 65536 | 13 / 14 | 100% | 9,344 | 79% |

**Diagnosis.**
- A block contribution has at most about 20 significant bits (|P| < 2^19). FP32 partial sums stay exact while the contribution span plus the sum's growth fits the 24-bit significand.
- The span is set by the within-row spread of block-scale exponents. Benign data keep it at about 4–9 binades, so FP32 is exact and hence order-free.
- There is a **sharp phase transition** at a span of about 11–13 binades (outliers of about 100–1000×). Beyond it FP32 accumulation is order-sensitive in essentially every output.
- Longer K moves the transition earlier.

**Consequence.** XACC's premise is *regime-dependent*.
- It is **false** for benign NVFP4 data (the pre-registered regimes).
- It is plausibly **true** for LLM activations with "massive activations" of 1000×+ in a few hidden dimensions, but *not* if an outlier-flattening rotation (a random Hadamard transform, as in NVFP4 training and inference recipes) is applied first.

The pre-registered test did not include that regime, so this does **not** reverse the kill. Reviving XACC requires a new, separately pre-registered study whose regime is justified from measured real-model activation statistics (08). This is recorded as the strongest near-miss, not as a result.

## XACC-E3 (XABFT, merged as C2) — **not run** (deviation D2)

XABFT's value was premised on FP32 ABFT needing tolerances because FP32 accumulation is inexact. E1b shows FP32 accumulation of NVFP4 is effectively exact in the pre-registered regimes.
- Tolerance-free checking is then already available for FP32-accumulated NVFP4 outputs whenever no rounding occurred.
- E3's pre-registered yardstick (the missed-fault error vs "the FP32 accumulation error of that output", which is ≈ 0 here) degenerates. Every miss would count as "material" by construction.

Running E3 would therefore be ritual, not evidence. XABFT inherits XACC's premise failure and is **KILLED with it**. This is logged as a deviation from the plan to run three evaluators.

## MR-SIGNOFF — **KILLED** (every relation exactly invariant on both designs)

`experiments/mr_signoff/mr_signoff.py` → `results/d1.json`, `results/d2.json`. OpenRCX extraction plus OpenSTA at tt, through the harness templates.

| Design | Nets | MR0 (rerun) | MR1 (permuted COMPONENTS/NETS) | MR2 (all nets and instances renamed) | Setup / hold WS (all variants) |
|---|---|---|---|---|---|
| D1: UBP W2 B60 base (39,890 components) | 13,126 | 0 nets differ | 0 nets differ | 0 nets differ | 0.8697 / 0.2189 ns, identical |
| D2: ORFS gcd | 506 | 0 | 0 | 0 | −1.4761 / 0.5327 ns, identical |

Per net, total C, coupling C and total R agreed exactly; the maximum relative difference was 0.0.
- MR3 (mirror) was optional and **not done**. Mirroring a routed DEF leaves the tech-LEF via definitions unmirrored, so any difference would be confounded, not a clean test.

**Decision (pre-registered): KILL.** The oracle-free relations found nothing: the open extraction plus timing stack is exactly invariant to order and naming. That is a positive fact about the tools, not a thesis.

## LIN-CEC screen (evidence for the proximity kill)

`experiments/lincec/crc_screen.py` → `results.json`; `linear_check.json`.

| CRC-32, data bits | Inputs | ABC `cec` | ABC `&cec` | Random simulation (4,096 vectors) | GF(2) matrices from n+1 simulations |
|---|---|---|---|---|---|
| 64 | 96 | > 70 s (hard timeout) | > 70 s | equal | **equal, 0.05 s** |
| 256 | 288 | > 70 s | > 70 s | equal | **equal, 0.02 s** |
| 1024 | 1,056 | > 70 s | > 70 s | equal | **equal, 0.23 s** |

The open tool's gap on XOR-dominated miters is **real and categorical**: at least 300–3,000× on circuits as common as CRC-32.
- ABC's classic `cec` also ignored its own `-T 60` limit; the first run hung more than 400 s until the container was killed.
- The closing technique (GF(2) linear algebra for XOR-dense regions, BDDs, Gauss–Jordan SAT) is published (01 §1.1).

**Classification: ENGINEERING** (a known principle to be integrated into an open tool). LIN-CEC stays killed as a research thesis.
