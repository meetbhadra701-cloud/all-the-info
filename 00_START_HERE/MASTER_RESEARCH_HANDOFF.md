# Master Research Handoff

## Current status (2026-09-28)

**UBP IS CLOSED: THESIS CLOSED — KILLED BY PREREGISTERED WEEK 2 PHYSICAL-FAIRNESS TEST.**

UBP was the universal block-pattern fabric for weight-independent inference silicon (Waves 13–14 "Fable"; `13_FABLE_5_1_SCIENTIFIC_DISCOVERY/` → `14_FABLE_5_1_SCIENTIFIC_DISCOVERY/`). At its pre-registered 60% operating point, fully physically sized and signed off at three corners, its conservative A×T advantage over the strongest baseline was 1.473×, below the required 1.5×. It is not to be rescued or restarted.

| Read | For |
|---|---|
| `14_FABLE_5_1_SCIENTIFIC_DISCOVERY/22_UBP_PROJECT_CLOSEOUT.md` | The canonical closeout (what worked, why it was killed, withdrawn claims, claims that remain true) |
| `14_FABLE_5_1_SCIENTIFIC_DISCOVERY/21_WEEK2_TIMING_CLOSURE.md` | The decisive experiment |
| `14_FABLE_5_1_SCIENTIFIC_DISCOVERY/23_REUSABLE_RESEARCH_ASSETS.md` | Reusable infrastructure vs UBP-specific code |
| `14_FABLE_5_1_SCIENTIFIC_DISCOVERY/24_LESSONS_FOR_NEXT_THESIS.md` | Lessons with evidence |
| `SUPPORTING_ARTIFACTS/research_harness/` | The extracted, tested research harness (config → verify → mutation control → baseline → physical flow → extraction → multi-corner timing → decision) |
| `SUPPORTING_ARTIFACTS/NEXT_THESIS_RESEARCH_RULES.md` | Twelve rules for the next thesis |

Sections 1–11 below predate the Fable waves and are kept as written. For Waves 13–14, the folder documents above are authoritative.

## Evidence status

This package is a curated local recovery, not a complete computer backup. Claims labeled **direct artifact** are supported by files copied into this package. Claims labeled **transcript-derived** come from final-session messages in a locally accessible Codex backup database; the original reports were not recovered. Claims labeled **interpretation** are synthesis across those records and should be rechecked against primary artifacts when available.

## 1. Research mission

The research program seeks one unusually high-impact, scientifically defensible semiconductor/EDA/formal-hardware contribution that can be implemented, independently evaluated, cited, and reused downstream. The operating method is discover → attack → kill → converge → validate → specify → build. A candidate must be more than an interesting tool failure or a familiar engineering seam: it needs a precise scientific problem, a materially unoccupied contribution, a credible independent oracle, feasible artifacts, and experiments that separate the claimed mechanism from implementation debt and benchmark luck.

The program also values a durable evidence trail: exact hypotheses, prior-art attacks, kill decisions, tool versions, source commits, scripts, logs, independent checks, and negative results.

## 2. Research domains

The recovered materials cover formal verification and IC3/PDR-style reasoning; arithmetic verification and synthesis; constant-time HLS and hardware security; RTL synthesis and translation validation; memory semantics and physical mapping; banked memories; sequential equivalence, retiming, liveness, and witness extraction; HLS and compiler/hardware co-design; MLIR/CIRCT/Dynamatic/Bambu-style lowering; physical design, ECO ordering, timing, power, and electrical legality; and reducer/localization workflows for hardware failures.

Technical capabilities demonstrated in the evidence include Yosys/ABC synthesis and formal flows, Icarus/Verilator-style simulation, SymbiYosys/Avy proof smoke tests, OpenROAD-style physical-design pilots, RTL generation and checking, source-level and netlist-level comparison, benchmark harnesses, and reproducibility packaging. Capability does not imply that every listed flow was successfully executed in every wave.

## 3. Chronological research history

The methodology began with broad semiconductor/EDA ideation and increasingly aggressive novelty and feasibility prosecution. The research process then moved toward small, falsifiable experiments: reproduce a frontier claim, define an independent oracle, test the narrowest mechanism, and record a kill or a bounded survivor. The Wave 3–6 transcript history shows increasing attention to physical effects, semantic contracts, clean witness construction, and the difference between a real failure and a novel general principle. The later MUXWISE and PassWitness work made tool provenance, formal-log interpretation, independent simulation, and release-grade evidence central.

