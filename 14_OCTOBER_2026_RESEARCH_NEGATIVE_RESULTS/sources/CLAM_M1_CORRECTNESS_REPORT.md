# CLAM M1 correctness report

Date: 2026-10-13. **PASS for the implemented finite pilot: zero production correctness violations.** This does not prove a generic compiler, arbitrary propagators, distributed protocol, or unbounded-integer solver correct.

All four M0 inputs were read completely before coding. The experiment uses their corrected universal-implication invariant, literal entailment reads, meet/union, pinned basal slot, sound eviction and immutable assumption meanings. The rejected overflow, compatible-slice partial read, immediate bit recycling, coherence and timing claims remain rejected.

## Independent oracle and certification

`m1/oracle.py` enumerates original variable assignments and directly checks original constraints. It does not import the solver, compiled support relations, cache operations or guard helpers. The solver separately compiles supports and performs incremental generalized arc consistency with a trail and explicit queue. Bit indices map bijectively to original values, including negative integers. At most 30 of the allowed 32 stable predicates are used by this suite; there is no bit recycling.

Every solution set is compared exactly with exhaustive enumeration, including absence of duplicates, SAT/UNSAT outcome and each infeasible subtree. Every emitted/derived domain claim and learned nogood is checked over all original solutions satisfying its guard. Exact-body certificate memoization changes checking cost, not the set of worlds checked. The performance workers validate before publishing a successful result; a failure would save its fixture/witness and stop the comparison driver.

An additional post-stop audit checks **every authoritative value-deletion transition**, including branch restrictions and conventional nogood units that bypass the cache, against the exhaustive relation. It changes no solver decisions and earns no performance credit. All 51 frozen bitset/interval variant runs pass 17,084 state checks.

## Executed validation

| Check | Executed cases | Result |
|---|---:|---|
| Actual cache claims against explicit independent world/value relations | 13,035 | PASS |
| Partial cache reads following actual admissions/evictions | 324,000 | PASS |
| Frozen bitset solver configurations, A/C/B | 42 | Exact solution sets agree |
| Seeded randomized finite CSP solver configurations | 200 | Exact solution sets agree |
| Signed 32-bit boundary membership/meet/hull checks | 16,807 | PASS |
| Frozen IDL checks in both bitset and interval modes | 18 | Exact solution sets agree |
| Seeded randomized signed IDL configurations | 160 | Exact solution sets agree |
| Post-stop authoritative-state audit | 51 runs; 17,084 transitions | No feasible value excluded |
| Published initial A/B/C comparison runs | 42 | All validated before publication |

The 42 comparison runs checked 19,431 fact-claim occurrences and 280 nogood occurrences, comprising 15,020 distinct fact bodies and 262 distinct nogood bodies. Valid domain nonemptiness is never used as a satisfiability proof. Every cache miss or insufficient bound is handled by ordinary propagation and exhaustive branching, with actual work charged.

| Frozen instance | Original candidate assignments | Exhaustive solutions | Predicate count |
|---|---:|---:|---:|
| queens4 | 256 | 2 | 12 |
| queens5 | 3,125 | 10 | 20 |
| queens6 | 46,656 | 4 | 30 |
| cycle7 | 2,187 | 126 | 14 |
| chorded_cycle7 | 2,187 | 54 | 14 |
| signed_chain5 | 3,125 | 1 | 20 |
| diamond5 | 1,024 | 42 | 15 |
| bounded_cycle4 | 625 | 5 | 16 |
| interleaved_equalities8 | 256 | 8 | 8 |
| interleaved_implications8 | 256 | 48 | 8 |
| dense_xor8 | 256 | 8 | 8 |
| inconsistent_parity6 | 64 | 0 | 6 |
| alldifferent6 | 46,656 | 720 | 30 |
| random_tables6 | 729 | 8 | 12 |

All three measured variants return these complete sets. Signed interval integration was added after a completed bitset gate, then independently checked before comparisons. Intervals are signed hulls with explicit empty handling; the authoritative state retains exact original finite values. Thus the signed tests do not establish unrestricted QF_IDL completeness or interval precision for arbitrary holes.

## Negative controls and development record

Six bitset controls detect compatible-slice reads, meet instead of union in resolution, an omitted solution, an extra invalid solution, a false unconditional nogood, and a false unconditional domain fact. The interval control detects unsigned comparison on `[-1,1]` at value 0. A resolution-meet mutation emits a false TRUE nogood rather than necessarily installing an empty basal fact; the test observes the correct failure mode.

Four deliberately invalid checker outputs have reproducible `failure_*.json` files under `evidence/m1/counterexamples/`. They are **expected negative controls**, not production violations. Primitive mutation witnesses are additionally recorded in `evidence/m1/results/negative_controls.json`; source assertions reproduce them. Original M0 counterexamples remain intact.

Development sequencing, interrupted validation attempts, the initially premature interval draft, observer optimizations and bounded optional-inference amendments are disclosed in `evidence/m1/logs/DEVIATIONS.md`. No performance comparisons or result-directed fixture selection preceded those amendments. Source drafts and logs were retained. The initially premature interval helper branches were removed before executing tests; the final interval extension followed the completed bitset gate. No production semantic failure was found or concealed.

## Scope and reproducibility

Selected gate artifacts: `bitset_correctness.json`, `interval_correctness.json`, `state_audit.json`, `oracle_inventory.json` and each measured run's `verification` section. The final-source interval gate includes bitset IDL regressions; the post-stop audit covers all frozen final-source configurations. M0 SMT evidence was not replaced or silently reinterpreted as an M1 proof.

Run commands and exact versions are in `evidence/m1/REPRODUCE.md` and `tool_versions.json`; SHA-256 manifests cover frozen inputs, source snapshots, reports and outputs. Constraints are small and finite; the proof of performance-case completeness is exhaustive enumeration, not the original architecture's claimed global fixed point.
