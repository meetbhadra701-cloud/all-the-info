# 06 — Primary thesis: **none selected**

No candidate survived its pre-registered test (04 Part 2), so B10 selects no primary. Per the task (B11), the honest outcome is **NO NEW THESIS READY**.

This document records the **strongest near-miss**, stated in the required final form, so it can be reviewed and, if the researcher chooses, re-registered as a new study (08). It is *not* a selected thesis. Its regime Z comes from a post-hoc diagnostic, and presenting it as a result would be exactly the rescue the rules forbid.

---

## Strongest near-miss: XACC-HDR — exact accumulation for NVFP4-class GEMMs in the high-dynamic-range regime

**Final form (the eight elements):**

> **(X)** Existing IEEE-FP32 accumulation of block-scaled 4-bit (NVFP4) GEMM partial results, made deterministic in software by fixing the reduction order (batch-invariant or tree-invariant kernels),
> **(Y)** returns bits that depend on the reduction order (split-K, tiling, tensor-parallel degree). The software fix constrains kernel choice and costs throughput,
> **(Z)** in the high-dynamic-range regime: a within-row block-scale exponent span of about 12 binades or more (activation outliers ≳ 1000×, as reported for LLM "massive activations" without an outlier-flattening rotation), where FP32 accumulation is order-sensitive in about 100% of outputs.
> We hypothesise that **(M)** a 60-bit fixed-point exact accumulator of NVFP4 block contributions P · 2^s (|P| < 2^19, s ∈ [0, 28]), with the FP32 tensor scales applied once and a single RNE readout rounding, addresses Y,
> because **(P)** integer addition is associative. The UE4M3 scale range bounds the exact window at 60 bits for K ≤ 65,536, and exactness removes normalisation and rounding from the accumulation loop.
> M differs from the strongest prior approach, **(Q)** fixed-order software determinism plus FP32 accumulators (with Kulisch long accumulators as the known exactness principle),
> by **(R)** order-freedom by construction, with no constraint on kernel order, at a width that is small *only* for bounded-range block scales: 60 bits for UE4M3 and 92 for UE5M3, against 533–561 for E8M0 (MX).
> The claim is falsified if **(E)** XACC-HDR-1 (08: real LLM GEMMs under deployed NVFP4 recipes) fails **(K)**:
> - at least 20% of outputs order-sensitive in at least one layer class, or token log-probabilities differing across orders in at least 1% of tokens, under a deployed recipe;
> - and the pre-registered PE-level cost criterion, A×T_ss(exact) ≤ 1.10 × the strongest FP32 accumulator.

## Evidence so far

| Element | Evidence | Label | Status |
|---|---|---|---|
| Width bound, 60 bits | Exhaustive enumeration (04 E1a); prediction confirmed | DERIVED | holds |
| Mechanism exactness | Exact path 100% order-invariant, equal to an independent element-level integer GEMM (04 E1b); PE RTL and post-route netlists match the exact golden, mutants detected (04 E2) | MEASURED | holds |
| **Premise on benign data** | FP32 accumulation of NVFP4 blocks is order-invariant for ≥ 99.9% of outputs on Gaussian, Student-t and 20×-outlier data (04 E1b) | MEASURED | **false, which killed XACC as registered** |
| Premise in regime Z | ×1000 outliers: 97.5–100% of outputs order-sensitive, thousands of ULP spread (04 post hoc) | MEASURED, **post hoc, synthetic** | plausible; not established |
| Cost at PE level | 04 E2: see the decision table there | EXTRACTED | E2 in progress at this checkpoint (see 04 Part 2 when complete) |

## Why it is not selected

1. **Its registered premise failed** on the pre-registered data. The regime where it holds was found after the fact, on synthetic outliers.
2. **Whether real NVFP4 deployments sit in regime Z is unknown.** Rotations (the random Hadamard transform in NVFP4 recipes) are designed to flatten exactly the outliers that create Z.
3. **Novelty is at best "obvious composition" until (1) and (2) are settled.** A long accumulator for a narrow format is textbook (05). Only the measured regime-by-cost interaction could make it distinct.

## Exactly what is missing

- **Real-model block-scale span statistics and order sensitivity** under deployed NVFP4 recipes, with and without rotation (08, XACC-HDR-1). This needs model weights; they cannot be downloaded in this environment.
- **Full texts** of the tensor-core accumulation models (2512.07004) and the NVFP4 hardware reports. They say whether vendors already accumulate NVFP4 block contributions exactly, which would make the mechanism pre-existing.
- **An array-level cost that includes accumulator storage** (tensor memory or register-file capacity). E2 measures PE-local accumulators only.