The current PPA-Delta material applies a similar discipline to hardware failure reduction: frozen suites, equal budgets, multiple baselines, candidate ledgers, and explicit gate/review documents. Its current status remains provisional because one review found a measurable but sub-threshold advantage and unsupported structural claims.

## 4. Previous research waves

### Waves 3–4: physical design and transformation seams — transcript-derived

Wave 3 investigated real-synthesis bridges, actual-netlist bridges, and incremental-versus-full ECO decision order. The strongest recovered quantitative result is a weak, seed-sensitive relationship between incremental and full ECO rankings, with many reversals and little top-five agreement. Waves 4A/4B investigated banked-memory topologies and temporal retiming/composition. Original reports are missing locally, so detailed conclusions remain provisional. See `04_EARLIER_RESEARCH_WAVES/CODEX_TRANSCRIPT_DERIVED_RESEARCH_HISTORY.md`.

### Wave 5: memory contracts, physical mapping, power, and security — transcript-derived

Wave 5B found concrete resource cliffs and memory-mapper behavior under different write/read contracts. The best-supported interpretation is a mapper emulation/composition or engineering-contract gap, not a new mathematical principle. A canonical witness was invalid because of a mask-encoding mismatch, which is an important warning. Wave 5C found an electrical-legality seam after power recovery in a corrected harness, but not a novel general method. A security-oriented Assassin review explained a resource cliff through ordinary retiming and incomplete memory inference. See the transcript-derived history and kill review files.

### Wave 6: formal, HLS, and cross-stage guarantees — mixed evidence

Wave 6A-C tested L2S liveness witness extraction against latch-changing preprocessing. The reported baseline and negative-control results support the conclusion that existing composition sufficed for the tested transformations. Wave 6C-B built CODO and ran a public GPT2 flow, but the exact claimed ping-pong case was absent; classification INCONCLUSIVE. Wave 6C-C identified a Dynamatic/EagerlyElastic × LSQ reproduction target, but no end-to-end execution completed because the required runtime was unavailable. Wave 6D-A could not reproduce MaskedHLSVerif because the required Vitis HLS and supporting stack were unavailable; no A/B experiment was run.

### MUXWISE experiments — direct artifacts

The MUXWISE project investigated whether resource sharing, arithmetic-tree mapping, and physical implementation created a credible residual research opportunity.

Experiment 1 completed 99/99 synthesis runs using Yosys 0.23 (`7ce5011c24b`) and ABC 1.01. Shared-versus-unshared formal checks passed; the intentionally incorrect subtraction failed as expected. The basic resource-sharing idea was already covered, and normal Yosys+ABC erased the tested sharing differences. No physical design was executed. Disposition: basic idea already covered.

Experiment 2 used Yosys 0.69+77 (`9ff27d29c-dirty`) and ABC 1.01, with 136 valid synthesis runs, seven formal checks, and two PicoRV32 current-flow runs. `synth -arith_tree` produced real family-sensitive mapped differences: it sometimes helped add-chains and sometimes harmed mixed/FIR cases. PicoRV32 normal and `-arith_tree` runs had the same 9,171-cell signature. The result retained F-AT-01 as a configuration-sensitive observation, not as a new research contribution.

Experiment 3 prosecuted the arithmetic-tree observation through a physical-design pilot. Placement/global routing ran, but there was no validated timing benefit from `-arith_tree`; equivalence was incomplete and the arithmetic-tree formal counterexample was real. Two seeded mapping runs matched while an unseeded repeat varied. An inherited manifest mislabeled a log containing `model found: FAIL` as PASS. Disposition: inconclusive; correctness had to be resolved first.

Experiment 4 resolved that correctness issue. Width-4 and width-8 normal flows passed, while `arith_tree` failed; `arith_tree -no-fma` passed both widths. The earliest divergence occurred immediately after `arith_tree`; pre-arithmetic-tree equivalence passed, post-pass equivalence failed, and techmap/ABC preserved the mismatch. Independent reference/simulation reproduced the difference (width 4 normal `0x00000` vs arithmetic-tree `0x00180`; width 8 normal `0x000186` vs arithmetic-tree `0x001986`). Disposition: genuine synthesis defect confirmed, qualified by dirty-binary provenance; `-no-fma` is a documented workaround. A clean build and broader ownership/novelty analysis are still required before claiming an upstream fix or research novelty.

