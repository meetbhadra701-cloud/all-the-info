# 00 — START HERE (Wave 14)

## Decision

**RESEARCH THESIS READY FOR FULL DEVELOPMENT (gated).** See 14.

## Thesis in one paragraph

- **The problem.** In hardwired LLM silicon whose base layers must stay weight-independent (regime V: HNLPU, Taalas, Ankhdjet), every neuron keeps one accumulation input per weight site.
- **The mechanism.** Share, across *all* neurons, weight-independent generators of every signed subset sum of g-input blocks. Each neuron leaf then picks one line **by via**.
- **The result.** In **bit-serial** form this halves the **routed** accumulation area on SKY130:
  - **2.13×** vs the per-input universal fabric;
  - both DRC-clean at 75% utilization;
  - equal 3.0 ns clock and throughput, +1 cycle latency;
  - 5.8× less via-programmed wiring;
  - final routed netlists equal numpy W@x.
- **The bit-parallel form** loses one utilization step to select-bus congestion («E5_RATIO»).
- **Standing:** novelty is provisional and possibly obvious (LUT-GEMM + hardwiring). Three cheap gates decide whether to continue: HNLPU full text, fixed-placement routing, DA-via-ROM baseline.

## Read in this order

| File | What it contains |
|---|---|
| 14_RESEARCH_DECISION.md | The class, the checklist, gates G1–G3 |
| 12_PRIMARY_RESEARCH_THESIS.md | The 24 required items |
| 13_FINAL_META_REVIEW.md | The 13 mandatory questions |
| 10_EXPERIMENTS_AND_RESULTS.md | E5/E6 tables; the A2 before/after |
| 03_RESEARCH_TREE.md | Problem → hypothesis → experiment → decision |
| 09_PREREGISTRATION.md | E5, E6, Amendments A1/A2, deviation logs |
| 08_EXPERIMENTAL_EVALUATOR.md | The flow, the invariants, bias directions |
| 07_PRIOR_ART_PROSECUTION.md, evidence/ | Element-by-element anticipation; search log |
| 04, 06, 11 | Generation/proximity, reflection/debate, evolution |
| 01_RESEARCH_HISTORY.md | Lineage and lessons, including the E3 width defect and the A2 pruning lesson |
| RESEARCH_STATE.md, REPRODUCTION.md | Working state; exact commands |

**Consolidated elsewhere:**
- 02 (problem landscape) and 05 (proximity analysis) are in 04, Stages A–B.
- The frontier map is inherited from `13_FABLE_5_1_SCIENTIFIC_DISCOVERY/02_PROBLEM_LANDSCAPE.md` and `04_STRONGEST_PRIOR_ART.md`. No boilerplate files were created.

## Status of the work

- Git: **local commits only** on `claude/compassionate-edison-91b73q`. **Nothing pushed, published or sent.**
- Nothing was bought. No paid APIs were used. Nobody was contacted.
- `13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION/` is untouched.
