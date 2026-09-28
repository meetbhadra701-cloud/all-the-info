# 00 — START HERE (Wave 14)

## Decision

**PHYSICALLY VALIDATED — NOVELTY PROVISIONAL** (the final UBP decision run, R3, 2026-09-27). See **19**.

- **Every pre-registered R3 criterion passed at 52% and 60%.** On one frozen weight-independent base per density:
  - all five weight programs route DRC-clean on met4–met5;
  - the base is verified unchanged after every program;
  - every programmed netlist is exact vs numpy;
  - A×T is 1.54× (52%) / 1.66× (60%) better than the strongest fixed-base competitor.
- **Standing qualification:** the advantage is robust at 60% (≥ 1.56× under every post-hoc check). At 52% it is at break-even (1.48–1.54×).
- **Novelty is provisional:** the decisive full texts (HNLPU, Taalas, TENET / T-MAC, US 11,663,490) are blocked in this environment.
- **Broad exploration stops; UBP is the research project.** The superseded class was PROMISING BUT KEY GATE UNRESOLVED (14, 18).

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
  - A W-blind crossbar floorplan (R2) restores routing of all test W at GRT level, with a 1.76–1.85× A×T advantage over the baselines' best.
  - But on R2, UBP3's detailed routing on SKY130's met4 does not close at a useful utilization.
  - **R3, segmented line access** (each line a base spine with one programmable tap per quarter of the rows) closes it:
    - 5 / 5 programs are DRC-clean at 52% and at 60%;
    - A×T is 1.54× / 1.66× better than A, and 1.61× / 1.74× better than P2;
    - P2 rebuilt with the same taps is weaker as built. With its line drivers sized (post hoc) it would be the strongest competitor, at 1.48× (52%) / 1.60–1.73× (60%).
- **Novelty** (G1 plus the final narrow check): likely an obvious composition. The physical results and the reachability / segmentation law are the contribution. Provisional until the blocked full texts are read.

## Development (after the decision)

**Week 1 (§H) is complete: `ubpgen/`** is a parametric generator for B, A and P2 with R3 access. See **`20_WEEK1_DEVLOG.md`**.
- It reproduces the validated R3 designs bit-for-bit, down to identical frozen-base ODBs.
- Its 12 routed programs match the historical records with 0 differences.
- One command rebuilds the R3 tables: `python3 -m ubpgen.tables ubpgen/configs/suite_r3_tables.json --run`.

**Week 2 (§H): WEEK 2 KILL CONDITION TRIGGERED** (2026-09-28). See **`21_WEEK2_TIMING_CLOSURE.md`**.
- **What was built.** Every design was rebuilt with physically sized drivers, under a pre-registered W-independent rule applied identically to all fabrics:
  - physical tap buffers: 2-site pad + buf_k, area counted;
  - spine drivers sized by the flow's own `repair_design`.
- **Sign-off:** OpenRCX-extracted, merged base + program, at tt / ss / ff.
- **What passed:** UBP3-R3 at 60% routes and is exact for all five programs; its driver-timing objection is closed (its programmable paths are no longer critical at any corner).
- **The ratio.** Against the strongest physically sized baseline (A-R2, 75%), R is 1.62 at tt but **1.47 at the conservative corner** (ss, worst program), below the 1.5 kill line.
- **The cause** is the combination of two things:
  - UBP pays +6.5% area for 2,192 physical taps;
  - at ss both designs are limited by the same unsized, W-independent tree-start control broadcast, which the tt-closing flow buffered worse in UBP (4.18 vs 3.89 ns).
- P2 is not routable at 67% once sized; at 60% it is 2.36× worse than UBP.
- Per the instructions: no rescue in the same run, and Week 3 not started.

## Read in this order

| File | What it contains |
|---|---|
| **19_FINAL_UBP_DECISION.md** | **The final verdict and package A–J** (contribution, architecture, math, physical evidence, competitors, scope, risks, 4–8-week plan, thesis, strongest attack) |
| 16_GATE2_FIXED_BASE.md §6 | R3 tables: bases, the ten programs, advantage, routed-parasitic timing, the P2-R3 fairness point (§6.6) |
| 09_PREREGISTRATION.md, section R3 | The R3 pre-registration (committed before any R3 result), its outcome and the deviation log D-R3.1–4 |
| 18_GATES_VERDICT_AND_PACKAGE.md | Gates G1–G3 and the superseded class (PROMISING BUT KEY GATE UNRESOLVED) |
| 14_RESEARCH_DECISION.md | The class history and why |
| 15 / 16 / 17 | Gate 1 novelty · Gate 2 fixed base (+ R2, R3) · Gate 3 DA / popcount competitors |
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
  - Pushes, each on the user's explicit request:
    - `acca499..3912b89` (Wave 14);
    - the gate commits (from `234df16` on);
    - the R3 / final-decision commits (from `f7f33ba` on). The final decision run authorized these, with no pull request and no merge.
  - Nothing else was published or sent.
- Nothing was bought. No paid APIs were used. Nobody was contacted.
- `13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION/` is untouched.