### PassWitness — direct artifacts

PassWitness is the most complete recovered hardware-debugging/reduction artifact. Its local docs describe architecture, prior art, limitations, Phase 3 validation, Phase 4 reduction, reducer hardening, reproducibility, and release packaging. The package includes localized FMA clean/patched output packages, signed-FMA and injected-fault fixtures, pilot-one/zero research material, selected pilot-two provenance, and source modules. Treat it as an implemented evidence/reduction system and research substrate, not automatically as a novel contribution; the prior-art and limitation documents are part of the evidence.

### PPA-Delta — current provisional lead

PPA-Delta is a structured reducer/research program with an operating protocol, technical specification, research audit, experiment index, evidence ledger, candidate ledgers, weekly gates, and review/handoff documents. A C10 comparison used equal 200-candidate / 1800-second budgets with caching disabled. Coupled reduction beat valid baselines on 3/3 cases; a repaired bugpoint baseline produced NO_GAIN; one report gives a 39-versus-60 candidate result on a 21-node case without matching. However, a separate review says the coupled method met the stated ≥20% bar on 0/3 cases and structural correspondence was unsupported. Status: provisional/revise, not proven novelty.

## 5. Killed research directions

The important candidate decisions are in `05_KILLED_CANDIDATES/RESEARCH_KILL_DATABASE.md`. Highlights: MOSAIC was killed at the novelty gate; HBRoute reduced to ordinary shortest-path and coupled routing; DITSpec-HLS needs a real cross-stage theorem because timing is not preserved by the proposed formal rewrite; DeltaRTL’s failure-region predicate can conceal changed wrong values/timing; ArchWitness’s generic loop overlaps RE3 and lacks a usable formal environment; GhostForge did not identify a new refinement mechanism; FPExtrema’s fixed-format hardness claim narrowed substantially; and several memory/physical-design candidates were real engineering seams without an independent novel principle.

## 6. Recurring research failure patterns

The collected history supports these recurring patterns:

- A real implementation problem is explained by a known principle such as retiming, memory-inference failure, shortest-path routing, standard rip-up/reroute, or ordinary benchmark reduction.
- A tool failure is genuine but the contribution is only implementation debt, configuration sensitivity, or a missing workaround.
- The proposed semantic problem is interesting, but the witness or oracle is malformed, incomplete, or not independently grounded.
- A proposed theorem ignores timing, scheduling, lowering, or physical state even though the claimed guarantee is cross-stage.
- A general loop—counterexample, refinement, localization, or certificate transport—is not novel without a new invariant, oracle, guarantee, or complexity result.
- A promising result falls below its predefined effect-size bar or is unstable under seeds, workloads, baselines, or tool versions.
- Reproduction stops at environment/tool-access boundaries; a script or repository is not evidence that an experiment executed.

## 7. Completed experiments

Directly recovered and completed: MUXWISE Experiments 1–4 as documented; the Yosys arithmetic-tree/FMA investigation; PassWitness validation/reduction artifacts and localized FMA packages; and the PPA-Delta C10 comparison as documented by its local reports. Older waves include transcript-derived completed claims, but their primary artifacts are missing. Incomplete or unverified items include Wave 6C-C end-to-end reproduction, Wave 6D-A baseline/A-B reproduction, exact CODO ping-pong reproduction, clean rebuild of the Yosys defect, and any physical timing advantage from `-arith_tree`.

## 8. Current research status

**Alive/provisional:** PPA-Delta coupled reduction; a carefully scoped mapper semantic-contract investigation; and a precise cross-stage guarantee question if it can be stated with a new theorem and independent oracle.

**Resolved as engineering evidence:** MUXWISE arithmetic-tree defect and `-no-fma` workaround; PassWitness implementation/reduction evidence; several Wave 5 mapper and electrical seams.

**Killed or redefined:** MOSAIC, HBRoute, DITSpec-HLS in its original form, DeltaRTL, ArchWitness, GhostForge as originally framed, fixed-format FPExtrema hardness, and generic retiming/certificate/liveness formulations.

