# 05 — Primary research thesis

## Cross-neuron sharing under weight-independent base layers: block-pattern generators for metal/via-programmable hardwired inference silicon

**Evidence labels:**
- **PROVEN:** a short counting argument, given here in full.
- **OBSERVED:** measured in this session, reproducible from `experiments/`.
- **MODEL:** analytic estimate, not a measurement.
- **[summary]:** from search-engine summaries only; primary texts were blocked by the environment.
- **HYPOTHESIS:** not yet shown.

---

### 1. Exact scientific problem

A hardwired linear layer computes y = W x with W ∈ {−1, 0, +1}^{m×n} fixed at fabrication (BitNet-b1.58-class ternary weights) and x a stream of 8-bit activations.

**Regime (V), metal/via-programmable:**
- The transistors and lower metal layers ("base layers") must be identical for *every* W of the given shape and format.
- W may only select among pre-built wires/vias in the upper layers, and choose an add/sub polarity.
- This is how hardwired silicon keeps per-model NRE viable:
  - HNLPU confines weight-dependent structure to M8–M11, so 60 of 70 masks are shared [summary];
  - Taalas changes two metal layers per model [summary];
  - Ankhdjet compiles a checkpoint into a via mask of a fixed macro [summary].

**The problem:** minimize the accumulation hardware (adders; cell area; area including select wiring) of such a layer, at exact function.

A secondary regime, **(F) full-custom** (base layers may depend on W), is used as the reference frontier.

### 2. Why it matters

- Model-specific silicon became a product and an acquisition target in 2026:
  - Taalas HC1: 815 mm², 53 B transistors, Llama 3.1 8B, about 17 k tokens/s per user; AMD agreed to acquire Taalas on 6 Aug 2026 [summary].
  - HNLPU (ASPLOS 2026): GPT-OSS-120B hardwired in 13,232 mm² of 5 nm silicon [summary].
- In *spatial* hardwired designs (HNLPU-class; hls4ml/da4ml-class real-time inference), every weight site carries accumulation hardware. A constant-factor cut in accumulation hardware is a constant-factor cut in die area, which at these die sizes means cost and yield.

### 3. Strongest relevant existing methods

