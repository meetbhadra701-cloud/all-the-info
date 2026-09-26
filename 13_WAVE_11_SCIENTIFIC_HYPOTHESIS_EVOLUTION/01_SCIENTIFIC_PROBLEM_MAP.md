# 01 — Scientific problem map (Wave 11)

**Evidence labels.**
- **OBSERVED:** we ran it, or read the source code ourselves.
- **PAPER:** stated by the authors.
- **INFERRED:** our reasoning.
- **UNVERIFIED:** not checked at the primary source.

## Part I — What the archive teaches (internalized, not re-investigated)

**Mission** (`00_START_HERE/MASTER_RESEARCH_HANDOFF.md`). The goal is one scientifically defensible semiconductor/EDA contribution. It needs:
- a precise problem;
- a materially unoccupied contribution;
- an independent oracle;
- experiments that separate the mechanism from implementation debt and benchmark luck.

**Record so far.**
- Waves 3–6 and MUXWISE/PassWitness/PPA-Delta are transcript-derived or direct artifacts. Waves 8/9 **remain unrecoverable** (`02_WAVE_8/`, `03_WAVE_9/RECOVERY_NOTE.md`).
- Session 1 ended with zero survivors after about 45 probes.
- TRACE/Yosys was ENGINEERING ONLY.
- Wave 10 killed C1 (MappingEvolve) and C6 (OpenROAD search-based resynthesis).

**Recurring failure patterns (handoff §6), and how Wave 11 guards against each:**

| Pattern | Guard in this wave |
|---|---|
| A real problem is explained by a known principle | A hypothesis must name its *mechanism*, and review must find the mechanism, not just the problem, in prior art. |
| A tool failure is only implementation debt | No hypothesis may rest on a bug. Wave 10's regressions are inputs, not candidates. |
| Malformed or ungrounded oracle | The evaluator (06) is designed before the experiment. Every generated netlist gets independent checking. |
| A cross-stage claim ignores timing or lowering | Objectives are stated with their constraint (e.g. area *at* a delay). |
| A generic loop is claimed as novel | Review distinguishes principle from mechanism (the Part V classification). |
| Effect below the bar or unstable | Pre-registered kill/advance thresholds. |
| Reproduction stops at tool access | Problems whose central test cannot run locally are marked as such and are not selected. |

**Wave 10's lesson, as the brief states it.** We are good at *finding limitations*. Wave 11 must *formulate and test mechanisms*.

The concrete consequence here is methodological. The first experiment tests a **necessary assumption of a mechanism class**, not a published claim.

**Successful techniques to keep:**
- a network-off container sandbox;
- pre-registration with a deviation log;
- independent netlist evaluators (`c1_eval.py`: own STA, simulation against the original AIG, CEC from own translation);
- iso-constraint comparison against the strongest baseline;
- mutation negative controls for every checker.

## Part III — Survey: consequential problems considered

The survey stays compact. Problems were screened on three criteria:
1. Is the limitation precise and caused by something identifiable?
2. Is there an independently checkable objective?
3. Can a central assumption be tested locally, inside a network-off sandbox, without a commercial licence?

**Logic synthesis: delay-constrained area recovery in technology mapping.**
- **Objective:** minimum cell area subject to worst arrival ≤ D.
- **Frontier:** cut-based mappers: ABC `&nf`, mockturtle `map`/`emap`.
- **Limitation (evidence):** mappers differ by 3–7% area at matched delay. Area-vs-D curves are non-monotone for `map` and `&nf`. Distance to optimum is unknown (OBSERVED, W10 D1/D2, E0).
- **Local testability:** yes. Exact optimization via Z3 νZ is available in the sandbox.
- **Selected:** **P1**.

**HLS / dataflow architecture: throughput-constrained buffering of dynamically scheduled circuits.**
- **Objective:** minimum buffer area subject to target throughput and clock period.
- **Frontier:** Dynamatic MILP (fpga20/fpl22) with per-CFDFC throughput and fluid retiming.
- **Limitation (evidence):** a MILP whose throughput part is per choice-free cycle set, needing a commercial solver in practice (OBSERVED: local Dynamatic is Gurobi-only).
- **Local testability:** no. No Gurobi or local MILP solver, and no Dynamatic runtime flow here.
- **Selected:** **P2** (generation and review only).

