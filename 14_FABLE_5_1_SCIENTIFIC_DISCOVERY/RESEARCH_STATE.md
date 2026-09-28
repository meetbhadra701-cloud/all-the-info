# RESEARCH_STATE — Wave 14 + gates G1–G3 + final UBP decision run (R3) + development Weeks 1–2 (current)

> **CURRENT STATUS (2026-09-28): UBP IS CLOSED — THESIS CLOSED — KILLED BY PREREGISTERED WEEK 2 PHYSICAL-FAIRNESS TEST** (R = 1.473 < 1.5 at 60%, conservative corner).
> - The state below is the record at the end of Week 2. Its "unresolved questions" and "next action" are not pursued.
> - Closeout: `22_UBP_PROJECT_CLOSEOUT.md`.
> - Reusable assets: `23_REUSABLE_RESEARCH_ASSETS.md`.
> - Lessons: `24_LESSONS_FOR_NEXT_THESIS.md`.

**Labels:**
- **HIST-OBS:** previous experiment.
- **HIST-INT:** previous reasoning.
- **NEW-OBS:** this session.
- **NEW-INF:** inferred.
- **NEW-HYP:** proposed.

## Objective

- One technically distinct mechanism for a consequential semiconductor/EDA problem, tested against the strongest baseline.
- At most 2 evolution iterations; a meta-review; one decision class.
- Commit locally only. **No push without authorization.**

## Established historical facts

- **HIST-OBS:** Waves 3–11 had no survivor.
- **HIST-OBS:** 13_FABLE_5_1 established UBP-g in regime V.
  - Adders ≈ g× lower; Theorem 1 (port bound, met with equality).
  - E3 cell ratios, plus a one-bit tree-width defect found this session (01).
  - The (F) claim was withdrawn.

## Problem tree (03)

- **P1 (primary):**
  - H1.1 (bit-parallel): **weakened**.
  - H1.2 (bit-serial): **survivor**.
  - H1.3: merged.
- **P2 (reserve):** not executable.
- **P3:** killed (CSE).

## Primary hypothesis and exact mechanism

- **H1.2:** W-independent SGEN(g) per block (all canonical signed subset sums, serial) + SNEG per line + STREE(⌈n/g⌉) per neuron, with via selection per leaf. Registered serial adders; T = output-width cycles per word.
- **Reserve:** H2.1 (adapter-as-redundancy).

## Strongest prior art (07)

- **Arithmetic:** TENET, T-MAC and LUT Tensor Core, with runtime indices.
- **Hardwired fabrics** (HNLPU, Taalas, Ankhdjet, TOM, BitROM): g = 1.
- **The combination:** not found. Obviousness is high; novelty is provisional.
- **Untested competitor:** DA-via-ROM.

## Critical assumptions (status after the gates)

- **(c) Fixed-base programmability.**
  - **Generic placement:** FAILED (K2b).
  - **Structured W-blind crossbar (R2):** passes at GRT level; detailed-route closure on met4 fails at useful U.
  - **Segmented line access (R3):** **HOLDS.** All 5 W are DRC-clean at 52% and 60%, and the base is invariant (NEW-OBS).
- **(e) No stronger regime-V baseline:**
  - Holds in the hardwired regime (G3; DA dominated; P2 1.84× worse).
  - On the R3 fixed base it holds against every measured competitor: A at 75% 1.54× / 1.66×; P2 1.61× / 1.74×; P2 with R3 taps 1.93× / 2.09×.
  - A driver-sized P2-R3 (post hoc, STA-only) gives 1.48× at 52% and 1.60–1.73× at 60%.
- **Novelty:** G1 → likely obvious composition. Only the physical characterization is new.

## Experimental status (NEW-OBS; final numbers in 10)

**E6 (bit-serial, n = 64):**
- g1/UBP3 routed area **2.13×**; both U_max = 75; timing met at 3.0 ns (2.08 vs 2.22 ns).
- +1 cycle latency; select WL 5.8× lower.
- Post-PnR validated. **A6 MET.**

**E5 (bit-parallel, n = 32):**
- UBP3 U_max = 60 (congestion at 75); g1 U_max = 75.
- Ratio 1.67× (A5 MET narrowly; 1.59× on the tie-corrected basis). Delay 1.10× at equal U, 1.12× at U_max.
- Post-PnR validated.

**Amendments:**
- **A1:** relaxed E5 clock.
- **A2:** W-dependent pruning removed; the pruned runs are superseded.
- **D6.1:** format fix.

## Killed mechanisms and revisions

- **Killed:** H3.1.
- **Revision 1:** H1.1 → H1.2.
  - Triggered by the pre-placement delay penalty.
  - Justified post hoc by the congestion that E5 revealed.
- **Revision 2:** not used.

## Gate results (NEW-OBS, 2026-09-27; details in 15–18)

- **G1:** materially downgraded, not killed.
- **G3:** survives (S3). A×T:
  - B 6.10e6
  - P2 11.23e6
  - A 13.84e6
  - P 15.24e6
- **G2, generic placement:** K2b → substantially weakened. B unroutable at U 60…8.
- **G2, R2 structured base:**
  - GRT: all 5 W route for B at 60 / 52 / 45, P2 at 60 / 67 and A at 60 / 75.
  - A×T: B 8.10e6; P2 14.98e6 (67%); A 14.28e6 (75%).
  - DRT at 20 iterations: B 1,167 / 881 / 416 at U60 / 52 / 45. P2 and A reach 0 at every U.
  - Post hoc, 64 iterations: B reaches 0 at U45 but not at U52 (117) or U60 (410). At U45: 1.40× vs P2, 1.33× vs A.
  - → **G2 unresolved.**
