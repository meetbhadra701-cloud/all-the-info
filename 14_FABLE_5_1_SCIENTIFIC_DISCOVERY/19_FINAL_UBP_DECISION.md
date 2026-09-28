# 19 — Final UBP decision (R3: the last layout revision)

> **Superseded (2026-09-28). UBP is CLOSED: THESIS CLOSED — KILLED BY PREREGISTERED WEEK 2 PHYSICAL-FAIRNESS TEST.**
> - The verdict below and the §H plan were overtaken by the pre-registered Week 2 test, which measured R = 1.473 < 1.5 at 60% (`21_WEEK2_TIMING_CLOSURE.md`).
> - The canonical account and the list of withdrawn claims, including "robust at 60%", are in `22_UBP_PROJECT_CLOSEOUT.md` (§8).
> - This file is kept unchanged as the record of the R3 decision.

**Verdict: PHYSICALLY VALIDATED — NOVELTY PROVISIONAL**

**Why not THESIS KILLED:** every pre-registered R3 criterion passed at the decisive 52% point, and again at 60%.
- One frozen base per density accepted all five weight programs through met4–met5 alone.
- Every program detailed-routed to **0 violations** at default router effort.
- The base was verified unchanged after every program (10 of 10), and every programmed netlist matched numpy W@x with its mutation control (10 of 10).
- Timing was met at 3.0 ns.
- A×T was **1.538× (52%)** and **1.663× (60%)** better than the strongest fixed-base competitor (the per-input serial fabric A at 75%, tap-credited).
- Gate 2, the gate left unresolved after R2, is closed.

