# 03 — Strongest prior art for the demonstrated C1 limitations

This document follows the Wave 10 rule: targeted prior art is searched only *after* a limitation has been demonstrated experimentally. Each limitation below is one that D1 showed (see `04_EXPERIMENTAL_INVESTIGATION.md`). For each, the prior art is separated into **claim**, **implementation**, **evaluation** and **what remains unresolved**.

Evidence labels:
- **OBSERVED:** our experiments.
- **PAPER:** the source states it; we read the abstract, HTML or blog.
- **UNVERIFIED:** search snippet only.

## Limitations demonstrated in C1 (OBSERVED, D1, 53 circuits × 35 configs, 1,855 netlists all independently validated)

- **L1 — the headline gains are mostly an area–delay trade-off, not a better mapper.**
  - GPT-5 it29 against mockturtle `map` on EPFL-20: area ratio 0.9186 = 0.9537 (relaxation) × 0.9632 (operator).
  - Against ABC `&nf`: 0.9496 = 0.9537 × **0.9957**. At equal delay, the evolved mapper is essentially equal to ABC.
- **L2 — the evaluation omits the strongest in-library baseline.**
  - mockturtle's own `emap` (same repository and commit) at the evolved mapper's delay is better. GPT-5 / DeepSeek / Qwen area ratios against emap@D_e:
    - EPFL-20: 1.024 / 1.029 / 1.052;
    - IWLS05-22 (held out): 1.062 / 1.053 / 1.075.
  - Against the best baseline at iso-delay:
    - EPFL: 1.050 / 1.044 / 1.075 (wins on 5, 3 and 1 of 20 circuits);
    - IWLS: 1.073 / 1.076 / 1.108.
- **L3 — the ABC baseline used in the paper is weaker than current ABC defaults.**
  - On identical compress2 AIGs, our yosys-abc `&nf` gives the paper's delays exactly on most circuits but 5.2% less area (mean our/paper = 0.9479).
  - GPT-5's "10.04%" becomes 5.13% against current `&nf` defaults (mean area ratio 0.8996 → 0.9487).
  - Which ABC version or options the paper used is UNVERIFIED.
- **L4 — provenance.** The paper's DeepSeek column is produced by *no* released DeepSeek operator state: all 5 distinct states of the proactive run, plus the direct-OpenEvolve runs, give at most 3/20 matches, and that 3/20 is the initial mapper. The GPT-5 and mockturtle columns reproduce 20/20.
- **Not a limitation — correctness.** All 159 evolved-operator netlists (3 variants × 53 circuits) pass independent simulation against the original AIG and ABC CEC of our own netlist translation. The paper's "0 equivalence failures" claim is **confirmed**.

## Targeted prior art

### P1. Iso-delay (constraint-matched) comparison of mappers — the remedy for L1

- **Claim/practice.** Standard-cell mappers are compared on area under a matched delay constraint, or on delay at matched area. This is why mappers expose required-time and relaxation knobs:
  - ABC `&nf -R/-D`;
  - mockturtle `map`/`emap` `required_time`;
  - emap's `relax_required`.
- **Implementation.** The knobs exist in exactly the tools MappingEvolve uses (OBSERVED: `mapping.hpp` `required_time`; emap `relax_required`; ABC `&nf -R`).
- **Evaluation.** MappingEvolve reports area and delay side by side and a scalarized S_overall (α = 0.5). That rewards buying area with delay, and no matched-delay comparison is reported (PAPER).
- **Unresolved?** No. The remedy is standard practice. This is an evaluation defect of one paper, not an open problem.

### P2. The stronger mockturtle mapper `emap` — the remedy for L2

- **Claim.** "Technology Mapping Using Multi-output Library Cells", A. Tempia Calvino and G. De Micheli, ICCAD 2023:
  - emap is an extended mapper supporting Boolean, structural and hybrid matching, large cells and multi-output cells;
  - it gives "a 2x speedup in mapping time compared to command map for similar or better quality" (PAPER/UNVERIFIED via mockturtle docs and search).
