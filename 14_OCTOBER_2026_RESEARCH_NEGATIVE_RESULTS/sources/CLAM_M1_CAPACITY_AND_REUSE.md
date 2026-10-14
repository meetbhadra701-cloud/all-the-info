# CLAM M1 capacity and reuse

Date: 2026-10-13. Some true facts are reused in different visited contexts, but **reuse does not produce the required computation saving**. Aggregate pruning-retention numbers can look favorable while preserving mostly information already available in authoritative solver state.

Reuse is counted only when a cached fact removes at least one currently present value at an actual node, with a creation context different from the current context. It is an application-event count, not a count of hypothetical `2^(K-|E|)` worlds or proof that a propagator was avoided. All resulting dependency wakeups and remaining exact propagation are charged.

## Per-workload cache behavior

| Instance | Cross-context useful applications B/C | C admissions | C evictions | C rederivations | Paired retention |
|---|---|---:|---:|---:|---:|
| queens4 | 0 / 0 | 28 | 9 | 0 | 100.0% |
| queens5 | 0 / 0 | 90 | 71 | 0 | 87.5% |
| queens6 | 3 / 0 | 244 | 198 | 2 | 80.9% |
| cycle7 | 0 / 0 | 248 | 213 | 4 | 95.1% |
| chorded_cycle7 | 12 / 6 | 125 | 100 | 9 | 93.5% |
| signed_chain5 | 0 / 0 | 0 | 0 | 0 | N/A |
| diamond5 | 13 / 8 | 30 | 20 | 5 | 99.0% |
| bounded_cycle4 | 0 / 0 | 27 | 15 | 0 | 91.7% |
| interleaved_equalities8 | 10 / 10 | 10 | 0 | 0 | 100.0% |
| interleaved_implications8 | 13 / 13 | 7 | 0 | 0 | 100.0% |
| dense_xor8 | 16 / 0 | 152 | 93 | 16 | 0.0% |
| inconsistent_parity6 | 0 / 0 | 116 | 56 | 0 | N/A |
| alldifferent6 | 0 / 0 | 2286 | 2209 | 0 | 74.0% |
| random_tables6 | 0 / 0 | 36 | 14 | 0 | 100.0% |

The JSON/CSV records contain the admissions and rederivation counters; the table reproduces C's normal-admission counters. Historical rederivations mean the same `(variable,guard,descriptor)` is newly admitted again after having appeared before, not merely that a propagator fires again. The budget fallback path does not maintain this historical counter, so B/all-different's admission-rederivation count is incomplete. `rederivation_inventory.json` independently counts repeated claim bodies from every saved claim record, including that fallback path; it distinguishes repeated produced claims from readmission events. No C run reaches the scan budget. Changing guards can reproduce a value exclusion under a different signature, separately visible in packets/firings.

Across the measured suite, B has 67 cross-context useful applications and C has 37. On the ten positive instances these are 51 and 37. Both sparse controls do reuse facts; nevertheless their propagator, queue and support-check counts are identical to A. This directly separates provenance reuse from saved computation.

## Capacity precision at genuinely visited nodes

At every actual C node before importing cached facts, probe C and an unbounded shadow of the same certified emission history. The shadow cannot alter search, learning, admission or timing decisions; its work is recorded separately. It receives emitted/derived claims and uses equal-guard meet and subsumption, without synthesizing its own additional resolutions. This isolates retention of C's emitted knowledge under capacity; it is not a claim about an independently saturated ATMS.

Total precision counts exclusions relative to original domains. Incremental precision counts exclusions still useful relative to the inherited authoritative state before cache import. Root/ancestor bounds can raise the total metric without saving any work.

| Family | Total bounded/unbounded exclusions | Total retention | Incremental bounded/unbounded | Incremental retention |
|---|---|---:|---|---:|
| Positive CSP | 2,298 / 2,495 | 92.10% | 6 / 15 | 40.00% |
| Positive IDL | 545 / 553 | 98.55% | 8 / 13 | 61.54% |
| Sparse positive controls | 199 / 199 | 100.00% | 23 / 23 | 100.00% |
| Dense parity controls | 0 / 16 | 0.00% | 0 / 16 | 0.00% |
| Low sharing controls | 13,168 / 17,766 | 74.12% | 0 / 0 | N/A |

The primary paired total metric exceeds 65% on each positive family, but it does not establish useful retained pruning. The incremental diagnostic falls below 65% in CSP and IDL, and even 100% in sparse controls yields no firing benefit. Cases with zero denominator remain N/A, not 100%.

## End-of-search historical query coverage

Separately query final B/C stores on **all baseline A actually visited contexts**, including those B/C did not visit. This is a read-only common-query test with no search-performance credit. It mixes capacity loss with different learning histories, so it cannot replace the paired temporal metric.

| Family | Final C/B exclusions on common A queries | Retention |
|---|---|---:|
| CSP | 910 / 3,186 | 28.56% |
| IDL | 489 / 644 | 75.93% |
| Sparse | 216 / 216 | 100.00% |
| XOR | 30 / 230 | 13.04% |
| Low sharing | 1,488 / 19,749 | 7.53% |

S=4 clearly forgets historical contextual information on several families, including 2,209 evictions on all-different. B's larger store still does not reduce search nodes or attain 2× less propagation. Capacity is therefore not the only reason for failure; replacing S=4 with more slots has no demonstrated computation win to preserve in this pilot.

Useful nogood applications are conventional and shared across all variants. Generation, unit-deletion application, cancellation and final common-query coverage are recorded separately in detailed outputs. Learning a sound conflict is not credited as hardware novelty or instant global work cancellation.

Per-instance retention, exclusion totals, nogood coverage, budgets and work counters are in `INITIAL_GATE.json` and the detailed run records. A performance S=1,2,8,16 sweep was deliberately not run after the early gate; varied capacities in correctness tests are not presented as performance evidence.
