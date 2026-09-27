# RESEARCH_STATE — Wave 14 + gates G1–G3 (current)

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
  - **Structured W-blind crossbar (R2):** passes at GRT level; detailed-route closure on met4 is **UNRESOLVED**.
- **(e) No stronger regime-V baseline:** holds in the hardwired regime (G3; DA dominated; P2 1.84× worse). On the fixed base, P2 and A close detailed routing where B does not.
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
  - GRT: all 5 W route at U60 for B, P2 and A.
  - A×T: B 8.10e6; P2 17.07e6; A 18.35e6.
  - DRT at 20 iterations: B 1,167 / 881 / 416 at U60 / 52 / 45. P2 and A reach 0 at U60.
  - → **G2 unresolved.**
- **Classification: PROMISING BUT KEY GATE UNRESOLVED.**

## Unresolved questions

- **G2 closure (the key gate):** a site/tap co-designed W-blind base, pre-registered, vs P2 and A.
- HNLPU / Taalas / TENET / T-MAC full texts (G1 is summary-based).
- Scale ≥ 256 with real BitNet weights (HuggingFace blocked here).
- An advanced PDK with ≥ 3 thin programmable layers; single-via programming.
- Energy.

## Next authorized action

None pending. The next step is the G2-closure experiment (14). It needs the researcher's go-ahead.

Pushing the local gate commits also needs explicit authorization.
