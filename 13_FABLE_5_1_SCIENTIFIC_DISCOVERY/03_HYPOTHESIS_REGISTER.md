# 03 — Hypothesis register

**Status keys:** GENERATED, then REVIEWED (with the objection), then TESTED (with the result). "Tested" refers only to experiments in `06_…`.

**Shared setting for Problem A:**
- y = W x.
- W ∈ {−1, 0, +1}^{m×n} (ternary, BitNet-b1.58-class) unless stated. x is 8-bit signed.
- Exact function.
- Cost is adders (U) and bit-weighted adders (B); later, synthesized area.

**Two regimes:**
- (F) full-custom: base layers may depend on W;
- (V) via/metal-programmable: base layers are fixed for every W of the shape/format, and W enters only through via/metal selections and add/sub polarity.

---

## A1 — Universal block-pattern generators (weight-independent sharing across inputs)

- **PROBLEM:** Problem A in regime (V).
- **EXISTING FRONTIER:**
  - per-input sharing, i.e. g = 1: Taalas's pre-multiply-once/select-per-weight; Ankhdjet's add/sub/skip; HNLPU's per-weight constant cells;
  - runtime LUT GEMM (LUT Tensor Core, TeLLMe v2, T-MAC), which precomputes all signed subset sums of G ≈ 3–4 activations and fetches them with a weight-indexed mux.
- **DOCUMENTED LIMITATION:**
  - In (V), per-input schemes need one accumulation input per nonzero weight: Σ_i(nnz_i − 1) adders.
  - Runtime LUT designs keep G small because every lookup costs a (3^G/2)-to-1 mux per output (the Apr-2026 generator paper reports diminishing returns).
- **PROPOSED TECHNICAL INSIGHT:** When W is constant, the lookup mux becomes a via/wire selection. That removes the term that capped G. The block size is then limited by
  - (i) the number of rows that share a block's generator (amortization), and
  - (ii) the select wiring (lines per input ≈ (3^g − 1)/(2g)),

  not by mux logic.
- **MECHANISM:**
  - Split the inputs into blocks of g.
  - A fixed generator per block computes all (3^g − 1)/2 canonical signed subset sums, at (3^g − 1)/2 − g adders.
  - Each row adds or subtracts one generator line per nonzero block, costing about ⌈n/g⌉ − 1 adders per row.
  - Only the line choice and polarity depend on W.
- **WHY IT MIGHT WORK:** The pigeonhole argument. With m ≫ 3^g/2 rows, every generator line is reused about 2m/3^g times. This is the Lupanov / Four-Russians construction, which is asymptotically optimal (mn/log(mn) additions) for incompressible matrices.
- **WHAT WOULD BE NOVEL (claimed narrowly):**
  - the *regime result*: under constant weights and via-programmability, the optimal block size is set by row count and wiring rather than by mux cost, with the quantitative optimum;
  - the *price of universality* vs weight-specific CSE, measured.

  The block-precompute math is NOT novel.
- **WHAT IS REUSED:** Four-Russians/Lupanov block sums; LUT-GEMM symmetry reduction; via-ROM programming.
- **STRONGEST PRIOR-ART OBJECTION:** "This is LUT-based mpGEMM with a constant index, an obvious composition of LUT Tensor Core (ISCA'25) / TeLLMe with Taalas-style via ROM."
- **KEY UNSUPPORTED ASSUMPTIONS:**
  - (a) the adder reduction is material (≥ 2×) at LLM row counts;
  - (b) it survives gate-level synthesis;
  - (c) the select wiring in (V) does not consume the gain.
- **CHEAPEST MEANINGFUL EXPERIMENT:** E1 (adder counts vs per-input and vs da4ml), then E2 (Yosys/ABC area on SKY130).
- **REUSABLE BY OTHERS:** a generator plus a cost model for hardwired layers; a new baseline for hardwired-silicon papers.
- **STATUS:** GENERATED, REVIEWED (`04_…`), TESTED.
  - **(F): withdrawn.** Against structurally hashed per-input trees, the gain is only 1.04–1.20× (E1-hashed), and da4ml is better.
  - **(V): supported.** Exact ≈ g× adders; E3 cell area at iso-delay 1.95× (n = 128) and 2.49× (n = 1024); model-adjusted about 2× at g = 3.

## A2 — The price of universality is small (a quantitative claim about A1 vs weight-specific CSE)

