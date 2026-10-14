# DISCOVERY_METHODOLOGY_V2
**Version:** 2.0 | **Date:** 13 October 2026 | **Status:** process recommendation; not authorization to build any project

## The changed unit of discovery
**Old unit:** a clever candidate implementation and a plausible unmet need. **New unit:** an externally documented, precisely stated *failure of existing methods* under an independently checkable contract. An idea is permitted only after its problem is admitted.

A problem dossier is not an invention pitch. It contains: affected community, real workflow, witnessed failure, formal or quantitative operational contract, strongest existing solution (including its modern implementations), missing theoretical/empirical evidence, and a low-cost way to show the opportunity does *not* exist. Only then ask whether any new method might close the residual.

## Required workflow: eleven gates

### G0 — Blind problem collection (do not generate solutions)
Start with recent **limitations**, negative results, reproducibility reports, public issue histories, industrial benchmark descriptions, unsolved problem lists and field-user complaints. For each field, gather at least one older foundational method, one modern contender and one domain practitioner's demonstration. Prefer artifacts with open workloads. Log named stakeholders and *what success would change for them*.

**Exit evidence:** several unaltered quotations/paraphrases with primary URLs and differing viewpoints; source dates, hardware context and versions. **Kill:** only a speculative pain point or invented customer.

### G1 — Formalize the task without proposing hardware
State input family, outputs, allowed approximation/error and numerical semantics, adversarial cases, correctness oracle, resource model (work, memory, communication, latency, energy), and whether future information is allowed. If important parameters are bounded constants, clarify that before complexity claims. Record exact unit of claimed scalability.

**Exit:** an expert can tell whether two algorithms solve the *same* problem. **Kill:** contract only says “faster, smarter, verifiable, or novel.”

### G2 — Construct the strongest incumbent and null alternatives
Create a baseline register before designing a new mechanism:
- no change / incumbent production flow;
- least complicated single-policy software replacement;
- strongest applicable peer-reviewed/open-source algorithm;
- optimized compiler, GPU/CPU or FPGA implementation as applicable;
- change in representation, data layout, batching, approximate quality, memory tier or specification that might erase the pain;
- known proof/verification oracle when a guarantee is asserted.

For each baseline, state supported modes and assumptions, not just benchmark numbers. A competitor that supports a narrower contract gets **N/A** outside that domain; timeouts are **UNKNOWN**, never failures. Compare against **the best feasible alternative at the same accuracy, delay, memory, security parameters and output guarantee**.

**Exit:** second reviewer signs off that no obvious cheap comparator is missing. **Kill:** improvement is only relative to an obsolete or deliberately untuned tool.

### G3 — Mathematical equivalence and older-overlooked research
Translate ideas into field-independent terms: graph search, matching, network flow, dynamic programming, fixed point, abstract interpretation, algebraic proof, translation validation, optimization under constraints, control with switching costs, index maintenance, queueing, event-triggered sampling, communication avoidance, online/competitive analysis.

Search both **1950–2000 foundational theory** and **2000–2018 overlooked application variants** before adding a “2026” filter. Search the identical mechanism under synonyms (see query crosswalk). Reduce to small cases and adversarial degenerate instances. Cite the strongest *method*, not only similar paper titles.

**Exit:** mechanism-to-known-equivalent table and a concrete technical distinction. **Kill:** method is a standard reduction with new terminology or tool placement.