**Physical design: post-placement timing repair.**
- **Objective:** close setup timing at minimum area.
- **Frontier:** OpenROAD `repair_timing` (path-based greedy); LR discrete sizing; differentiable sizing.
- **Limitation (evidence):** greedy repair grinds on large designs (#10900: 290 iterations, −803 → −603 ps). It interacts badly with resynthesis (W10 C6: EST-0104, RSZ-0075).
- **Local testability:** partly. ORFS runs locally, but large designs are needed.
- **Selected:** **P3** (generation and review only).

Problems considered and not selected:

| Area | Problem | Reason not selected |
|---|---|---|
| Logic synthesis | Structural bias of the subject graph | Choice networks (`&dch`, lossless synthesis) and our TRACE session already cover this neighbourhood. |
| Physical design | Macro placement quality; routing | ChiPBench/PPAPlace; ISPD GR contests (W10 screening). |
| Architecture / accelerators | Dataflow mapping of DNN accelerators | Crowded (Timeloop/ZigZag), and no local simulator. |
| Memory | Banked-memory mapping cliffs | Archive Waves 4A/5B: engineering seams. |
| Hardware security | Masking or constant-time preservation through synthesis/HLS | DITSpec-HLS killed in the archive. Needs verification tools (SILVER/Coco) that are not local. |
| Formal verification | (Deliberately de-emphasized; the brief asks us to leave this neighbourhood.) | n/a |
| AI-assisted EDA | Evolved heuristics that transfer to stronger baselines | The only real test needs LLM API spend, which is not authorized. A methodology audit is excluded by the brief. |
| DSE | Flow-parameter search under tool noise | ORFS-agent / AutoTuner / "noise" studies (UNVERIFIED titles from W10 search). |

## P1 — Delay-constrained area recovery in cut-based standard-cell technology mapping

**Scientific objective.** Given a subject AIG, a cell library and a delay bound D, choose a cover (cell netlist) that minimizes total cell area subject to worst arrival ≤ D. Every synthesis flow solves this. Area at fixed delay is die cost and leakage.

**Current frontier.** The dominant paradigm is cut-based DAG covering (ABC `map`/`amap`/`&nf`; mockturtle `map`, `emap` [ICCAD'23]). It proceeds as follows:
1. Enumerate priority cuts (≤ 6 inputs).
2. Boolean-match each cut to library gates, in both output phases.
3. Run a delay-optimal pass. For load-independent delays this is exact over the cut space (DAG covering, Kukimoto–Brayton–Sawkar DAC'98 — UNVERIFIED citation detail).
4. Recover area: compute required times on the current cover, then re-select each node's match to minimize **area flow** (sharing-amortized area) or **exact local area** (MFFC-based), subject to its required time.

emap adds two things (OBSERVED in `emap.hpp`):
- area-oriented *match alternatives* kept during the delay pass;
- exact-area recovery run in **reverse** topological order (`compute_mapping_exact_reversed`).

**Important limitation (OBSERVED).**
1. **Mappers disagree materially at the same delay.** At each evolved mapper's delay on EPFL-20, emap beats mockturtle `map` by several percent (W10 D1: GPT-5/`map`@D_e 0.963 vs GPT-5/emap@D_e 1.024). ABC `&nf -p` wins on other circuits. At least some of them are far from optimal, but **nobody in our data knows how far the best one is**.
2. **Area recovery is path-dependent.** Changing only which match the *delay pass* keeps, with no change to area recovery, reduces area by 3.6% at the *same* delay (W10 D2, 168 validated netlists). The recovered area therefore depends on the starting cover, not only on D.
3. **Recovered area is non-monotone in D for some mappers (E0, this wave).** A looser constraint gives more than 1% *more* area on 2.0% of ordered constraint pairs for `map` (13/53 circuits; worst +14% adder, +11% vga_lcd), 1.9% for ABC `&nf` (worst +38% priority), and only 1.3% for emap (worst +2.7%).
   - Honest reading: erratic trade-off curves are **not** the main symptom for the strongest mapper, which is nearly monotone.
4. **ABC's relaxation knob is inert on the three deepest circuits** (div, hyp, sqrt: identical results for R = 2…37; W10).

**Cause (OBSERVED in `mapping.hpp`/`match_phase.cpp`; INFERRED for `&nf`).**
- **Timing slack is allocated greedily.** Required times come from the *previous* cover. Each area pass visits nodes in a fixed order and lets each node take any match whose arrival fits its own required time. A node visited early consumes slack that nodes visited later can no longer use, so the allocation follows traversal order, not where slack buys the most area. emap's reversed exact-area pass changes *which* nodes get first claim; it does not allocate slack globally.
- **Sharing is estimated, not modelled.** Area flow divides a node's area by an *estimated* fanout count. Exact local area is exact only for a node's MFFC. Neither sees how a choice at one node changes the best choices elsewhere.

**Opportunity.** A covering method that treats slack allocation and sharing *jointly and globally*, even approximately, could find covers with less area at the same D.

**The quantity we do not know, which decides whether this opportunity is real:** how far the heuristics are from the *optimum within their own search space* (same cuts, same matches, same delay model). If that headroom is small, better covering algorithms cannot matter, and the lever would be the representation instead (cut sets, supergates, structural choices).

**Evidence.** W10 D1/D2 records (1,855 + 168 validated netlists), E0 (`experiments/results/e0_monotonicity.json`), the mockturtle source (OBSERVED), the emap paper (PAPER/UNVERIFIED).

## P2 — Throughput-constrained buffering of dynamically scheduled (elastic) HLS circuits

**Scientific objective.** Insert the fewest or smallest buffers into a dataflow circuit so that each choice-free cycle set (CFDFC) reaches its target throughput and every combinational path meets the clock period.

**Current frontier (OBSERVED in local Dynamatic `0cab874`, `lib/Transforms/BufferPlacement/`).** A Gurobi MILP with:
- per-channel slot counts and buffer-presence variables;
- per-CFDFC, per-unit "fluid retiming" variables and per-channel throughput variables;
- timing path constraints through potential buffers.

Two published variants exist: fpga20 (Josipović et al., FPGA 2020) and fpl22 (timing-aware) (PAPER/UNVERIFIED titles).

**Important limitation.**
- The throughput model is enumerated per CFDFC. The number of CFDFCs grows with control-flow structure, and each adds its own continuous throughput variables and linearized retiming constraints to a single integer program.
- In practice a commercial MILP solver is required (OBSERVED: `GUROBI_LIBRARY-NOTFOUND` disables the algorithms locally).
- *Runtime* growth is **not** measured by us (UNVERIFIED).

**Cause (INFERRED from the formulation).**
- Throughput of a marked graph is a max-cycle-ratio property. Encoding it with continuous retiming variables *per cycle set*, coupled to integer buffer decisions, yields a MILP whose size is the sum over CFDFCs.
- The integrality comes from buffer slots, which interact with both the throughput and the timing constraints.

**Opportunity.** Exploit marked-graph structure (cycle-ratio duality, retiming as min-cost flow) to decouple or tighten the throughput part.

**Local test:** not possible. Recorded as a generation/review-only problem.

## P3 — Post-placement timing repair (gate sizing, buffering)

**Scientific objective.** Meet setup timing after placement with minimum added area/power.

**Current frontier.**
- OpenROAD `repair_timing` (OBSERVED locally): path-based greedy repair using sizing, buffering, pin swap, cloning and Vt swap, iterating over violating endpoints.
- Academic global methods: Lagrangian-relaxation discrete sizing (ISPD 2012/2013 sizing contests) and differentiable GPU sizing (W10 search results, UNVERIFIED details).

**Important limitation.**
- On large designs, greedy repair makes slow progress and stops far from closure (#10900, PAPER via issue text: 23,616 violating endpoints; 290 iterations / 14 min for −803 → −603 ps).
- On small designs it is fast: our aes goes from −29.38 to −5.53 ps in 4.7 s (OBSERVED, W10 C6).

**Cause (INFERRED).** Repair acts one endpoint and one path at a time with local moves. Shared logic couples paths, so fixing one path can degrade another. The stopping rules are heuristic.

**Opportunity.** Global allocation of sizing across shared paths is already the standard academic answer (LR/differentiable). The open question is whether anything *beyond* that exists for this setting.

**Local test:** partial.
