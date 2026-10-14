# CLAM M1 gate decision

Date: 2026-10-13. **Final verdict: NO-GO for the hardware architecture.** Keep the independently checked reference/oracle as an experimental correctness artifact; do not infer a useful software speedup from its existence.

The strongest objection was that incremental ordinary propagation already preserves deductions and suppresses redundant events, leaving little computation for a guarded memory-port cache to eliminate. The frozen execution-driven pilot supports that objection. S=4 uses exactly the same total propagator evaluations and search nodes as A on every one of 14 instances. Unbounded storage achieves only **0.984335×** A/B total-work reduction on the ten positive instances, against the pre-registered **2×** requirement. Constraint-only work is essentially unchanged as well: **1.000164×**.

## Decision ledger

| Continuation criterion | Evidence | Decision |
|---|---|---|
| Zero correctness violations | Exhaustive original-constraint oracle, fact/nogood validation, complete solution sets, infeasible subtrees, mutation controls; 51 final-source state-audit runs | PASS for the finite implemented scope |
| At least 2× fewer total evaluations | A/B positive geometric mean 0.984335×; A/C 1× on every instance | **FAIL—decisive early stop** |
| At least 65% unbounded precision retained per positive family | Paired total: CSP 92.10%, IDL 98.55%, sparse 100%; paired incremental: 40%, 61.54%, 100%; final B/C common-query CSP retention 28.56% | Paired proxy passes its stated scope; broader unbounded retention is not established, and the historical CSP comparison fails |
| At least 2× credible placement-specific benefit vs strongest contextual software | No such baseline or validated placement model; same queue counts as ordinary propagation | **UNRESOLVED**, no manufactured cycle/energy result |

The primary capacity metric's favorable numbers do not override the computation failure. It mostly retains exclusions already present in authoritative state. End-of-search contextual history retention is only 28.56% on CSP and 7.53% on low-sharing controls, but even the larger B store has no useful search-node reduction to preserve.

## Work completed and where it stopped

- Read all mandatory M0 documents and recorded contract reconciliation before coding.
- Froze 14 original-semantics fixtures and sources/transformations before comparisons; seed `20261013` and hashes are preserved.
- Implemented single-owner execution-driven GAC/search, causal guarded facts, entailment reads, safe meet/conjunction/nogoods/single-pivot lifting, sound LRU eviction, explicit subscriptions/queue and charged complete fallback.
- Passed bitset gates, then added/validated signed intervals. Measured the initial A/B/C bitset suite, including bounded signed IDL semantics. Every published run was independently validated.
- Applied the early gate and stopped. No performance capacity sweep, stronger-software/BDD/coalescing expansion, interval performance stage, multicore/timing/coherence model, protocol-cost study, RTL or physical design followed.
- Performed a final correctness-only audit of authoritative state, with no performance credit or workload expansion, and packaged the evidence/reproduction commands.

The optional inference budgets and interrupted development checks are disclosed rather than hidden. Unbounded B means source-fact storage without eviction, with finite optional computation budgets. Its all-different negative case reaches the scan budget and falls back; **no positive-suite case reaches that cap**. The pilot is not represented as a complete ATMS saturation experiment.

## Limits of this NO-GO

The suite is small, largely generated, and includes public-definition queens kernels rather than large industrial datasets. The ordinary baseline uses table GAC and pairwise decompositions, not a best-in-class native solver with stronger global propagators. The contextual implementation eagerly imports facts at nodes and wakes every changed dependency; alternative scheduling/certificates could behave differently. Interval performance, large-window predicates, deep search, native SIMD and physical placement remain unmeasured.

These limitations prohibit universal claims that contextual reasoning or all possible hardware realizations are useless. They do not justify continuing this candidate after its pre-registered necessary threshold fails. More than naming a different policy would be needed: a new, concrete mechanism and independent evidence of a bottleneck would require a separately authorized research task.

The evidence shows a mathematically sound mechanism with sparse cache-level reuse and minor support-probe savings, not a practical reason to build CLAM as a chip. Criterion 4 stays unresolved because it was neither needed nor justified after the early failure. Passing correctness alone does not authorize implementation.

Deliverables: `M1_EXPERIMENT_SPEC.md`, `M1_CORRECTNESS_REPORT.md`, `M1_BASELINE_RESULTS.md`, `M1_CAPACITY_AND_REUSE.md`, `M1_HARDWARE_NECESSITY.md`, this gate decision, and the versioned code/inputs/logs/results under `m1/` and `evidence/m1/`. The M0 inputs, rejected claims and evidence remain preserved.
