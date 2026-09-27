# RESEARCH_STATE — Wave 14 (final)

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

## Critical assumptions

- **(c)** Fixed placement / top-metal routing behaves like placement-free routing. **Untested → gate G2.**
- **(e)** No stronger regime-V baseline. **Untested → gate G3.**
- **Novelty → gate G1.**

## Experimental status (NEW-OBS; final numbers in 10)

**E6 (bit-serial, n = 64):**
- g1/UBP3 routed area **2.13×**; both U_max = 75; timing met at 3.0 ns (2.08 vs 2.22 ns).
- +1 cycle latency; select WL 5.8× lower.
- Post-PnR validated. **A6 MET.**

**E5 (bit-parallel, n = 32):**
- UBP3 U_max = 60 (congestion at 75); g1 U_max = 75.
- Ratio «E5_RATIO» («E5_VERDICT»). Delay 1.10×.
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

## Unresolved questions

- HNLPU full text.
- Fixed-placement ECO.
- DA-via-ROM.
- Scale ≥ 256 with real BitNet weights.
- Advanced PDK.
- Energy.

## Next authorized action

None pending in this session. Gates G1–G3 (14) are the recommended next steps and need the researcher's go-ahead: G1 needs human full-text access.
