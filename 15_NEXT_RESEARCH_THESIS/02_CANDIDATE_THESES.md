# 02 — Candidate theses (phase B5)

Four candidates. The scan (01) found no others that survived screening; the set-aside areas are listed in 01 §1.8. Each candidate carries the full tuple:
- **P:** the problem;
- **L:** the limitation of current practice;
- **M:** the mechanism;
- **causal reason;**
- **B:** the strongest baseline;
- **E:** the evaluator;
- **F:** the cheap falsifier;
- **C:** the claim.

**Label convention for numbers below:**
- **DERIVED:** exact arithmetic. It is re-checked by enumeration in the XACC evaluator (04); nothing is measured yet.
- **[S]:** a literature summary (see 01).

None of the four is a programmable inference fabric. XACC and XABFT are arithmetic and reliability mechanisms for matrix units in general, used in training and inference alike.

---

## Candidate 1 — XACC: exact, order-free accumulation for bounded-scale block formats

**Problem (P).** Low-precision GEMMs are not bitwise reproducible. The same product computed with a different batch size, split-K factor, tile shape, tensor-parallel degree or GPU generation returns different bits.
- In RL post-training, the inference engine (rollouts) and the training engine then disagree on log-probabilities. That training–inference mismatch is documented to degrade or collapse training [S: 2510.26788, 2511.17826, 2605.14220].
- Serving is irreproducible across batch compositions.
- Bit-exact audit of inference is impossible without replaying the exact kernel configuration [S: 2606.00279, 2609.11356].

**Current strongest approach and limitation (L).** Every fix found is software, and each pays:
- batch-invariant kernels fix the reduction order (about 20% throughput at first, per the Thinking Machines report [S]);
- tree-based invariant kernels impose one binary-tree order on GEMM and collectives [S: 2511.17826];
- fixed-configuration upcast GEMMs [S: 2609.25624];
- DeepSeek-V4 runs dual kernels to recover the performance [S: 2605.14220].

The hardware accumulates in FP32, which is not associative. NVFP4's specified datapath accumulates block results in FP32 [S: 2509.25149]; tensor-core accumulation differs across vendors and generations [S: 2512.07004, 2609.14845].

**Mechanism (M).** For block-scaled formats whose block scales have a *bounded* exponent range (NVFP4: E2M1 elements, one UE4M3 scale per 16 elements, an FP32 per-tensor scale):
1. Keep the 16-element block sum exact. This is what the hardware already does [S: HiF4 analysis]: S = Σ q_a q_b with q ∈ {0, ±1, …, ±12} in half-units, so |S| ≤ 2,304 in quarter-units.
2. Form the block contribution exactly as an integer P = S · M_a M_b with an exponent t = E_a + E_b − 22 ∈ [−20, 8], where M ≤ 15 and E ∈ [1, 15] are the scale's significand and biased exponent (DERIVED).
3. Add P · 2^(t+20) into a **fixed-point accumulator of W = 60 bits** for K ≤ 65,536 (DERIVED: the 49-bit shifted contribution plus 11 guard bits).
4. Apply the two FP32 per-tensor scales and round **once**, at readout.

There is no normalisation and no rounding in the accumulation loop. The loop is one 60-bit addition; the shift is outside the loop.

**Causal reason.**
- Integer addition is associative and exact, so any reduction order, split or tiling yields identical bits. Determinism follows by construction, not by scheduling.
- The bounded scale exponent (UE4M3 covers 2^-9…448) bounds the window at about 60 bits.
- A wide add happens once per 16 MACs, and the FP32 alternative also does one FP32 add per block, with alignment, normalisation and rounding.

The expected cost is therefore at or below FP32 accumulation.

**The scale format decides feasibility (DERIVED, to be enumerated in E1):**
- UE5M3 scales (2^-17…) widen the window by 32 bits, to about 92 bits;
- MX formats with E8M0 scales (2^±127) need about 530–570 bits: exactness is not cheap there;
- BF16 needs about 550 bits.

So the thesis is format-specific, and it says which formats admit free determinism.

**Structural headroom.**
- Determinism is categorical, all or nothing.
- The cost side is predicted *below* parity: the loop drops normalise/round, and FP32's own 1-cycle loop is longer.
- The one real cost is accumulator state, 60 bits against 32. It is judged against the strongest FP32 design, which must interleave two accumulators (64 bits of state) to reach a comparable clock.

