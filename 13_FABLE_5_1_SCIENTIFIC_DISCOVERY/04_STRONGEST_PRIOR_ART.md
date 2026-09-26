# 04 — Strongest prior art, with the exact overlap and remaining delta

**Access limitation (important).**
- The session's egress policy blocks arxiv.org, dl.acm.org, ieeexplore.ieee.org, semanticscholar.org, openreview.net, huggingface.co and personal pages (yongwei.site, substack).
- Paper claims below therefore come from search-engine summaries **[summary]**, unless we ran the artifact **[OBSERVED]**.
- A full-text read of the items marked ★ is the first task of the prototype phase.
- No novelty is inferred from an absent search result.

## 1. Direct neighbours: hardwired / model-specific inference silicon

| Work | What it does (as retrieved) | Overlap with A1 | Remaining delta |
|---|---|---|---|
| ★ **HNLPU**, "Hardwired-Neurons Language Processing Units…", ASPLOS 2026 (arXiv 2508.16151) [summary] | Metal-Embedding (weights in 3-D metal topology). **"Sea-of-Neurons"**: a pre-fabricated generic neuron array in which the weight-dependent structure is confined to **M8–M11**, so 60 of 70 masks are reused across models. **Per neuron, 16 weight-value regions: each input is routed to the region of its weight value and summed by bit-serial POPCNT, then each region is scaled by its constant once.** FP4 multiply-by-constant ≈ 42.5 T. GPT-OSS-120B at 13,232 mm² (5 nm) | Spatial and metal-programmable: **exactly regime (V).** Its grouping is the distributive law *within one neuron*: Σ_j w_j x_j = Σ_v v·Σ_{j: w_j=v} x_j | As retrieved, HNLPU groups **within** a neuron. Every neuron still consumes about one popcount input per nonzero weight (g = 1 across neurons). A1 shares block partial sums **across neurons** and keeps the same M8–M11-only programmability, since pattern-line selection is a metal choice. Confirming that HNLPU has no cross-neuron sharing requires the full text; this is the **#1 novelty risk**. |
| **Taalas HC1** (product, Feb 2026) [summary: company statements, Zhao's "Taalas HC1 Architecture Decoded"] | Mask-ROM recall fabric; 4-bit weights; "Multiply-Select-Add": pre-multiplication once per input (1-D periphery), selection by a 2-D crossbar, one-hot via a 3-to-8 decoder | Sharing of per-input products across rows, i.e. **g = 1 of A1** | Block (multi-input) patterns are not described. HC2 details are unknown; it is proprietary. |
| ★ **Ankhdjet** (arXiv 2608.26206, Aug 2026) [summary] | Open compiler: BitNet checkpoint → via-mask program of a fixed SKY130 compute-in-ROM macro; "a ternary MAC is an add, a subtract, or a skip" | Via-programmable ternary; per-input (g = 1) | Block patterns are not described in the summaries. Its macro is the natural *baseline host* for A1. |
| **BitROM** (ASP-DAC 2026) [summary] | CiROM; two ternary weights per transistor; tri-mode local accumulator; eDRAM KV cache | Ternary CiROM density | Time-multiplexed macro. Accumulation sharing is not described. |
| **Physical Foundation Models** (Apr 2026) [summary] | Perspective on fixed-hardware NN implementations | Motivation only | — |

## 2. The known ingredient: block precomputation of signed subset sums

| Work | Content | Relation to A1 |
|---|---|---|
| Arlazarov–Dinic–Kronrod–Faradzev ("Four Russians", 1970); Lupanov (1956) linear-operator circuits | Precompute all subset sums of blocks of ~log n columns; asymptotically optimal O(mn/log(mn)) additions for most matrices | **The mathematical core of A1.** A1 claims no new math. |
| ★ **LUT Tensor Core** (ISCA 2025) [summary]; T-MAC; LUT-GEMM | Runtime LUT mpGEMM: precompute tables of activation partial sums; weights index the table; symmetry halves the table; bit-serial; elongated tiling for table reuse | Same decomposition with a **runtime** index (a mux per lookup) | In A1 the index is a design-time constant, so the mux becomes a via/wire. That changes the cost terms, and hence the optimal g, and removes per-lookup mux logic. |
| ★ **"Hardware Generation and Exploration of LUT-Based Accelerators for 1.58-bit LLM Inference"** (arXiv 2604.25183; IEEE; TSMC 16 nm) [summary] | Formalizes the ternary LUT design space (L, μ, K); Chisel generator; diminishing returns for small activation types; a few large LUT cores beat many small ones | The closest *design-space* study, for runtime weights | It does not consider constant weights or via-programmability. Its "diminishing returns" come from lookup/fetch cost, which A1 removes by construction. |
| TeLLMe / TeLLMe v2, TENET, Vec-LUT, "Unified LUT inference with signed-digit K/V caches" (2025–26) [summary] | FPGA/edge ternary LUT accelerators: group size G, offline index encoding, adder/subtractor-tree precompute, symmetry reduction | Same precompute structure; runtime indices | As above. |

## 3. The strongest baseline for full-custom sharing: weight-specific CSE

| Work | Content | Relation |
|---|---|---|
| **da4ml** 0.6.0 (Sun, Que, Loncar, Luk, Spiropulu; TRETS 2025; arXiv 2507.04535; in hls4ml) [OBSERVED: ran it] | Distributed-arithmetic CMVM: graph-based CSE producing a shift-add DAG, delay-aware; up to one-third resource reduction on quantized networks | The strongest open weight-specific method. **Not applicable in regime (V):** its DAG depends on W. It is the upper reference for the "price of universality". |
| Tridgell, Kumm, Hardieck, Boland, Moss, Zipf, Leong, "Unrolling Ternary Neural Networks" (TRETS 2019) [summary] | Fixed ternary weights on FPGA with CSE | Occupies "CSE for hardwired ternary layers" (regime F). |
| Ternary-weight RF-modulation ASIC with CSE (2024) [summary] | CSE on fixed ternary weights in an ASIC | Same. |
| MCM/CMM literature: Hcub, RPAG, Boullis–Tisserand CMM, Aksoy et al., Kumm's ILP; Paar / Boyar–Peralta SLP (GF(2)) | Adder-count minimization for constant (matrix) multiplication | Occupies full-custom adder minimization. Scalability to 10^7-weight matrices is the open practical issue. |

## 4. Engineering finding produced while running the baseline (not a contribution)

**da4ml 0.6.0 `cmvm.solve` silently mis-solves Fortran-ordered inputs [OBSERVED].**
- Given `W.T.astype(float32)` (an F-contiguous array), it returned a pipeline whose `.kernel` equals Kᵀ, not K. There is no error.
- For square inputs this is undetectable without an independent check. Our checker caught it.
- Workaround: `np.ascontiguousarray`.
- Evidence: `evidence/da4ml_layout_hazard.txt`.
- Could be reported to the authors. **Nothing has been sent.**

## 5. Contribution boundary (after prosecution)

**Occupied:**
- block-precompute mathematics;
- runtime LUT mpGEMM architectures;
- weight-specific CSE for hardwired layers (regime F);
- via/metal-programmable model silicon as a concept;
- per-input product sharing (g = 1).

**Not found (≠ novel):**
1. A treatment of accumulation sharing **under the constraint that base layers are weight-independent** (regime V): the optimal block size, and the adder-vs-select-wiring trade-off it creates.
2. A measurement of the **price of universality**, i.e. universal block fabrics vs the best weight-specific CSE, at LLM-relevant sizes.
3. Evidence on whether the adder-count advantage survives synthesis, and in which arithmetic style (bit-parallel vs bit-serial) it survives wiring.

**Strongest remaining objection, stated in advance:**
- "This is the LUT-GEMM decomposition with constant indices. Any hardwired-silicon team would try it; HNLPU or Taalas HC2 may already do it."
- The answer can only come from the full texts (★). If either paper already reports cross-input block sharing under metal-only programmability, A1's novelty is occupied. What would remain is the quantitative study (items 2–3), which is an engineering characterization.