### G4 — Don Swanson-style literature-based discovery
This is a **hypothesis generator, not a novelty detector**. Swanson connected separately documented A→B and B→C relationships without claiming this guarantees a clinically useful A→C outcome; see [Swanson 1986](https://pubmed.ncbi.nlm.nih.gov/3797213/) and [review](https://pmc.ncbi.nlm.nih.gov/articles/PMC5771422/).

1. Choose **A = independently documented problem**, e.g. unpredictable change in mesh topology creates synchronization/communication costs.
2. Identify **B = causal intermediate**, e.g. decisions incur reconfiguration cost and stale-state risk. Each A→B link needs a specific paper/experiment.
3. Find separate **C = mechanism/limit from another field**, e.g. online control with switching costs, amortized data-structure repair, conservative bounds on error propagation; document its theorems and preconditions.
4. Write an **A→B→C bridge** with exact corresponding state variables, objective, decision timing and failure mode. If conditions differ (nonstationarity, nonlinearity, adversarial inputs), state the missing bridge as a hypothesis.
5. Search directly for A↔C combinations and synonyms, backward/forward citations, code and patents. **No bibliographic edge is not evidence no technical edge exists.**
6. Test an obvious direct application of C *before* claiming a new C-like algorithm.

A bridge is promising only when it predicts a **new measurable consequence**: tighter rigorously valid bound, new possible input class, resource lower bound, avoided dependency, or well-supported win over the incumbent. Mere A+C juxtaposition is **engineering integration**.

### G5 — Scientific hypothesis and the opposing/null hypothesis
Write a causal claim with a falsifier, not a feature list. Example *abstract template*: “Under input class X and guarantee Y, established method Z incurs unavoidable cost W due to mechanism M; alternative principle P would remove that cost without losing Y.” The null: “Z or a small adjustment already matches P” (or the alleged cost was a benchmark artifact).

Require one of: (a) novel formal guarantee and independent proof, (b) algorithm with a significant capability/complexity change, (c) reproducible previously inaccessible operating regime, (d) fundamental measured limit/negative result that challenges published assumptions. **A tool patch is not automatically (a)–(d).**

### G6 — Soundness and external oracle
The claimed checker and golden standard may not come from the same untrusted generation path. For hardware: original design semantics, actual generated netlist, all live output cones, signedness, time semantics, optimized representations, and final I/O must be independently bound. A hash protects identity, not semantic equivalence. For numerical science: conservation laws, error measures and convergence references must be external to the optimized approximation. For learning: separate training data from evaluation and report uncertainty.

**Exit:** trusted computing base, counterexample classes, fail-closed outcome set and a mutation designed to exploit the proof boundary. **Kill:** a self-consistent certificate could pass on an incorrect emitted artifact (the PCAS problem).

### G7 — Falsification before implementation
Order by **negative information gained per unit effort**:
1. Desk-only mathematical counterexample and strongest competing algorithm.
2. Tiny instance where the alleged barrier/guarantee is directly testable.
3. Existing framework's built-in implementation or read-only structural oracle.
4. Only then a prototype restricted to the novel mechanism.

Preregister exact instances, one held-out family, failure criterion, independent expected result, resource budget and how timeouts/missing data are reported. A solver returning FEASIBLE does *not* prove optimality; finite mutation kills do *not* prove soundness.

### G8 — Software-to-silicon necessity analysis
Mandatory counterfactual ladder: mathematical reformulation → data representation/index → best optimized CPU → GPU → existing FPGA → hardware/software co-design → new ASIC. For each, compute/measure bottleneck type, arithmetic intensity, end-to-end transfers and data reuse, memory capacity, reconfiguration, precision/accuracy, economics, energy, and required fabrication/PPA validity. A simulator-only speedup is insufficient.

Only cross the silicon threshold if a **hardware-dependent capability or scientifically meaningful performance envelope** remains after strong software optimization. The result can appropriately be **SOFTWARE ONLY**, **FPGA MAYBE**, **EDA ONLY** or **NO HARDWARE CASE**. Never set a chip budget to zero for an architecture whose FPGA/toolchain and real-world oracle cannot be accessed.

### G9 — Independent adversarial prosecution
Assign four explicit roles: domain specialist (importance), algorithmic reviewer (prior reductions), experimentalist (measurement/correctness), hardware architect (resource realism). Have adversaries write *the cheapest thing that would make this uninteresting*. Evidence grades are attached per claim: external primary, archival observation, reproduced now, inference, unknown.

Search papers, code *and* patents with full synonyms and earlier dates; separately disclose proprietary/inaccessible coverage. No numeric “novelty probability.” Log newly found competitors even after an apparent winner; a new source can kill the hypothesis retroactively.

### G10 — Decision and postmortem
Decisions are `PROBLEM_NOT_DEMONSTRATED`, `OCCUPIED`, `MATHEMATICALLY_INVALID`, `BASELINE_DEFEATED`, `ORACLE_MISSING`, `HARDWARE_UNJUSTIFIED`, `RESEARCH_M0_ONLY`, `ENGINEERING_USEFUL` or `READY_FOR_PROTOTYPE_REVIEW`. The last label is never assigned from a desk literature search alone. For every kill, record whether the *problem, proposed mechanism, expected advantage or hardware premise* was invalidated. Store source links and a short counterexample in a searchable kill register; do not bury negative evidence inside pitch decks.

## Explicit equivalence-search crosswalk
| Our tempting phrase | Necessary alternative vocabularies |
|---|---|
| “proof-carrying synthesis” | certified compilation; translation validation; independent checkable proof logs; polynomial calculus; proof replay; arithmetic circuit checking |
| “early causal trace” | checkpointing; dynamic slicing; bounded observability; post-silicon trace compression; finite-state diagnosis |
| “global ambiguity selection” | constrained DAG cover; priority cuts; SAT exact area recovery; cut pruning; candidate selection; Lagrangian relaxation |
| “adaptive hardware scheduling” | online scheduling with switching costs; work stealing; latency hiding; graph partition refinement; load imbalance |
| “secure adaptive inference” | anytime algorithms; selective prediction; early exit; conformal risk; interval bound propagation; dynamic voltage/precision scaling |
| “dynamic graph accelerator” | fully-dynamic algorithms; streaming graph processing; update propagation; differential computation; cache maintenance |
| “new memory controller” | OS page placement; NUMA balancing; CXL tiering; wear leveling; locality-aware graph partitioning |

## Scientific value dimensions must not be collapsed
| Dimension | Minimum evidence | Why it does not imply the next |
|---|---|---|
| Engineering usefulness | Users, reproducible reliability/throughput/workflow improvement | Existing algorithm can deliver benefit |
| Scientific novelty | Explicit distinction from nearest equivalent primary method; new theorem/capability/causal result | Novelty may not matter or generalize |
| Architectural value | Fair co-design/energy/area/speed data and a hardware-specific bottleneck | A useful algorithm may still be better in software |
| Patent potential | Patent specialist's separate claim/priority/enablement search *if later authorized* | Academic novelty ≠ patentability/freedom to operate |
| EB‑1A relevance | Sustained independently recognized contributions; external impact and field response | A paper/patent count alone doesn't establish field significance |

**Do not optimize a weighted sum of these five.** Store five independent verdicts with evidence. An industry-useful PR can be a success even when a paper is a NO-GO; external adoption can matter even if no ASIC exists.

## Resource discipline and stop rules
- **Desk M0:** reading, mathematical analyses and baseline contracts only. This reset authorizes no new experiments.
- **Feasibility gate:** the *first* future experiment, if a new M0 approves it, must kill the central assumption cheaply. No full toolchain, design space search or RTL until a problem passes.
- **Abort immediately** for a discovered mathematically equivalent method, unsupported semantic contract, self-oracle, a superior simple baseline, absence of user need, or hardware-losing counterfactual.
- **Freeze truth conditions before runs**; record versions/SHA, platform, legal licenses, raw artifacts, negative controls, output checks, full elapsed/cost/energy accounting and any missing telemetry. If there is no independent oracle, do not benchmark under a correctness claim.
- **Record negative results as output**, not as intermediate disappointment; periodically audit all archived claimed winners for stale statuses.

## Why V2 should outperform V1 — narrowly stated
V2 should reduce **false positive research starts** because its earliest gates specifically target the common observed failure causes (old equivalent algorithm, absent headroom, specification/measurement defect, cheap comparator, silicon premise). The ordering minimizes sunk-cost bias. Swanson-style bridges make the search less limited by EDA vocabulary while the mathematical translation prevents superficial interdisciplinarity from appearing novel. Independent reviewers and outcome labels preserve evidence quality. These are methodological predictions; we have **not** run a controlled study showing better discovery yield, faster time to publishable idea, or guaranteed novelty. Test V2 prospectively by tracking screened-problem survival, number of prior-art collisions discovered *before coding*, cost per decisive kill, and externally confirmed utility, while disclosing any selection effects.
