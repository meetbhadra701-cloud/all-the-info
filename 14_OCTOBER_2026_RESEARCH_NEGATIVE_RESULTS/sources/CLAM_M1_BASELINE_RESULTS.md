# CLAM M1 baseline results

Date: 2026-10-13. **The required 2× computation reduction fails.** S=4 executes the same total rule evaluations and search nodes as ordinary propagation on every frozen instance. Unbounded storage achieves a positive-suite geometric mean A/B ratio of **0.984335×**, meaning slightly more total work, not a speedup.

A is incremental ordinary propagation with reversible trail, residual supports and a coalesced dependency queue. B adds unbounded guarded-fact storage. C adds S=4, including basal and three speculative slots. All share conventional nogood learning/unit handling, the constraint transformer, initial preprocessing, immutable predicates and fixed positive-first branch policy. The realized decision predicates and visited contexts are saved; cache-induced pruning may change a realized trace, so the report does not equate a fixed policy with a fixed replay.

## Per-instance results

Total evaluations count GAC constraint invocations plus actual conventional nogood-clause checks. Fallback work is included. Constraint-only invocations and support checks are separately available, preventing nogood granularity from hiding a possible effect.

| Instance | Total A | Total B | Total C | GAC A/B/C | Search nodes A/B/C | Solutions |
|---|---:|---:|---:|---|---|---:|
| queens4 | 86 | 86 | 86 | 47 / 47 / 47 | 7 / 7 / 7 | 2 |
| queens5 | 257 | 257 | 257 | 227 / 227 / 227 | 21 / 21 / 21 | 10 |
| queens6 | 5,192 | 6,080 | 5,192 | 609 / 608 / 609 | 41 / 41 / 41 | 4 |
| cycle7 | 669 | 669 | 669 | 669 / 669 / 669 | 251 / 251 / 251 | 126 |
| chorded_cycle7 | 469 | 469 | 469 | 469 / 469 / 469 | 107 / 107 / 107 | 54 |
| signed_chain5 | 10 | 10 | 10 | 10 / 10 / 10 | 1 / 1 / 1 | 1 |
| diamond5 | 195 | 195 | 195 | 195 / 195 / 195 | 83 / 83 / 83 | 42 |
| bounded_cycle4 | 44 | 44 | 44 | 44 / 44 / 44 | 9 / 9 / 9 | 5 |
| interleaved_equalities8 | 25 | 25 | 25 | 25 / 25 / 25 | 15 / 15 / 15 | 8 |
| interleaved_implications8 | 122 | 122 | 122 | 122 / 122 / 122 | 95 / 95 / 95 | 48 |
| dense_xor8 | 2,865 | 2,865 | 2,865 | 257 / 257 / 257 | 63 / 63 / 63 | 8 |
| inconsistent_parity6 | 2,366 | 2,366 | 2,366 | 126 / 126 / 126 | 63 / 63 / 63 | 0 |
| alldifferent6 | 14,045 | 14,045 | 14,045 | 14,045 / 14,045 / 14,045 | 1,439 / 1,439 / 1,439 | 720 |
| random_tables6 | 141 | 154 | 141 | 68 / 67 / 68 | 17 / 17 / 17 | 8 |

The positive suite includes the first ten instances: CSPs, IDL fragments and sparse controls. A/B geometric means are CSP **0.968916×**, IDL **1.000000×**, sparse **1.000000×**. Its constraint-only geometric mean is **1.000164×**. Total positive work is A=7,069, B=7,957, C=7,069. Removing nogood-check overhead therefore does not rescue the result.

Unbounded storage saves one GAC invocation on queens6 and one on random_tables6, but triggers more nogood checks. It saves some tuple probes: queens6 5,688→5,665, chorded_cycle7 2,035→1,999, diamond5 1,012→963 and dense_xor8 6,309→6,165. C also reduces chorded_cycle7 probes to 2,017 and diamond5 probes to 981. These small reductions do not approach 2×. The full CSV is authoritative for these secondary counts. No reduction in complete search nodes occurs. C preserves exactly A's queue-event counts on all 14 instances.

