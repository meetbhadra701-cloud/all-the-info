# 02 — Hypothesis generation (Wave 11)

This is the generation stage only. Criticism is deliberately withheld until `03_ADVERSARIAL_REVIEW.md`, as the brief requires. The one exception is the template's "main scientific risk" and "cheapest falsifying experiment" fields.

- No hypothesis is given a marketing name. Identifiers such as H1.1 are labels only.
- No performance figures are claimed.

Contribution types:
- A = algorithmic improvement;
- B = representation;
- C = optimization mechanism;
- D = compositional methodology;
- E = architectural mechanism.

---

## P1 — Delay-constrained area recovery in cut-based standard-cell mapping

Common setting for all P1 hypotheses:
- a subject AIG;
- the mapper's own cut set (priority cuts, ≤ 5 leaves usable with the 47-gate ASAP7 genlib);
- Boolean matches in both output phases;
- a load-independent pin-delay model;
- delay bound D.

The strongest existing methods for every P1 hypothesis are mockturtle **emap** (area flow; exact area in *reverse* topological order; area-oriented match alternatives) and ABC **`&nf -p`** (area flow plus exact area with relaxation). mockturtle `map` is the simple baseline.

### H1.1 — Lagrangian pricing of arrival constraints inside covering (type C)

- **PROBLEM:** P1.
- **STRONGEST EXISTING METHODS:** emap; `&nf -p`.
- **EXACT LIMITATION:** Area recovery enforces hard per-node required times derived from the previous cover. Slack goes to whichever node the traversal reaches first.
- **PROPOSED TECHNICAL INSIGHT:** Give every timing arc a price (Lagrange multiplier) instead of a hard deadline. A node then chooses the match with the best *area + priced delay*. Slack flows to nodes where it buys the most area, whatever the visiting order.
- **POSSIBLE MECHANISM:**
  1. Initialize multipliers λ on node-output arrival constraints.
  2. For fixed λ, run one topological pass that picks, per node and phase, the match minimizing area flow + Σ_arcs λ·(pin delay contribution).
  3. Time the resulting cover.
  4. Update λ by subgradient: raise it on arcs of paths violating D, lower it where slack remains.
  5. Repeat, then legalize with a required-time-constrained pass.
- **WHY IT MIGHT WORK:** Pricing is the established way to trade a separable cost against a global timing constraint. It is what Lagrangian discrete gate sizing does.
- **WHAT WOULD BE NEW:** Pricing over *discrete covering with sharing and output phases*, where the subproblem is area flow rather than a convex sizing function.
- **WHAT WOULD BE REUSED FROM PRIOR ART:** Lagrangian/subgradient methods; cut enumeration; Boolean matching; area flow.
- **MAIN SCIENTIFIC RISK:** Covering with sharing is not convex, so the dual gap may be large. The subproblem is itself heuristic.
- **CHEAPEST FALSIFYING EXPERIMENT:** Measure how far existing heuristics are from the *exact* optimum within the same cut-match space at the same D. If they are already near-optimal, no pricing scheme can help.

### H1.2 — Per-node area-versus-required-time functions (type B)

- **PROBLEM:** P1.
- **STRONGEST EXISTING METHODS:** emap (single best plus one area-oriented alternative per phase); `&nf`.
- **EXACT LIMITATION:** Each node keeps one or two candidate matches, so information about intermediate area/delay trade-offs is discarded before slack is allocated.
- **PROPOSED TECHNICAL INSIGHT:** Represent each node by the *function* A_n(r): the minimum sharing-amortized area achievable if the node must be ready by r. Slack allocation between a node's fanins then becomes part of composing these functions, not a consequence of traversal order.
- **POSSIBLE MECHANISM:**
  1. Bottom-up, compute A_n(r) as a step function over the achievable arrivals:
     A_n(r) = min over matches m of [ area(m) + Σ_leaves A_l(r − d_m,l) / est_refs(l) ].
  2. Prune dominated breakpoints.
  3. Top-down, select matches from D at the outputs.
- **WHY IT MIGHT WORK:** On trees this composition is exact. Carrying the whole trade-off curve up to the outputs means no slack decision is made before it is known which downstream node needs the slack.
- **WHAT WOULD BE NEW:** A cut-based DAG version with phases and amortized sharing.
- **WHAT WOULD BE REUSED FROM PRIOR ART:** Area–delay curve composition for tree covering; area flow.
- **MAIN SCIENTIFIC RISK:** Breakpoint growth, and error from the sharing approximation. The representation may already exist.
- **CHEAPEST FALSIFYING EXPERIMENT:** The same headroom measurement as H1.1. The optimum also shows whether the gap is about slack allocation, which this hypothesis targets.

### H1.3 — Exact delay-constrained re-covering of bounded windows (type D)