**Why not READY FOR PAPER-SCALE RESEARCH DEVELOPMENT:**
- The narrow prior-art check on the exact claimed object found no identical object.
- But the full texts that could decide novelty are blocked in this environment, so only search summaries could be read: HNLPU (ASPLOS'26), the Taalas disclosures, TENET / T-MAC, and US 11,663,490.
- Gate 1 already classified the arithmetic as a likely-obvious composition. Novelty therefore rests on the physical results and the layout law, and it stays **provisional** until those texts are read.

**Standing qualification** (from the post-hoc checks; the pre-registered classification is unchanged):
- The ≥ 1.5× advantage is **robust at 60%**: ≥ 1.56× against every measured or driver-sized competitor under every timing rule, and 1.67× vs A with routed parasitics.
- It is **marginal at 52%**:
  - 1.495× vs A with routed parasitics and the worst program;
  - 1.478× vs P2 rebuilt with the same segmented taps and with its line drivers sized (§E; 16 §6.6).
- The paper-facing operating point is 60%.

**Consequence, as the decision run specified:** broad exploration stops, and UBP is the research project.

**Labels:**
- **MEASURED:** our flow — SKY130 HD, ORFS image 69df744e2b5c, own cycle-accurate simulator vs numpy.
- **MODELED:** placement-parasitic or lumped-RC timing.
- **DERIVED:** exact counts and models.
- **UNVERIFIED:** full texts that could not be read.

**Sources:** the pre-registration is in `09_PREREGISTRATION.md` (section R3), written, committed and pushed before any R3 physical result. Raw records: `experiments/results/G2/r3/`.

---

## The decisive experiment in one table

**Setup:** SKY130 HD, one 64 × 64 ternary layer, INT8 activations, 3.0 ns clock.
- The base (cells, placement, met1–met3 wiring) is built once per density and never changed.
- Five weight programs are routed on met4–met5 only.

| | R2 (structured, single tap) | **R3 (segmented taps): 52%** | **R3: 60%** |
|---|---|---|---|
| Programs with 0 DRT violations (default effort) | 0 of 1 tested at 52% (117 left); 1 at 45% | **5 / 5** (1–14 iterations) | **5 / 5** (1–13 iterations) |
| Base changed by any program | never | **never** (hash, placement, masters, layers, power grid) | **never** |
| Programmed netlist = numpy W@x, mutation detected | ✓ | **5 / 5** | **5 / 5** |
| Timing at 3.0 ns (base / programmed) | met | met (+0.976 / ≥ +0.888 ns) | met (+1.022 / ≥ +0.788 ns) |
| A×T, pre-registered rule (µm²·ns) | 10.71e6 at 45% | **9.26e6** | **8.57e6** (worst program 8.77e6) |
| vs A at 75% (14.25e6) | 1.33× at 45% | **1.538×** | **1.663×** (worst 1.624×) |
| vs P2 at 67% (14.93e6) | 1.39× at 45% | **1.612×** | **1.743×** |
| Rigor check: routed parasitics, worst program, vs A | — | **1.495×** (break-even) | **1.673×** |
| vs P2 rebuilt with R3's taps (pre-registered fairness point), measured: 17.88e6 | — | 1.931× | 2.088× |
| Post hoc: vs that P2-R3 with spine drivers sized: 13.69e6 | — | **1.478×** | 1.598× (1.725× with B sized too) |

**Pre-registered rule:** at 52% (decisive), every criterion passes, so the thesis survives Gate 2. The 60% strength point also passes.

**Post-hoc checks:** they leave the classification unchanged but move the claim. 60% is the robust operating point, and 52% is at break-even.

---

## A. Exact contribution

A bit-serial universal-block-pattern (UBP) fabric for ternary matrix–vector multiplication can be built on a genuinely weight-independent base, with every weight matrix programmed only through the two upper metal layers. Under the same constraint it keeps a ≥ 1.5× area×time advantage over the strongest per-input fabric: robustly at 60% utilization (≈ 1.6–1.7×), and at break-even at 52%.

- **Base:** cells, placement and met1–met3 wiring are fixed once.
- **Arithmetic:** each row selects, per block of three inputs, one of 26 shared bit-serial lines. The lines carry all signed subset sums of the block, generated once for all rows.
- **What is known and what is new:** this is an instance of known activation-side partial-sum sharing. What is new is its weight-independent physical realization, and the quantitative law behind it.
- **The law:**
  - The fixed-base cost of cross-neuron sharing is **reachability**: 4.3× more programmable lines per input than a per-input fabric. Adder count and port count are not the binding cost.
  - Connectivity-driven placement cannot absorb it: no routable utilization down to 8%.
  - A structured crossbar absorbs it only at the global-routing level.
  - A W-blind **segmented-access** organization absorbs it fully. Each line runs as a spine in the fixed layers with one programmable tap per quarter of the rows.
- **Measured result (SKY130):**
  - One frozen base per density routes five different 64 × 64 ternary programs DRC-clean at 52% and 60% utilization, and every programmed netlist is functionally exact.
  - A×T is 1.54× (52%) and 1.66× (60%) better than the per-input serial fabric, and 1.61× / 1.74× better than the frontier-style bit-plane popcount fabric.
  - Under the most conservative timing (routed parasitics, worst program), 52% is the break-even point (1.495×) and 60% stays robust (1.67×).
  - **The popcount fabric with the same segmented taps** (the pre-registered fairness point) is slower as built (1.93× / 2.09×).
    - With its line drivers sized (post hoc), it becomes the strongest competitor.
    - UBP3 then leads by 1.48× at 52%, and by 1.60× at 60% (1.73× when both designs are sized).
  - **The defensible headline is ≈ 1.6–1.7× at 60%.**

## B. Algorithm / architecture (precise enough to re-implement)

**Arithmetic (UBP-g, g = 3; bit-serial).**
- **Input:** x ∈ INT8ⁿ as two's-complement serial words, LSB first. Words are sign-extended to the output width w_o = 14, so one word takes 14 cycles; `start` marks bit 0.
- **Blocks:** the n inputs are split into ⌈n/3⌉ blocks of 3 consecutive inputs; the last block may be shorter.
- **Canonical patterns:** for a block of size g, 𝒫_g is the set of non-zero ternary g-vectors whose first non-zero entry is +1. |𝒫_3| = 13, |𝒫_1| = 1.
- **Generator SGEN(g), one per block, W-independent:**
  - It emits, every cycle, one serial bit of each pattern value p·x_block for all p ∈ 𝒫_g.
  - It uses registered serial adders and subtractors: sum = a ⊕ b ⊕ c, carry = maj(a, b, c), reset at `start`; subtraction complements b and presets carry-in to 1.
- **Negator SNEG, one per pattern:** it emits −(p·x_block) serially (~a + 1), and delays the positive stream by one cycle to keep the two aligned.
- **Lines:** each block has 2|𝒫_g| lines (26 for g = 3), shared by all m rows. In total there are 548 lines for n = 64.
- **Row i:** a registered serial adder tree STREE over ⌈n/3⌉ leaves (22 for n = 64). Leaf (i, b) is one line of block b or the constant 0.
- **Programming (the only W-dependent step).** For row i and block b, let q = (w_{i,3b}, w_{i,3b+1}, w_{i,3b+2}).
  - If q = 0, the leaf takes the site's local zero option.
  - Otherwise let s be the sign of q's first non-zero entry. The leaf is line pp_b(p) if s > 0 and pn_b(p) if s < 0, where p = s·q ∈ 𝒫_3.
  - This is exact for every W: y_i = Σ_b (s·p)·x_block = Σ_j w_ij x_j.
- **Timing:** latency 8 cycles from word start to the first output bit; throughput 14 cycles per word.

**Physical organization: the fixed base, W-blind (R3).**
- **Layers:** the base holds every cell plus all wiring on met1–met3. Programs use met4–met5 nets only, plus identical-footprint via-site master swaps (the local zero option).
- **Via site VSITE,** one per leaf: 4 sites wide. Its A pin (met4 pad, 1.24 × 1.12 µm) is programmable; its Z pin (li1) drives the leaf.
- **Line access:**
  - Every line has **K = 4 taps** (LTAP2: 2 sites wide, single-track met4 pad 0.62 × 1.12 µm).
  - The four taps sit on the same base net. The base routes the line as a **spine** on met2/met1 from its driver through its four taps.
  - Rows are split into four segments of 16. A leaf in segment s may connect only to its line's tap in segment s.
- **Placement** (FIRM before global placement):
  - 22 vertical **bands**, one per block, of equal width.
  - The band's 64 via sites sit in one column at the band centre, row i at height (i + 0.5)/64, with pads centred on met4 tracks.
  - Tap (line t of the band's T lines, segment s) sits at height (s + (t + 0.5)/T)/4, at the line's home x = (t + 0.5)/T of the band width, track-aligned.
  - Everything else is placed by the tool from base connectivity only.
- **Area:** 4 taps × 2 sites = 8 sites per line, identical to one 8-site tap. Base cell area is 169,952 µm², the same as R2.

## C. Mathematical results (with assumptions)

1. **Exactness (DERIVED).** Every non-zero ternary g-vector is ±p for exactly one p ∈ 𝒫_g, so the programming rule above computes W x exactly for every W ∈ {−1, 0, 1}^{m×n}.
2. **Port bound — Theorem 1 (proven in the previous session).**
   - *Model:* a DAG of two-input adders with fixed base connectivity. Port p has s_p options: pre-built candidate signals, one of which may be 0; a non-zero candidate may be taken with either polarity. A fabric is *universal* if some programming realizes y = W x for every ternary W.
   - *Claim:* a universal fabric with port fan-in ≤ s has P ≥ m n log₂3 / log₂(2s − 1) programmable ports, and A ≥ (P − m)/2 adders.
   - *UBP-g meets the port bound with equality* when g | n: P = m⌈n/g⌉ and 2s − 1 = 3^g.
3. **Reachability, not port count, sets the fixed-base cost (DERIVED; new in G2/R3).**
   - In a W-blind base, every port of block b must be able to reach each of its block's 2|𝒫_g| = 3^g − 1 lines. That is m⌈n/g⌉(3^g − 1) potential connections, against 2mn for a per-input fabric: a ratio of (3^g − 1)/(2g) = **4.33 at g = 3**.
   - Theorem 1's port minimum is bought with this reachability.
   - **Interval model.** The programmable met4 demand of a band is the maximum overlap of its (line, segment) nets' vertical spans.
   - **Calibration on R2 (single tap, K = 1):** peak / usable tracks is 0.96 at U45 (closed), 1.05 at U52 and 1.15 at U60 (neither closed).
   - **K = 4 segmentation** cuts the worst peak from 23 to 12 lines per band on development matrices. The price is base spine wiring of about (K − 1)/K of the band height per line.
   - This is a model, not a theorem. R3's outcome is its test.
4. **DA width lemma (DERIVED).**
   - A ternary K-input distributed-arithmetic leaf needs ⌈log₂(2K + 1)⌉ ≥ K bits for K ≤ 4, so it never reduces compressor input bits below the K = 1 popcount fabric.
   - Its ROM grows as 2^K (Gate 3).

## D. Physical evidence (MEASURED unless labelled)

**Everything below is on one frozen base per density.**
- The base is built once, with DRC 0 on met1–met3; its ODB sha256 is recorded before any program is applied.
- Programs use met4–met5 plus the local zero option.
- Base cell area is 169,952 µm² at both densities, including 1,408 via sites and 2,192 taps.

**R3, per program.** Timing is MODELED with placement parasitics, as pre-registered. Every row has 0 GRT overflow and 0 residual DRT violations.

| U | W | DRT iterations to 0 | GRT met4 / met5 | met4 / met5 WL (µm) | via4 | Setup / hold / programmable-path WS (ns) |
|---|---|---|---|---|---|---|
| 52% | W1 | 14 | 16.5% / 7.5% | 60,063 / 4,236 | 772 | +0.888 / +0.192 / +1.094 |
| 52% | W2 | 13 | 17.1% / 7.9% | 62,396 / 4,464 | 823 | +0.888 / +0.192 / +1.082 |
| 52% | W3 | 7 | 8.9% / 4.0% | 32,097 / 1,905 | 361 | +0.888 / +0.192 / +1.071 |
| 52% | W4 | 14 | 16.5% / 7.4% | 60,641 / 5,174 | 937 | +0.888 / +0.192 / +1.073 |
| 52% | W5 | 1 | 3.5% / 0.5% | 12,533 / 23 | 4 | +0.888 / +0.192 / +0.996 |
| 60% | W1 | 13 | 18.1% / 7.8% | 57,018 / 3,340 | 685 | +0.840 / +0.213 / +0.840 |
| 60% | W2 | 13 | 18.8% / 8.6% | 58,847 / 4,190 | 789 | +0.939 / +0.213 / +0.998 |
| 60% | W3 | 7 | 9.7% / 5.1% | 30,419 / 1,356 | 253 | +0.939 / +0.213 / +0.971 |
| 60% | W4 | 13 | 18.1% / 6.6% | 57,409 / 4,148 | 879 | +0.825 / +0.213 / +0.825 |
| 60% | W5 | 1 | 3.9% / 0.6% | 11,649 / 0 | 0 | +0.788 / +0.213 / +0.788 |

**Base:**
- 52%: core 324,261 µm²; setup / hold +0.976 / +0.268 ns; base met2 GRT usage 61.2% (the line spines).
- 60%: core 281,558 µm²; +1.022 / +0.293 ns.

**Invariant-base verification, after every program (10 of 10 pass):**
- base ODB sha256 unchanged;
- every instance (14,027 at 52%, 14,078 at 60%) has the same location, orientation and status;
- master changes equal exactly the program's zero-site swaps;
- routing only on met4/met5, only the M4M5 via, and no base net re-routed;
- power grid byte-identical.

**Correctness (10 of 10):** the complete programmed netlist written by OpenROAD, simulated by our own cycle-accurate simulator, matches numpy W@x, and flipping one weight is detected.

**Area × time** (base cell area / U × 14 cycles × T, with T = 3.0 − min(base WS, programmable-path WS)):

| U | T (ns), W1 / worst program | A×T (µm²·ns) | vs A (U75, 14.25e6) | vs P2 (U67, 14.93e6) |
|---|---|---|---|---|
| 52% | 2.024 / 2.024 | 9.26e6 | 1.538× | 1.612× |
| 60% | 2.160 / 2.212 | 8.57e6 / 8.77e6 | 1.663× / 1.624× | 1.743× / 1.702× |
| 52%, routed parasitics | 2.024 / 2.082 | 9.26e6 / 9.53e6 | 1.538× / **1.495×** | 1.612× / 1.567× |
| 60%, routed parasitics | 2.118 / 2.147 | 8.40e6 / 8.51e6 | 1.696× / **1.673×** | 1.778× / 1.753× |
| 60%, spine drivers sized (post hoc; +2,057 µm²) | 1.978 / 1.978 | 7.94e6 | 1.795× | 1.881× |

The comparison against P2 rebuilt with the same segmented taps, and the driver-sizing sensitivity, are in §E and 16 §6.6.

**History of the same question (all MEASURED):**
- **E6, hardwired, the layout sees W:** 2.13× less routed area than the per-input serial fabric.
- **G3, hardwired:** 1.84× better A×T than P2.
- **G2 with generic placement:** unroutable at every utilization down to 8%.
- **R2, structured single-tap:** global routing passes; detailed routing closes only at 45% (1.33× vs A).
- **R3, segmented taps:** closes at 52% and 60%.

## E. Strongest competitors

**Measured fixed-base competitors.** All share one frozen-base protocol: base met1–met3, programs on met4–met5, the same ORFS flow and the same A×T rule. Ratios are the competitor's A×T divided by UBP3's.

| Competitor | What it is | A×T (µm²·ns) | UBP3 at 52% (9.26e6) | UBP3 at 60% (8.57e6 as built; 7.94e6 sized) |
|---|---|---|---|---|
| **A** at 75%, tap-credited | Per-input bit-serial fabric: one line pair per input, registered serial adders | 14.25e6 | **1.538×**; 1.495× with routed parasitics and worst program | **1.663×**; 1.673× with routed parasitics; 1.795× sized |
| **P2** at 67%, tap-credited | Pipelined bit-plane popcount: the spatial form of the frontier's DA-K=1 arithmetic (HNLPU POPCNT, BitROM, Ankhdjet) | 14.93e6 | 1.612× | 1.743× / 1.881× |
| **P2-R3** at 67%, measured (pre-registered fairness point) | P2 with exactly R3's segmented taps. Valid point: DRC 0, W4 closes in 14 iterations, invariant, = numpy | 17.88e6 | 1.931× | 2.088× / 2.253× |
| **P2-R3, spine drivers sized** (post hoc) | The same, with 128 line drivers at drive 4 (+561 µm²) | **13.69e6** | **1.478×** | 1.598× / **1.725×** |
| P2-R3, base-only-T bound | Idealized: programmable-line delay set to zero | 12.61e6 | 1.362× | 1.472× / 1.589× |

**Competitors evaluated analytically, or from the literature.** "Summary" means only search-result summaries could be read.

| Competitor | Mechanism | Relation to UBP3-R3 | Evidence |
|---|---|---|---|
| **Via-ROM distributed arithmetic** (Peled–Liu 1974; White 1989) | Per-output ROM of weight subset sums, indexed by input bits | The transpose of UBP. For ternary W, a K-input leaf is never narrower than K one-bit leaves (K ≤ 4), and the ROM grows as 2^K. **Dominated** (Gate 3). | DERIVED + MEASURED |
| **Ankhdjet** (open compiler, mask-programmed ternary compute-in-ROM, SKY130) | One NMOS per weight; drain via-routed to BL+ / BL− / GND; time-multiplexed, g = 1 | Far denser (2.21 µm² per weight), but ≈ 512 cycles per dot product → ≈ 10–40× worse A×T. An area-first point with no cross-output sharing. | Primary source read (RTL) |
| **HNLPU** "Sea-of-Neurons" (ASPLOS'26) | Structured ASIC: weights in M8–M11 metal, 60 of 70 masks shared. Per summaries: 16 value regions per neuron, POPCNT on bit-serial inputs | **The closest host-fabric prior art.** It groups inputs by weight value *within* a neuron; UBP shares activation-group sums *across* neurons. If its full text shows cross-neuron shared multi-input sums with W-blind metal selection, UBP's architecture is anticipated. | Summary; full text blocked |
| **Taalas HC1** | Mask ROM encoded by via presence in top metal; "Multiply-Select-Add": ROM → 3-to-8 decoder → one-hot select of pre-multiplied values; 2 custom masks | Universal precompute per *input* (g = 1) with decoded selection. UBP: per *3-input block*, with bare-via selection. | Summaries |
| **T-MAC, LUT Tensor Core, TENET, TeLLMe, 2604.25183** | Activation-group tables shared across outputs; mirror-half symmetry. TENET shares precompute across its TLUT PEs | **The same arithmetic, runtime-indexed** (index memory + mux). UBP replaces the index with a fabrication-time via. | Summaries |
| **US 11,663,490**, "Partial sum pre-computation to implement quantized neural networks on programmable devices" | Per the abstract: a neuron's MACs become memory lookups of pre-computed outputs for all input combinations, on FPGAs | Per-neuron, W-specific tables (the LogicNets / TLMAC family), not W-independent shared activation sums with fixed selection. Assignee and claims unread. | Search abstract; USPTO blocked |
| **CSHM / alphabet-set multipliers** (~2002–04) | Universal precompute of odd multiples, shared across constant multipliers, with per-constant select | The g = 1 principle, decades old. UBP is its signed g = 3 block form with via selection. | Summaries |
| **Four Russians / Lupanov** | Shared subset-sum tables of column blocks | The mathematical core | Textbook |
| **Segmented channel routing** (Greene, Roychowdhury, Kaptanoglu, El Gamal, DAC 1990; Actel antifuse FPGAs; US 5,598,343) | Fixed wire segments joined by programmable connections | **The layout principle behind R3's segmented access.** R3 applies it to W-blind line reachability; it is not a new interconnect idea and must be cited. | Summaries |
| **Structured ASIC / via-configurable gate array + W-specific CSE** | A generic via-programmed host running weight-specific shared-adder logic | A plausible competitor that was **not built**. It remains a missing baseline. | Not measured |
| **BitROM, TOM, YOLoC** (compute-in-ROM) | Per-weight accumulation, or ternary ROM synthesized as logic | No cross-output activation sharing | Summaries |

**Net:**
- No retrieved source contains a W-independent base that generates all signed block patterns once and selects them per row by via, let alone its physical characterization.
- The arithmetic and the interconnect principle are both known.
- The contribution is the physical law and its measured consequences (§A, §C3).

## F. Scope

- **Weights:** ternary {−1, 0, +1}. Binary ±1 is the special case with 2^(g−1) patterns per block.
- **Activations:** INT8, two's complement.
- **Bit-serial,** 14 cycles per 14-bit output word. The bit-parallel form is excluded; it lost a utilization step in E5.
- **Measured size:** one 64 × 64 layer, g = 3, K = 4.
- **Programmable-layer assumptions:**
  - Weights change only met4–met5 wiring (and via4) plus a local zero option. The zero option is modelled as an identical-footprint master swap standing for a via choice.
  - met1–met3, the cells and their placement are frozen. The line spines live in the base.
- **Technology:**
  - SKY130 HD: met4 0.92 µm pitch, met5 3.4 µm, 0.8 µm via4. Base PDN is met1 rails only (IR out of scope).
  - The via sites and taps are abstract cells (buffer-modelled via stacks).
- **Timing:**
  - Pre-registered: the base's routed timing plus placement-parasitic timing of the programmed netlist.
  - Rigor check: extracted base parasitics plus routed-geometry lumped RC for every programmable net.

## G. Remaining risks

Ordered by how likely each is to change the claim.

1. **Novelty is provisional.**
   - The decisive full texts are unread: HNLPU, the Taalas filings (including the WO2025217724A1 applicant), TENET / T-MAC, and US 11,663,490.
   - Gate 1 already rates the arithmetic a likely-obvious composition. If HNLPU's neurons consume shared multi-input sums across neurons, the architecture is anticipated, and the paper shrinks to the physical characterization.
2. **The margin is thin, and only 60% is robust.**
   - At 52%: 1.538× pre-registered; 1.495× with routed parasitics and the worst program; 1.478× against a driver-sized P2-R3.
   - At 60%: 1.56–1.80× across all treatments. The advantage is a factor of about 1.6, not an order of magnitude, so a stronger baseline or a better P2 layout could erode it.
3. **The timing methodology is approximate.**
   - The pre-registered timing is placement-parasitic STA, with an effective period T = 3.0 − WS (no re-closure at the tighter clock).
   - Line spines are untimed in the base: the driver sizing a production base would need was only simulated (D-R3.4), not implemented.
   - One corner (tt, 25 °C, 1.8 V); no SI or IR analysis. The routed-parasitic check uses a lumped (pessimistic) RC for program nets.
4. **Baseline quality.**
   - A and P2 went through the same flow, but each is one design point.
   - P2-R3 shows that line-driver design alone moves a baseline by 1.3×.
   - A W-specific structured-ASIC CSE baseline was never built.
5. **Technology and abstraction.**
   - SKY130 has only two coarse programmable layers (met4 0.92 µm, met5 3.4 µm, 0.8 µm via4).
   - Via sites and taps are abstract cells: buffer-modelled via stacks.
   - The zero option is a master swap standing in for a via choice.
   - The PDN is met1 rails only.
   - There is no LVS or GDS signoff of programmed designs; the evidence is DRT-clean routing plus netlist-level verification.
6. **Scale.**
   - Only 64 × 64 was measured.
   - Programmable lines grow with n, and sinks per line with m. K = 4 was chosen for 64 rows.
   - The segmentation law must be re-measured at 256–1024.
7. **Real weights.** Only synthetic random and structured W were tested. BitNet b1.58 weights were unavailable (HuggingFace is blocked here). W3 and W5 suggest structure helps routing, but that is untested on real models.
8. **Energy is unmeasured.** 548 bit-serial lines toggle every cycle, against 128 for the per-input fabric. The A×T advantage may not carry over to energy.
9. **Metric scope.**
   - A×T uses synthesized cell area / U, not the full die with I/O and PDN; this is consistent across designs.
   - One placement seed; one base per density.

## H. Paper-scale plan (4–8 weeks)

| Week | Work | Deliverable / decision point |
|---|---|---|
| 1 | **Parametric generator.** UBP-g fabric (n, m, g, K), bands, taps and spines. Per-input baselines A and P2 built with the **same** segmented access **and the same sized spine drivers** (fairness by construction). The invariance, verification and collection scripts become the test suite. | Reproduces the R3 tables from one command. |
| 2 | **Line-driver timing closure, for every design.** W-blind worst-case load constraints on tap outputs; sized spine drivers placed and routed, not just simulated; extracted-parasitic STA of merged base + program (OpenRCX); three corners. Re-measure P2-R3 physically with sized drivers. | Removes the W5 spine-driver path and settles the post-hoc 1.48× point. **Kill point:** at the operating density (60%), UBP must stay ≥ 1.5× over the best driver-sized baseline. |
| 3 | **Real weights.** BitNet b1.58 layers (must be supplied locally; HuggingFace is blocked in this environment). 64 × 64 and 256 × 256 tiles through the full five-program protocol. | Real-weight programs route and verify like random ones. |
| 4 | **Scale and ablations.** 128 × 128 and 256 × 256. K ∈ {2, 4, 8}. g ∈ {2, 3, 4}. Utilization sweep 45–70% for B, A and P2. Re-derive and measure the reachability model at scale (sinks per line grow with m). | Where the segmentation law breaks; the best K(m). |
| 5 | **Technology.** A predictive advanced PDK (e.g. ASAP7) with a two-thin-layer programmable stack, and a single-via-layer programming variant. | Does the reachability cost shrink or grow with finer upper metal? |
| 6 | **Energy.** Activity-based power from real activation traces: B vs A vs P2. | pJ per MAC-equivalent; the energy × time ratio. |
| 7 | **Theory.** Formalize the reachability bound: potential-connection counting plus a band track-density lower bound for W-blind bases. The segmentation trade-off (spine vs programmable demand). The port bound and DA lemma already exist. | A stated theorem with assumptions, or an explicitly labelled model. |
| 8 | **Paper and artifact.** Figures: R2 vs R3 layouts, congestion maps, DRT convergence, A×T vs U, timing sensitivity. Tables for all measured points. Open-source release of scripts, cells, programs and verification. Novelty closure by full-text / expert review of HNLPU, the Taalas filings, TENET / T-MAC and the partial-sum-precompute patent. | Submission-ready draft, with novelty wording fixed by that review. |

## I. Candidate paper thesis

> "In weight-independent, metal/via-programmable inference silicon, sharing computation across neurons moves the cost from adders to programmable-line reachability. We quantify that cost and show that connectivity-driven placement cannot pay it. A W-blind segmented-access layout does: line spines sit in the fixed layers, and each quarter of the rows gets its own programmable tap.
>
> On this base, a bit-serial universal-block-pattern fabric accepts arbitrary ternary matrices through the top two metal layers of a frozen SKY130 base. Every program is DRC-clean and functionally exact. At 60% utilization, area×time is 1.6–1.7× lower than the best per-input fabrics under identical fixed-base constraints, including a popcount fabric given the same segmented access and sized line drivers. At 52% it is at break-even (≈ 1.5×)."

The claim is **the characterization and the layout methodology, with measurements**. It is not the invention of partial-sum sharing, and not a production-grade accelerator.

## J. Strongest reviewer attack

> "This is LUT-GEMM with the index hard-wired, laid out with 1990s segmented-channel routing. The arithmetic is known (T-MAC, TENET), the host fabric is known (HNLPU's Sea-of-Neurons, Taalas), and segmentation is textbook FPGA interconnect.
>
> The advantage is 1.5× at your pre-registered density and disappears under your own stricter checks: 1.495× with extracted parasitics, and 1.478× against a popcount fabric whose line drivers you sized in one STA run. It is measured on one 64 × 64 layer with random weights, in a 130 nm open PDK with two coarse programmable layers, and never signed off at GDS level.
>
> Why should anyone believe the advantage survives a competently built baseline, real weights, 256 × 256 tiles, and an advanced node with a thin, dense programmable stack?"

**What can be rebutted now:**
- **The physical consequences were not predictable from any reference:**
  - the sign of the result flips with implementation form (bit-parallel loses in E5; bit-serial wins 2.1× in E6);
  - the same logic is unroutable under connectivity-driven placement (G2);
  - it routes only at GRT level under a crossbar (R2);
  - it closes DRC-clean only with segmented access (R3).
  
  The reachability law explains all four and predicted R3's outcome beforehand (interval model, pre-registered).
- **At 60%, the advantage survives every symmetric treatment tried:** ≥ 1.56× against every measured or driver-sized competitor; 1.725× with both sides sized; 1.67× vs A with routed parasitics.
- **The weight-independence is verified, not asserted:** for 10 of 10 programs, the hash, placement, masters, layers and power grid were checked, and every netlist was simulated against numpy with a mutation control.

**What cannot yet be rebutted:**
- novelty against the unread full texts;
- scale;
- real weights;
- an advanced node;
- signoff;
- energy.

The 4–8-week plan (§H) takes these in that order of risk, each with a kill point.
