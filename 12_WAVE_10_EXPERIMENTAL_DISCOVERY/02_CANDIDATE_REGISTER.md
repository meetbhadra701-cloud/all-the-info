# 02 — Candidate register (Wave 10)

Evidence labels:
- **OBSERVED:** we ran it.
- **PAPER:** stated by the authors.
- **INFERRED:** our reasoning.
- **UNVERIFIED:** search-snippet only.

The allocation was progressive. Screening kills were cheap, and one candidate received the decisive experiment. The discovery order is the one the Wave 10 prompt requires: method → exact claim/baseline → strongest implementation → limitation → independent validation → cause → existing solutions → unresolved → contribution → killing experiment.

## Screening-level entries (killed before any experiment)

### S-1 Cross-stage (PPA-aware) placement for AI placers — KILLED at screening

- **Method and claim:** RePlAce/DREAMPlace-class placers; the claim is that AI placers improve PPA.
- **Why killed:** ChiPBench (NeurIPS'25) already shows HPWL is a poor proxy and that all six AI placers degrade PPA vs Hier-RTLMP. PPAPlace (ICCAD'26) already makes WNS/TNS differentiable using post-GR labels.
- **Labels:** PAPER/UNVERIFIED.

### S-2 OpenROAD `repair_timing` effort/grinding — KILLED at screening

- **Method and claim:** OpenROAD rsz; the claim is that `repair_timing` grinds.
- **Why killed:** Issue #10900 (2026-07-13) measures it and proposes `-effort explore|tapeout`. bazel-orfs "study" PRs quantify the ranking and yield of repair. AuDoPEDA applies coding agents to OpenROAD QoR.
- **Labels:** PAPER (issue text), UNVERIFIED (PR titles).

### S-3 Parallel RTL simulation scaling — KILLED at screening

