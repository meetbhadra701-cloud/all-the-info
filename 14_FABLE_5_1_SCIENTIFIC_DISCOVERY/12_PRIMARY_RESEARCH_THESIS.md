# 12 — Primary research thesis (Wave 14)

**Title:** Universal block-pattern sharing for via/metal-programmable hardwired inference silicon — its bit-serial form halves routed accumulation area at equal clock and throughput.

## Thesis statement (template form)

- **X, Y, Z.** Hardwired inference fabrics with per-input accumulation (X) give every neuron one accumulation input per weight site (Y). This happens when the base layers must stay weight-independent so that one mask set serves every model (Z).
  - X includes HNLPU value regions + POPCNT, Taalas pre-multiply-and-select, and Ankhdjet/TOM add/sub/skip.
  - Y costs m(n − 1) adder inputs.
- **M and P.** We hypothesize that weight-independent universal generators of all signed subset sums of g-input blocks, shared by every neuron with each leaf's line picked by a via (M), address Y. Hardwired fabrics lose the cross-neuron pigeonhole redundancy that runtime LUT accelerators exploit (P).
- **Q and R.** The closest prior art is runtime LUT-GEMM: T-MAC, LUT Tensor Core, TENET's mirror-half shared table (Q). It differs in one technical respect (R): its index is a runtime value, read through a mux from stored indices. Here the index is a fabrication-time via, so the mux disappears and the cost moves into select wiring. Only a *physical* evaluation can price that.
- **E.** Place-and-route at matched constraints against the per-input universal fabric can falsify M. It must enforce W-independence and validate every routed netlist functionally. **E5/E6 did not falsify it.**

## 1. Exact scientific problem

- **Setting:** regime V, i.e. model-specific inference silicon whose base layers are weight-independent and whose weights live only in upper metal/vias.
- **Question:** what is the minimum physical cost of the accumulation hardware there?
- **Precisely:** can a W-independent fabric beat the per-input fabric's m(n − 1) adders after routing, at matched timing?

## 2. Why it matters

- **Metal-only programmability is the stated NRE strategy** of every hardwired-LLM effort found:
  - HNLPU: 60 of 70 masks shared, M8–M11 programmable;
  - Taalas HC1: two masks;
  - Ankhdjet: a via-mask program.
- **Accumulation is what grows with weight count** in spatial fabrics. HNLPU reports 13,232 mm² at 5 nm for GPT-OSS-120B.
- **Stakes:** a ~2× cut in routed accumulation area would roughly halve the logic die area of such chips.

## 3. Strongest existing methods

**Regime V:**
- per-input add/sub/skip (Ankhdjet, TOM, BitROM-style accumulation);
- HNLPU in-neuron value regions + bit-serial POPCNT;
- Taalas per-input pre-multiplication with ROM-decoder selection.

All are g = 1 across inputs in every retrieved summary.

**Outside V:**
- runtime LUT-GEMM (T-MAC, LUT Tensor Core, TeLLMe, TENET, 2604.25183);
- weight-specific CSE (da4ml, Paar/Boyar–Peralta). This is regime F, not allowed in V.

## 4. Exact unresolved limitation

- Every neuron keeps ≈ one accumulator input per weight site. Sharing across neurons needs either W-specific base layers (CSE) or runtime indices with muxes (LUT).
- **No published regime-V fabric shares multi-input partial sums across neurons** (provisional; 07).
- **Its physical cost is unknown:** select wiring vs logic saving.

## 5. Proposed technical mechanism

**Per block of g inputs:**
- **GEN(g):** computes all (3^g − 1)/2 canonical signed subset sums (ternary W).
- **NEG:** one negated copy per pattern line, shared.

**Per neuron:**
- **TREE(⌈n/g⌉):** each leaf's via selects one line, its negation, or zero.

**Two realizations:**
- **H1.1 bit-parallel:** w-bit lines.
- **H1.2 bit-serial:** single-wire lines; generator, negators and tree built from registered serial adders; LSB-first; T = output-width cycles per word.

## 6. Mathematical / algorithmic formulation

