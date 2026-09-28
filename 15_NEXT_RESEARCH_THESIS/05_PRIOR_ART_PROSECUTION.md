# 05 — Prior-art prosecution (phase B9)

**Scope.** B9 prosecutes a mechanism once it is precise. After B8, no candidate survived its own pre-registered test (04 Part 2). This document therefore prosecutes:
1. the **strongest near-miss**, XACC restated for the regime where the post-hoc diagnostic says its premise holds. It is prosecuted so the researcher knows what a revived study could still claim.
2. the two kills that turned on novelty rather than data: LIN-CEC and MR-SIGNOFF.

**Categories**, as the task defines them:
- **known ingredient** — the mechanism's parts are known, and the claim may still be new in how they are used;
- **equivalent mechanism** — the same mechanism already exists for the same purpose;
- **obvious composition** — known parts combined with a predictable result;
- **distinct contribution** — a new mechanism, or a non-obvious measured interaction the claim needs.

**Evidence access.** Search summaries [S] and GitHub [G] only; full texts are blocked in this environment (01). A category below is therefore a *provisional* classification. The specific full texts that could overturn it are named.

---

## 1. XACC (near-miss form): exact accumulation for NVFP4-class GEMMs in the high-dynamic-range regime

**The mechanism, stated precisely:**
- a 60-bit two's-complement accumulator (LSB 2^-20) per output;
- block contributions P · 2^s with |P| < 2^19 and s ∈ [0, 28], derived exactly from the NVFP4 encoding;
- FP32 per-tensor scales applied once at readout, then one RNE rounding.

The claimed effect: bitwise order-invariance, where FP32 accumulation is order-sensitive — a within-row block-scale span of 12 binades or more.

| Element | Closest prior art | Category |
|---|---|---|
| Exact fixed-point accumulation of floating-point products over a window | Kulisch long accumulator; FloPoCo FPGA long accumulator; posit quire; ExBLAS | **Known ingredient** |
| Exact accumulation in matrix units | "FP8 is All You Need" Part 2 (2606.23698) [S]: INT8 tensor core with 6×INT64 positional accumulation, proposed as minimal hardware for Ozaki-II FP64 emulation | Known ingredient in a *different* use (integer slices, FP64 accuracy, not determinism of FP4 GEMMs) |
| Integer accumulation inside a block-scaled dot product | HiFloat4 [S]: format redesign keeps a 64-element group integer, then FP. NVFP4 hardware keeps 16-element block sums integer, then FP32 [S] | Known ingredient. XACC extends exactness *across blocks* without changing the format |
| Determinism by fixing reduction order | Batch-invariant kernels (Thinking Machines) [S]; TBIK (2511.17826) [S]; fixed-configuration upcast GEMM (2609.25624) [S]; compiler enforcement and static verification (2609.11356) [S] | Different mechanism for the same goal (software, order-fixing rather than order-free) |
| Width bound from the scale format | The 60 / 92 / 533–561-bit table (04 E1a), from exhaustive enumeration | **Not found** in any summary or repository |
| FP32-accumulated NVFP4 is exact in benign regimes, with a sharp order-sensitivity transition at a span of about 11–13 binades | 04 post-hoc | **Not found**. Closest are generic statements that FP accumulation is order-dependent [S], and tensor-core accumulation models (2512.07004) [S] |
| Cost of exact vs FP32 accumulation at PE level | Qualcomm FP8 vs INT8 (2303.17951) [S] argues FP accumulators beat Kulisch for FP8-E4 (per product) | **Opposing prior claim, contradicted for the NVFP4 per-block case.** E2 measured A×T_ss 0.738× the strongest FP32 accumulator on SKY130 (04). The strongest *vendor* fused multi-term accumulator was not implemented |

**Classification: OBVIOUS COMPOSITION of known ingredients, unless the regime-plus-cost interaction is established.**
- A long accumulator for a narrow format is the textbook use of Kulisch accumulation. A reviewer would call "use a Kulisch accumulator for NVFP4" obvious.
- What would be distinct is the *measured interaction*: the phase transition, together with a real-model demonstration that NVFP4 GEMMs cross it, together with exact accumulation at ≤ FP32 cost.

  That is a non-obvious, quantitative statement no found source makes. It is the only route to "distinct contribution", and it is *unproven*: the transition is post hoc on synthetic outliers, The cost half is now measured at PE level (E2), but only against single-contribution FP32 adders.

**Full texts that could overturn the classification:**
- 2606.23698 and 2609.25624, for any exact-accumulation or determinism hardware discussion of FP4/FP8;
- the NVFP4 pretraining report (2509.25149) and HiFloat4, for accumulator internals;
- Khattak & Mikaitis (2512.07004), for whether current tensor cores already accumulate block contributions exactly (then the regime question is moot on NVIDIA hardware);
- UE5M3 (2609.02846), whose wider scale range pushes data *toward* the order-sensitive regime.

## 2. LIN-CEC

- **Mechanism:** GF(2)-affine cone detection plus n+1-simulation matrix comparison, inside CEC.
- **Prior art** [S]: Gaussian elimination over GF(2) in XOR-dense regions of circuit equivalence checking; CryptoMiniSat Gauss–Jordan; BDD parity; the DAC'26 best-paper line on restructuring for CEC.
- **Classification: EQUIVALENT MECHANISM** (occupied).
- **Measured (04):** ABC's `cec` and `&cec` fail on CRC-32 pairs where the known method takes 0.02–0.23 s. That is an **engineering** gap in the open tool. The research claim is occupied.

## 3. MR-SIGNOFF

- **Mechanism:** exact metamorphic invariances (order, naming) for extraction plus STA.
- **Prior art:** metamorphic testing (a general method, known ingredient); no EDA-sign-off application found [S].
- **Classification:** moot. The method found **no** violation on either design (04), so there is no claim to prosecute. The known-ingredient status means that even a positive result would have been "known method, new application", which leans engineering.

---

## Summary

| Candidate | Evaluator outcome | Prior-art category | Research thesis? |
|---|---|---|---|
| XACC (as registered) | KILLED (premise false on benign NVFP4 data) | — | No |
| XACC, high-dynamic-range regime (near-miss) | Not tested under pre-registration | Obvious composition unless the regime × cost interaction is established | **Not yet.** See 08 |
| XABFT | KILLED with XACC | Known ingredient (ABFT) | No |
| MR-SIGNOFF | KILLED (all invariant) | Known ingredient | No |
| LIN-CEC | Proximity kill, confirmed | Equivalent mechanism (occupied) | No (engineering gap) |
