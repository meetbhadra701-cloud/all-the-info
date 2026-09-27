# 00 — START HERE (Wave 14)

## Decision

**PROMISING BUT KEY GATE UNRESOLVED** (after gates G1–G3). See 14 and 18.

## Thesis in one paragraph

- **The problem.** In LLM silicon whose base layers must stay weight-independent (regime V: HNLPU, Taalas, Ankhdjet), every neuron keeps one accumulation input per weight site.
- **The mechanism.** Share, across all neurons, weight-independent generators of every signed subset sum of g-input blocks. Each neuron leaf then picks one line by via/top metal.

**Where the evidence stands:**
- **Hardwired weights** (layout sees W; E6, G3):
  - bit-serial UBP3 has 2.13× less routed area than the per-input serial fabric;
  - its A×T is 1.84× better than the frontier's bit-plane popcount fabric;
  - MEASURED, DRC-clean, validated.
- **Weight-independent fixed base** (G2):
  - With generic placement, UBP3's 548 programmable lines (vs 128) do not route at any utilization.
  - A W-blind crossbar floorplan (R2) restores routing of all test W at GRT level, with a 2.1–2.3× A×T advantage.
  - But UBP3's detailed routing on SKY130's met4 does not close in the pre-registered effort, while the per-input fabrics' does.
- **Novelty** (G1): likely an obvious composition. Only the physical results are new.
- **Key open gate:** a DRC-clean fixed-base UBP that keeps its advantage.

## Read in this order

| File | What it contains |
|---|---|
| 18_GATES_VERDICT_AND_PACKAGE.md | Gate outcomes, final class, the 12-question package |
| 14_RESEARCH_DECISION.md | The class and why; the key unresolved gate |
| 15 / 16 / 17 | Gate 1 novelty · Gate 2 fixed base (+ R2) · Gate 3 DA / popcount competitors |
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

- Git: branch `claude/compassionate-edison-91b73q`.
  - One push was made on the user's explicit request (`acca499..3912b89`).
  - All later commits (the gates) are **local only**.
  - Nothing else was published or sent.
- Nothing was bought. No paid APIs were used. Nobody was contacted.
- `13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION/` is untouched.
