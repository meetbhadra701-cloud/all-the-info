# CLAM M1 hardware necessity

Date: 2026-10-13. **No hardware architecture continuation is justified by this pilot. Criterion 4 is UNRESOLVED, not demonstrated false or passed.** The necessary computation-saving screen already fails, so a protocol/timing/energy study would be premature.

## What the execution evidence supports

An incremental ordinary solver already retains ancestor deductions and suppresses no-change wakeups. Guarded facts are true and sometimes useful in another visited context, but importing them does not authorize dropping a constraint's remaining dependency work. On this suite, S=4 preserves all A propagator and queue-event counts and all search-node counts. It saves a few support probes, adds guarded-cache operations, and does not change outcomes.

This tests the strongest practical objection raised before coding: the proposed mechanism may mostly re-express work suppression already available to ordinary software. The data support that objection in this implementation/suite. It is not a theorem that every possible cache policy or workload fails, or a measured comparison to all solver techniques in the M0 prior-art report.

## Explicit interface accounting

These are logical operation/interface counts, not measured cache traffic:

- Reading an occupied slice accounts for its 16-byte guard/domain payload. Line/model metadata is accounted in storage; actual bank/NoC transfer behavior is unimplemented.
- An update packet is 48 bytes: address, guard, descriptor, problem/version identity, epoch and provenance, each eight bytes.
- A subscriber event is 32 bytes: operation ID, context guard, problem/version and epoch. The actual reference queue is owner-local; this is a stated transferable interface schema.
- A candidate S=4 line estimate is 64-byte payload plus 96 bytes of per-entry provenance/LRU/birth-context metadata and 32 bytes of line metadata: 192 bytes in this conservative logical layout. Birth context is audit/reuse metadata and might be removed by a future design; it is charged here rather than hidden. Solver state, subscriptions, supports and nogoods are additional.

The packet and queue counts correspond to actual execution. Subsumption-pair checks are a counted subset of cache bookkeeping; no claim is made that they count every host instruction or every guard test. Conditional conjunctions, narrowing, resolution candidates, reads and budget events are exposed separately in the metric records.

| Instance | C slice payload bytes inspected | C update-packet bytes | A=C queue-event bytes |
|---|---:|---:|---:|
| queens4 | 864 | 2,112 | 1,760 |
| queens5 | 5,088 | 5,520 | 7,456 |
| queens6 | 12,592 | 16,656 | 23,360 |
| cycle7 | 89,440 | 12,240 | 21,408 |
| chorded_cycle7 | 36,960 | 6,384 | 15,008 |
| signed_chain5 | 80 | 960 | 320 |
| diamond5 | 13,504 | 1,632 | 6,240 |
| bounded_cycle4 | 1,392 | 2,160 | 1,408 |
| interleaved_equalities8 | 3,536 | 480 | 800 |
| interleaved_implications8 | 17,264 | 336 | 3,904 |
| dense_xor8 | 17,312 | 7,296 | 10,016 |
| inconsistent_parity6 | 9,872 | 5,568 | 5,056 |
| alldifferent6 | 466,848 | 109,728 | 449,440 |
| random_tables6 | 3,856 | 2,256 | 2,304 |

Moving the cache computation to a memory port could hide some of its software costs. That alone is not evidence for CLAM: A avoids those added operations entirely while doing the same required propagation. Even an ideal zero-cost contextual-cache implementation has no demonstrated 2× logical saving here. Generic propagation acceleration or SRAM locality might still help, but that would require comparison to a propagation accelerator without the contextual mechanism and cannot be inferred as CLAM novelty.

## Why criterion 4 remains unresolved

There is no native/SIMD contextual implementation, strongest-contextual-software/coalescing comparison, validated bank-placement model, host instruction/memory trace, queue service model or hardware timing/energy evidence. The Python process timings include reference and audit costs. Logical packet schemas do not predict physical L1/L2/NoC traffic. No artificial 64-byte-per-update CPU penalty, MESI invalidation cost, one-cycle kill bus or zero-cost queue is imposed.

The early stop therefore prevents the stronger-baseline expansion and architectural cost/protocol study. Criterion 4 cannot be scored as a 2× advantage; nor does this experiment establish an absolute upper bound on possible hardware speedup. The hardware NO-GO follows from failing the prior necessary 2× computation gate, with no measured differentiated mechanism to carry forward.

## Software value kept separate

The surviving artifact is a small, exhaustively checked guarded-domain reference, oracle and reproducible falsification suite. It may be useful as a correctness/regression substrate. This pilot does not establish that the guarded cache is a faster software solver, a new algorithm, an advantageous library or a publishable systems result. ATMS, bounded context caching, symbolic sharing and commutative cache updates remain established prior art; no novelty or citation claim is made.
