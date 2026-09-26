# 03 — Adversarial review (Wave 11)

This review was performed *after* `02_HYPOTHESIS_GENERATION.md` was written and was not edited back into it. Each hypothesis is judged on the brief's eight questions:

1. The problem is real.
2. The mechanism is coherent.
3. No existing method already does it.
4. It is not parameter tuning.
5. It is not a routine application of a known principle.
6. A new algorithmic or architectural idea exists.
7. It could make a meaningful difference.
8. A falsification path exists.

Each hypothesis then receives the strongest reviewer objection, grounded in identifiable prior art, and one of the brief's five classes:
- OCCUPIED;
- ENGINEERING;
- INVESTIGATE FURTHER;
- FALSIFY BEFORE DEVELOPMENT (an unsupported assumption).

**Citations.** Every source below was retrieved or seen in this wave. Details beyond the retrieved text are marked **UNVERIFIED**. The satlut paper's text was extracted locally from its PDF (`sources/SOURCES.md`).

---

## P1 — Delay-constrained area recovery in cut-based standard-cell mapping

### Evidence that the problem is real (applies to all P1 hypotheses)

The problem is real, but its size is unknown.
- **OBSERVED:** heuristic mappers differ by several percent at matched delay (W10 D1). Recovered area depends on the starting cover (W10 D2).
- **PAPER (the strongest independent evidence):** Schmitt, Mishchenko and Brayton, *SAT-Based Area Recovery in Structural Technology Mapping* (ASP-DAC 2018). They start from 6-LUT mappings by a high-effort area-oriented flow. SAT over small windows still found **3–4% more area on average, >10% on some circuits**. They diagnose the cause: area-recovery heuristics "often make incorrect decisions when choosing one local mapping among many candidates, due to the lack of clear winner", and "these mistakes accumulate".
- **Caveat:** that evidence is for **LUT** mapping (unit area, depth delay). For standard cells (per-cell area, pin delays, two output phases, inverters) the headroom has not been measured by us or located in literature.
- **Classification of the common assumption:** "heuristic SC area recovery leaves material area at fixed delay" → **FALSIFY BEFORE DEVELOPMENT**.

### H1.1 — Lagrangian pricing of arrival constraints

**The eight questions.**
1. **Problem real?** Yes (above).
2. **Coherent?** Yes.
3. **Already implemented?** Pricing criticality with Lagrangian relaxation inside DAG technology mapping is published *for delay*: Liu, Shelar and Hu, *Delay-optimal simultaneous technology mapping and placement* (ICCAD 2008) and *Simultaneous Technology Mapping and Placement for Delay Minimization* (TCAD 2011). They "employ Lagrangian relaxation … to assess timing criticality of paths beyond a tree" (search abstract; author list UNVERIFIED). Lagrangian relaxation for area subject to delay is textbook in gate sizing (search results: *Gate sizing by Lagrangian relaxation revisited*; *Fast and efficient LR-based discrete gate sizing*; titles only).
4. **Parameter tuning?** No.
5. **Known principle applied routinely?** Largely yes. It is the sizing formulation transplanted onto covering.
6. **Substantive new idea?** Only if pricing *with sharing* needs a new subproblem solver. The generated hypothesis does not supply one; it uses area flow.
7. **Meaningful difference?** Unknown; it depends on the headroom.
8. **Falsification path?** Yes (headroom).

**Strongest objection.** "Lagrangian pricing of timing in mapping (Liu/Shelar/Hu) and of area-under-delay in sizing are both published. Pricing area flow is their composition, and the covering subproblem with sharing is still solved by the same area-flow heuristic that causes the problem."

**Class: OCCUPIED principle / ENGINEERING composition.** Revisit only if headroom is shown *and* traced to slack allocation.

### H1.2 — Per-node area-versus-required-time functions

