# 22 — UBP project closeout (canonical)

**Final classification: THESIS CLOSED — KILLED BY PREREGISTERED WEEK 2 PHYSICAL-FAIRNESS TEST**

This is the one document to read about UBP. Every number is taken from the cited records and is labelled:
- **MEASURED:** our SKY130 flow;
- **EXTRACTED:** OpenRCX parasitics, OpenSTA timing;
- **MODELED:** placement-parasitic or lumped timing;
- **DERIVED:** exact counts and proofs.

Nothing here replaces the historical documents. They stay as they were written, with short "superseded" notices where needed.

---

## 1. The thesis (final form)

> In weight-independent ("regime V") inference silicon, the base layers (cells, placement, lower metal) must not depend on the weights, which live only in the upper metal/vias. There, a bit-serial **universal block-pattern (UBP-g)** fabric shares accumulation *across neurons*: one generator per block of g inputs emits every signed subset sum of the block, and each neuron selects one of those lines per block by a via. On a physically realized frozen base with **R3 segmented access**, this fabric keeps a **≥ 1.5× area×time advantage** at its paper-facing operating point, **60% utilization**, over the strongest per-input fabric built under the same constraints and the same physical treatment.

The 1.5× bar and the 60% point were pre-registered for Week 2 (`21_WEEK2_TIMING_CLOSURE.md` §1.7; `19_FINAL_UBP_DECISION.md` §H).

## 2. Scientific motivation

