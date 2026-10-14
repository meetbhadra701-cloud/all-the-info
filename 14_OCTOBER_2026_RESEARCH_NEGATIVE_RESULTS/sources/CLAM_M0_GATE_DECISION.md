# CLAM M0 gate decision

Date: 2026-10-13.

**Decision: GO for a narrowly scoped, small execution-driven M1 falsification experiment on the corrected mechanism. NO-GO for the original CLAM specification and its architectural performance claims. No simulator, RTL or physical-design work begins in this deliverable.**

The mathematical gate passes for certified guarded facts, entailed-slice reads, finite bitsets, signed intervals, conjunction, conflict generation, single-pivot lifting and bounded admission by eviction. The scientific gate passes only at the level of a plausible, falsifiable architecture hypothesis. It does not pass as established novelty, hardware necessity or publication readiness. If the research policy requires proven architectural novelty before any pilot, the correct disposition at that stronger gate is HOLD, not a claim that the literature is cleared.

## What survives and why it is useful enough to test

The surviving mechanism accepts certified conditional domain bounds at a variable's memory-bank interface, filters guard-sensitive redundancy, derives local joint bounds/conflicts, and optionally lifts a complementary pair. A fixed resident budget limits access work; safe eviction limits precision rather than creating false exclusions. Software keeps authoritative constraints and a complete fallback. This preserves the original location and guarded operation proposal while changing its incorrect semantics and removing unsupported protocol claims.

A concrete usefulness witness exists: `a=>X in {0,1}` and `NOT a=>X in {0,1}` lift to `TRUE=>X in {0,1}`. A later `b=>X in {0,1,2}` is redundant, and all queries can safely use the stronger basal fact. Likewise, `(a,{0})` and `(b,{1})` yield the valid nogood `a AND b`. These are ordinary reasoning rules, but their availability at an update port could save state movement and subscriber work. They establish functional usefulness, not workload prevalence or speedup.

The hard remaining hypothesis is that a small per-variable overlapping fact cache and its event interface offer a worthwhile architectural placement advantage after comparison with software using the same semantics. Historical parallel ATMS already implements hardware-assisted partial-world reasoning; cache coalescing and bounded reuse are also prior art. The exact combination has not been established as novel by this search. Mere 64-byte packing or renaming those mechanisms would fail the gate.

## Gate ledger

| Gate | Finding | Disposition |
|---|---|---|
| Independent F1/F2 reproduction | Supplied script, separate oracle and pinned Z3 witnesses agree | Original rules rejected |
| Guard implication and reads | Correct query-to-guard entailment preserves all solutions | PASS for specified outer-bound API |
| Domain algebra | Arbitrary 64-bit sets and signed 32-bit intervals verified | PASS for modes 0/1; Mode 2 rejected |
| Six corrected operations | Symbolic obligations pass, broken variants refuted | PASS for primitive soundness |
| Overflow | General guard-mask intersection plus domain join is unsound | Evict-only default; lifting requires coverage certificate |
| Assumption recycling | Immediate unit-based reuse permits stale aliasing | Disabled within M1 epochs; drain/version contract required later |
| Replicas/coherence | Same-model stale facts are sound, freshness and convergence do not follow | Single authoritative owner in first experiment |
| Nogoods | Validity is model-relative; only entailed contexts may be cancelled | PASS for logical rule; no global one-cycle claim |
| Propagation completeness | Threshold-only events and bounded eviction can lose closure | Mandatory exact-solver fallback and complete event handling |
| Novelty | Fundamental rules occupied; possible narrow placement/interface contribution | Eligible for cheap falsification; novelty unproven |
| Practical significance | No workload evidence, timing or energy measurements | Must be tested, cannot be inferred from guard coverage |

Verification totals: 73 Z3 queries with all expected results, including 50 UNSAT obligations and 23 SAT refutations/witnesses. Independent checks include 46,656 guard/domain pairs, 135,000 partial queries in each domain mode, 16,807 signed boundary memberships and 10,000 bounded transitions. See `M0_PROOF_RESULTS.md` for the exact scope and trust boundary.

## Small M1 experiment justified by this gate

This is a prospective protocol only. No implementation is included or dispatched. It should test a necessary condition cheaply before building the handoff's multi-tile simulator.

1. Freeze a small suite before running: several finite-domain CSPs with repeated conditional deductions, several bounded integer-difference-constraint fragments, and both sparse-sharing and dense XOR/parity controls. Include genuine independent assumption meanings, at most 32 per immutable epoch. Start with small instances whose solution sets can be independently enumerated. Add an external exact solver check before scaling beyond enumeration. Do not inject artificially pre-lifted facts to produce a sharing win.
2. Execute search and sound propagators so that admissions, evictions and nogoods affect subsequent computation. Replaying a fixed update list alone cannot measure lost pruning or fallback. Preserve exact branch decisions, seeds, dependency provenance and all residual work. Validate outputs with an oracle independently constructed from original constraints, not from the same translated graph.
3. Keep authoritative ordinary solver state. Add the corrected optional cache with `S in {1,2,4,8,16,infinity}` including basal in S. S=4 means three speculative slots. Fix per-variable mode and immutable epochs; use an explicit work queue and fair subscriptions. Disable intra-epoch recycling, asynchronous replicas and width-only threshold wakeups. All fallback work and any epoch reset count toward execution cost.
4. Compare optimized ordinary propagation, unbounded and bounded ATMS-style labelled bounds, contiguous/SIMD four-slice software, a symbolic/decision-diagram or bounded context-cache competitor, and software contextual batching/coalescing. Controlled comparisons share branch order and root preprocessing; a secondary comparison lets tuned solvers use their native policies. Materialized batches are optional additional baselines. Match memory budgets including model IDs, guard metadata, subscriptions, queues and nogoods.
5. Record completed solutions/validated infeasibility, actual propagator evaluations, fallback work, guard introduction/lifting, successful reuse in distinct visited contexts, evictions/rederivations, queue events, storage including side metadata, and bytes required by each specified placement/interface. Logical algorithm counters may match the identical optimized software implementation; that is expected. Separate algorithmic reuse from host instructions/state movement that an offloaded port might avoid.
6. Ablate lifting, guard filtering, contextual storage, admission policy and event filtering. A PHI-style basal-only path is an ablation; contextual batching software is the stronger comparison. Sweep assumed port/update costs conservatively and report estimates as estimates. This pilot cannot establish GHz timing, energy or a global cache protocol.

