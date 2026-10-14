# RESEARCH_FAILURE_FORENSICS
**Silicon Discovery Lab | Forensic audit | 13 October 2026**

## Verdict in one sentence
The program too often starts from a *proposed technical device* and searches for a defensible problem, rather than starting from an independently documented unsolved problem and first exhausting equivalent mechanisms and simple baselines. Strong falsification and artifact discipline have developed, but generally arrived *after* candidate selection or implementation.

## Scope and evidence grades
- **E1 — independently observed in this audit:** the supplied `M0_GATE_REPORT(2).md` was read; the linked GitHub archive directories and selected files were fetched through the GitHub connector; GitHub's PR API confirms [Yosys #6231](https://github.com/YosysHQ/yosys/pull/6231) is **merged** (`merged_at=2026-10-07T11:46:33Z`, merge commit `0d0bd04c684ba4f4dddf9cd14bdaabb35a722491`). Relevant external papers, tool pages, and two patent documents were researched. *No software or benchmark was executed for this reset.*
- **E2 — primary document/source statement, not independently replicated:** published papers describing their own evaluation, tool READMEs/source observations, patent disclosures, and the M0 audit's reasoning. Publications are not a guarantee of reproduced claims.
- **E3 — repository-reported, with some inspectable artifacts:** archive experiment reports, test logs, and preregistrations. Counts listed below were not recalculated from every raw log, and this review did not re-run experiments.
- **E4 — older reconstructed or prior-conversation report:** projects not documented by independently retrieved primary project files here (especially CausalTrace, Decision-Sufficient Silicon and Silicon Opportunity), plus missing legacy Waves 3–6 reports. Do not upgrade E4 to E1 by repetition.
- **E5 — analytical hypothesis:** our interpretation or possible cross-field connection. Must be independently falsified.

