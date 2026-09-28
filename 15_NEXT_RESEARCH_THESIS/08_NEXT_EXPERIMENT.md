# 08 — The next experiment (proposed; not started)

This is **not** authorised to run as part of this run. The task was explicit: "Do NOT begin weeks of implementation automatically". The experiment is also blocked here: model weights and activations are not downloadable, because HuggingFace and arXiv are refused by the egress proxy (01).

It is the single experiment that decides whether the strongest near-miss (06) becomes a thesis. If run, it is a **new study** that starts at rule 1 (`SUPPORTING_ARTIFACTS/NEXT_THESIS_RESEARCH_RULES.md`). It is **not** a rescue of the killed XACC registration, whose kill stands.

## XACC-HDR-1: do real NVFP4 GEMMs cross the order-sensitivity transition?

**Question.** In deployed or training NVFP4 recipes on real LLMs, does IEEE-FP32 accumulation of block contributions change bits with reduction order often enough to matter? The post-hoc diagnostic (04 Part 2) shows this depends on the within-row block-scale exponent span:
- a span of 9 binades or less gives exact, order-free FP32;
- a span of 12–13 binades or more makes almost every output order-sensitive.

**Design (to be pre-registered before any model is loaded).**

1. **Models:** at least three open LLMs of different families and sizes (for example one each of the Llama, Qwen and Mistral families, 7–14B), plus one NVFP4-trained checkpoint if one is public.
2. **Data:**
   - real prompts (a fixed public set, 256 sequences);
   - capture the inputs of every linear layer (Q/K/V/O, MLP up/gate/down) at every depth;
   - dequantised weights.
3. **Recipes, each defined by its source before any data is seen:**
   - (a) NVFP4 as specified: per-tensor FP32 scale, UE4M3 block scales, RNE, no rotation;
   - (b) the same with the random Hadamard transform used by NVFP4 training / inference recipes;
   - (c) UE5M3 scales.
4. **Measurements, per GEMM:**
   - the within-row shift-span distribution;
   - the fraction of outputs order-sensitive across the 8 orders of E1b;
   - the maximum ULP spread;
   - the downstream effect: log-probability differences at the model output across orders.
5. **Strongest baselines:** the batch-invariant / TBIK software approach (order fixed) and FP32 as-is.

**Pre-registered decision (proposed):**
- **KILL XACC-HDR** if, under the deployed recipe (b) and also under (a), fewer than 5% of GEMM outputs over all layers are order-sensitive, *and* model-output log-probabilities are bitwise identical across orders in more than 99% of tokens. Real NVFP4 data would then sit in the benign regime.
- **Premise holds** if at least 20% of outputs in at least one layer class are order-sensitive under a deployed recipe, *or* token log-probabilities differ across orders in at least 1% of tokens.
- **In between: UNRESOLVED.** Report and stop.

**If the premise holds, the cost question is already partly answered** by E2 (04 Part 2), which measures exact accumulation against IEEE-RNE, truncating and pipelined-interleaved FP32 accumulators at PE level on SKY130. Two things would still be missing:
- (i) an array-level evaluation that includes accumulator storage (tensor memory / register-file capacity);
- (ii) comparison with a vendor-style fused, truncating multi-term accumulator. Khattak & Mikaitis models describe such accumulators; the full text was blocked here.

**Cost.**
- Model runs: CPU-feasible for activation capture at small batch, or one GPU-day.
- The accumulation study is numpy on captured tensors, a few hours.
- It needs network access to model weights, which is the researcher's environment decision.

**What would kill the near-miss outright:**
- Real recipes stay benign because of rotations or scale choice: the determinism problem does not exist for NVFP4 GEMMs in practice.
- Vendor tensor cores already accumulate NVFP4 block contributions exactly: the mechanism exists already (a full-text check of 2512.07004 and the NVFP4 reports settles this).