- **Pattern selection:** row i, block b: q = W[i, b·g : (b+1)·g] ∈ {−1, 0, 1}^g. Leaf = sign(first nonzero of q) · line(canonical(q)), or 0 if q = 0.
- **Adders (exact, W-independent):** A_UBP = m(⌈n/g⌉ − 1) + ⌈n/g⌉((3^g − 1)/2 − g), versus A_g1 = m(n − 1).
- **Theorem 1** (previous session, proven): a universal fabric with fan-in s needs P ≥ mn·log₂3 / log₂(2s − 1) programmable ports. UBP-g meets it with equality.
- **Select-wiring connection count:**
  - UBP: m⌈n/g⌉ connections.
  - g1: m·n·(1 − p0) nonzero connections.
  - Ratio ≈ g/(1 − p0) = 5 at g = 3, p0 = 0.4. **Measured routed select-WL ratio (bit-serial): 5.8×.**

## 7. Why the mechanism might work (causal account)

1. **Pigeonhole amortization.** With m ≫ 3^g rows, generator cost is shared. Row trees shrink g-fold.
2. **Fewer programmable connections.** Each row makes n/g connections instead of ≈ 0.6n.
3. **In bit-serial form, a line is one wire and a leaf is one serial input.** Select wiring then no longer scales with word width. In E6 it routes at the same 75% utilization as g1; in bit-parallel form (E5) it does not.

## 8. What is technically novel (provisional)

- **The combination** (07 §2 element (d)), not found in any retrieved source: W-independent multi-input universal pattern generators, shared across all neurons (and all matrices fed by the same activation), with via selection per leaf.
- **The bit-serial realization feeding serial neurons with shared pattern streams.** The closest reference, HNLPU, feeds its popcount neurons with raw input streams.
- **The physical characterization:**
  - select-bus congestion costs bit-parallel UBP one utilization step;
  - bit-serialization removes it;
  - select wiring falls ≈ g/(1 − p0)-fold.
- **Caveat:** obviousness risk is **high** (07 §4). HNLPU's full text is unread.

## 9. What is reused

- Four-Russians/LUT-GEMM block precompute (mirror-half symmetry: TENET, T-MAC).
- Via-programmable fabrics (HNLPU, Taalas, Ankhdjet).
- Bit-serial arithmetic (standard; HNLPU).
- ORFS/OpenROAD, Yosys/ABC, SKY130.

## 10. Strongest prior-art objection

"This is TENET/LUT-GEMM with the index hardwired, obvious to any hardwired-silicon team; HNLPU or Taalas HC2 may already do it."

**Answer:**
- The arithmetic is conceded as known.
- The complete regime-V contribution is not found. Its physical outcome was not predictable: bit-parallel loses a utilization step, bit-serial does not.
- **Novelty remains provisional** pending full texts.

## 11. Required assumptions

- **(a) Ternary/binary weights.** int4 is wire-bound (HIST-INT).
- **(b) m ≫ 3^g**, for amortization.
- **(c) Upper-metal-only programmable routing with fixed placement behaves like E5/E6's placement-free routing** (untested).
- **(d) Standard-cell costs are representative** of the product's custom neurons (untested).
- **(e) No stronger regime-V baseline exists.** DA-via-ROM is untested (07 §3).

## 12. Initial experimental evidence (this session; NEW-OBS)

**E6 — bit-serial, 64×64, real 3.0 ns clock, equal throughput:**
- Routed area g1/UBP3 = **2.13×**, both DRC-clean at U = 75, the top of the tested range.
- Setup and hold met. UBP's minimum period is *shorter*: 2.08 vs 2.22 ns.
- Latency is +1 cycle (8 vs 7).
- Routed WL 1.98× lower; **select WL 5.8× lower**.
- Final routed netlists match numpy W@x, and the mutation control is caught.

**E5 — bit-parallel, 32×32:**
- UBP3 is routable at U = 60 but **fails global routing at U = 75** (congestion), where g1 routes.
- Pre-registered ratio **1.67×** (A5 met). It is 2.08× at equal utilization.
- Post-route natural delay is 1.10× that of g1.

Details: 10.

## 13. Result of the mechanism revision