## Work and memory beyond propagator counts

C handles 3,611 guarded packets and 13,664 counted subsumption-pair comparisons, plus additional conjunction/resolution/narrowing and cache-read work. These costs are not assigned invented cycle equivalents. A has no corresponding contextual-cache overhead. All required residual propagation runs after imports; a fact is not permission to discard subscriber obligations.

| Instance | Sampled logical layout A/B/C, KiB | Measured process peak RSS A/B/C, MiB |
|---|---|---|
| queens4 | 3.78 / 4.53 / 4.53 | 20.64 / 20.64 / 20.64 |
| queens5 | 8.21 / 13.29 / 9.15 | 20.64 / 20.64 / 20.64 |
| queens6 | 16.07 / 29.84 / 17.20 | 20.64 / 21.01 / 20.64 |
| cycle7 | 3.69 / 20.91 / 5.00 | 20.64 / 22.39 / 20.64 |
| chorded_cycle7 | 4.84 / 11.58 / 6.15 | 20.64 / 20.64 / 20.64 |
| signed_chain5 | 2.98 / 3.33 / 3.91 | 20.64 / 20.64 / 20.64 |
| diamond5 | 3.41 / 4.74 / 4.35 | 20.64 / 20.64 / 20.64 |
| bounded_cycle4 | 3.83 / 5.05 / 4.58 | 20.64 / 20.64 / 20.64 |
| interleaved_equalities8 | 1.77 / 2.73 / 3.27 | 20.64 / 20.64 / 20.64 |
| interleaved_implications8 | 1.88 / 2.72 / 3.38 | 20.64 / 20.64 / 20.64 |
| dense_xor8 | 7.54 / 10.04 / 9.04 | 20.64 / 20.64 / 20.64 |
| inconsistent_parity6 | 6.03 / 7.86 / 7.16 | 20.64 / 20.64 / 20.64 |
| alldifferent6 | 17.51 / 119.77 / 18.63 | 20.64 / 23.98 / 22.57 |
| random_tables6 | 4.52 / 5.95 / 5.65 | 20.64 / 20.64 / 20.64 |

The logical schema charges payload, validity/model/epoch metadata, provenance, replacement stamps, subscriptions, exact domains/reasons, trail, supports/residues, nogoods and queues. It is a sampled layout estimate, not an exact peak hardware footprint. Fresh-process RSS is sampled before oracle construction, includes interpreter and audit-history allocations, and is too coarse to resolve many small-instance differences. Full source, counters and rows are retained for inspection.

Single-run diagnostic construction/search times total approximately A=0.398 s, B=2.371 s, C=0.501 s after subtracting the explicitly measured shadow work. These are Python reference measurements with audit bookkeeping and millisecond cases, not throughput claims; no confidence interval, native SIMD comparison or chip inference is justified. The decision rests on deterministic logical work, not those timings.

## Budget and stopping boundary

Optional resolution uses a context-wide 64-candidate budget. Optional cross-guard optimization switches to source-fact admission/equal-guard meet after one million counted subsumption checks. B retains unbounded source-fact storage and the ordinary solver still completes all work. The latter fallback occurs only on **B/alldifferent6**: 1,812 packets; no positive-suite run triggers it. Counted checks slightly exceed one million because an already-started packet finishes its scan. Thus B is not claimed to reach complete ATMS closure, and the capped negative case cannot prove unrestricted label complexity.

The frozen positive suite nevertheless misses the necessary 2× threshold even without that cap. Early stopping therefore ends performance work: no S=1,2,8,16 performance sweep, SIMD/ATMS/BDD/coalescing expansion or signed-interval performance comparison. Signed intervals were correctness-tested before the gate; bounded IDL already has measured bitset results. Their separately recorded correctness executions are not converted into favorable performance numbers after the stop.

Evidence: `baseline_bits.csv/json`, all 42 detailed `bits_*_[ABC].json` records, their summaries, `baseline_bits.log` and `INITIAL_GATE.json`. This is a small public-definition/generated suite with pairwise decomposition and table GAC, not a state-of-the-art industrial CP/SMT evaluation.
