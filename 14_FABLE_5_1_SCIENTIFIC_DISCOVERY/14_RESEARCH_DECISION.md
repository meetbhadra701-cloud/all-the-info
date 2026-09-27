# 14 — Research decision

## Classification: **RESEARCH THESIS READY FOR FULL DEVELOPMENT** (gated)

**Why this class:**
- The mechanism has **survived an informative prototype experiment**. E5/E6 are physical PnR experiments with pre-registered kill conditions that could have fired.
- The bit-serial form (H1.2) keeps a **2.13× routed-area advantage** over the per-input universal fabric at an equal real clock and equal throughput. It stays DRC-clean at the top of the tested utilization range, and its final routed netlists are functionally validated.
- The run exposed a real physical price in the bit-parallel form: one utilization step lost to congestion. This shows the evaluator can discriminate.
- The remaining work is research, not repair: a stronger baseline, fixed-placement routing, scale, and novelty. It justifies a multi-week implementation.

## Positive-decision checklist (prompt §21)

| Requirement | Status |
|---|---|
| Consequential problem | ✓ The dominant area term of metal/via-programmable LLM silicon (HNLPU, Taalas, Ankhdjet) |
| Precise mechanism | ✓ UBP-g, exact and W-independent. Adders in closed form; port-optimal (Theorem 1). Bit-serial realization specified and validated. |
| Defensible technical distinction | ◐ vs runtime LUT: via instead of mux, with the cost moved to wiring. vs hardwired g = 1: cross-neuron multi-input sharing. **The combination is not found, but obviousness risk is high. Provisional.** |
| Causal reason it could work | ✓ Physically confirmed: select WL ≈ 1/g · (1 − p0)⁻¹ of g1's (5.8× measured); bit-serial removes bus congestion |
| Trustworthy evaluator | ✓ Post-PnR functional validation vs numpy; mutation controls; W-independence invariant (A2); parser cross-check. Limitations declared (08). |
| Meaningful falsifier | ✓ E5/E6 could have failed; the next falsifier (fixed-placement ECO) is specified |
| Executable next step | ✓ See the gates below |

## Why not the neighbouring classes

- **Not "READY FOR INITIAL PROTOTYPE":** that was the state before this session. The initial prototype experiment has now been run and passed.
- **Not "NOVELTY OCCUPIED":**
  - The occupying references cover **ingredients**: the LUT arithmetic, via fabrics, bit-serial neurons.
  - No retrieved source shows the complete regime-V combination.
  - This is **provisional** (HNLPU full text unread) and is gate G1.
- **Not "MECHANISM FALSIFIED":** K5 and K6 did not trigger.
- **Not "INSUFFICIENT EVIDENCE":** the evidence is physical, validated and discriminating. It is limited in scale and scope, which the gates address.

## Pre-registered outcomes

| | Result | Decision |
|---|---|---|
| **E6 (H1.2, bit-serial, n = 64)** | g1/UBP3 routed area 2.13× (both U_max = 75; timing met; +1 cycle latency) | **A6 MET** |
| **E5 (H1.1, bit-parallel, n = 32)** | g1/UBP3 = 1.67× (UBP3 U_max = 60; congestion at 75) | A5 MET narrowly (1.59× on the tie-corrected basis) |

## Gates for the full-development phase

Each gate is cheap, and each can stop the project.

- **G1 — Novelty.** A person with access reads HNLPU (ASPLOS'26) and any Taalas disclosure. **Kill** if shared multi-input pattern streams across neurons are described.
- **G2 — Fixed placement.** Place once with W₁, then ECO-reroute W₂ with W-dependent nets confined to the top metals. **Kill** if bit-serial UBP falls below 1.5× or fails to route where g1 routes.
- **G3 — Strongest baseline.** Compare against ROM-based distributed arithmetic as a via-ROM macro: analytic plus a transistor-level area model at an advanced node. **Kill or rescope** if DA is ≥ 1.5× smaller per weight than UBP-serial.

## If all gates pass (weeks 3–8)

- n, m ≥ 256 with real BitNet b1.58 weights.
- The ASAP7 PDK.
- Activity-based power.
- Integration into an open via-programmable macro.

## Record-keeping

- Everything is committed **locally only**, on branch `claude/compassionate-edison-91b73q`. **Nothing was pushed, published or sent.**
- Nothing was bought, no paid API was used, and nobody was contacted.
- The ORFS container ran all EDA tools in isolation.
