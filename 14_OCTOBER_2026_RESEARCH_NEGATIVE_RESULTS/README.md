# October 2026 — Research failure and opportunity audit

**As-of:** 13 October 2026 (America/Los_Angeles)  
**Purpose:** searchable negative-result index and evidence-preserving research reset; not a proposal to restart killed work.  
**Status:** research archival update; no code execution, new architecture, RTL, chip design or independent benchmark reproduction performed in *this GitHub archival update*.

Read the [master handoff](../00_START_HERE/MASTER_RESEARCH_HANDOFF.md), [kill database](../05_KILLED_CANDIDATES/RESEARCH_KILL_DATABASE.md), [experimental index](../06_EXPERIMENTAL_EVIDENCE/EXPERIMENT_INDEX.md), [full failure forensics](sources/RESEARCH_FAILURE_FORENSICS.md) and [discovery protocol V2](sources/DISCOVERY_METHODOLOGY_V2.md) together. This folder supplements earlier waves; it does not rewrite their contemporaneous verdicts.

## Decision register

| Work / time | Decision and scope | Decisive evidence | Supporting report |
|---|---|---|---|
| PCAS / Oct 13 | **NO-GO at M0** for proposed proof-carrying arithmetic-synthesis research claim and chip/project escalation | Proof-producing/translation-validation prior art; possible post-hoc RTLIL `$fa` reader; self-consistent certificate not bound to actual gates, outputs or final `$add`; proposed speed/linear-cost claims unmeasured | [PCAS M0 audit](sources/PCAS_M0_GATE_REPORT.md) |
| CLAM / Oct 13 | **NO-GO for CLAM hardware candidate at M1**; retain finite correctness/oracle artifacts | 42 frozen bitset solver A/B/C runs across 14 instances passed solution-set correctness. S=4 had **identical** search nodes, propagation evaluations and queue counts to ordinary A on every instance; positive-family unbounded A/B work ratio **0.984335×** vs a pre-registered **2×** target | [gate](sources/CLAM_M1_GATE_DECISION.md), [correctness](sources/CLAM_M1_CORRECTNESS_REPORT.md), [baseline](sources/CLAM_M1_BASELINE_RESULTS.md), [capacity](sources/CLAM_M1_CAPACITY_AND_REUSE.md), [hardware](sources/CLAM_M1_HARDWARE_NECESSITY.md) |
| CausalTrace closure-aware retention / Oct 11–12 | **M0 allowed one software falsifier; M1 NO-GO** for tested hardware retention policy | **48 frozen RTL-based traces**, both enhanced schemes B/C reconstructed **48/48**; C achieved **zero additional correctly reconstructed cases** over simple pinned-descriptor/history hybrid B at equal 16 KiB | [M0 scope](sources/CAUSALTRACE_M0_FINAL_DISCOVERY_DECISION.md), [Stage 0 gate](sources/CAUSALTRACE_M1_DECISION.md), [results](sources/CAUSALTRACE_M1_RESULTS.md) |
| Decision-Sufficient Silicon / by Oct 12 | **NO-GO for ASIC**; fixed-affine interval correctness is not chip advantage | Synthetic eight-feature query savings **46.6–51.4%** are abstract cost weights rather than measured energy/real deployment benefit; exact early stopping and decision hardware have strong prior art; no sensor-energy/quality, PPA, RTL or real-workload evidence | [Gate 2](sources/DECISION_SUFFICIENT_RESEARCH_GATE_2.md) |
| Silicon Opportunity (SAT, RTL simulation, mapping) / Oct 13 | **INSUFFICIENT EVIDENCE; no silicon advances** (not a general no-silicon theorem) | **126 completed native runs**/42 configurations×3; MiniSAT **0.783s** vs Kissat **10.739s** on selected UNSAT case, tuned Verilator **2.326s** vs Icarus **31.706s** on selected benchmark. Missing PMU counters, 2 profile timeouts, mapping equivalence and published-score discrepancies prohibit bottleneck/necessity claim | [opportunity decision](sources/SILICON_OPPORTUNITY_DECISION.md) |
| Wave 10 MappingEvolve / archived earlier | **Original mapped-area advantage not sustained under strongest fair iso-delay baseline** | Matched-delay `emap` baseline defeated the evolved variants on the audited cohort; prior claim comparison confounded by delay relaxation | [Wave 10 final](../12_WAVE_10_EXPERIMENTAL_DISCOVERY/06_FINAL_DECISION.md) |
| Wave 10 OpenROAD resynthesis / archived earlier | **NO-GO for suggested performance gain** | Eight default-script search runs worsened timing; ordinary `repair_timing -setup` won; functional equivalence alone did not confer utility | [Wave 10 final](../12_WAVE_10_EXPERIMENTAL_DISCOVERY/06_FINAL_DECISION.md) |
| Wave 11 H1.6 exact covering / partial historical record | **UNRESOLVED / do not promote to a win or a definitive kill without raw re-audit** | Archive has clear prior-art/evaluator specification; retrospective report of weak near-tie capture and many FEASIBLE rather than OPTIMAL solves is prior-session evidence only | [forensics](sources/RESEARCH_FAILURE_FORENSICS.md), [evaluator](../13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION/06_EXPERIMENTAL_EVALUATOR.md) |

