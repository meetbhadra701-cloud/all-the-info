# 04 — Hypothesis evolution (Wave 11)

**Rule applied (brief, Part VI).** For each strong objection, decide *what it invalidates*: the problem, the mechanism, the novelty, an experimental assumption, an implementation, or the expected improvement. Then:
- evolve only where a genuinely different technical approach exists;
- never rescue an idea by narrowing the benchmark, renaming it, or adding an LLM;
- record how each revised hypothesis relates to the original;
- keep unresolved problems unresolved.

## What each objection actually invalidated

| Hypothesis | Objection | Invalidates | Does not invalidate |
|---|---|---|---|
| H1.1 Lagrangian pricing | Pricing is published for mapping-delay and for sizing-area | novelty of the mechanism | the problem; the headroom question |
| H1.2 Trade-off curves | Chaudhary–Pedram 1992/95 | novelty of the representation | — |
| H1.3 Exact windows | satlut (LUT); `&nf -a` / preliminary standard-cell version; mfs3 (Boolean) | novelty of *window* re-covering | the idea of exact resolution under a *different decomposition* |
| H1.4 Slack budgeting | Unified budget-management theory (min-cost flow, integer budgets) | novelty of budgeting | the unmodelled part: rates under sharing |
| H1.5 Area-tolerant delay pass | emap alternatives; W10 D1 | novelty and expected gain | — |
| H2.1–H2.3 | TRETS'21 decomposition; R-HLS heuristics; slack-matching theory; HEART'25 phase-aware | novelty; local testability | the importance of the P2 problem |
| H3.1–H3.3 | LR sizing, TNS criticality, budgeting | novelty (an engineering integration remains) | the P3 limitation (#10900) |

## Evolution of P1: from *where* to re-solve to *which decisions* to re-solve

### The diagnosis we did not have when generating

The strongest prior art explains *why* area recovery loses area:

> "area-recovery heuristics … often make incorrect decisions when choosing one local mapping among many candidates, due to the lack of clear winner among them. These mistakes accumulate …"
> — Schmitt, Mishchenko, Brayton, ASP-DAC 2018 (text extracted locally; LUT mapping)

Two independent observations of ours point the same way:
- **W10 D2:** changing only *which near-equal match the delay pass keeps* (one tolerance rule) moved final area by 3.6% at iso-delay.
- **E0:** the looser-constraint area inversions for `map` and `&nf` are what you would expect if small tie-breaking differences cascade.

**Decisive remark.** satlut and H1.3 answer "*where* should exact search be applied?" with topology: a connected window. The diagnosis says the errors are located by *ambiguity*: nodes whose candidate matches are near-equal. Those nodes are not necessarily close to one another. A window around one ambiguous node can therefore miss the coupled ambiguous nodes elsewhere, for example those sharing the same fanout cone through multiple paths.

### H1.6 — Global exact resolution of near-tie decisions (evolved from H1.3 + H1.4, motivated by the satlut diagnosis)

- **PROBLEM:** P1 (unchanged).
- **STRONGEST EXISTING METHODS:** emap; `&nf -p`; satlut-style exact window re-covering (LUT; standard-cell variants experimental or unpublished).
- **EXACT LIMITATION:** Area-flow and exact-local-area recovery commit every near-tie decision locally and in traversal order. Exact post-processing, where it exists, only re-examines *topological windows*.
- **PROPOSED TECHNICAL INSIGHT:** Decompose the covering problem by **decision ambiguity** instead of topology.
  - Candidates that the heuristic's own cost model rates as clearly worse (by more than a factor ε at their node) are removed.
  - Every node keeps only its ε-near-ties, plus the heuristic's choice so that the incumbent stays feasible.
  - The resulting *whole-circuit* covering problem, with exact timing and exact sharing, is solved globally and exactly.
  - It is small because most nodes have a clear winner, and correct because it is still exact covering over a subset of the same candidates.
- **POSSIBLE MECHANISM:**
  1. Run emap (or `&nf`) to completion.
  2. Read its final area-flow ranking of every candidate.
  3. Build the ε-restricted exact model (choose one match per needed (node, phase); leaf-need implications; arrival constraints; phases and inverters; the delay bound D).
  4. Solve with SAT/SMT/MILP, warm-started from the heuristic cover.
  5. Validate the result independently.
- **WHY IT MIGHT WORK:** If the diagnosis is right, the optimum differs from the heuristic mainly at near-tie decisions. The restriction then keeps nearly all of the headroom while removing most of the search space.
- **WHAT WOULD BE NEW:** Two things:
  - an **ambiguity-based decomposition** of standard-cell covering, in contrast to satlut's topology-based windows;
  - evidence that standard-cell area-recovery headroom *concentrates* in ambiguous decisions.
  Both remain to be checked by prosecution (05).
- **WHAT WOULD BE REUSED FROM PRIOR ART:** Cut enumeration, matching and area flow (the mapper); SAT/SMT/ILP; the satlut-style exact covering encoding.
- **MAIN SCIENTIFIC RISK (three necessary assumptions):**
  - **A1 (headroom):** at fixed D, the exact optimum over the mapper's own cut-match space is materially smaller than the heuristic cover. If not, *no* covering-algorithm contribution exists in this space, and the problem is invalidated for this space.
  - **A2 (concentration):** most of that headroom is reachable by changing only ε-near-tie decisions, for small ε. If not, the ambiguity decomposition is invalidated, and topology windows (occupied) would be the route.
  - **A3 (reduction):** the ε-restricted problem is a small fraction of the full problem. If not, the decomposition brings no tractability.
- **CHEAPEST FALSIFYING EXPERIMENT:** Measure A1, then A2/A3, on small circuits where the *whole-circuit* exact optimum over mockturtle `map`'s own space is computable with the local Z3 optimizer. Compare at the same D:
  - heuristic;
  - exact optimum (full space);
  - exact optimum over the ε-restricted space for several ε.

  Every resulting netlist is independently validated.

**Relation to the originals.**
- H1.6 keeps H1.3's *exactness*.
- It keeps H1.4's *global* treatment of timing, which the exact model handles jointly rather than through a linearized budget.
- It replaces H1.3's topology windows with an ambiguity restriction taken from the strongest prior art's own diagnosis.
- It drops H1.1, H1.2 and H1.5 (occupied, nothing distinct left).

**Why this is not a cosmetic rescue.**
- The change is to the *decomposition principle* (which decisions are re-solved). That changes what the exact solver sees, and it can be falsified independently (A2/A3).
- It is not a benchmark narrowing or a rename, and it adds no LLM component.

### H1.7 — Diagnostic question retained as part of the evaluator, not as a contribution

The following question is **not** a contribution by itself:

> Where does standard-cell mapping headroom live?
> - slack allocation;
> - sharing or tie decisions;
> - the representation (cuts, structure).

It is kept because A1/A2 answer part of it. The *oracle-budget* test (feed the optimum's own arrival times to the heuristic as budgets) would separate slack allocation from tie decisions. It is scheduled only if A1 holds (`06_EXPERIMENTAL_EVALUATOR.md`).

## Evolution of P2 and P3: none justified

- **P2 (elastic buffering).**
  - The mechanisms are occupied by the TRETS'21 decomposition, R-HLS heuristics, slack-matching theory and HEART'25's phase-aware work.
  - No distinct mechanism emerged that could be tested with local tools (no Gurobi, no Dynamatic runtime).
  - **Preserved as UNRESOLVED (not locally testable).** Revisiting it would require a licensed MILP solver, the user's decision, or an open-solver port of the Dynamatic MILP. The port would be engineering.
- **P3 (timing repair).**
  - The limitation (#10900) is real.
  - The remaining work is integrating an established global method, which is **ENGINEERING**.
  - No distinct mechanism emerged.

## Result of evolution

**One evolved hypothesis (H1.6) survives to prior-art prosecution**, with three explicit necessary assumptions (A1–A3) and a local falsification path. P2 and P3 are preserved as unresolved or engineering, without artificial rescue.
