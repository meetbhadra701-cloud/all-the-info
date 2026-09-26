# 04 — Stage A (generation) and Stage B (proximity)

## Frontier reconstruction (Phase 1, brief)

The archive plus the previous session already map the frontier (`13_FABLE_5_1_…/02_PROBLEM_LANDSCAPE.md`, `04_STRONGEST_PRIOR_ART.md`). The one new check this session changes nothing:
- **NEW-OBS:** HNLPU is still describable only from summaries. They consistently report: 16 weight-value regions per neuron, inputs routed by metal, bit-serial POPCNT, and the distributive law *within* a neuron.

Selection rule applied: choose problems where (i) the strongest method's limitation is structural, (ii) a mechanism can be written as an algorithm or architecture, and (iii) the central assumption can be tested with open tools on this machine.

Three problems were considered.

---

## P1 — Accumulation hardware under weight-independent base layers (regime V)

- **WHY IT MATTERS:**
  - Model-specific silicon keeps per-model NRE viable only by confining weights to upper metal/vias. HNLPU (ASPLOS'26) shares 60 of 70 masks; Taalas HC1 changes 2 layers.
  - In spatial fabrics, every weight *site* carries accumulation hardware.
- **STRONGEST EXISTING METHODS:** per-input or in-neuron grouping (HNLPU value regions + POPCNT; Taalas pre-multiply-and-select; Ankhdjet add/sub/skip).
- **EXACT LIMITATION:**
  - Weight-specific sharing (CSE; synthesis hashing) needs W-dependent base layers.
  - So every neuron keeps about one accumulation input per weight site: m(n − 1) adder inputs.

### H1.1 — Bit-parallel universal block patterns (UBP-g) [inherited; cell level passed]

- **INSIGHT:**
  - With constant W, the table-lookup mux of runtime LUT-GEMM becomes a via.
  - A *weight-independent* generator of all (3^g − 1)/2 signed subset sums of g inputs can be shared by every neuron.
  - Each neuron then needs ⌈n/g⌉ leaves.
- **MECHANISM:** GEN(g) per block; TREE(⌈n/g⌉, w) per neuron; a via selects a line, or zero, per leaf; polarity comes from shared negated lines.
- **WHY IT COULD WORK:** pigeonhole amortization. Port-optimal (Theorem 1).
- **NEW:** cross-neuron sharing under W-independence; the regime's optimal g (set by rows and wiring, not by mux cost).
- **REUSED:** Four-Russians/LUT-GEMM math; via-programmable fabrics.
- **CRITICAL UNSUPPORTED ASSUMPTION:** *the (3^g − 1)/2 × w-bit candidate buses that must cross every site can be routed without eating the logic savings.* This was only modelled (g = 3 fits at both pitches; g = 4 does not at the wide pitch).
- **STRONGEST NOVELTY OBJECTION:** LUT-GEMM with constant indices; HNLPU/Taalas may do it. Provisional; full texts are blocked.
- **CHEAPEST FALSIFIER:** place-and-route of weight-independent, hierarchy-preserved fabrics (E5).
- **REUSABLE:** the fabric generator, the port bound, the PnR evaluator.

### H1.2 — Bit-serial universal block patterns (NEW-HYP; an evolution of H1.1)

- **INSIGHT:** Two costs work against H1.1: wire cost proportional to (lines × bits) per site, and wider leaves (10 bits vs 8). Both collapse in **bit-serial** arithmetic, which HNLPU itself uses.
  - A pattern line becomes **one wire**.
  - A leaf becomes **one serial/popcount input per cycle**, independent of value width.
- **MECHANISM:**
  - The generator is built from serial adders (1 FA + 1 carry flip-flop each).
  - Each neuron's region popcounts take ⌈n/g⌉ pattern streams instead of about n input streams.
  - Serial sign extension is free (the MSB repeats); subtraction uses the negated region, as in HNLPU.
- **WHY IT COULD WORK:**
  - Per-site cost drops to about a constant.
  - Select wiring per site drops w× (from 40 × 10 to 40 tracks at g = 4).
- **HIDDEN TRADEOFF TO MEASURE:**
  - Pattern values are ⌈log₂ g⌉ + 1 bits wider, which may add cycles per output at iso-throughput.
  - In LSB-first serial accumulation, however, the cycle count is set by the *output* width, which is the same for both fabrics (NEW-INF, to be checked).
- **NEW vs HNLPU:** HNLPU's POPCNT neurons consume raw input streams (g = 1). H1.2 feeds them shared multi-input pattern streams.
- **CRITICAL ASSUMPTION:** the serial per-leaf cost is width-independent, and the generator's serial adders plus added latency stay small.
- **CHEAPEST FALSIFIER:** a gate-level iso-throughput comparison of bit-serial neuron slices (E3-style), then PnR.

### H1.3 — Cross-matrix generator sharing (merged, not a mechanism)

- Q/K/V projections, and gate/up projections, consume the *same* activation vector. One generator bank can therefore serve all of them: m_eff = 6,144 rows (QKV) or 28,672 rows (gate+up) for Llama-3-8B shapes.
- This lowers generator overhead and raises the useful g, but g is ceilinged by wiring.
- **Proximity:** a design rule for H1.1/H1.2, not a separate hypothesis.

---

## P2 — Functional yield of hardwired weights (reserve)

- **WHY:** 815–13,232 mm² dies. ROM/via weights cannot be repaired with spare rows.
- **H2.1 (adapter-as-redundancy):** a rank-r SRAM adapter (already on die for fine-tuning) can replace r defective rows or columns exactly (e_i W_i is rank 1). Clustered defects map to low-rank weight errors.
- **H2.2 (defect-benign encodings):** one-hot selection maps a missing via to a zero weight (dropout-like).
- **CRITICAL ASSUMPTION:** that realistic defect statistics produce errors within adapter capacity, and that accuracy loss is measurable.
- **NOT TESTABLE HERE:** no checkpoints (HF blocked), no via-defect data.
- **OBJECTION:** DNN fault tolerance for yield exists for programmable accelerators; LoRA-style compensation exists for RRAM compute-in-memory.

## P3 — Hash-friendly constant matrix-vector multiplication in full-custom silicon (considered, merged)

- This came from our own E1-hashed finding: plain balanced trees plus structural hashing capture most pigeonhole sharing.
- **H3.1:** choose each row's pairing order to maximize hash hits, i.e. greedy pairwise CSE.
- **Proximity verdict:** that *is* Paar-style greedy CSE, which da4ml improves on. Merged into the known CSE literature; no distinct mechanism.

---

## Stage B — proximity summary

| Pair | Relation |
|---|---|
| H1.1 ↔ H1.2 | Same core (universal block sharing). H1.2 changes the *cost structure* (per-site cost width-independent; 1-wire lines; new cycle tradeoff). Substantive, not cosmetic. |
| H1.3 → H1.1/H1.2 | Design rule; merged. |
| H1.x ↔ LUT-GEMM (T-MAC, LUT Tensor Core, TeLLMe) | Shared known ingredient (block precompute). The delta is the constant index (a via, not a mux), W-independence, and cross-neuron sharing in a metal-programmable fabric. |
| H1.2 ↔ HNLPU | Same arithmetic style (bit-serial POPCNT). The delta is what feeds the popcounts (shared pattern streams vs raw inputs). The closest prior art; its full text is unread. |
| H2.x ↔ P1 | Independent problem; the same product domain. |
| H3.1 ↔ da4ml / Paar | Collision: merged and killed. |