### Not failures: useful engineering contributions

- **Yosys signed-FMA correction PR [#6231](https://github.com/YosysHQ/yosys/pull/6231): merged on 7 October 2026.** This is verified upstream engineering, **not** a newly established proof-producing synthesis theory or a claim that `arith_tree` yields a general PPA improvement. See [Yosys FMA evidence](../06_EXPERIMENTAL_EVIDENCE/YOSYS_FMA/FINAL_VALIDATION_REPORT.md).
- **PassWitness:** reproducible localization/reduction workflow. Its engineering value is separate from novel algorithmic guarantees; see [prior art](../06_EXPERIMENTAL_EVIDENCE/PASSWITNESS/docs/prior-art.md).
- **GateTruth:** benchmark/infrastructure documentation is promising as engineering. The failure forensics separately notes benchmark limitations, and does *not* certify third-party impact, independent model-score reproduction or paper acceptance.

## Evidence grading and portability

This folder copies user-provided Markdown decision reports into `sources/` to preserve the actual reasoning. It does **not** upload or recompute every raw solver trace, benchmark run, input hash, script, git SHA or archive the complete Windows/WSL project trees. The source reports are **author-supplied project records**; claims of independently checked runs inside them describe the *original reported experiment*, not this archive operation. Their raw details and reproducibility instructions should be consulted on the originating projects. Some copied reports contain absolute local `/mnt/c/Users/...` paths that are **not accessible within this GitHub archive**; they are kept verbatim as provenance, not working links.

The [forensics](sources/RESEARCH_FAILURE_FORENSICS.md) defines its own evidence tiers (E1 public independently inspected, E2 literature, E3 repo report, E4 prior-conversation reconstruction, E5 interpretation). Do not upgrade E4 to E1 by copying it. A SAT timeout, unverified equivalence check, missing performance counter or missing source remains UNKNOWN.

## Prevent the same failure cycle

1. **Problem evidence first.** No architecture advances because its mechanism looks original. Demand practitioner-grounded evidence of an important problem still unsolved by strong existing methods.
2. **Semantic and mathematical reduction first.** Try a known algorithm, degenerate-instance reduction, post-hoc graph reader, no-change or baseline software policy before proposing new circuitry.
3. **Same contract / same resource budget.** Compare at equivalent accuracy, delay, memory, correctness, workload and tuning budgets; inspect direct logs, not inferred PASS statuses.
4. **Independent checker that binds the actual artifact.** Producer-written claims, hashes and locally valid components do not by themselves prove source-to-netlist semantics.
5. **Fail cheaply.** Preregister a decisive counterexample/threshold and stop if it fails; do not post-rationalize architecture need from successful correctness tests.
6. **Silicon only after a persistent residual.** Show algorithmic headroom against modern optimized software and a real limiting resource/data movement/energy case; simulation-only speed predictions do not qualify.
7. **Keep verdict dimensions separate.** Problem importance, scientific novelty, engineering value, ASIC justification, and external impact do not imply one another.

**Prospective experiment:** treat V2 as a hypothesis about lowering false research starts, not as a guaranteed discovery formula. Track per-candidate M0 rejection reason, actual cash/computation spent, evidence grade, published incumbent, and whether an independently useful contribution survives.
