# 14 — Research decision

## Current classification (after gates G1–G3, 2026-09-27): **PROMISING BUT KEY GATE UNRESOLVED**

The full package is in `18_GATES_VERDICT_AND_PACKAGE.md`. Gate details are in 15 (G1), 16 (G2) and 17 (G3). Every kill and advance condition was pre-registered in 09 before its data.

| Gate | Outcome |
|---|---|
| **G1** novelty | **Materially downgraded, not killed.** No identical or technically equivalent mechanism was found. The composition (activation-group LUT sharing + a via/metal-programmable W-independent base) is likely obvious. Only its physical consequences are new. |
| **G3** strongest competitor | **Survives.** Hardwired-W regime, MEASURED and validated: A×T of B 6.10e6 vs P2 11.23e6 (1.84×), P 15.24e6 and A 13.84e6. Spatial via-ROM DA (K ≥ 2) is never smaller than the K = 1 popcount fabric for ternary W. |
| **G2** fixed base, generic placement (pre-registered) | **K2b fires: substantially weakened.** B's random programs do not route on met4–met5 at any utilization from 60% to 8%. Diagnosis: the connectivity-driven placer clusters all 548 line taps. |
| **G2 / R2** structured W-blind crossbar base (the one bounded revision) | **Unresolved.** At GRT level, B routes all five W at U60 with 1.85× (P2 at 67%) and 1.76× (A at 75%) better A×T under modeled timing. Its programmable-layer detailed routing does not close in the pre-registered 20 iterations at U60 / 52 / 45 (1,167 / 881 / 416 met4 violations), while P2 and A close at every U tested. R2-K does not fire; R2-A is not granted. *Post hoc: with the router-default 64 iterations B closes at U45 but not at U52 (117) or U60 (410). At U45 it is 1.40× better than P2 but only 1.33× better than A (bar 1.5×).* |

## Why this class and not the others

- **Not THESIS KILLED:**
  - No pre-registered kill condition fired: G1 was downgraded, not killed; G3 passed; G2 was substantially weakened on the generic protocol, and R2-K did not fire.
  - Against the Gate-2 kill condition, W changes never move base cells or touch forbidden layers.
  - On the structured base there is no routability or timing collapse. The advantage holds at GRT level, and B has the best timing.
- **Not READY FOR FULL RESEARCH DEVELOPMENT:**
  - The thesis is specifically about a **weight-independent** fabric, and its physical advantage in that regime is not closed.
  - B fails the pre-registered detailed-route criterion at every tested utilization, where both per-input competitors pass.
  - After G1, the physical characterization is the **only** candidate contribution, so an unclosed G2 leaves the contribution unestablished.
- **Not READY TO BEGIN PAPER-SCALE IMPLEMENTATION:** all of the above, plus no scale, no real weights and no energy data.

## The key unresolved gate, and the decisive next experiment

**G2 closure.** Does a W-blind fixed base exist in which UBP3-serial's programmable layer routes DRC-clean for all test W, at a utilization where its A×T stays ≥ 1.2× better than P2 and ≥ 1.5× better than A?

**Next revision (not run here: this session's one bounded revision was R2).** Pre-register a site/tap co-designed band:
- stagger the via sites across the band width, so each site's met4 pad sits on its own track;
- split the taps into two half-height groups;
- keep the pin pads off the line tracks.

Run it against P2 and A on the same grid and criteria. Route at the ORFS-default 64 detailed-route iterations. Sensitivity: a third programmable layer (base met1–met2).

Post hoc, 64 iterations on the R2 layout close B only at U45, so router effort alone does not resolve G2. **B must close at U ≥ ≈ 51%** to keep both bars against P2 at 67% and A at 75%.

**Kill** the via-programmable claim if B still cannot close at a utilization that keeps those ratios.

## Earlier (Wave 14, pre-gate) classification, superseded

**RESEARCH THESIS READY FOR FULL DEVELOPMENT (gated)**, on E5/E6: bit-serial UBP3 2.13× smaller routed area than g1, hardwired W. The gates it named (G1–G3) have now been run; the result is the class above.

## Record-keeping

- **Pushes:** two, each on the user's explicit request, to `claude/compassionate-edison-91b73q`:
  - `acca499..3912b89` (Wave 14);
  - the gate commits, from `234df16` on.
- Nothing else was published or sent.
- Nothing was bought, no paid API was used, and nobody was contacted.
- All EDA tools ran inside the ORFS container.
