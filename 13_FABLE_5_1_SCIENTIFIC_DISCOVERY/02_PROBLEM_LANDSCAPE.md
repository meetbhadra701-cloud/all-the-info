# 02 — Problem landscape: consequential tensions considered

**How this was searched.**
- The archive already maps logic synthesis, formal verification, physical design, HLS buffering and hardware security (`01_…`).
- This session calibrated the *less-explored* territories with live search: AI-inference hardware, datapath power, and hardware compilation.
- Primary papers could not be opened: the environment's egress policy blocks arxiv.org, dl.acm.org, ieeexplore.ieee.org, semanticscholar.org, openreview.net and huggingface.co.
- Claims from search-engine summaries are therefore marked **[summary]**. Claims we ran ourselves are **OBSERVED**.

## The technology shift that selected the territory (2025–2026)

**Model-specific ("hardwired-weight") inference silicon has moved from concept to product within a year.**

- **Taalas HC1 (Feb 2026) [summary].**
  - TSMC N6, 815 mm², 53 B transistors, Llama 3.1 8B hard-coded; up to about 17,000 tokens/s per user at about 200 W.
  - Weights live in a "mask-ROM recall fabric". Only two metal layers change per model.
  - The CEO's claim: "a single transistor stores a 4-bit weight and performs its multiply".
  - An independent analysis (Zhao) describes the compute as "Multiply-Select-Add": products are pre-multiplied once per input and shared by every row, then selected by a 2-D crossbar. Decoders, pre-multiplication and accumulation sit on the 1-D periphery.
  - **AMD agreed to acquire Taalas on 6 Aug 2026.**
- **HNLPU (ASPLOS 2026; arXiv 2508.16151) [summary].**
  - "Metal-Embedding": weights are embedded in the 3-D topology of the metal wires.
  - FP4 multiply-by-constant is about 42.5 transistors on average, roughly 6× smaller than a generic FP4 multiplier. Inputs are bit-serial with carry-save accumulation.
  - GPT-OSS-120B in 13,232 mm² at 5 nm; 249,960 tokens/s.
  - Metal-Embedding cuts photomask cost 112×. The authors estimate that naive hardwiring would need at least $6 B of masks.
- **BitROM (ASP-DAC 2026) [summary].** Compute-in-ROM for BitNet b1.58: two ternary weights per transistor, a tri-mode local accumulator, eDRAM KV cache.
- **Ankhdjet (arXiv 2608.26206, 26 Aug 2026) [summary].**
  - An open-source compiler from a HuggingFace ternary checkpoint to the via-mask program of a *fixed* compute-in-ROM macro on SKY130. DRC, LVS and timing are clean.
  - "A ternary MAC is an add, a subtract, or a skip."
- **Physical Foundation Models (Yale/Cornell/BU/NTT, Apr 2026) [summary].** A perspective arguing for fixed-hardware implementations on a model-release cadence.

## Tension examined in depth: **specialization vs. per-model re-spin cost**

Hardwiring deletes weight movement, which gives orders-of-magnitude efficiency. But every new model needs new masks.

The industry answer is to make the *base layers weight-independent* and encode weights only in top metal/vias: Taalas's two layers, HNLPU's Metal-Embedding, Ankhdjet's via-mask.

**Consequence (INFERRED, the key structural observation of this session).**
- In a via/metal-programmable fabric, every adder must exist in the base layers *before the weights are known*.
- The classical tool for shrinking constant matrix–vector hardware is weight-specific common-subexpression elimination. Examples: da4ml (TRETS 2025, in hls4ml), Tridgell et al. "Unrolling Ternary Neural Networks" (TRETS 2019), and MCM/CMM heuristics. Its adder DAG *depends on W*, so it **cannot be used** in these fabrics without giving up metal-only programmability.
- What the existing via-programmable designs share is only **per-input** (g = 1):
  - Taalas pre-multiplies each input once and selects per weight;
  - Ankhdjet adds, subtracts or skips each input per weight.
- Every row therefore needs about one accumulation input per nonzero weight.

**Problem A (selected):**
- *What is the minimum accumulation hardware of a hardwired linear layer when the base layers must be weight-independent, and how close can it come to weight-specific CSE?*
- **Objective:** adders or area for y = W x, with W ternary or low-bit, exact function.
- **Constraints:**
  - (i) full-custom, or
  - (ii) weight-independent base layers, with W entering only through via/metal selection.
- **Scope limit (INFERRED from Taalas's transistor budget, stated up front):**
  - This matters most for **spatial** hardwired layers, where every weight has dedicated accumulation hardware: HNLPU-class designs and hls4ml/da4ml-class real-time inference.
  - In a time-multiplexed ROM design like Taalas HC1, ROM, SRAM and periphery appear to dominate the 53 B transistors, and adders are a small share.

## Other tensions considered (kept, not selected)

| # | Tension | Why considered | Status |
|---|---|---|---|
| B | **Functional yield of hardwired weights.** A ROM/via weight cannot be repaired with spare rows the way SRAM can, yet the dies are 815–13,232 mm². | A new tension created by hardwiring. The existing on-die SRAM adapters (Taalas uses them for fine-tuning) could double as repair capacity. | Hypotheses in `03_…` (B1–B3). **Not tested:** it needs defect statistics and model-accuracy runs, and model checkpoints are blocked here. |
| C | Delay-constrained area recovery in standard-cell mapping (inherited, Wave 11) | The strongest earlier lead. | **Closed on evidence:** the covering-level headroom over the best heuristic is about 2–3% on half the circuits (`01_…` §3). |
| — | Glitch power in AI MAC arrays | A real energy issue [summary: SemiEngineering]. | Not pursued. It is a mature field (path balancing, pipelining, glitch-aware sizing) with no distinct mechanism identified. It needs timing-accurate simulation. |
| — | Runtime LUT-based low-bit GEMM (T-MAC, LUT Tensor Core ISCA'25, TeLLMe v2, TENET, Vec-LUT, the Apr-2026 ternary LUT generator 2604.25183) | This is where the block-precompute *principle* lives. | **Occupied as a principle.** Used here as the source of the known ingredient (`04_…`). |

## Why Problem A over B

- A has an exact, falsifiable objective (adders and area at identical function).
- It has a strongest open baseline that runs locally (da4ml 0.6.0 via PyPI).
- It has an independent correctness oracle (exact integer simulation, plus Yosys/ABC equivalence checking).
- B's central quantities (via-defect statistics, accuracy under defects) cannot be measured here.