- **Method and claim:** Verilator, RepCut and Parendi; the claim is parallel RTL simulation scaling.
- **Why killed:** Parendi (ASPLOS'25), RTeAAL Sim and CCSS occupy the space, and our hardware (no IPU or GPU) cannot test the frontier.
- **Labels:** PAPER/UNVERIFIED.

### S-4 Processor fuzzer effectiveness — KILLED at screening

- **Method and claim:** Cascade and Encarsia; the claim is fuzzer coverage and bug-finding.
- **Why killed:** Encarsia's bug-injection evaluation and the ARCUS SoK (arXiv 2608.23933, one month old) occupy it.
- **Labels:** PAPER/UNVERIFIED.

### S-5 Exact CGRA mapping scalability — KILLED at screening

- **Method and claim:** SAT-MapIt; the claim is that exact mapping does not scale.
- **Why killed:** Monomorphism-based mapping (arXiv 2512.02859) reports "approximately 10^5×" speedup on 20×20 CGRAs, from the same group.
- **Labels:** PAPER.

### S-6 Accelerator mapping DSE optimality — KILLED at screening

- **Method and claim:** Timeloop and ZigZag; the claim is mapper optimality.
- **Why killed:** A mature, crowded area, and no local checkable gap was identified.
- **Labels:** UNVERIFIED.

## Credible candidates

### C1 — LLM-evolved technology-mapping operators (MappingEvolve)

- **Important method:** mockturtle `map` (ABC-`map`-style cut-based standard-cell mapping) plus LLM code evolution of its three operators (MappingEvolve, arXiv 2604.26591; MIT artifact with 30-iteration runs from 3 LLMs).
- **Exact claim** (*PAPER*):
  - EPFL: "10.04% area reduction versus ABC and 7.93% versus mockturtle", with a 4.46–6.50% delay trade-off. From the paper's own table averages, the 4.46% is GPT-5's delay increase over mockturtle (1.0369/0.9926) and the 6.50% is DeepSeek's (1.0571/0.9926).
  - 0 equivalence failures (ABC `cec`).
  - The headline mapper is GPT-5 iteration 29.
- **Why selected:**
  - The claim is exact and was reproduced locally.
  - The evaluation has three testable weak points:
    - scalarized area+delay fitness, so gains may be trade-off moves;
    - an ISCAS85-only fitness set;
    - a load-independent genlib delay with no physical design.
  - The baselines omit mockturtle's own newer mapper, `emap`.
- **Decisive experiment:** D1, iso-delay dominance vs the in-framework, emap and ABC baselines with independent validation. See `experiments/results/c1_PREREGISTRATION.md` and `04_EXPERIMENTAL_INVESTIGATION.md`.
- **Status:** see `06_FINAL_DECISION.md`.

### C2 — Multi-width/Vt exploitation of the GT2N 2 nm GAAFET PDK in the open flow

- **Important method:** ORFS on GT2N (w13/w31 nanosheet widths × 5 Vt flavors, backside power).
- **Observation** (*OBSERVED*, gcd, `LEC_CHECK=0`):
  - All 27 CI metric rules pass.
  - Finish setup WS is +150.06 ps.
  - The final netlist uses ELVT (e.g. 35 `dffasync_x1_w13_elvt`, 23 `aoi21_x1_w31_elvt`) and ULVT (54 `buf_x2_w13_ulvt`) cells despite the slack.
  - Leakage is 5.2% of total power.
- **Why not advanced:** Vt/width recovery under positive slack is a standard leakage-recovery knob, not a research gap. At 5.2% leakage share the consequence is small.
- **Status:** **ENGINEERING ONLY** (screening-level; one design).

### C3 — FPGA timing-driven placement (nextpnr class)

- **Important method:** nextpnr, VTR and analytical FPGA placers.
- **Status:** **NOT REACHED.** It was held in reserve as the next candidate if C1 died. No experiment was run and no claim about it is made here.

### C4 — MILP buffer placement in dynamically scheduled HLS (Dynamatic)

- **Important method:** Dynamatic's fpga20/fpl22 MILP buffer placement.
- **Observation** (*OBSERVED*, `experiments/logs/screening/probe_dynamatic.log`): the local Dynamatic is at `0cab874` (2024-03), and `GUROBI_LIBRARY-NOTFOUND`. The MILP buffer algorithms cannot run.
- **Status:** **BLOCKED (licensing).** No results claimed.

## Candidates screened after C1 died (progressive allocation)

### C3 (re-screened) — nextpnr placement

- **Observation** (*OBSERVED*, `probe_nextpnr.log`): the local OSS CAD Suite 20260921 (Linux) ships nextpnr-ecp5, -ice40, -himbaechel, -machxo2 and -nexus with chip databases, so it is runnable in a sandbox.
- **Prior art:** "Revisiting Gradient Direction Algorithms in Electrostatic Placers" (Springer) already studies nextpnr's electrostatic placer, comparing Nesterov with RMSProp, Adam, Adan and adaptive restarts (*UNVERIFIED*). No other exact, checkable open claim was identified.
- **Status:** NOT PURSUED. No decisive experiment could be defined without first inventing a claim.

### C5 — mockturtle emap inside OpenROAD (`resynth_emap`, Antmicro, PR #9097)

- **Claim** (*PAPER*, blog 2026-06-30): 10% area on jpeg_encoder/SKY130 with multi-output cells. The blog gives no ABC comparison and no post-route result.
- **Why blocked:** the local OpenROAD has `resynth`, `resynth_annealing` and `resynth_genetic`, but **no `resynth_emap`** (*OBSERVED*, `probe_emap_openroad.log`). Testing would need an OpenROAD rebuild from source.
- **Status:** BLOCKED (would need a from-source OpenROAD build).

### C5b — whether mapping-level (genlib) QoR rankings survive P&R

- **Prior art:** the mismatch is stated and targeted by physically aware mapping: PigMap/PigMap2 (arXiv 2408.07886), LevelSyn (2609.03594), GNN path-aware mapping (2601.14286) (*UNVERIFIED*).
- **Status:** NOT REGISTERED. It is occupied, and a study would only confirm it.

### C6 — search-based post-placement resynthesis in OpenROAD (`resynth_annealing` / `resynth_genetic`)

- **Important method:** OpenROAD mainline rmp (Antmicro 2025). Simulated annealing or a GA searches ABC operation sequences on logic below a slack threshold, with worst slack as the objective.
- **Exact claim** (*PAPER*, blog 2025-11): AES/ASAP7 WNS −30.92 → +20.59 ps. The blog gives no baseline, no area or runtime, and no LEC.
- **Why selected:**
  - it is runnable locally;
  - the claim is exact;
  - the natural baseline, `repair_timing`, is absent from the claim;
  - the published "before" state is reproducible (ours: −29.38 ps).
- **Decisive experiment:** `experiments/results/c6_PREREGISTRATION.md`; results in 04 §7.
- **Status:** see `06_FINAL_DECISION.md`.

## Allocation record

| Candidate | Effort spent | Outcome |
|---|---|---|
| S-1..S-6 | search plus abstract reading | killed at screening (occupied) |
| C2 | one full ORFS gt2n run (65 s) plus probes | ENGINEERING ONLY |
| C4 | local probe only | BLOCKED |
| C1 | build, 2 reproduction stages (R1, R2), decisive D1 (53 circuits × 35 configs = 1,855 validated netlists), cause isolation D2 (168 netlists) | KILLED (see 06) |
| C3 | re-screen (probe plus prior-art search) | NOT PURSUED (occupied; no exact claim) |
| C5 / C5b | probes plus prior-art search | BLOCKED / not registered |
| C6 | ORFS aes placement, 13 treatment runs, equivalence checker | see 06 |