### Pre-registered continuation and stop rules

These replace the handoff's inconsistent 65% versus 70% pruning-retention targets. They are prospective project acceptance criteria, not measured results or universal scientific constants.

- **Correctness:** zero excluded feasible values, invalid nogoods or incorrect final solver outcomes. Any failure blocks further architecture development until independently resolved; preserve the witness.
- **Meaningful reuse:** at least 2× fewer total propagator evaluations, including fallback, than optimized ordinary propagation on the frozen positive suite's geometric mean. Report every instance, not only the mean. Count reuse only in visited contexts where a useful deduction is actually avoided; `2^(K-|E|)` is not the metric. If a stronger symbolic or context-sharing competitor dominates the same metric, the algorithmic rationale needs revision.
- **Bounded precision:** on an identical pre-registered set of visited query contexts, let `P=number of sound value exclusions` for finite domains. For interval fixtures use reduction in the finite original integer range, counting excluded integers. Require aggregate `P_S4/P_unbounded >= 0.65` separately in each workload family; instances with zero denominator are N/A. Also compare validated conflict-context coverage. During execution separately report extra search nodes and fallback work, since identical exclusions on a query sample do not imply identical search cost. Falling below the threshold kills the four-slice design point.
- **Architectural headroom:** against the strongest contextual software/coalescing implementation, require at least 2× reduction in measured/explicitly accounted host state movement or event-service work attributable to the memory-port interface after charging metadata and fallback. An idealized zero-cost port is insufficient. If there is no credible headroom even under favorable, clearly stated assumptions, issue architecture NO-GO. Equal logical firing counts against identical software are not a failure by themselves, but cannot be presented as hardware speedup.
- **Controls:** dense cube-unfriendly contexts should reveal bounded-cache pressure. Parity may favor BDDs; do not require every symbolic method to fail. Positive controls must show an independently explained reuse effect. Any universal win caused by uncharged dropped work invalidates the evaluator.

Passing this pilot permits a separately scoped protocol/cost study. It does not justify RTL. The handoff's AVX-512 “within 1.5× hardware throughput/energy” threshold is not actionable before a validated throughput/energy model exists; use measured software costs and explicit optimistic/pessimistic placement estimates now. Preserve the original threshold in the input archive, but do not manufacture hardware energy from Python operation counts.

## Nonnegotiable rejections

The original proposal is not a monotone four-slot replicated semilattice memory. Eviction removes retained knowledge; byte-delta filtering misses contextual changes; recycled predicates can invalidate old facts. General overflow compression and compatible-slice partial reads are demonstrably unsound. One-cycle global kill, zero-invalidations coherence, complete fixed points, constant-size exact exponential reasoning, and 4× improvements remain unsupported. The six-rule proof also does not certify arbitrary compiler lowering or propagator arithmetic.

The small pilot is justified because a sound and operationally useful guarded-port candidate remains and can be tested with strong falsification controls. It is not a rescue through nomenclature. If useful precision and a differentiated placement benefit fail to survive those comparisons, the final architecture decision must be **NO-GO**, even if an optimized software library remains useful.

## Unresolved assumptions carried forward

| Assumption | Current treatment | Evidence needed before broader claims |
|---|---|---|
| Real workload sharing is shallow/local enough | Unknown | Execution-driven reuse and occupancy distributions |
| Four slots retain useful pruning | Unknown | Capacity sweep with equal semantic query samples and actual fallback cost |
| Port placement beats optimized software/coalescing | Unknown | Measured host costs and fully charged interface traffic |
| Propagators and branch compilation are sound | Required input contract | Independent translation/transformer checks |
| Guard lifecycle is safe under deep search | Immutable K<=32 epoch in pilot | Versioned translation and drain proof for larger windows |
| Replicas reliably converge/process obligations | Excluded from initial pilot | Protocol safety/liveness verification and termination model |
| Metadata and subscriptions fit realistic budgets | Charged, layout unimplemented | Concrete storage/packet format and cost sensitivity |
| Novelty is more than established mechanism composition | Unproven | Further citation/patent mapping and experimental separation |
| CLMU timing/area/energy are practical | No evidence | Later validated cost study, followed by separately authorized implementation |

Deliverables and executable evidence are complete for this M0 scope. The gate decision is a bounded research judgment, not a prediction that CLAM will survive M1.