- **Already implemented?** Yes. Chaudhary and Pedram, *Computing the Area versus Delay Trade-off Curves in Technology Mapping* (DAC 1992; IEEE TCAD 1995) "computed delay functions (which capture gate area-arrival time tradeoffs) at all nodes", then selected solutions from the curves in reverse topological order. The method is polynomial on node-balanced trees and "easily extended to mapping a DAG" (search summary of the paper).
- **Only residual:** reviving curve composition inside modern *cut-based* mappers. That is re-implementation.
- **Strongest objection.** "The representation is 30 years old. Modern mappers dropped it for runtime and sharing reasons, and re-adding it is engineering unless you show a new composition rule for sharing."
- **Class: OCCUPIED.**

### H1.3 — Exact delay-constrained re-covering of bounded windows

**Already implemented?** Yes, at the level of principle.
- For **LUT** mapping: *SAT-Based Area Recovery in Structural Technology Mapping* (Schmitt/Mishchenko/Brayton, ASP-DAC'18; IWLS'17 version) — windows, CNF over all structural K-LUT covers, delay via an interfaced timer. It is ABC `&satlut`.
- For **standard cells:**
  - the same paper's future-work list says "Extending SAT-based mapping to work for standard cells. A preliminary implementation confirmed that the approach is practical and leads to area savings";
  - ABC `&nf -a` is documented as "SAT-based area-oriented mapping (experimental)" (OBSERVED in the yosys-abc help text);
  - SAT-based *Boolean* remapping of standard-cell windows is `mfs3` (Mishchenko, Brayton, Besson, Govindarajan, Arts, van Besouw, *Versatile SAT-based remapping for standard cells*, IWLS'16; area-oriented with delay preserved, per the talk slides);
  - post-mapping resubstitution for standard cells: *Post-mapping resubstitution for area-oriented optimization* (IWLS'24) and *Area-Oriented Optimization After Standard-Cell Mapping* (ASP-DAC'25).

**Strongest objection.** "Structural SAT window re-covering is `&satlut`. Its standard-cell extension exists at least as a preliminary implementation inside ABC. Adding output phases and pin delays is engineering."

**Class: OCCUPIED principle.** Standard-cell exact structural re-covering with phases and pin-delay timing may exist only in unpublished or experimental form (`&nf -a`), so that detail is UNVERIFIED. Even so, it is *same problem, same method*.

### H1.4 — Global slack budgeting from match trade-off data

- **Already implemented?** Yes. Ghiasi, Bozorgzadeh et al., *A Unified Theory of Timing Budget Management* (ICCAD 2004; IEEE TCAD). It unifies delay-budgeting problems as min-cost flow, including **integer budgeting motivated by "discreteness of libraries of components during library mapping"**, which it shows is solvable optimally in polynomial time (search summary). Budget management for mapping to smaller/slower cells is also a long-standing theme (*Delay budgeting for a timing-closure-driven design method*, ICCAD 2000, title only).
- **Strongest objection.** "Budgeting on a DAG is solved. The only open part — where the per-node area/delay rates come from when sharing couples nodes — is precisely what makes the budget wrong, and the hypothesis does not address it."
- **Class: OCCUPIED principle.** The unresolved part (rates under sharing) belongs to the headroom question.

### H1.5 — Area-tolerant delay pass

- **Already implemented?** Yes. emap keeps area-oriented *match alternatives* during the delay pass and selects them when their flow plus an inverter beats the other phase (OBSERVED, `emap.hpp` `select_alternatives`). W10 showed emap beats the evolved rule at iso-delay (GPT-5/emap@D_e = 1.024 on EPFL-20).
- **Strongest objection.** "This is emap's alternatives mechanism, and emap already wins."
- **Class: OCCUPIED.**

### Summary for P1

Every generated *mechanism* is occupied at the level of principle. None of the objections invalidates the *problem*. The strongest prior art (satlut) actually *supports* the problem's existence for LUTs, and gives a specific causal diagnosis: near-tie ("no clear winner") decisions that accumulate. What remains unsupported is the standard-cell headroom itself. See `04_HYPOTHESIS_EVOLUTION.md` for what the objections do and do not invalidate.

---

## P2 — Throughput-constrained buffering of elastic HLS circuits

### H2.1 — Critical-cycle-driven buffer insertion

- **Already implemented?** In substance, yes:
  - Dynamatic's own journal version (Josipović et al., *Buffer Placement and Sizing for High-Performance Dataflow Circuits*, ACM TRETS 2021) decouples the MILP over **disjoint CFDFC sets** with the same throughput. It also offers "optimize only the most relevant loops" modes (search summary);
  - R-HLS "employ[s] heuristics for buffer placement, reaching state-of-the-art performance" (search summary; arXiv 2408.08712);
  - latency-insensitive queue sizing is an older line (UNVERIFIED specifics).
- **Strongest objection.** "Greedy critical-cycle buffering is how pre-MILP tools worked. Dynamatic's scalability issue already has a published decomposition, and a heuristic tool matches its throughput."
- **Class: OCCUPIED.**

### H2.2 — Fixed-throughput buffering as a network-flow problem

- **Already implemented?** Yes, at the level of theory:
  - Beerel et al., *Slack Matching Asynchronous Designs* (ASYNC 2006), and *Performance Estimation and Slack Matching for Pipelined …* (ICCAD 2008) formulate buffer insertion for throughput on marked graphs as a MILP, prove NP-completeness, and state "under what circumstances the MILP solution admits a polynomial time solution", with an LP-based approximation otherwise (search summary).
- **Strongest objection.** "The polynomial special cases and the hardness boundary are already mapped. A total-unimodularity claim for elastic buffers must beat a known NP-completeness result, and the brief forbids assuming it."
- **Class: OCCUPIED**, or at best a narrow theory question. It cannot be tested locally.

### H2.3 — Capacity sharing across mutually exclusive control paths

- **Already implemented?** Partly:
  - *Resource and Phase Awareness for Dynamically Scheduled HLS* (HEART 2025) performs "phase-aware optimization that considers phase information … and optimizes buffer placement for each phase such that runtime reconfiguration can achieve improved performance", reporting up to 40% fewer buffers (W10 search summary, UNVERIFIED details).
- **Strongest objection.** "Run-time phase-based buffer adaptation exists. Slot-pool sharing adds protocol risk, with no local way to measure the savings."
- **Class: OCCUPIED**, and **not testable locally** (no Gurobi, no Dynamatic runtime flow).

---

## P3 — Post-placement timing repair

| Hypothesis | Strongest prior art | Class |
|---|---|---|
| H3.1 Lagrangian sizing pre-pass | LR discrete sizing is the standard academic method (search titles: *Gate sizing by Lagrangian relaxation revisited*; *Fast and efficient LR-based discrete gate sizing*; *Fast LR-based multithreaded gate sizing*). ISPD 2012/2013 sizing contests (UNVERIFIED details). | **OCCUPIED principle; ENGINEERING** if integrated into OpenROAD. |
| H3.2 Shared-criticality ordering | TNS-weighted criticality is standard in sizing/repair (UNVERIFIED specific citation). OpenROAD has `TNS_END_PERCENT` (OBSERVED in ORFS aes config). | **OCCUPIED / parameter-level.** |
| H3.3 Budget-first repair | The unified budgeting theory (Ghiasi, Bozorgzadeh et al.), as for H1.4. | **OCCUPIED principle.** |

The P3 limitation (grinding on large designs) is real (#10900). It is a problem of *engineering an established method into OpenROAD*, which the brief says is not a contribution.

---

## Overall result of the review

| Hypothesis | Class | What the objection targets |
|---|---|---|
| H1.1 | OCCUPIED / ENGINEERING | mechanism novelty |
| H1.2 | OCCUPIED | mechanism novelty |
| H1.3 | OCCUPIED (principle) | mechanism novelty |
| H1.4 | OCCUPIED (principle) | mechanism novelty |
| H1.5 | OCCUPIED | mechanism novelty |
| P1 common assumption (standard-cell headroom) | FALSIFY BEFORE DEVELOPMENT | experimental assumption |
| H2.1–H2.3 | OCCUPIED; not locally testable | mechanism novelty / testability |
| H3.1–H3.3 | OCCUPIED / ENGINEERING | mechanism novelty |

The review killed mechanisms, not the P1 problem. It also delivered a *causal diagnosis from the strongest prior art* (accumulated near-tie decisions) that none of the five P1 mechanisms targets directly. `04_HYPOTHESIS_EVOLUTION.md` follows that lead.
