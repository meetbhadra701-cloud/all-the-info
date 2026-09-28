# 01 — Frontier scan (literature phase 1, before any mechanism was fixed)

**Date:** 2026-09-28.

**Access constraint (read first).** From this environment only web-search result summaries and GitHub pages are reachable. arXiv, dblp, ACM DL, IEEE Xplore, Semantic Scholar, FMCAD and HWMCC pages are refused by the egress proxy; the HWMCC page was read through its GitHub raw source.

**Labels:**
- **[S]:** summary-level (a search-engine abstract; the paper was not read).
- **[G]:** read on GitHub (README, code or raw page).
- **[A]:** established in this archive by an earlier wave, with its own evidence.
- **[O]:** observed here by running a tool.

Decisive claims never rest on [S] alone.

The scan deliberately starts where the archive's earlier searches stopped.
- The 2026-09-23 investigation's register of about 45 probes found **no survivor** (`10_OPUS_5_5_INVESTIGATION_2026-09-23/INVESTIGATION_REPORT.md` §B–C).
- TRACE closed open arithmetic-LEC certification (`11_TRACE_YOSYS_FRONTIER_PROSECUTION/`).
- Waves 10–11 closed or parked mapping, elastic buffering and timing repair (`12_…/06_FINAL_DECISION.md`, `13_WAVE_11_…/04_HYPOTHESIS_EVOLUTION.md`).
- UBP is closed (`14_FABLE_5_1_SCIENTIFIC_DISCOVERY/22_UBP_PROJECT_CLOSEOUT.md`).

These are not re-searched here. They are the exclusion set, together with `05_KILLED_CANDIDATES/RESEARCH_KILL_DATABASE.md` and the rediscovery warnings in `00_START_HERE/MASTER_RESEARCH_HANDOFF.md` §9.

---

## 1. Where the frontier is in September 2026, by community

### 1.1 Equivalence checking and logic verification

- **DAC 2026 best paper.** "Miter-Aware LUT Mapping: Aligning Structure and Solvability for Efficient Logic Equivalence Checking" (Zhu, Shi, Tao, Li, Li, Xu; CUHK; arXiv 2607.07164) [S].
  - General CEC is still an award-level problem.
  - The winning method composes known techniques (LUT mapping, SAT sweeping) with strong evidence.