**Strongest baseline (B):**
- the same NVFP4 PE accumulating in **IEEE FP32 (RNE)**, the specified behaviour;
- an **RZ (truncating) FP32** accumulator, cheaper and closer to observed tensor cores;
- a **2-stage pipelined FP32 accumulator with two interleaved accumulators**, the throughput-optimal FP32 design.

At system level the baseline is software batch invariance. For the exactness principle it is Kulisch / FloPoCo long accumulators, a known ingredient.

**Evaluator (E):**
- **E1 (DERIVED + MEASURED numerics):**
  - enumerate every E2M1 product and every scale pair to verify the width bound, and derive W for NVFP4-UE4M3, NVFP4-UE5M3, MXFP4, MXFP8, FP8 per-tensor, FP16 and BF16;
  - on realistic quantised data, compare bitwise outputs across at least six reduction orders (sequential, split-K 2–32, random block permutation, tree), exact vs FP32.
- **E2 (MEASURED physical):**
  - SKY130 PEs (common NVFP4 block front end + each accumulator) through ORFS with extracted three-corner sign-off (the research harness);
  - A×T per block at the best of three clock targets;
  - final netlists functionally equal to exact / IEEE goldens, with mutation controls.

**Cheap falsifier (F), a few hours:**
- the ratio A×T_ss(exact, readout converter amortised) / min over FP32 baselines of A×T_ss is above **1.10**;
- or the width bound fails;
- or realistic FP32-accumulated outputs are already order-invariant in more than 99% of cases (no problem to solve).

**Claim (C).** For two-level-scaled 4-bit formats (NVFP4-class), exact, order-free accumulation costs no more than FP32 accumulation at the conservative corner, so bitwise determinism across any reduction order is available in hardware for free. For E8M0-scaled (MX) formats it is not.

**Strongest prior-art threat:**
- Kulisch and long accumulators (the known principle);
- HiFloat4's integer group accumulation;
- the Ozaki / "FP8 is All You Need" hardware proposals, which use exact INT64 positional accumulation for FP64 emulation;
- the undocumented internals of NVIDIA's NVFP4 accumulator.

**Artifacts.** SKY130, ORFS, Yosys and the research harness are all open. The E1 data is synthetic but quantised with the published NVFP4 recipe.

**If it fails:**
- above 1.10: exactness is not free at the PE level, and the determinism case goes back to software;
- width bound fails: the mechanism is wrong;
- no order sensitivity: the problem does not exist for this format.

---

## Candidate 2 — XABFT: threshold-free SDC detection for low-precision GEMM hardware

**Problem (P).** Silent data corruption from marginal or defective units is a production problem in large-scale training [S: 2502.12340; OCP white paper]. ABFT is the low-overhead detector for GEMMs.

**Current approach and limitation (L).**
- FP ABFT compares checksums with a tolerance, because rounding makes the checksum identity inexact.
- The tolerance trades false positives against missed errors, and low-precision error analysis for it is open [S].
- Exact ABFT exists only for integer GEMMs [S: 2609.19743].
- FP-Sketch avoids false positives post hoc in software [S: 2609.19758].

**Mechanism (M).** With XACC's exact accumulators, the checksum identity holds exactly for block-scaled float GEMMs:

  Σ_j C_ij = Σ_k A_ik · (Σ_j B_kj), all in exact fixed point before readout rounding.

The column sums of B are wider than NVFP4, so they need one wider checksum lane per tile. Detection is then equality, not tolerance: every single-bit fault in the accumulation path that changes an output is detected, with zero false positives.

**Causal reason.** Exact arithmetic removes the noise floor that forces a tolerance.

**Strongest baseline (B):**
- FP-ABFT with the tightest zero-false-positive threshold;
- FP-Sketch (software);
- dual modular redundancy / lockstep (≈100% overhead).

**Evaluator (E).** A model-level NVFP4 GEMM tile, injecting single-bit flips into accumulator state:
- the detection rate and false positives of exact equality against threshold FP-ABFT;
- the size of the errors the threshold scheme misses, relative to the FP32 accumulation error itself.

**Cheap falsifier (F).** If every fault the zero-false-positive FP threshold misses has an output error within 10× the FP32 accumulation error bound (that is, only noise-level faults escape), exactness buys nothing material. XABFT is then killed.

**Claim (C).** Exact accumulation turns GEMM ABFT for float block formats from a tolerance test into an equality test, catching faults that tolerance-based ABFT must let through.

**Structural headroom.** Detection is categorical. But the value depends on whether small missed faults matter, and that is the weakest assumption.

**Strongest prior-art threat.**
- ABFT itself (Huang & Abraham 1984);
- exact integer ABFT;
- FP-Sketch;
- Freivalds-style exact verification.

