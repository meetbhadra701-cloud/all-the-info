# 13_FABLE_5_1_SCIENTIFIC_DISCOVERY — start here

> **UBP, proposed here and developed in `../14_FABLE_5_1_SCIENTIFIC_DISCOVERY/`, is CLOSED (2026-09-28): THESIS CLOSED — KILLED BY PREREGISTERED WEEK 2 PHYSICAL-FAIRNESS TEST.**
> - This folder is the historical origin.
> - Current status: `../14_FABLE_5_1_SCIENTIFIC_DISCOVERY/22_UBP_PROJECT_CLOSEOUT.md`.

**Session date:** 2026-09-26. Investigator: Claude (single-threaded, no subagents, as requested).

**Numbering note:** the archive already contains `13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION/`. This folder uses the name the researcher requested; the two are unrelated waves.

## One-paragraph result

- **The problem.** Model-specific inference silicon became real in 2026 (Taalas HC1 → AMD acquisition; HNLPU at ASPLOS'26; BitROM; Ankhdjet). It keeps per-model mask cost down by making every base layer **weight-independent**: weights live only in upper metal/vias. That constraint switches off the classical way to shrink constant matrix–vector hardware (weight-specific common-subexpression elimination).
- **The mechanism.** We propose and analyse **universal block-pattern generators (UBP-g)**:
  - a fixed generator per block of g inputs computes all signed subset sums of those inputs;
  - each neuron's weight-independent adder tree has ⌈n/g⌉ leaves;
  - weights choose, by via, which pattern line feeds each leaf.
- **What was established:**
  - Accumulation is shared *across neurons* with no weight-dependent base layer. For ternary/binary layers this gives ≈ g× fewer adders than today's per-input fabrics. The ratio is exact and W-independent: 3.2× at n = 128, 3.9× at n = 1024.
  - **Cell area is 1.95× (n = 128) and 2.49× (n = 1024) smaller at iso-delay on SKY130** (E3, independently checked).
  - Adding a wiring model to those measured cells leaves about 2× at g = 3.
  - Such fabrics provably meet a port lower bound with equality.
  - They cost 1.22–1.37× more adders than the strongest weight-specific CSE (da4ml), which cannot be used in this regime.
- **A correction made during the session.** In *full-custom* silicon the idea gives almost nothing: synthesis structural hashing recovers most of the sharing automatically. That claim was withdrawn (`06_…`, E1-hashed).
- **What is not established:**
  - whether the select wiring fits after real place-and-route;
  - whether the HNLPU/Ankhdjet full texts (blocked here) already do this.

## Decision

**RESEARCH THESIS READY FOR INITIAL PROTOTYPE**, scoped to via/metal-programmable (weight-independent) fabrics and to ternary/binary weights, and conditional on a one-day full-text novelty check (`07_FINAL_RESEARCH_DECISION.md`).

## Read in this order

1. `05_PRIMARY_RESEARCH_THESIS.md`: the thesis (20 required parts; Theorem 1 with proof).
2. `07_FINAL_RESEARCH_DECISION.md`: classification, the self-review, the exact next steps, blockers.
3. `06_EXPERIMENTAL_PLAN_AND_RESULTS.md`: E1, E1-hashed (the correction), E2, E3 (the regime-V test) and the wire model, with verdicts against the pre-registered kill/advance conditions.
4. `04_STRONGEST_PRIOR_ART.md`: exact overlaps and remaining deltas. Items marked ★ must be read in full next.
5. `03_HYPOTHESIS_REGISTER.md`, `02_PROBLEM_LANDSCAPE.md`, `01_RESEARCH_HISTORY_AND_LESSONS.md`: how we got here and what was rejected.
6. `REPRODUCTION.md`, `experiments/` (pre-registrations, scripts, logs, results) and `evidence/`.

## Honesty ledger

- Primary papers could not be opened: arxiv.org, ACM, IEEE, Semantic Scholar, OpenReview and HuggingFace are blocked by the environment. Every paper claim is marked **[summary]**.
- All weights are i.i.d. ternary; no real checkpoints were available.
- The wire-level area gains are a **model**, not a measurement.
- Nothing was submitted or sent externally (no issues, PRs, or emails).
- `LIVING_RESEARCH_STATE.md` is the working memory kept during the session.