The [master handoff](https://github.com/meetbhadra701-cloud/all-the-info/blob/main/00_START_HERE/MASTER_RESEARCH_HANDOFF.md) itself says the recovery is curated, not a complete backup: some earlier evidence is transcript-derived. The [kill database](https://github.com/meetbhadra701-cloud/all-the-info/blob/main/05_KILLED_CANDIDATES/RESEARCH_KILL_DATABASE.md), [experimental index](https://github.com/meetbhadra701-cloud/all-the-info/blob/main/06_EXPERIMENTAL_EVIDENCE/EXPERIMENT_INDEX.md), [Wave 10 decision](https://github.com/meetbhadra701-cloud/all-the-info/blob/main/12_WAVE_10_EXPERIMENTAL_DISCOVERY/06_FINAL_DECISION.md) and [Wave 11 adversarial review](https://github.com/meetbhadra701-cloud/all-the-info/blob/main/13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION/03_ADVERSARIAL_REVIEW.md) are the backbone of the history here.

## Candidate-level failure autopsies
For each item: attraction → wrong or untested assumption → exposure → pre-implementation interception → change to process.

### F1 — MOSAIC: decoder residual/contract quotient
- **Attraction:** a apparently formal, compositional treatment of unknown components, weak assumptions, shielding and interposers.
- **Fault:** novelty was assumed from an unusual application vocabulary; the residual/alias mechanism reduced to known decoder inverse-image reasoning.
- **Exposure:** repository kill entry reports 37 engineering tests and formal smoke checks passing **without clearing novelty**; the independent novelty gate killed the centerpiece (E3, with details derived from recovered Codex transcript).
- **Early interception:** write the Boolean/set-theoretic operation and search for *inverse image*, quotient, abstract interpretation, weakest preconditions before writing a framework.
- **Change:** mathematics-first equivalent-mechanism gate; passing implementation tests never changes a novelty verdict.

### F2 — HBRoute: hardware routing guarantee
- **Attraction:** ostensibly new connector-selection/routing formulation.
- **Fault:** single-net structure was ordinary shortest path; multi-net structure returned to standard coupled routing/rip-up-and-reroute.
- **Exposure:** algorithmic reduction in [kill database](https://github.com/meetbhadra701-cloud/all-the-info/blob/main/05_KILLED_CANDIDATES/RESEARCH_KILL_DATABASE.md) (E3/transcript reconstruction).
- **Early interception:** simplify to one net and then two nets; map each to classical shortest path, Steiner, multicommodity routing.
- **Change:** mandatory degenerate-instance reduction and reduction-to-known-problem memo before algorithm work.

### F3 — DITSpec-HLS / generic cross-stage guarantees
- **Attraction:** meaningful security/functional properties potentially preserved through HLS.
- **Fault:** proposed formal rewrite's *value semantics* did not imply *cycle timing or leakage* preservation under scheduling, buffering and lowering.
- **Exposure:** Bambu/Dynamatic and earlier liveness composition prosecution in archive; no complete new end-to-end theorem (E3/E4).
- **Early interception:** state a trace-level contract including timing, initial state, environmental assumptions and observable interface; find a two-trace counterexample.
- **Change:** semantic-boundary audit for any cross-stage claim; if theorem cannot state its observation boundary, stop.

### F4 — GhostForge / ArchWitness / DeltaRTL: general CEGAR-like schemes
- **Attraction:** broadly reusable counterexample-guided history summaries, witness alignment, or failure-region objects.
- **Fault:** existing methods already perform related alignment/invariant discovery (e.g. RE3, PDR-ER); proposed regions could hide changed wrong output values or timing.
- **Exposure:** [candidate review](https://github.com/meetbhadra701-cloud/all-the-info/blob/main/05_KILLED_CANDIDATES/CODEX_TRANSCRIPT_DERIVED_CANDIDATE_REVIEWS.md) and kill database (E3 / older reports sometimes missing).
- **Early interception:** formulate a *minimal distinguishing counterexample* where generic CEGAR or partition/refinement cannot do the same task; test a wrong-value but same predicate-label case.
- **Change:** generic feedback/refinement loops are presumed occupied absent a new invariant, completeness property, complexity separation, or oracle.

### F5 — FPExtrema: computational hardness
- **Attraction:** difficult numeric optimization over expression trees seemed to imply a novel complexity boundary.
- **Fault:** fixing format/leaf order changes the problem; fixed binary32/64 arbitrary topology/order is finite-state and thus polynomial-time in input length under the stated family, though constants may be astronomical. Variable precision is a distinct problem.
- **Exposure:** algorithmic/complexity critique in [kill database](https://github.com/meetbhadra701-cloud/all-the-info/blob/main/05_KILLED_CANDIDATES/RESEARCH_KILL_DATABASE.md) (E3 reconstructed).
- **Early interception:** quantify input size, whether precision is fixed or variable, and exactly what complexity measure scales.
- **Change:** complexity claims need a formal parameterized problem statement before experimental work.

### F6 — MUXWISE generic resource sharing
- **Attraction:** intuitive repeated-expression sharing suggested measurable circuit savings.
- **Fault:** existing Yosys+ABC already finds/erases the tested differences.
- **Exposure:** archive reports [99/99 synthesis runs plus positive/negative formal checks](https://github.com/meetbhadra701-cloud/all-the-info/blob/main/06_EXPERIMENTAL_EVIDENCE/EXPERIMENT_INDEX.md) (E3, not rerun here).
- **Early interception:** strongest standard synthesis optimization with same RTL and constraints before custom sharing logic.
- **Change:** baseline-first gate and explicit measure of residual *after* incumbent optimization.

### F7 — MUXWISE `arith_tree` PPA → real Yosys defect → merged PR
- **Attraction:** tool-dependent mapping differences might reveal a new arithmetic optimization and PPA win.
- **Fault:** correctness could not be assumed; a log was inherited with `model found: FAIL` incorrectly labeled PASS. Physical benefit was unvalidated and seeded behavior varied.
- **Exposure:** experiment reports identified the first PASS→FAIL immediately after `arith_tree`; `-no-fma` passed; signed wider-accumulation Baugh–Wooley correction missing sign-extension mask. The later clean-current-main patch report records 42 completed PASS proofs, two timeouts and still-inconclusive FIR4 W16 (E3); actual [#6231 merge](https://github.com/YosysHQ/yosys/pull/6231) is E1.
- **Early interception:** correctness gate before any PPA or optimization claim; inspect raw proof markers, not exit codes, and isolate the first divergent pass.
- **Change:** class **successful upstream engineering**, not a failed project and not proof that a new arithmetic verification theory exists. Update time-dependent facts against primary PR status.
- [Yosys validation report](https://github.com/meetbhadra701-cloud/all-the-info/blob/main/06_EXPERIMENTAL_EVIDENCE/YOSYS_FMA/FINAL_VALIDATION_REPORT.md).

### F8 — PassWitness: useful workflow, occupied algorithmic core
- **Attraction:** first-bad-pass localization with replayable witnesses and portable packages solves a real pain.
- **Fault if marketed as theory:** orchestration of preexisting Yosys SAT, EQY-like equivalence, reduction and checkpointing is not a new solver/theorem.
- **Exposure:** its [own prior-art](https://github.com/meetbhadra701-cloud/all-the-info/blob/main/06_EXPERIMENTAL_EVIDENCE/PASSWITNESS/docs/prior-art.md) and [limitations](https://github.com/meetbhadra701-cloud/all-the-info/blob/main/06_EXPERIMENTAL_EVIDENCE/PASSWITNESS/docs/limitations.md) concede this. [Phase 3](https://github.com/meetbhadra701-cloud/all-the-info/blob/main/06_EXPERIMENTAL_EVIDENCE/PASSWITNESS/docs/phase3-validation.md) reports 32 passing tests, including genuine localization and injected-fault controls (E3).
- **Early interception:** capability chart vs Yosys, EQY, SymbiYosys, Verismith, `bugpoint` before seeking research novelty.
- **Change:** allow useful engineering products to succeed as engineering. Reject forced paper/patent framing.

### F9 — Wave 10 MappingEvolve: weak comparator and constraint mismatch
- **Attraction:** a paper's headline LLM-evolved mapping improvement appeared reproducible.
- **Fault:** much improvement reflected delay relaxation and comparison to weak ABC settings; strong `emap` iso-delay comparator beat the evolved variants.
- **Exposure:** archive reports a preregistered **53×35=1,855** netlist evaluation, with independent timing, simulation and CEC. The paper's EPFL area claim did not survive best-applicable-mapper-at-same-delay comparison; source trace for one DeepSeek result was incomplete (E3).
- **Early interception:** match the target delay first; always use strongest contemporary same-library mapper, own model's improved modes, hold-out workloads, and exact provenance.
- **Change:** two-key baseline approval (domain specialist + adversary) and explicit iso-constraint metric before benchmark execution.
- [Wave 10 executive report](https://github.com/meetbhadra701-cloud/all-the-info/blob/main/12_WAVE_10_EXPERIMENTAL_DISCOVERY/00_EXECUTIVE_SUMMARY.md).

### F10 — Wave 10 OpenROAD search resynthesis
- **Attraction:** general AI/heuristic exploration of synthesis scripts might improve timing.
- **Fault:** doing nothing and standard `repair_timing -setup` were much stronger than an elaborate search with poor acceptance behavior.
- **Exposure:** archive reports eight search runs regressed slack; standard repair improved it; all 19 checked outputs were equivalent. Thus **correctness passed, utility failed** (E3).
- **Early interception:** untouched-flow and incumbent repair must be first baselines; isolate a no-harm acceptance rule and test one case.
- **Change:** compare algorithm against existing production heuristic, not only a publication demo; do-not-degrade controls before optimization loops.

### F11 — Wave 11 H1.6, mapping ambiguity-restricted exact covering
- **Attraction:** accumulated near-tie decisions plausibly explained area recovery, leading to a nonlocal exact solver restricted by ambiguity.
- **Fault at risk:** source diagnosis of heuristic near-ties did not establish concentration of *global* optimum improvements inside near-tie choices; older exact recovery and SAT covering were already close.
- **Exposure:** [evolved hypothesis](https://github.com/meetbhadra701-cloud/all-the-info/blob/main/13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION/04_HYPOTHESIS_EVOLUTION.md), [prior-art prosecution](https://github.com/meetbhadra701-cloud/all-the-info/blob/main/13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION/05_PRIOR_ART_PROSECUTION.md), and [evaluator](https://github.com/meetbhadra701-cloud/all-the-info/blob/main/13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION/06_EXPERIMENTAL_EVALUATOR.md). Prior-session readouts say ε=.05 captured too little headroom on most tested instances, and many solves were FEASIBLE rather than OPTIMAL; those readouts are E4 until raw results are reaudited.
- **Early interception:** analytically ask why a *locally near-tied* cost is a sufficient proxy for a *globally decisive* match under sharing. Run small exact optimum first, before claiming coverage.
- **Change:** certify the assumption that defines the search-space restriction; distinguish feasible incumbent from proven optimum and rerun stronger modern comparisons (e.g. UniMap where appropriate).

### F12 — PCAS: occupied proof principles and an unbound checker
- **Attraction:** genuine signed-FMA error suggested generator-side arithmetic certificates checked in allegedly linear time.
- **Fault:** proof-producing synthesis, algebraic certification, and netlist-bound proof logs already exist. Post-hoc reading of Yosys `$fa` graph plausibly reconstructs the same information. Producer-authored C1–C4 statements do not inherently prove actual connected gates/output/final CPA or post-ABC netlist. Generic `O(#FA)`/LPAC speed claims were not established.
- **Exposure:** attached supplied `M0_GATE_REPORT(2).md` (local source), [AMulet2](https://github.com/anthropics/amulet2), [Arisca](https://github.com/LittleBlackCQ/arisca), [TRACE](https://github.com/jan-kl/trace), [TalisMan](https://github.com/d-kfmnn/talisman), [Konrad–Scholl 2026](https://doi.org/10.1007/s10703-026-00494-9), [IBM US12475287B2](https://patents.google.com/patent/US12475287B2/en).
- **Early interception:** insist on a graph-vs-spec soundness theorem and build a *conceptual* strongest non-invasive reader baseline (B5) before generator instrumentation, as the M0 report requires.
- **Change:** **NO-GO remains final for PCAS as claimed**; do not rename or fork it.

### F13 — CausalTrace / Decision-Sufficient Silicon / Silicon Opportunity (additional, lower-grade historical record)
- **CausalTrace:** prior-session Stage 0 reported 48/48 validated reconstructions, but closure-aware retention delivered no win over simpler hybrid retention. The problem was not whether it could reconstruct—rather whether the proposed extra state was *necessary*. No monitor RTL was warranted (E4; exact project data not in prioritized archive).
- **Decision-Sufficient Silicon:** prior-session Gates 1/2 reported small fixed-affine interval tests passing, but toy assumed costs, no real label accuracy/energy evidence, and nearest early-exit/reconfigurable NN prior art (Sayadi, ConvReLU++) closed the hardware case. Mathematical validity for a toy oracle does not establish user benefit or energy advantage (E4).
- **Silicon Opportunity:** prior-session verdict `INSUFFICIENT EVIDENCE` despite 126 successful repeated runs; available performance counters missing, some key timeouts and mapping-score discrepancy. Existing solver/simulator choices, not new silicon, dominated headline speed gaps (E4).
- **GateTruth:** a comparatively **positive benchmark/infrastructure** effort, not classified here as a novelty failure. The independently retrieved [project README](https://github.com/meetbhadra701-cloud/GateTruth/blob/main/README.md) confirms a documented mutation-testing methodology, 60 RTL-generation tasks, eight repair tasks, seven-model scoreboard, and a disclosed limitation: **14 of 60** Track A testbenches fail the stated ≥95% mutation-kill floor. This is **E2/E3** for repository-documented methodology/results, *not* independent reproduction of model scores, measured rigor, third-party adoption, or paper novelty. The README reports paper/arXiv submission pending.
- **Early interception across these:** select a stronger simple retention rule, an actual deployment cost/label/energy oracle, stable production metric, and external adopters before architecture or paper claims.

## Failure taxonomy, including non-failures
| Root cause | Illustrative cases | What the finding does and does not establish |
|---|---|---|
| Prior-art collision | MOSAIC, GhostForge, PCAS, H1.1–H1.5 | Occupied *mechanism*, not proof no research problem exists |
| Mathematical equivalence/reduction | HBRoute, FPExtrema | Existing problem/complexity class under exact assumptions |
| Incorrect proof/semantic assumptions | DeltaRTL, DITSpec-HLS, PCAS C1–C4 | Fatal to stated guarantees; might allow a distinctly new theorem, not cosmetic revision |
| Weak/non-matched baseline | MappingEvolve, OpenROAD resynth, H1.6 risk | Headline advantage is not credible under fair control |
| Measurement/provenance artifacts | MUXWISE inherited FAIL→PASS metadata, DeepSeek provenance, seed variability | Recompute direct oracle from artifact |
| No demonstrated extra utility | CausalTrace, Decision-Sufficient Silicon | Correct implementation alone does not pay for complexity |
| Hardware unjustifiability | Decision-Sufficient Silicon, Silicon Opportunity | Software approach may be superior; no chip funding |
| Successful engineering, not general novelty | Yosys #6231, PassWitness, GateTruth infrastructure | Valuable outcomes deserving accurate labels |

## Process root causes (causal, not chronological)
1. **Solution anchoring**: idea first, problem/customer later. This invites motivated prior-art search.
2. **Surface novelty bias**: different artifact format, pipeline stage, name or hardware target is mistaken for a new invariant/capability.
3. **Baseline debt**: cheapest direct reader, native compiler, no-change, existing exact method and modern alternative not elevated soon enough.
4. **Specification debt**: incomplete trusted boundaries, mismatched signedness, timing, reference/oracle, precision or output mapping.
5. **Evidence-label drift**: PASS tests become general proof; FEASIBLE solver result becomes OPTIMAL; paper's performance claims become observations; old PR status persists after merge.
6. **Hardware eagerness**: specialized silicon considered before proving algorithmic residual under software and data-movement analysis.
7. **Selection bias**: candidate search intentionally seeks dramatic gains; negative results are numerous and underrepresented in later idea narratives.

## Corrections to the *discovery protocol*
No project implementation, RTL, FPGA purchase, patent outreach, or benchmark harness may begin until a **problem dossier** has: (i) named practitioner and primary evidence, (ii) mathematical contract, (iii) rival mechanisms from older and current research, (iv) reduction test, (v) independent oracle and missing-data list, (vi) minimal killing experiment, (vii) fair incumbent software baseline, and (viii) a stated scientific consequence unavailable from mere integration. The protocol is detailed in `DISCOVERY_METHODOLOGY_V2.md`.

## Not independently checked
This review did **not** clone the full 509,569-KB-sized research archive, audit every nested log, audit complete GateTruth results or recover local-only CausalTrace/Silicon Opportunity folders, rerun any benchmark, check every patent claim family, or resolve all E4 cases. It read the GitHub-listed top-level structure and selected substantive reports, plus the supplied full PCAS M0. Source accessibility and audit boundaries are enumerated further in `PRIOR_ART_AND_OPEN_QUESTIONS.md`.