- **PROBLEM:** Problem A, comparing (V) vs (F).
- **EXISTING FRONTIER:** da4ml 0.6.0 (weight-specific CMVM CSE, the strongest open implementation).
- **PROPOSED INSIGHT:**
  - Weight-specific CSE finds sharing that exists in *this particular* W.
  - For random-like (high-entropy) quantized weights, most of the available sharing is the *combinatorial* sharing that any matrix has (the Lupanov bound), which a universal fabric captures.
  - Hence U(A1) / U(CSE) → a small constant.
- **MECHANISM:** None new. This is a measurement hypothesis that decides whether (V) costs much.
- **STRONGEST OBJECTION:**
  - Trained weights are not random; CSE may exploit structure (e.g., correlated columns).
  - Also, da4ml optimizes delay as well as adders, so it is not purely adder-minimizing.
- **KEY ASSUMPTION:** Real ternary checkpoints behave like i.i.d. weights for sharing purposes. **Untestable here:** huggingface.co is blocked.
- **CHEAPEST EXPERIMENT:** E1 (i.i.d.), then real BitNet layers (future).
- **STATUS:** GENERATED, TESTED in E1 (i.i.d. only): UBP/da4ml = 1.22–1.37 in adders (n ≤ 256). The pre-registered '≤ 1.25' advance clause is not met in general; the price of universality is about 20–37%.

## A3 — Weight-specific block patterns (CBP) as a scalable CSE (regime F)

- **INSIGHT:** Generating only the block patterns that are used, plus their parent closure, gives a linear-time CSE. It may match iterative CSE (da4ml) quality at LLM scale, where da4ml's runtime explodes.
- **OBJECTION:** This is a restricted form of CSE. For large g it is the Lupanov construction; for CMM there are many fast heuristics (Hcub, RPAG, da4ml).
- **STATUS:** GENERATED, TESTED in E1 as a control. CBP is within 1–4% of UBP, so universality itself is nearly free. CBP is no better than hashed per-input trees in (F), so A3 as a scalable (F) CSE is not competitive with da4ml's quality.

## A4 — Codebook-constrained ternary blocks (quantization–hardware co-design)

- **INSIGHT:** Constrain training so that each g-block of every row is one of K ≪ 3^g codewords (vector quantization over ternary codewords).
  - The generator shrinks to K lines.
  - Wiring per input drops to K/g, so larger g (fewer accumulations) becomes wire-feasible.
- **OBJECTION:** VQ for LLMs is established (AQLM, QuIP#, GPTVQ). At about 1 bit/weight, quality likely degrades; it requires training.
- **STATUS:** GENERATED, REVIEWED; **not testable here** (no GPU, no checkpoints). Preserved as the main co-design follow-up.

---

## B1–B3 — Functional yield of hardwired weights (Problem B)

- **B1 (defect-benign encodings):** One-hot/select encodings map a missing via to a *zero* weight (dropout-like). Binary via encodings map one defect to arbitrary value errors. Hypothesis: encoding choice changes functional yield materially.
- **B2 (adapter-as-redundancy):**
  - The per-layer SRAM low-rank adapter already on die can replace up to r defective rows/columns exactly: e_i W_i is rank-1.
  - Clustered defects in a physically contiguous array map to low-rank weight errors.
  - Hypothesis: the adapter provides repair capacity that raises yield without dedicated spares.
- **B3 (post-test bias compensation):** Known defects' mean effect E·μ_x can be folded into biases, as in data-free-quantization bias correction.
- **Strongest objections:**
  - DNN fault tolerance for yield is established for programmable accelerators (application-driven yield loss reduction, 2020; IBM TrueNorth yield-tolerance patents).
  - Low-rank/LoRA compensation of device errors is studied for RRAM compute-in-memory.
- **Remaining delta:** the application to mask-ROM weights that cannot be remapped after test.
- **STATUS:** GENERATED, REVIEWED; **not tested** (needs defect statistics and model evaluation). Preserved as Problem B.

## C — Standard-cell mapping (inherited): closed

Closed on re-read Wave 11 evidence (`01_…` §3). No new hypothesis generated.

## Rejected during this session (with reason)

| Idea | Reason |
|---|---|
| Hardwired CMVM via generic CSE | Occupied: da4ml 2025; Tridgell 2019; ternary-ASIC CSE 2024 [summary]. |
| Block precompute as a new *principle* | Occupied: Four-Russians (1970), Lupanov (1956), T-MAC, LUT Tensor Core. |
| Via-programmable model silicon as a concept | Occupied: Taalas, HNLPU Metal-Embedding, Ankhdjet. |
| Glitch-aware MAC design | No distinct mechanism identified; mature field. |