- **PROBLEM:** P1.
- **STRONGEST EXISTING METHODS:** emap / `&nf` area recovery (local, approximate); Boolean resubstitution on mapped networks (changes logic rather than cover).
- **EXACT LIMITATION:** Both approximations (order-dependent slack use; estimated sharing) act together. Local re-selection cannot make coordinated changes to several nodes at once.
- **PROPOSED TECHNICAL INSIGHT:** Restrict the covering problem to a window of the current cover and fix the window's boundary arrival and required times. It is then small enough to solve *exactly* over the mapper's own cut-match space. Inside the window, slack allocation and sharing are resolved jointly, and repeated window moves never break global timing.
- **POSSIBLE MECHANISM:**
  1. Map with emap.
  2. Time the cover.
  3. Choose a window: a cluster of nodes in one another's fanin cones, bounded in size.
  4. Encode choose-one-match-per-needed-(node, phase), leaf-need implications, timing implications and boundary times as an SMT/ILP optimization.
  5. Accept the window solution if its area decreases.
  6. Iterate as a large-neighbourhood search.
- **WHY IT MIGHT WORK:** Exactness inside the window removes both approximations, while the bounded size keeps the solver tractable. Large-neighbourhood search is effective in other combinatorial layout problems.
- **WHAT WOULD BE NEW:** Exact, timing-bounded re-covering over the mapper's *own* match space for standard cells, as a refinement layer on top of a heuristic mapper.
- **WHAT WOULD BE REUSED FROM PRIOR ART:** SAT/SMT/ILP solvers; large-neighbourhood search; cut enumeration and matching.
- **MAIN SCIENTIFIC RISK:** Little headroom. Improvements may need slack moved *across* window boundaries. Solver runtime.
- **CHEAPEST FALSIFYING EXPERIMENT:** Whole-circuit exact optimum on small circuits. If there is no headroom there, windows cannot find any.

### H1.4 — Global slack budgeting from the mapper's own trade-off data (type C)

- **PROBLEM:** P1.
- **STRONGEST EXISTING METHODS:** emap / `&nf` with required times propagated from the current cover.
- **EXACT LIMITATION:** The required times used during recovery are not the result of any allocation objective. They are whatever the previous cover implied.
- **PROPOSED TECHNICAL INSIGHT:** Decide *where* slack should go before recovery. Solve a budgeting problem that maximizes estimated area saved per unit of slack, subject to every path meeting D. Then recover area against those budgets.
- **POSSIBLE MECHANISM:**
  1. Per node, take the lower convex hull of its (arrival, area-flow) match points to get a marginal area-per-picosecond rate.
  2. Solve a delay-budgeting LP with difference constraints along the timing graph, whose dual is a min-cost flow.
  3. Set per-node required times from the budgets.
  4. Run the existing exact-area recovery.
- **WHY IT MIGHT WORK:** Budgets decouple the global allocation from the local choice. The local choice (exact-area recovery) is already good.
- **WHAT WOULD BE NEW:** Budgeting driven by the mapper's match trade-off hulls, inside technology mapping.
- **WHAT WOULD BE REUSED FROM PRIOR ART:** Delay/slack budgeting (zero-slack algorithm, min-cost-flow budgeting); exact-area recovery.
- **MAIN SCIENTIFIC RISK:** Rates change once neighbours change (sharing), so a one-shot linearized budget may misguide recovery.
- **CHEAPEST FALSIFYING EXPERIMENT:** First, the headroom measurement. Then an *oracle-budget* test: give the heuristic the optimal solution's own arrival times as budgets. If it still cannot approach the optimum, budgeting cannot close the gap.

### H1.5 — Area-tolerant delay pass (starting-cover shaping) (type A; seeded by Wave 10 D2)

- **PROBLEM:** P1.
- **STRONGEST EXISTING METHODS:** emap's area-oriented match alternatives.
- **EXACT LIMITATION:** A strictly delay-optimal starting cover pins area recovery to a costly neighbourhood. W10 D2 showed one tolerance rule in the delay pass is necessary and sufficient for a 3.6% iso-delay area gain in `map`.
- **PROPOSED TECHNICAL INSIGHT:** Shape the starting cover. In the delay pass, prefer a cheaper match whose arrival is within a tolerance of the fastest.
- **POSSIBLE MECHANISM:** Tolerance-gated comparison in the delay pass, with the tolerance chosen adaptively per node from its slack.
- **WHY IT MIGHT WORK:** The observed path dependence of recovery.
- **WHAT WOULD BE NEW:** An adaptive-tolerance form.
- **WHAT WOULD BE REUSED FROM PRIOR ART:** The evolved rule; emap alternatives.
- **MAIN SCIENTIFIC RISK:** It may be what emap alternatives already do.
- **CHEAPEST FALSIFYING EXPERIMENT:** Transplant into emap and compare at iso-delay.

---

## P2 — Throughput-constrained buffering of dynamically scheduled (elastic) circuits

The strongest existing method for every P2 hypothesis is the Dynamatic MILP (fpga20/fpl22): Gurobi, per-CFDFC throughput with fluid retiming, and timing paths through potential buffers.

### H2.1 — Critical-cycle-driven buffer insertion (type A)