- **XOR-dense regions.** Gaussian elimination over GF(2) inside XOR-dense regions is already used in circuit equivalence checking, and CryptoMiniSat's Gauss–Jordan solves XOR-intensive instances in seconds [S].
- **Arithmetic.** TRACE (arXiv 2608.16458) and the Bremen MAC/dot-product line occupy arithmetic certification [A: 11_TRACE].
- **Open flow.** ORFS now runs LEC and SEC through kepler-formal, including a PDR engine for SEC (ORFS PRs #4224 "global LEC check", #4329 "Global SEC check", #4538) [S, GitHub PR titles].

### 1.2 Hardware model checking

- **HWMCC'25 bit-level track** [G: raw page]:
  - rIC3 solved 274 (99 sat / 175 unsat), with all 274 certified;
  - super-prove 255, supercar 255, aic3 250, avy 245.
  - Per the search summary, 46 instances were solved by no entrant [S].
- **2026 entries.** LLM-guided invariant or heuristic evolution: CIll (2602.23389), IC3-Evolve (2604.03232), A-IC3 (2604.21688) [S].
- **Certification.** Certificates are part of the competition (Froleyks et al., CAV'25) [S].
- **Reading.** A crowded race against a strong, open, certified baseline, with no structural lever visible from here.

### 1.3 RTL optimisation, agentic EDA, ML-for-EDA

- **Collision set** [A: `01_RESEARCH_OBJECTIVES_AND_STRATEGY/PPA_DELTA/Existing-Research-Audit.md`]:
  - ROVER (TCAD'24), SymRTLO, ASPEN (MLCAD'25);
  - Dr. RTL (2604.14989), with sequential equivalence via Jasper and learned strategies;
  - RTLScout (2606.06530), on Yosys/OpenROAD.
- **ICCAD'26 examples** [S]: CorrectRTL, E-Layout (RL-optimised equality-saturated graph RAG). The field has moved to agentic flows.
- **Agentic physical design** [S]: AgenticPD (2607.04758), CLOSER-Bench (2607.16632), PDAgent-Bench.
- **Physically aware synthesis** [S]: 2408.07886; LevelSyn (2609.03594).
- **Reading.** Crowded; the remaining open items in the archive are engineering.

### 1.4 Numerical determinism of AI arithmetic (the fastest-moving area found)

- **Problem statement.** Thinking Machines, "Defeating Nondeterminism in LLM Inference" (2025) [S].
  - GEMM, attention and norm kernels change reduction order with batch size (split-K, split-KV).
  - Batch-invariant kernels fix the order, at roughly 20% throughput initially.
- **Training–inference mismatch in RL post-training:**
  - "Defeating the Training-Inference Mismatch via FP16" (2510.26788) [S];
  - "Deterministic Inference across Tensor Parallel Sizes…" (TBIK, 2511.17826; a fixed binary-tree order shared by local GEMM and collectives) [S];
  - "Diagnosing Training Inference Mismatch in LLM RL" (2605.14220; DeepSeek-V4 uses dual-kernel strategies to pay for batch invariance) [S];
  - "Accelerating the Mitigation of LLM Inference Nondeterminism Across GPU Architectures" (2609.25624; fixed-configuration fused-upcast GEMMs with an order that is a function of shape) [S].
- **Verification and characterisation:**
  - "Bit-Exact AI Inference Verification Without Performance Tradeoffs" (2606.00279), LLM-42 (2601.17768), Hawkeye (2603.20421) [S];
  - "Taming Bitwise Behavior in GPU Kernels with Tensor Core: black-box reconstruction, compiler enforcement, static verification" (2609.11356) [S];
  - Khattak & Mikaitis, "Accurate Models of NVIDIA Tensor Cores" (TACO; 2512.07004): tensor-core products are aligned with a fixed number of extra bits, the accumulation is not IEEE and differs across vendors and generations, and B200 matches H100 for 16/19-bit inputs [S];
  - "Accurate Models of AMD Matrix Cores" (2609.14845) [S].
- **Reading.** The *problem* is recognised and hot in 2026. Every published *fix* found is software: fixed order, fixed configuration, trees, or verification. Hardware appears only as a thing to characterise.

### 1.5 Block-scaled low-precision formats and their dot-product hardware

- **NVFP4:**
  - E2M1 elements;
  - one UE4M3 scale per 16 elements, plus an FP32 per-tensor scale;
  - accumulation in FP32 ("Pretraining LLMs with NVFP4", 2509.25149) [S].
- **HiFloat4 (Huawei; 2602.11287, 2604.08826)** [S]. Per its analysis:
  - NVFP4 hardware keeps integer arithmetic only up to four S10P2 block sums per 64 products;
  - it then needs four small FP multiplies, four large integer multiplies and FP accumulation.
  - HiF4's hierarchical scales keep a 64-element group in integers, then need one FP multiply.
- **UE5M3 scales (Graphcore, ICML'26, 2609.02846)** [S]. Minimum scale 2^-17 instead of 2^-9, for pretraining stability.
- **Other format work** [S]: MixFP4 (2605.31035); adaptive block-scaled types (2603.28765); Four Over Six (2512.02010).
- **MX hardware** [S]: MXDOTP (2505.13159; RISC-V MXFP8 dot product, E8M0 scales); "Jack of All Scales" FPGA tensor block (2607.13898).
- **Kulisch / exact accumulation:**
  - Qualcomm "FP8 versus INT8" (2303.17951) [S]: Kulisch accumulators are exact and efficient for INT8, while FP8-E4 is argued to favour FP accumulators; FP8-E4 with FP32 accumulation is 183% less efficient than INT8.
  - FloPoCo long accumulators (FPGA; de Dinechin et al.) [A: known principle].
  - "Reproducible and Accurate Matrix Multiplication for GPU Accelerators" (ExBLAS line) [S].
  - "FP8 is All You Need" Parts 1–2 (2606.06510, 2606.23698) [S]: FP64 emulation (Ozaki-II) needs exact integer (Kulisch-style) accumulation. The binding cost is an integer epilogue, and hardware options are proposed ("INT8-TC restore with positional 6×INT64 accumulation", modular reduction at MMA output).
- **Hobby-scale exact accumulation.** `sashakatne/nvfp4-dotprod-formal-dv` [G] is an 8-lane INT8/BF16/NVFP4 dot-product core.
  - BF16 lanes use exact fixed-point accumulation in a bounded exponent window [119,134]; operands outside it are flagged QNaN.
  - It is formally verified (VC Formal) against a golden model.
  - It makes no cost, determinism-at-system-level or format claim.
- **Reading.** Exact accumulation is a *known ingredient*, and 2026 hardware proposals use it for FP64 emulation.

  **No source found** — which is not evidence of absence, since full texts are blocked — quantifies:
  - whether exact accumulation of *two-level-scaled 4-bit formats* is cheaper than their FP32 accumulation at the physical level;
  - how the *scale format* (UE4M3, UE5M3, E8M0) sets the exact-accumulator width.

### 1.6 Silent data corruption (SDC) and ABFT

- **Production evidence.** "Understanding Silent Data Corruption in LLM Training" (2502.12340) [S], plus an OCP white paper on SDC in AI.
- **Low-precision ABFT:**
  - ABFT bounds come from FP32-or-higher error analysis;
  - low-precision datatypes need new analysis, and thresholds trade misses against false positives [S].
- **2026 work** [S]:
  - FP-Sketch (2609.19758), post-hoc fault localisation for half-precision GEMM, with no false positives by construction;
  - syndrome decoding for SDC in quantized **integer** GPU GEMMs (2609.19743).
- **Systolic-array detection** [S]: SCISSORS (TCAD'25); a reliable BFP NPU (2604.10494).
- **Reading.** Exact integer ABFT is known for INT GEMMs. FP-ABFT needs tolerances, and post-hoc sketches avoid false positives in software.

### 1.7 Physical design and sign-off tools (open flow)

- **OpenRCX** is the ORFS extractor [G/S]. An alternative calibrated sky130 extractor exists (`vyges-tools/extract`, "tracks OpenRCX") [S].
- **Metamorphic testing.** Search found metamorphic testing of other tool classes (for example, 19 real bugs in 7 of 15 variability-analysis tools) but **none for placement, extraction or STA** [S]. This is absence in summaries only.
- **Glitch power.** An average of 26% of dynamic power; the techniques are decades old; 2026 work is GPU/heterogeneous gate-level power analysis (2609.05960) [S].

### 1.8 Other areas scanned and set aside at screening

| Area | Evidence | Why not pursued |
|---|---|---|
| Memory reliability (ECC) | ISCA'26 best paper "Cerberus: Cross-Layer ECC Co-Design" [S] | Crowded, strong groups |
| Reset/clock domain crossing | Siemens/DVCon methodology papers [S] | Industrial methodology; no scientific boundary found |
| FPGA toolchain end-to-end verification | Bitstream equivalence exists (avionics); open flows with fasm2bels / icebox_vlog [S] | Engineering |
| Functional safety of NPUs | Selective TMR, ECC, activation-range supervision [S] | Folded into XABFT (02) |
| Wave 11 H1.6 (exact near-tie re-covering in mapping) | Pre-registered, with a partial experiment log in `13_WAVE_11_…/experiments/` [A] | Not new. It belongs to Wave 11 and is not re-prosecuted here (that folder is left untouched) |
| Deterministic in-network (switch) reduction | Derived here | Exact tensor-parallel all-reduce would move 64-bit partial sums instead of 16-bit ones (4× traffic); software TBIK is cheaper |
| Exact / deterministic attention | Derived here | exp is transcendental: exactness needs a global max pass. A kernel question, not a hardware one |

## 2. What the scan implies for candidate generation

1. **The one new cost regime with a hardware-shaped cause** is bitwise determinism of low-precision GEMMs (§1.4).
   - Its root cause is arithmetic: floating-point accumulation is not associative.
   - Every 2026 fix pays in software: fixed orders cost throughput, and upcasting costs bandwidth.
   - The block-scaled formats that are becoming standard (§1.5) have *bounded* per-block exponent ranges.

   The combination suggests a mechanism: **exact accumulation, which is associative by construction, made cheap by the bounded scale range**. That is candidates XACC and XABFT in 02.
2. **EDA correctness** has a gap in *oracle-free* testing of deterministic sign-off tools (§1.7). That is candidate MR-SIGNOFF.
3. **Equivalence checking of XOR-dominated logic** looks like a gap from the tool side, but the method is occupied (§1.1). That is candidate LIN-CEC, kept to document the kill.
4. Everything else hit an occupied frontier or reduced to engineering, consistent with the 2026-09-23 register.