**Dependency.** XABFT *requires* XACC's mechanism. It cannot survive if XACC is killed on cost, unless its detection value alone justifies the cost.

**Artifacts.** Python model-level simulation.

**If it fails.** Exactness is a determinism mechanism only; its detection benefit is immaterial.

---

## Candidate 3 — MR-SIGNOFF: oracle-free metamorphic validation of the open sign-off stack

**Problem (P).** Chips from open flows (Tiny Tapeout, ChipIgnite, wafer.space, IHP MPWs) are signed off with OpenRCX extraction and OpenSTA timing.
- These tools have no independent oracle: commercial extractors and silicon correlation data are unavailable to the community (the archive's C-2 "open-flow signoff vs silicon" was hardware-gated).
- A silent defect in extraction or timing is a silent tape-out risk.

**Current approach and limitation (L).**
- Tool unit and regression tests; rule calibration against a field solver when an extraction deck is made; user bug reports.
- Differential testing needs an independent second implementation. The one found tracks OpenRCX [S: vyges extract].

**Mechanism (M).** Metamorphic relations with **exact** expected invariance, because extraction and STA are deterministic functions of geometry and netlist semantics:
- **MR0:** run-to-run determinism;
- **MR1:** permuting the order of DEF COMPONENTS and NETS;
- **MR2:** consistently renaming nets and instances;
- **MR3:** mirroring the routed layout about a vertical axis (physics and rules are mirror-symmetric);
- **MR4:** splitting a routed segment at an interior point.

Any difference in per-net SPEF R/C, worst slacks or path delays beyond zero is a defect or an undocumented dependence.

**Causal reason.** Names and file order carry no physical meaning, and mirror symmetry holds for the physics.

**Strongest baseline (B):**
- the tools' own regression suites;
- run-to-run comparison;
- differential testing against a second extractor, where one exists.

**Evaluator (E).** Apply MR0–MR3 to two routed designs (the frozen UBP B60 base and one ORFS reference design), through the harness's `extract.tcl` + `sta_corner.tcl`, comparing SPEF per net and STA results.

**Cheap falsifier (F).** Every MR exactly invariant on both designs means no evidence that the method finds anything: killed.

**Claim (C).** Exact metamorphic invariances expose defects in the open sign-off stack that its tests miss.

**Structural headroom.** Oracle-free and categorical: one reproducible violation is a finding. The research value is methodological. Individual defects are engineering (kill-database warning: "a real defect is not a research contribution by itself").

**Strongest prior-art threat.**
- Metamorphic testing as a method (compilers, SMT, databases);
- equivalence-based fuzzing of synthesis (Verismith);
- possibly unpublished tool QA.

**Artifacts.** Open; the designs and tools are on disk.

**If it fails.** No violations: the open sign-off tools are invariant under these relations, which is a positive fact about the tools and not a thesis.

---

## Candidate 4 — LIN-CEC: linear-algebraic equivalence checking for XOR-dominated logic

**Problem (P).** Combinational equivalence of XOR-dominated logic (CRC, ECC encoders/decoders, crypto linear layers) after restructuring is hard for CDCL-based SAT sweeping: parity reasoning is exponential for resolution.

**Limitation (L).** When synthesis refactors XOR trees, SAT sweeping finds few internal equivalences.

**Mechanism (M).**
- Identify GF(2)-affine cones (structural XOR extraction plus a simulation linearity test).
- Compare their matrices by n+1 simulations and Gaussian elimination.
- Sweep the remainder.

**Causal reason.** Linear maps are fixed by their values on a basis; Gaussian elimination is polynomial.

**Strongest baseline (B):**
- ABC `&cec` / `cec`;
- BDD-based CEC (parity has linear-size BDDs);
- CryptoMiniSat Gauss–Jordan;
- the DAC'26 miter-aware mapping.

**Evaluator (E).** CRC and SECDED encoder pairs with two XOR factorisations, at increasing widths, under ABC.

**Cheap falsifier (F).** ABC proves the pairs quickly, or the method is already published.

**Claim (C).** Linear-algebraic cone matching closes a class ABC cannot.

**Strongest prior-art threat.** Gaussian elimination inside XOR-dense regions of circuit equivalence checking is already reported [S: 01 §1.1], and BDDs handle parity trivially.

**Structural headroom.** Exponential versus polynomial on the class, *if* the class is hard for the baseline.

**Artifacts.** Open.

**If it fails.** Either there is no gap in practice, or the gap is occupied.