- **The product setting.** Model-specific inference silicon became real in 2026: Taalas HC1, HNLPU (ASPLOS'26), BitROM, Ankhdjet. It keeps per-model mask cost low by programming weights only in upper metal or vias above a shared base.
- **The consequence.** That constraint switches off the classical way to shrink constant matrix–vector hardware: weight-specific common-subexpression elimination (CSE, e.g. da4ml), which needs base logic that depends on W.
- **The question.** Can structure that does *not* depend on W still share arithmetic across neurons, and does the sharing survive physical implementation?

## 3. Mechanism

- **Universal block patterns (DERIVED).**
  - Split the n inputs into blocks of g = 3.
  - A W-independent generator SGEN per block computes all 13 canonical signed patterns p·x_block; a negator SNEG supplies their negations. That is 26 lines per block, shared by all m rows: 548 lines for n = 64.
  - Row i's adder tree has ⌈n/3⌉ = 22 leaves instead of 64.
  - Programming rule: for each row and block, pick the line ±p that equals the row's three weights, or a local zero. It is exact for every ternary W.
  - The fabric meets a proven port lower bound with equality (Theorem 1).
- **Bit-serial implementation.**
  - Registered serial adders; INT8 activations sign-extended to 14-bit words, LSB first.
  - 14 cycles per word, latency 8 cycles.
  - This replaced a bit-parallel form whose generator carry chains cost 1.43× in delay (E5).
- **Weight-independent base.** Every cell, its placement and all met1–met3 wiring are fixed once and hashed. A weight program may only add met4–met5 nets and swap a via-site master (the local zero option).
- **Upper-layer programming.**
  - Each leaf is a *via site* whose input pad sits on met4.
  - Each line reaches the leaves through *taps* on met4.
  - A program is the set of met4/met5 nets from taps to via sites.
- **R3 segmented access.**
  - Every line runs as a spine in the base layers through K = 4 taps.
  - Rows are split into four segments; a leaf in segment s connects only to its line's tap in segment s.
  - Placement is W-blind and track-aligned: 22 bands, one per block.

## 4. What actually worked

| Result | Evidence | Label |
|---|---|---|
| **Functional exactness.** Every programmed netlist, including OpenROAD's routed netlist, simulated cycle-accurately against numpy W@x, with oracle and program mutations detected. This held for every design and program in Gates G2/R2/R3, Week 1 and Week 2 (Week 2 alone: 6 sized designs × 5 programs). | 16 §6, 20, 21 §3.2 | MEASURED |
| **Invariant frozen bases.** After every program: base ODB sha256 unchanged, identical placement and masters (except the zero-site swaps), routing only on met4/met5, byte-identical power grid. | 16 §6, 21 §3.2 | MEASURED |
| **Physical programming.** One frozen base accepts arbitrary ternary programs through met4–met5 alone, DRC-clean. This holds for UBP at 52% and 60%, A at 75%, and P2 at 60% (sized). | 19 §D, 21 §3.1 | MEASURED |
| **Routing closure (R3).** 5/5 programs reach 0 DRT violations in 1–14 iterations, where generic placement never routed and R2 closed only at 45%. | 19 §D | MEASURED |
| **Generator reproducibility.** `ubpgen` regenerates the validated R3 designs bit-for-bit, down to identical frozen-base ODB hashes; 12 routed programs match the historical records with 0 differences; 106 regression tests pass. | 20, 21 §2.1 | MEASURED |
| **Competitor evaluations.** Against the per-input serial fabric A and the frontier-style bit-plane popcount fabric P2, each in R2 and R3 access: hardwired (G3), fixed base with idealized taps (R3), and physically sized (Week 2). Via-ROM distributed arithmetic is dominated for ternary weights (Gate 3 width lemma). | 17, 19 §E, 21 §3.4 | MEASURED + DERIVED |
| **Hardwired regime (layout sees W).** 2.13× less routed area than A (E6); 1.84× better A×T than P2 (G3). | 10, 17 | MEASURED |

## 5. Evolution history

| Step | What happened |
|---|---|
| 13_FABLE_5_1 (origin) | UBP-g proposed. Adder counts ≈ g× lower (DERIVED); port bound proved; cell area 1.95× / 2.49× at iso-delay (E3, ABC delay model). The full-custom claim was withdrawn after structural hashing (E1-hashed). |
| E5 → E6 | Bit-parallel lost to its generator carry chains (1.43× delay). Bit-serial won in the hardwired regime: 2.13× routed area (E6). |
| G1 / G3 | The arithmetic is a likely-obvious composition (activation-group sharing + via-programmable base), so novelty rests on the physical characterization. 1.84× vs P2, hardwired. |
| G2 (generic placement) | With a frozen base, UBP's 548 lines did not route at any utilization down to 8%. Diagnosis: the placer clustered the taps. The binding cost is **reachability**: 4.33× more potential programmable connections than a per-input fabric (DERIVED). |
| R2 (structured crossbar) | Global routing passes, but detailed routing closes only at 45% (1.33× vs A). |
| R3 (segmented access) | Pre-registered; 5/5 programs DRC-clean at 52% and 60%; A×T 1.538× / 1.663× vs A with idealized taps, unsized spines and placement-parasitic tt timing. Classified PHYSICALLY VALIDATED — NOVELTY PROVISIONAL. |
| Week 1 | Parametric generator `ubpgen`; bit-exact reproduction of R3. |
| Week 2 | Fair driver sizing, physically implemented for every design; extracted three-corner sign-off. **Kill criterion fired (1.473 < 1.5).** |

## 6. The final decisive experiment (Week 2)

**Protocol** (pre-registered in 21 §1, committed before any build):
- **Tap drivers:** every tap is a real cell, a 2-site pad plus the smallest `buf_k` meeting 0.30 ns at its worst-case W-independent load, with its full area counted.
- **Spine drivers:** sized by the flow's own `repair_design` through a transition limit on the tap inputs.
- **Identical treatment:** the same rule for every fabric; W1–W5 for every design.
- **Sign-off:** OpenRCX extraction of the merged base + program; OpenSTA at tt, ss and ff.
- **Metric:** A×T = floorplan instance area / U × cycles per word × T.
- **Decision:** R = min over the sized competitors of A×T_cons(competitor) / A×T_cons(UBP) at 60%, with T_cons = the worst program at ss. **R < 1.5 → kill.**

| Design (all physically sized, EXTRACTED) | U | Area (µm²) | T, tt (worst program) | T, ss (worst program) | A×T at ss | Relative to UBP |
|---|---|---|---|---|---|---|
| **UBP3-R3** | 60% | 180,922 | 2.134 ns | 4.180 ns | **17.64 M** | 1.00 |
| **A-R2 (strongest)** | 75% | 358,018 | 2.184 ns | 3.888 ns | **25.99 M** | **1.473** |
| A-R3 | 75% | 358,979 | 2.219 ns | 4.380 ns | 29.35 M | 1.66 |
| P2-R2 (67% not routable) | 60% | 276,264 | 5.455 ns | 10.440 ns | 38.46 M | 2.18 |
| P2-R3 (67% not routable) | 60% | 277,225 | 6.040 ns | 11.245 ns | 41.57 M | 2.36 |

**Three readings of the same data:**
- **Nominal tt result:** R = 1.62 (W1 and worst program alike). tt is the corner the flow optimizes and closes the 3.0 ns clock at. It is real, but it is not the decision criterion.
- **Conservative slow-corner result:** R = **1.473**. This is the pre-registered decisive comparison: the worst program at ss, the corner where every design is slowest.
- **Pre-registered criterion:** R ≥ 1.5 at 60%, with every UBP program valid. UBP was valid (correct, 0 DRC, hold ≥ 0 at all corners). R was not ≥ 1.5, so **the kill fired.** 52% (secondary) gave 1.21.

## 7. Why the thesis was killed

**It did not fail because it was:**
- functionally incorrect: every program was exact;
- unroutable: every UBP program routed DRC-clean at 52% and 60%;
- an impossible programmable fabric: the frozen base was invariant under every program;
- unreproducible: the generator rebuilds everything from configuration.

**It failed** because, after realistic physical tap cost, implemented driver sizing, extracted timing and identical treatment of the baselines, the conservative advantage was **1.473×, not the required ≥ 1.5×.** Precisely:
1. **2,192 real taps cost area.** UBP needs 548 lines × 4 taps.
   - The historical accounting drew each tap as 2 sites carrying `buf_4` timing, i.e. a buffer without its area.
   - As physical cells (`buf_2` + pad, 6 sites) the taps add 10,971 µm²: **+6.5% of UBP's area**, against +0.7% for A-R2's 128 taps.
2. **Spine sizing changed placement and utilization.**
   - Every one of UBP's 548 spines needed a repeater: 551 violating nets at placement, 609 repeaters in the frozen base.
   - Utilization after placement rose from 60.4% to 64.1%.
3. **The slow-corner critical path moved to the shared tree-start broadcast.**
   - Sizing removed the programmable paths from the critical path at every corner (tap-input transition 1.32 → 0.30 ns).
   - At ss both UBP and A are then limited by the same W-independent control net, `st_tree`: one flop driving the first adder-tree stage of all 64 rows. The rule does not size it, for any fabric.
   - In UBP the flow's tt-driven buffering left that flop driving 25 loads and 256 fF directly: 1.471 ns at ss, **T_ss = 4.180 ns**. Before sizing, the same path was 3.893 ns.
4. **A-R2 handled the same situation better.** Its broadcast was buffered earlier (10 loads, 59 fF on the flop): **T_ss = 3.888 ns**, down from 4.208 ns unsized.
5. **The remaining advantage was insufficient.** R = 1.583 (area / U) × (3.888 / 4.180) = **1.473 < 1.5**. It stays below 1.5 under every area accounting except the historical 2-site tap convention (1.557), which the pre-registration excluded from the decision.

## 8. Claims explicitly withdrawn (never repeat as current conclusions)

1. **"UBP has a robust ≥ 1.5× advantage under full physical sign-off,"** including 19's "robust at 60%: ≥ 1.56× under every post-hoc check" and "defensible headline ≈ 1.6–1.7× at 60%." Week 2 measured 1.473× at the conservative corner.
2. **The full-custom (F) claim.** E1 showed 1.8–3.7× fewer adders than per-input trees. Structurally hashed trees come within 1.07–1.20×, and weight-specific CSE (da4ml) is better. Withdrawn in 13_FABLE (E1-hashed).
3. **Every pre-Week-2 fixed-base A×T comparison as a physical result:**
   - the R3 ratios 1.538× / 1.663× and their routed-parasitic variants (1.495× / 1.673×);
   - the post-hoc "driver-sized" what-ifs (1.478×, 1.598×, 1.725×, 1.795×).

   They used area-free tap buffers, unsized or STA-only-sized spines, and single-corner timing. They remain the record of the R3 decision under its own model, not current physical comparisons.
4. **E3's iso-delay cell-area ratios (1.95× / 2.49×) and the wire model as physical evidence.** They are ABC-delay-model numbers for the bit-parallel form, optimistic by E5's carry-chain finding.
5. **Hardwired-regime savings (E6's 2.13×, G3's 1.84×, the 5.8× select-wiring saving) as evidence for the weight-independent thesis.** A layout that sees W hides the reachability cost a W-blind base must pay (Lesson 6 in 01).
6. **"Novelty provisional"** as a live claim. No novelty claim is made any more.

## 9. Claims that remain true

1. **Exactness (DERIVED; MEASURED on every design and program).** The UBP-g programming rule computes W x exactly for every ternary W.
2. **Port bound (DERIVED, proved).** A universal fabric with port fan-in ≤ s needs P ≥ mn log₂3 / log₂(2s − 1) programmable ports; UBP-g meets it with equality.
3. **Frozen-base programmability works (MEASURED).** A weight-independent SKY130 base accepts arbitrary ternary programs through met4–met5 only, DRC-clean, invariant and exact: for UBP, A and P2, idealized and physically sized.
4. **R3 solves the reachability failure (MEASURED).**
   - Segmented access closes routing where generic placement (G2) and single-tap crossbars (R2) failed.
   - Reachability, not port or adder count, is the binding fixed-base cost of cross-neuron sharing. The interval/track-demand model behind this is a calibrated **model**, not a theorem.
5. **Nominal-condition advantage (EXTRACTED).** At tt, sized UBP3-R3 at 60% has 1.62× lower A×T than the strongest sized baseline, and 1.68–1.70× at ff. Real, but not the decisive criterion.
6. **The physical phenomenon and the negative result are reproducible.**
   - After fair sizing, the slow-corner period of both UBP and A is set by the shared W-independent control broadcast.
   - P2 no longer routes at 67% once sized.
   - UBP's conservative advantage is 1.473×.
   - All of it regenerates from `ubpgen/configs/suite_week2.json` (records in `ubpgen/results/week2/`).
7. **Hardwired regime (layout sees W; MEASURED).** E6's 2.13× routed area and G3's 1.84× vs P2 are valid **for that regime**.
8. **Via-ROM distributed arithmetic is dominated for ternary weights (DERIVED).** A K-input leaf is never narrower than K one-bit leaves for K ≤ 4, and its ROM grows as 2^K (Gate 3).

## 10. Final classification

**THESIS CLOSED — KILLED BY PREREGISTERED WEEK 2 PHYSICAL-FAIRNESS TEST**

- No Week 3.
- No rescue: the control broadcast will not be optimized, the taps will not be redesigned, the threshold will not be lowered.
- No "UBP v2."
- Reusable infrastructure: `23_REUSABLE_RESEARCH_ASSETS.md`.
- Lessons: `24_LESSONS_FOR_NEXT_THESIS.md`.

**Where the evidence is**

| What | Path (in this folder) |
|---|---|
| Week 2 dev log, decision, pre-registration | `21_WEEK2_TIMING_CLOSURE.md` |
| Week 2 records, sign-off reports, decision table | `ubpgen/results/week2/` (summary in `week2.md`) |
| Week 1 generator dev log / tables | `20_WEEK1_DEVLOG.md`, `ubpgen/results/week1_r3_tables/` |
| R3 decision (historical, superseded) | `19_FINAL_UBP_DECISION.md`, `16_GATE2_FIXED_BASE.md` §6, `09_PREREGISTRATION.md` (R3) |
| Gates G1–G3 | `15_GATE1_NOVELTY.md`, `16_GATE2_FIXED_BASE.md`, `17_GATE3_DA_COMPETITOR.md`, `18_GATES_VERDICT_AND_PACKAGE.md` |
| Origin (13_FABLE_5_1) | `../13_FABLE_5_1_SCIENTIFIC_DISCOVERY/00_START_HERE.md` |
| Generator | `ubpgen/` (README, configs, tests) |