- **Implementation.** `emap.hpp` is present in the same mockturtle commit MappingEvolve vendors (`420f027`, OBSERVED).
- **Adoption.** Antmicro integrated emap into OpenROAD as `resynth_emap` (PR #9097, blog 2026-06-30). It reports a 10% area reduction on jpeg_encoder/SKY130 using multi-output cells, with timing repaired afterwards by `repair_timing` (PAPER; no ABC or post-route comparison given). The local ORFS image predates it: `resynth_emap` is absent (OBSERVED, `probe_emap_openroad.log`).
- **Unresolved?** No. The baseline exists and is actively deployed. Our emap runs used single-output cells only, the same library view as `map`.

### P3. Scalarized versus multi-objective fitness in LLM-driven heuristic evolution — the root cause of L1 in the method

- **MEoH.** "Multi-Objective Evolution of Heuristic Using Large Language Model" (Yao, Liu, Lin, Lu, Wang, Zhang; AAAI 2025): LLM-based evolution of a non-dominated *set* of heuristics with dominance-dissimilarity selection (PAPER).
- **REMoH.** Reflective evolution of multi-objective heuristics, arXiv 2506.07759 (UNVERIFIED).
- **Pareto-Grid-Guided LLM heuristic design.** arXiv 2507.20923 (UNVERIFIED).
- **TIDE.** Tuning-integrated dynamic evolution, arXiv 2601.21239. It separates structure evolution from parameter tuning. The confound we isolated (code change vs knob setting) is its motivation (PAPER/UNVERIFIED).
- **Unresolved?** No. Replacing a scalarized fitness with Pareto or iso-QoR selection is established in the LLM-AHD literature; applying it to tech mapping would be routine integration.

### P4. Critiques of LLM-based heuristic-design evaluation — the general form of L1–L3

- **Zhang, Liu, Lin, Wang, Lu, Zhang**, "Understanding the Importance of Evolutionary Search in Automated Heuristic Design with Large Language Models", PPSN 2024 (arXiv 2407.10873). It names "inconsistent benchmark settings, inadequate baselines" as the reason true progress is unclear (PAPER).
- **Machine referee review of MappingEvolve.** Pith / grok-4.3, 2026-05-07. It flagged equivalence enforcement and generalization / data leakage; it did **not** raise iso-delay fairness, the emap baseline or the ABC configuration (PAPER, fetched).
  - Our D1 answers its equivalence concern *in the paper's favour*: 1,855 of 1,855 netlists validated.
  - Its generalization concern is also partly answered: the in-framework operator gain persists on held-out IWLS05, 0.960 vs initial@D_e.
- **Unresolved?** The *specific* findings L1–L3 are new relative to this review, but they are findings about one paper's evaluation. A critique note is not a research contribution under the Wave 10 criteria (not A–E).

### P5. Related LLM/agent evolution of EDA code — context for what an extension would compete with

- Multi-Agent Self-Evolved ABC, arXiv 2604.15082. The abstract gives no numbers and releases no code (PAPER).
- AuDoPEDA, arXiv 2601.06268: coding agents improving OpenROAD QoR (PAPER).
- "Rethinking Logic Optimization Operators: Theory-Derived Operator Compression via Agentic Source Analysis", arXiv 2607.23672 (UNVERIFIED).
- "Order Matters: … Macro Placement Sequences via Proxy-Guided LLM Evolution", arXiv 2606.08904 (UNVERIFIED).
- **Unresolved?** One direction is not closed by these works: *evolving from the strongest mapper (emap) and selecting at iso-delay*. It cannot be tested here, because the user's approval excluded LLM API calls. It is recorded as untested (UNRESOLVED as a direction, no claim made).

### P6. Physically aware mapping — relevant if post-route were the next question

- The mismatch between mapping-level delay models (load-independent) and post-layout delay is stated and targeted in prior art:
  - "Physically Aware Synthesis Revisited" / PigMap (arXiv 2408.07886, ASAP7 + OpenROAD P&R);
  - PigMap2 (2025);
  - LevelSyn (arXiv 2609.03594);
  - GNN path-aware mapping (arXiv 2601.14286).
- All are UNVERIFIED beyond abstracts and snippets.
- **Unresolved?** Occupied. A post-route re-ranking study of mappers would be confirmatory, so it was not registered as a candidate.

## Contribution test for C1 (as required by the prompt)

| Type | Does anything from C1 qualify? |
|---|---|
| A. New mechanism | No. The evolved mechanism is tolerance-gated match selection. D2 tests where its effect comes from; the ideas are tie-breaking variants of existing area-flow and exact-area selection. |
| B. Nontrivial extension | Not testable here. "Evolve from emap with iso-delay selection" needs LLM calls, which were excluded. It would also mostly be integration of P2 + P3. |
| C. New guarantee | No. |
| D. Substantial algorithmic improvement | No. The evolved operators are dominated by emap at iso-delay on EPFL and on held-out IWLS. |
| E. New methodology | No. Iso-delay evaluation (P1), multi-objective fitness (P3) and the baseline critique (P4) are established. |

**Result: C1 has no research residual → KILLED.** The engineering residual is a reproducible critique package: harness, independent validator and pre-registered tables. The user could send it to the MappingEvolve authors. Nothing has been sent.

---

# C6 — targeted prior art for the demonstrated limitation

## Limitation demonstrated (OBSERVED, 04 §7)

On placed ORFS asap7/aes (WNS −29.38 ps), OpenROAD's search-based resynthesis with default parameters ends *worse than doing nothing* on **every** run:
- `resynth_annealing`, 5 seeds: −88.8 to −141.2 ps, median −113.7;
- `resynth_genetic`, 3 seeds: −117.1 to −123.5 ps.

Annealing followed by repair ends 10.3 ps (median) worse than repair alone. In the blog's own unplaced setting, the 3 annealing seeds also end worse (−3.6 to −21.1 ps). All 19 treated netlists are functionally equivalent.

The fixed-script `resynth` gives −193.5 ps. Standard `repair_timing -setup` gives −5.5 ps in 4.7 s.

The tool's own log shows the mechanism: the annealing starts from a random 10-operation ABC script at −147 to −196 ps and climbs back for 100 iterations. It then applies the best script found, even when that script is worse than the untouched netlist. There is no "do no harm" comparison against the original. The blog's positive example ran on an unplaced test netlist, not the documented placed setting.

## Claim / implementation / evaluation / unresolved

- **Claim** (PAPER, Antmicro blog 2025-11): AES WNS −30.92 → +20.59 ps. One example, no baseline.
- **Implementation** (OBSERVED + upstream source): upstream `Restructure.h` defaults are `annealing_iters_ = 100`, `annealing_init_ops_ = 10`, GA population 4 × 10 iterations. The end-of-search application of the best-found script has no acceptance test against the starting netlist; this is INFERRED from the RMP-0068 log line and the observed regressions.
- **Evaluation:** the blog ran on an unplaced netlist from a unit test. It gave no multi-seed statistics, no comparison with `repair_timing`, and no equivalence evidence.

## Prior art on the method class

All UNVERIFIED beyond titles and snippets seen in this wave.
- Searching ABC optimization-script sequences for QoR is an established, crowded topic: SA/GA/RL/bandit script search, e.g. DRiLLS (RL), FlowTune (multi-armed bandits), Bulls-Eye (few-shot active learning), "Exploring Logic Optimizations with Reinforcement Learning" (dl.acm.org/doi/10.1145/3380446.3430622, seen in this wave's search results).
- OpenROAD-level agentic and flow tuning: AuDoPEDA (2601.06268), ORFS-agent (2506.08332), OR-AutoTuner.

## Unresolved?

No research residual:
- The defect found is an **implementation/evaluation** issue. Fixing it is standard engineering: compare against the untouched netlist and keep the better, start from the identity or the default script, and report `repair_timing` as the baseline.
- The method class is occupied.

## Contribution test (C6)

**A–E all fail.** The residual is an engineering bug report that the user could file with OpenROAD/Antmicro. Nothing has been filed; filing is outward-facing and is the user's decision.
