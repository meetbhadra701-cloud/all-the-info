# Prior-art search log — 2026-09-26 (Wave 14)

**Tools and access:**
- Web search, free, US index. No paid API was used.
- Full texts were **not readable**: the egress proxy blocks arxiv.org, awesomepapers.io, pith.science, substack, yongwei.site and emergentmind.
- Everything below is therefore **search-engine summaries** (secondary). A full-text read by a person with access remains required. See 07_PRIOR_ART_PROSECUTION.md.

## Query log (verbatim queries; the claims each result summary makes)

### 1. `HNLPU hardwired neural language processing unit metal-embedding POPCNT neuron value regions`
- Source: arxiv 2508.16151 / ASPLOS'26 (dl.acm.org/doi/abs/10.1145/3779212.3790169).
- Summary claims:
  - Weights are "etched" into metal topology (Metal-Embedding).
  - "For 4-bit precision, 2^4=16 unique weight regions are created per neuron, and inputs are routed accordingly."
  - "POPCNT operations on bit-serialized inputs allow grouping multiple constant multiplications."
- **Relation to UBP:** grouping is **within one neuron, by weight value**. Nothing indicates a pre-summed multi-input stream shared by many neurons.

### 2. `BitROM ternary weights ROM compute-in-memory LLM accelerator`
- Source: BitROM, ASP-DAC 2026 (arxiv 2509.08542).
- Summary claims: "Bidirectional ROM Array that stores two ternary weights per transistor; Tri-Mode Local Accumulator; DR eDRAM".
- The Ankhdjet summary says BitROM uses "tri-state multi-level accumulation, and a shared adder tree".
- **Relation to UBP:** per-weight accumulation in a ROM macro. No shared block patterns mentioned.

### 3. `"TOM" ternary read-only memory accelerator … sparsity-aware ROM MVU datapath adder tree ternary weights`
- Source: TOM, arxiv 2602.20662.
- Summary claims:
  - "The sparsity-aware ROM architecture synthesizes ternary weights as standard-cell logic, eliminating area overhead from zero-valued bits."
  - "The ternary multiplication is as simple as a conditional negation and the adder tree is re-used between the FP8 x FP8 and Ternary x FP8 units."
- **Relation to UBP:** ROM-as-logic plus a conventional adder tree with conditional negation, i.e. per-input accumulation (g = 1).

### 4. `Ankhdjet mask-programmed ternary compute-in-ROM compiler open PDK adder tree shared`
- Source: Ankhdjet, arxiv 2608.26206.
- Summary claims: it compiles a HuggingFace ternary checkpoint "to a via-mask program of a fixed compute-in-ROM macro on the open SKY130 PDK".
- It names BitROM as the closest prior work.
- **Relation to UBP:** a fixed macro with a via program. The per-weight add/sub/skip is per input (g = 1). This is exactly the regime-V status quo that our baseline g1_V represents.

### 5. `TOM ternary ROM accelerator "lookup" OR "LUT" precomputed activation group sums ROM indices`
Surfaced the **LUT-based ternary accelerator family**:
- VitaLLM 2604.27396;
- Hardware Generation and Exploration of LUT-Based Accelerators for 1.58-bit LLM Inference 2604.25183 (TSMC 16 nm; open-source generator; design space of ternary LUT accelerators);
- Vec-LUT 2512.06443;
- TeLLMe v2 2510.15926;
- TENET 2509.13765;
- Unified LUT inference with signed-digit K/V caches 2608.03229.

Summary claims:
- "the ternary weight matrix is partitioned into groups of size G, encoded into compact indices, with N_TB = 3^G unique combinations per group. The table is populated by a pre-computation unit and stores all possible partial sums for the current activations." (TeLLMe-style TLMM)

### 6. `hardwired weights ROM LUT-based ternary matmul precompute all combinations of activations shared by all output neurons mask-programmed`
- Source: TENET.
- Summary claims:
  - "TLUT PEs that share the precompute logic and table, where input activations are divided into groups, which are processed by mirror-half pre-compute adder logic to construct the shared pre-compute table."
  - "a 2-bit dense index (DIdx) to select one of four pre-computed, symmetric partial products, and a 1-bit sign index (SIdx) to flip the selected value if a negative mirror is required."
- **Relation to UBP: this IS the UBP arithmetic** (canonical half of the signed subset sums + sign selection, shared across output computations). It is realized with **runtime indices** (weights in memory, decoded, table read through muxes) on FPGA/ASIC, not with weight-independent base layers plus a via program.

### 7. `hardwired LLM chip weights in metal layers "lookup table" precomputed partial sums via-programmable Taalas HC1 architecture`
- Taalas HC1: "mask-programmable 1T cell with via-selectable bitline connection, and model swaps confined to two metal masks."
- The source (kevinyuan1.substack.com) is blocked; the claim is secondary.

### 8. `Taalas HC1 "pre-multiply" OR "premultiplied" activations select via weight mask ROM multiplier-free`
- Source: yongwei.site/en/taalas-hc1-arch/ (the HNLPU author's analysis) and others.
- Summary claims:
  - "The strategy adopted by Taalas uses a Look-Up Table (LUT) scheme … the products of the input activation value and all possible weight values can be entirely pre-computed once, and every subsequent individual multiplication operation can then be replaced by selecting a ready-made value from the pre-computed results."
  - "The weights burned into the ROM are original weight values, which are then converted to one-hot via a decoder."
- **Relation to UBP:** Taalas (as decoded by a third party) shares **per-input multiples across weight values** (g = 1 over inputs, all values), selected through a ROM + decoder. UBP groups **g inputs** (all signed subset sums), selected directly by a via.

## What the evidence establishes (NEW-OBS, secondary sources)

1. **Cross-neuron sharing of pre-computed group partial sums is published prior art** (T-MAC, LUT Tensor Core, TeLLMe, TENET, 2604.25183), including the mirror-half/sign-index trick (TENET).
   - **This corrects the earlier short answer to the researcher** ("not as far as I can find"). That answer is true only for the *hardwired, weight-independent-base* realization.
2. **Hardwired / via / ROM LLM silicon is published** (HNLPU, Taalas as analysed, BitROM, TOM, Ankhdjet).
   - Every summary retrieved shows g = 1 over inputs: per input, per weight value, or within-neuron value grouping.
3. **Not found in any retrieved summary:** the *combination*, i.e. weight-independent generators of multi-input signed subset sums shared by all neurons, with each leaf's selection done by a via in a metal-programmable fabric, plus its physical cost (select wiring) measured after place-and-route.
4. **Obviousness risk is HIGH.** The combination joins two known lines (LUT sharing + via-programmed hardwiring) with a predictable logic saving. A patent examiner would likely reject on obviousness. The defensible scientific contribution is not the arithmetic. It is:
   - (a) the regime-V cost structure: the mux disappears and the cost moves into select wiring;
   - (b) whether the logic saving **survives physical routing**, which E5/E6 measure;
   - (c) the port-bound optimality (Theorem 1, previous session).