- **Classification (after G1–G3): PROMISING BUT KEY GATE UNRESOLVED** — superseded by R3 below.

## Final UBP decision run: R3 (NEW-OBS, 2026-09-27; details in 16 §6, 09 R3, 19)

- **Design:** segmented line taps, pre-registered (commit f7f33ba) before any R3 result.
  - Four 2-site taps per line on a base spine; sites connect only within their row quarter.
  - Area-neutral: B's cell area stays 169,952 µm².
  - W-blind placement from development matrices only.
- **52% (decisive): PASS on all criteria.**
  - 5 / 5 W reach 0 DRT violations in 14 / 13 / 7 / 14 / 1 iterations.
  - Invariance 5 / 5; numpy + mutation 5 / 5.
  - Base +0.976 / +0.268 ns.
  - A×T 9.26e6: 1.538× vs A at 75% (credited), 1.612× vs P2 at 67%.
- **60%: PASS on all criteria.** 5 / 5 DRC-clean (13 / 13 / 7 / 13 / 1). A×T 8.57e6: 1.663× vs A (worst program 1.624×).
- **Routed-parasitic check (post hoc):** 52% worst program 1.495×; 60% 1.673×.
- **P2-R3 at 67% (pre-registered fairness point):**
  - Valid: DRC 0, W4 closes in 14 iterations, invariant, = numpy.
  - A×T 17.88e6 (W1 programmable path −2.45 ns), so A stays the strongest competitor. Base-only bound 12.61e6.
- **Driver-sizing sensitivity (post hoc, D-R3.4):** P2-R3 at 13.69e6 would lead; B then leads it by 1.478× (52%) and 1.598× / 1.725× (60%, as built / sized).
- **Classification: PHYSICALLY VALIDATED — NOVELTY PROVISIONAL.**
  - The advantage is robust at 60% and at break-even at 52%.
  - The narrow prior-art check found no identical object, but the decisive full texts are blocked.

## Week 2: physical timing closure (NEW-OBS, 2026-09-28; details in 21)

- **Pre-registered and committed before any build** (21 §1): a W-independent rule, the same for every fabric.
  - Tap drivers: the smallest buf_k meeting 0.30 ns at the worst-case segment load. They are physical cells (2-site pad + buffer, area counted).
  - Spine drivers: sized by the flow's own `repair_design` through a `max_transition` constraint on the tap inputs.
  - Sign-off: OpenRCX-extracted, merged base + program; tt / ss / ff.
  - Decisive: worst program at ss.
- **Built** (all through `ubpgen`, all programs 0 DRC, exact, invariant):
  - B60 and B52;
  - A-R2 at 75% and A-R3;
  - P2-R3 and P2-R2 at 60%, since both fail global routing at 67% once sized.
- **Driver objection closed for UBP:**
  - tap-input transition 1.32 → 0.30 ns;
  - programmable paths no longer critical at any corner.
- **Kill condition triggered.** R = A×T_cons(A-R2 sized) / A×T_cons(B60 sized) = 25.99 M / 17.64 M = **1.473 < 1.5**. Nominal (tt) 1.62; 52% (secondary) 1.21.
- **Cause:**
  - physical taps cost UBP +6.5% area;
  - at ss both designs are limited by the same unsized W-independent tree-start broadcast, which the tt-closing flow buffered worse in B60 (4.18 vs 3.89 ns; the same path was 3.89 ns in the unsized B60).

## Unresolved questions

- ~~G2 closure~~ **closed by R3** (pre-registered, passed at 52% and 60%).
- ~~Line-driver timing closure, implemented rather than simulated~~ **done in Week 2** (21): implemented and extracted; the Week 2 kill condition triggered (R = 1.47 at ss).
- HNLPU / Taalas / TENET / T-MAC / US 11,663,490 full texts (novelty is summary-based).
- Scale ≥ 256 with real BitNet weights (HuggingFace blocked here).
- An advanced PDK with ≥ 3 thin programmable layers; single-via programming.
- Energy.

## Next authorized action

**Week 2 ended with its kill condition triggered** (21 §4). Per the Week 2 instructions: no new architecture, no rescue, Week 3 not started. The next step is the researcher's decision.

(Before Week 2:) None pending. The decision run ends here, as specified.

- **Next:** the paper-scale plan in 19 §H. It starts with the parametric generator and line-driver closure, and needs the researcher's go-ahead.
- **Pushes:** the R3 / final-decision work was pushed to `claude/compassionate-edison-91b73q` under the decision run's explicit authorization, with no pull request and no merge. Any later push needs new authorization.

## Closeout (2026-09-28, transition run)

The researcher decided to close UBP permanently.
- **Written:** 22 (closeout), 23 (reusable assets), 24 (lessons).
- **Extracted:** the generic harness, `SUPPORTING_ARTIFACTS/research_harness/`, with equivalence tests. `ubpgen/` itself is unchanged.
- **Added:** superseded notices on 12, 13, 14, 18 and 19.
- **Pushed** to `claude/compassionate-edison-91b73q` under the transition run's authorization, with no pull request and no merge.
- **Final state:** closed. Nothing further is planned for UBP.