**Closed (2026-09-28):** UBP, the weight-independent universal block-pattern fabric (Waves 13–14). It was killed by its pre-registered Week 2 physical-fairness test; see the current-status section at the top.

**Missing/uncertain:** explicit Wave 8 and Wave 9 research packages; original Wave 3–6 reports; some candidate dossiers; clean source/build provenance for the Yosys defect; and material that may remain on another computer or account.

## 9. Rediscovery warnings

Do not propose generic resource sharing, generic retiming certification, generic counterexample-guided refinement, generic failure-region localization, generic shortest-path/rip-up routing, generic HLS configuration enumeration, or fixed-format extrema hardness without materially new evidence. Do not call a synthesis script an experiment unless the execution log, version, input, result, and independent check are present. Do not reuse the malformed memory witness. Do not label an inherited `model found: FAIL` log as PASS because the process exited zero. Do not treat a real Yosys defect, a benchmark win, or a tool workaround as a novel research contribution by itself.

## 10. Opportunities for a different research strategy

The program has already heavily explored broad ideation, prior-art attack, generic formal loops, synthesis configuration seams, physical-design ranking, memory-mapper cliffs, and single-tool reproduction. A different strategy should begin from an explicit unresolved scientific obligation and build the oracle first. Promising directions are narrower: prove a cross-stage semantic/security theorem that survives scheduling and lowering; establish a mapper contract theorem with a clean independent semantic and physical oracle; or rigorously determine whether PPA-Delta’s coupled reduction advantage persists across a broader, frozen, externally reproducible benchmark suite and stronger baselines. Any direction should include adversarial negative controls, clean rebuilds, seed/workload sensitivity, and a quantitative acceptance gate before implementation expands.

## 11. Source references

The most important direct sources are:

- `06_EXPERIMENTAL_EVIDENCE/MUXWISE/muxwise-experiment-01/EXPERIMENT_REPORT.md`
- `06_EXPERIMENTAL_EVIDENCE/MUXWISE/muxwise-experiment-02/EXPERIMENT_02_REPORT.md`
- `06_EXPERIMENTAL_EVIDENCE/MUXWISE/muxwise-experiment-03/EXPERIMENT_03_REPORT.md`
- `06_EXPERIMENTAL_EVIDENCE/MUXWISE/muxwise-experiment-04/EXPERIMENT_04_REPORT.md`
- `06_EXPERIMENTAL_EVIDENCE/YOSYS_FMA/FINAL_REPORT.md`
- `06_EXPERIMENTAL_EVIDENCE/YOSYS_FMA/FINAL_VALIDATION_REPORT.md`
- `06_EXPERIMENTAL_EVIDENCE/YOSYS_FMA/PR_6231_OWNERSHIP_REVIEW.md`
- `06_EXPERIMENTAL_EVIDENCE/PASSWITNESS/docs/`
- `06_EXPERIMENTAL_EVIDENCE/PASSWITNESS/output_packages/`
- `01_RESEARCH_OBJECTIVES_AND_STRATEGY/PPA_DELTA/Existing-Research-Audit.md`
- `01_RESEARCH_OBJECTIVES_AND_STRATEGY/PPA_DELTA/Experiment-Index.md`
- `01_RESEARCH_OBJECTIVES_AND_STRATEGY/PPA_DELTA/analysis/`
- `07_REMAINING_RESEARCH_LEADS/PPA_DELTA/docs/`
- `04_EARLIER_RESEARCH_WAVES/WAVE_6C_C/WAVE 6C-C — EAGERLYELASTIC × LSQ FRONTIER DOSSIER.md`
- `04_EARLIER_RESEARCH_WAVES/GHOSTFORGE_IDEATION_V2/`
- `04_EARLIER_RESEARCH_WAVES/CODEX_TRANSCRIPT_DERIVED_RESEARCH_HISTORY.md`
- `05_KILLED_CANDIDATES/CODEX_TRANSCRIPT_DERIVED_CANDIDATE_REVIEWS.md`

The transcript-derived files state which conclusions lack their original primary artifact. The package manifest gives source paths, destinations, sizes, hashes, categories, and inclusion reasons.