| Regime | Method | What it shares |
|---|---|---|
| V | HNLPU "Sea-of-Neurons": per neuron, 16 weight-value regions; inputs routed by metal; bit-serial POPCNT; one constant multiply per region [summary] | Within one neuron (distributive law) |
| V | Taalas "Multiply-Select-Add": pre-multiply each input once and select per weight via a crossbar [summary, third-party analysis] | Products across rows, per input |
| V | Ankhdjet: ternary add/sub/skip in a fixed CiROM macro [summary] | Nothing across inputs |
| F | **da4ml 0.6.0** (TRETS 2025; in hls4ml): weight-specific CSE for constant matrix–vector products [OBSERVED: run here] | Arbitrary W-specific subexpressions |
| runtime W | LUT Tensor Core (ISCA'25), T-MAC, TeLLMe v2, TENET; ternary LUT generator 2604.25183 [summary] | Signed subset sums of G ≈ 3–4 activations, fetched by a weight-indexed mux |

### 4. Exact technical limitation

- **In (V), weight-specific CSE is unavailable by definition:** its adder DAG depends on W, so it needs weight-specific base layers.
- **The (V) schemes in use share at most per input or within a neuron,** so every neuron needs one accumulation input per weight *site*. That is m(n − 1) adders for a universal fabric, which cannot know where the zeros are.
- **Runtime-LUT designs do share across inputs,** but each lookup is a (3^G/2)-to-1 mux per output. That caps G near 3–4, and 2604.25183 reports diminishing returns [summary].

### 5. Proposed technical mechanism (UBP-g)

1. Partition the n inputs into blocks of g.
2. For each block, a **weight-independent generator** computes all (3^g − 1)/2 canonical signed subset sums of its g inputs (first nonzero coefficient +1), costing (3^g − 1)/2 − g adders. Each pattern is its parent pattern ± one input.
3. Each neuron (row) has a **weight-independent adder tree with ⌈n/g⌉ leaves.**
4. **W enters only as upper-layer selections:** for each (row, block), a via chooses which generator line feeds that leaf, or none for an all-zero block, and a polarity chooses add or subtract.

Consequences:
- g = 1 recovers today's per-input schemes.
- The base layers are identical for all W ∈ {−1, 0, 1}^{m×n}, i.e. the construction is sea-of-neurons plus sea-of-generators.
- Regime-(F) variant (CBP-g): build only the patterns W uses.

### 6. What makes it distinct

- It shares **across neurons** (each generator line serves about 2m/3^g rows) while keeping the base layers W-independent.
- Neither HNLPU's in-neuron grouping nor Taalas's per-input pre-multiplication does this, as far as the retrieved descriptions show.
- **Hardwiring removes the lookup mux** that bounds runtime-LUT designs. The optimal block size is then set by row count (amortization) and select wiring, not by mux logic.
- The block-precompute *mathematics* is not new (Four Russians 1970; Lupanov 1956; T-MAC; LUT Tensor Core). The claim is the construction and analysis **under the weight-independence constraint**, and the regime result below.

### 7. Why it might address the limitation

- **Amortization (pigeonhole).** With m ≫ 3^g/2, each generator adder is reused by many rows. Each neuron's accumulation shrinks from about n leaves to ⌈n/g⌉.
- **Optimality (PROVEN, §8).** Among *all* via-programmable fabrics with select fan-in s, UBP meets the programmable-port lower bound with equality, and its adder count is within about 2× of any such fabric's minimum, plus the shared generator.

### 8. Mathematical formulation

**Model.**
- A fabric is a DAG of two-input adders with fixed base connectivity.
- Some adder inputs are **programmable ports**. Port p has s_p options: pre-built candidate signals, one of which may be the constant 0. For a nonzero candidate it also chooses a polarity. Its contribution therefore takes at most 2s_p − 1 distinct values: ± each nonzero candidate, and 0 once.
- A fabric is *universal* if for every W ∈ {−1, 0, 1}^{m×n} some port programming makes it compute y = W x.

**Theorem 1 (port and adder bounds; PROVEN).** A universal fabric with port fan-in ≤ s has

 P ≥ m n log₂3 / log₂(2s − 1) programmable ports, and A ≥ (P − m)/2 adders.

*Proof.*
1. W is recoverable from the function x ↦ W x (apply unit vectors). So distinct W need distinct programmings, and ∏_p (2s_p − 1) ≥ 3^{mn}. Taking logs gives the port bound.
2. Every programmable port is an input of some adder or one of the m outputs. Each adder has two inputs, so P ≤ 2A + m. ∎

**UBP-g meets the port bound with equality.**
- Its ports: P = m⌈n/g⌉, with s = (3^g − 1)/2 + 1 = (3^g + 1)/2. So 2s − 1 = 3^g, and P·log₂(2s−1) = m⌈n/g⌉·g·log₂3 ≥ m n log₂3, with equality when g | n.
- Its adders: A_UBP = m(⌈n/g⌉ − 1) + ⌈n/g⌉((3^g − 1)/2 − g).
- The row-tree part is within a factor 2 of Theorem 1's adder bound at the same fan-in. The generator part is amortized by m.
- **Design law:** *wiring buys adders only logarithmically.* Halving the adders requires squaring the select fan-in.

**Regime-(V) cost ratio vs today's per-input fabric (exact, W-independent):**

 A_g1,V / A_UBP,V = m(n−1) / [m(⌈n/g⌉−1) + ⌈n/g⌉((3^g−1)/2 − g)] → ≈ g for m ≫ 3^g.

- Measured closed forms: 2.62× (n=64), 3.17× (128), 3.54× (256) at g = 4 (`experiments/results/E1_summary.md`).
- Because both sides are W-independent, **this ratio holds for every weight matrix, trained or random.**

**Area model with select wiring (MODEL, `scripts/wire_model.py`).**
- Per (row, block) site: area = max(logic, lines × bits × pitch × row-height).
- SKY130 HD: FA = DFF = 20.02 µm², row height 2.72 µm; pitch 0.46–0.92 µm.

| Style | Predicted area gain vs g = 1 | Best g |
|---|---|---|
| Bit-parallel | 1.67–2.3× | 2–3 |
| Bit-serial (HNLPU-style) | 3.0–3.2× | 3–4 |

At g ≥ 5 the fabric is wire-bound in both styles.

### 9. Required assumptions

1. **Spatial (per-site) accumulation hardware is a material share of die area.** True for HNLPU-class and hls4ml-class designs. It is **not established** for time-multiplexed ROM designs such as Taalas HC1, where ROM, SRAM and periphery likely dominate.
2. **Pattern lines fit in the programmable upper metal at the chosen g** (§8 model). This is unverified by PnR.
3. **Weights are ternary or binary.** For 4-bit/FP4, value-domain blocks are wire-bound and digit-plane blocks revert to about one leaf per site. HNLPU's in-neuron value grouping is already efficient there (INFERRED; §17).
4. **Exact function; no retraining; no accuracy change.**

### 10. Smallest implementable prototype

- A Python generator emitting (V) and (F) Verilog for g1, UBP-g and CBP-g layers. It is implemented here: `experiments/scripts/hwlayer.py` and `emit_verilog.py`.
- Next:
  - (a) a bit-serial variant with shared serial generators and per-neuron serial adder or popcount trees;
  - (b) OpenROAD place-and-route of a 256×256 macro with all P_g candidate lines physically present in upper metal, compared against g = 1 in both arithmetic styles.

### 11. Strongest experimental baseline

- **Regime (V):** the per-input / in-neuron universal fabric (HNLPU- and Ankhdjet-style, g = 1) at the same arithmetic style, library and delay target.
- **Regime (F) and "price of universality":** da4ml 0.6.0.
- **Generic synthesis:** Yosys + ABC on the behavioural `W·x`.

### 12. Independent correctness check

1. **Construction level:** our own integer evaluator vs numpy on random vectors; da4ml's circuits are translated by our own translator and never executed by da4ml; four mutation controls are rejected.
2. **RTL/AIG level:** our own AIGER simulator vs numpy; a flipped-weight control is rejected.
3. **Mapped level:** ABC `cec` ("Networks are equivalent" only).
4. **Prototype phase:** post-PnR LVS and gate-level simulation.

### 13. Falsifying experiment

The mechanism is abandoned in regime (V) if **either** of these holds:
- after place-and-route with all candidate lines present, area(UBP_V, best g) > area(g1_V)/1.3 in both bit-serial and bit-parallel styles on SKY130 or ASAP7;
- the full texts of HNLPU / Ankhdjet / Taalas show cross-neuron block sharing under metal-only programmability (novelty occupied).

Already tested at the adder and cell level (E1, E2): see `06_…`.

### 14. Expected implementation challenges

- Routing P_g lines across all rows in the programmable layers (congestion, via density rules).
- Balancing generator depth against row-tree depth for timing.
- Bit-serial control and pipelining.
- Fitting the metal-only programming into existing macros (Ankhdjet is the open host).

### 15. Strongest novelty objection

"This is LUT-GEMM (LUT Tensor Core / T-MAC / TeLLMe) with constant indices, plus Taalas-style via selection: an obvious composition that HNLPU or Taalas HC2 may already contain."

**Answer, which only full texts can settle:**
- The retrieved descriptions of HNLPU and Taalas share within a neuron or per input only.
- The composition changes the governing cost term (the mux vanishes), which gives a different optimal g and a provable port-optimality.
- If the full texts show the same construction, the contribution reduces to the bound plus the measurement, which is a short paper at best.

### 16. What success would establish

- A W-independent construction that cuts the accumulation hardware of ternary/binary metal-programmable hardwired layers by about 3× in adders (exact) and by about 1.7–3× in area (model; measured at cell level in E2).
- A proof that it is port-optimal.
- A measured price of universality of about 1.22–1.37× vs the strongest weight-specific CSE.

### 17. What success would not establish

- Anything about accuracy (the function is exact), energy (not measured) or time-multiplexed ROM designs (Taalas-class).
- Benefits for 4-bit/FP4 weights.
- Routability, until PnR is done.
- Superiority over weight-specific CSE in regime (F); da4ml is better there.

### 18. What other researchers could reuse

- The open generator and cost model.
- The port/adder bound as a design law for any via-programmable arithmetic fabric.
- The independent checking harness (the translator for da4ml's op lists; the AIGER simulator).
- The da4ml input-layout finding.

### 19. Realistic path toward a full research project (about 2–4 months)

1. **Week 1:** read the ★ full texts (HNLPU, Ankhdjet, 2604.25183). Kill or narrow the novelty claim.
2. **Weeks 2–4:** bit-serial RTL generator; OpenROAD PnR of 256×256 macros on SKY130 and ASAP7 with all candidate lines present, vs g = 1 (the falsifying experiment). This needs the ORFS container.
3. **Weeks 5–6:** real BitNet-b1.58 layers (2B4T) for the (F) comparisons with da4ml and CBP. This needs huggingface.co access.
4. **Weeks 7–10:** integrate UBP into Ankhdjet's open macro; A/B at equal metal-only programmability; timing and energy with OpenSTA power; optionally a Tiny Tapeout / open-shuttle test vehicle.
5. **Paper:** target DAC/ICCAD/ASP-DAC (EDA angle), or ASPLOS/MICRO if combined with a system-level study.

### 20. The most important remaining research risk

**Novelty against full texts not readable in this session.**
- HNLPU (ASPLOS'26) and Taalas are the natural places for this construction to already exist.
- The second risk is physical: whether the candidate lines fit the programmable metal at g = 3–4.