- **Iteration 1 (H1.1 → H1.2).** The trigger was the pre-placement delay penalty of bit-parallel generator chains.
- **E5 later showed a different binding cost:** select-bus congestion (a lost utilization step). The pre-placement delay penalty shrank to 1.10× post-route.
- **H1.2 removed the congestion:** it routes at 75% like g1, keeps 2.13×, and meets the same real clock with CTS.
- **The revision is substantive in cost structure but not a new principle** (13 Q6).

## 14. Strongest baseline

**g1_V**, the per-input universal fabric: shared negation per input plus an n-leaf tree per neuron, each leaf via-selecting x, −x or 0.
- This is the ternary optimum of the HNLPU/Ankhdjet style under W-independence.
- It uses the same synthesis script, the same flow and the same constraints.
- **Not tested:** DA-via-ROM (07 §3), and HNLPU's custom-cell neurons.

## 15. Evaluator

ORFS PnR of hierarchy-preserving, W-independent netlists with a utilization sweep; details in 08.
- **Routed area** = synthesized cell area / U_max.
- **Invariants:** functional validation before and after PnR, a mutation control, and the W-independence invariant (A2).

## 16. Independent validity check

- **Our own** AIG simulators, combinational and cycle-accurate sequential, run against numpy, on the ORFS *final routed* netlists.
- The DEF wiring parser reproduces ORFS's total wirelength exactly.

## 17. Cheapest remaining falsifier

The **fixed-placement, upper-metal-only ECO test:**
1. Place each fabric once with W₁.
2. Re-route with W₂ using only met4–met5 for the W-dependent nets.
3. Require DRC-clean routing and a ratio ≥ 1.5 at matched utilization.

This is doable in OpenROAD in days. If bit-serial UBP fails where g1 passes, assumption (c) falls and the thesis weakens to "placement-aware only".

## 18. Generalization requirements

- **Scale:** n, m ≥ 256 (the ratio should rise toward g, per E1 closed forms).
- **Real BitNet b1.58 weights**, with real sparsity and correlation.
- **A second PDK**, e.g. ASAP7 or a 7/5 nm-class stack with more metal layers.
- **Multiple W samples.**
- **Energy/activity:** toggle rates of the shared lines.

## 19. What success establishes

At the tested scale, on SKY130, under placement-aware routing:
- A W-independent universal block-pattern fabric **halves routed accumulation area** relative to the per-input universal fabric at equal clock and throughput, in bit-serial form.
- Its via-programmed select wiring is **~5–6× lower**, not higher.
- The bit-parallel form pays a real congestion price (one utilization step), which bit-serialization removes.

## 20. What success does not establish

- Novelty.
- Superiority over DA-via-ROM or HNLPU's custom neurons.
- Behaviour with fixed placement / upper-metal-only programmability.
- Scaling to real layer sizes; advanced nodes.
- Energy.
- Real-model accuracy (the mechanism is exact, so accuracy is unaffected by construction; only quantization matters).

## 21. What other researchers could reuse

- The **regime-V PnR evaluator**: hierarchy-preserving W-independent netlists, the W-independence invariant checks, and post-PnR simulation against numpy.
- The DEF **select-wiring decomposition**.
- The **A2 lesson:** default dead-logic elimination silently makes universal fabrics W-specific.
- The E3 width-defect note.

## 22. Realistic implementation path

1. **Weeks 1–2 (gates):** full-text novelty check of HNLPU/Taalas (needs human access); DA-via-ROM analytic comparison; the fixed-placement ECO falsifier.
2. **Weeks 3–5:** n = 256–1024 tiles with real BitNet weights; ASAP7; activity-based power.
3. **Weeks 6–8:** integration into an open via-programmable macro (Ankhdjet-style host); a comparison write-up.

## 23. Most serious scientific risk

**A stronger regime-V baseline — ROM-based distributed arithmetic in a via-ROM** — or HNLPU's full text showing the same sharing. Either would make the result a characterization of a dominated, or already-known, design point.

## 24. What an expert reviewer should check next

1. HNLPU (ASPLOS'26) full text: any shared multi-input pre-summed streams?
2. Whether a transistor-level via-ROM DA beats UBP-serial per weight at an advanced node.
3. Whether E5/E6's placement freedom inflates the result (the fixed-placement ECO).
4. Whether the ≈ g/(1 − p0) select-wire law holds for trained weight statistics.