- **EXACT LIMITATION:** A single MILP that grows with the number of CFDFCs.
- **PROPOSED TECHNICAL INSIGHT:** Each CFDFC's throughput is set by its maximum cycle ratio. Repeatedly locate the critical cycle and add the one buffer slot that raises it most.
- **POSSIBLE MECHANISM:** Howard policy iteration per CFDFC union, greedy slot insertion, then a separate timing pass.
- **WHY IT MIGHT WORK:** Each iteration is polynomial.
- **WHAT WOULD BE NEW:** An open-solver-free buffer placer for Dynamatic's elastic model.
- **WHAT WOULD BE REUSED FROM PRIOR ART:** Cycle-ratio algorithms; relay-station / queue-sizing ideas from latency-insensitive design.
- **MAIN SCIENTIFIC RISK:** Greedy area suboptimality; occupancy.
- **CHEAPEST FALSIFYING EXPERIMENT:** Buffer count vs the MILP optimum on Dynamatic kernels. This needs Gurobi and is **not locally available**.

### H2.2 — Fixed-throughput buffering as a network-flow problem (type B)

- **EXACT LIMITATION:** Throughput and integrality are coupled in one MILP.
- **PROPOSED TECHNICAL INSIGHT:** For a *fixed* target throughput θ, "enough slots on every cycle" may reduce to difference constraints over the union graph, as retiming legality does. If the constraint matrix is totally unimodular, the minimum-slot problem is a min-cost flow; θ can then be searched.
- **POSSIBLE MECHANISM:** A retiming-style formulation with slot variables per channel, a min-cost-flow solve per θ, and bisection on θ.
- **WHY IT MIGHT WORK:** Minimum-register retiming under a period constraint is already a min-cost-flow dual (Leiserson–Saxe).
- **WHAT WOULD BE NEW:** An exact polynomial special case of elastic buffering.
- **WHAT WOULD BE REUSED FROM PRIOR ART:** Retiming theory; cycle-ratio duality.
- **MAIN SCIENTIFIC RISK:** Opaque/transparent buffer types, token/bubble counts and timing constraints may break unimodularity. General slack matching may be NP-hard.
- **CHEAPEST FALSIFYING EXPERIMENT:** A theoretical check: construct a small elastic instance whose constraint matrix is not totally unimodular, or find a hardness result.

### H2.3 — Capacity sharing across mutually exclusive control paths (type E)

- **EXACT LIMITATION:** Static per-channel slots must cover the union of the needs of all CFDFCs, including CFDFCs that never execute at the same time.
- **PROPOSED TECHNICAL INSIGHT:** Channels whose throughput-critical cycles lie on mutually exclusive control paths could draw on a shared slot pool.
- **POSSIBLE MECHANISM:** A slot-pool elastic buffer, selected by the same control that selects the CFDFC.
- **WHY IT MIGHT WORK:** Mutually exclusive CFDFCs never need their buffer capacity simultaneously.
- **WHAT WOULD BE NEW:** Run-time buffer-capacity sharing in dynamically scheduled HLS.
- **WHAT WOULD BE REUSED FROM PRIOR ART:** Elastic protocols; NoC buffer sharing.
- **MAIN SCIENTIFIC RISK:** Protocol correctness and control overhead may exceed the savings.
- **CHEAPEST FALSIFYING EXPERIMENT:** On real kernels, measure the share of buffer area on channels whose need comes only from mutually exclusive CFDFCs. This needs a Dynamatic flow and is **not locally available**.

---

## P3 — Post-placement timing repair

The strongest existing methods for every P3 hypothesis are OpenROAD `repair_timing`, Lagrangian-relaxation discrete sizing and differentiable sizing.

### H3.1 — Global Lagrangian sizing pre-pass before path-based repair (type C)

- **PROPOSED TECHNICAL INSIGHT:** Globally price all timing arcs, size gates to the dual optimum, then let path-based repair fix the residue.
- **WHAT WOULD BE REUSED FROM PRIOR ART:** Lagrangian-relaxation sizing (ISPD contests).
- **MAIN SCIENTIFIC RISK:** It is an integration of an established method.
- **CHEAPEST FALSIFYING EXPERIMENT:** Compare WNS/TNS/area at an equal runtime budget on large ORFS designs.

### H3.2 — Shared-criticality ordering of repair (type A)

- **PROPOSED TECHNICAL INSIGHT:** Repair gates in order of total negative slack over *all* endpoints they affect, not endpoint by endpoint.
- **MAIN SCIENTIFIC RISK:** TNS-weighted criticality is standard.
- **CHEAPEST FALSIFYING EXPERIMENT:** Instrument `repair_timing`'s move sequence and see whether its moves undo each other.

### H3.3 — Budget-first repair (type D)

- **PROPOSED TECHNICAL INSIGHT:** Allocate slack budgets globally by min-cost flow, then repair each region to its budget independently.
- **MAIN SCIENTIFIC RISK:** Budgeting is classic in physical synthesis.
- **CHEAPEST FALSIFYING EXPERIMENT:** Budget feasibility on the #10900-type design class. Large designs are required.
