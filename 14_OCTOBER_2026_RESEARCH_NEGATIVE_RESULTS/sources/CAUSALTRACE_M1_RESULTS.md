# Mission 1 — executed Stage 0 results

Completed **2026-10-12, America/Los_Angeles**. **Decision: NO-GO.**

All **48 frozen traces** were generated on real existing RTL: 24 on the AXI width adapter and 24 on the AXI crossbar. Each block exercised two legal write-load regimes, three delay regimes, and seeds 101, 211, 307, and 401. The same actual observed trigger, source records, ingress contract, projection, and 16 KiB budget were used by all policies.

**Closure-aware C reconstructed no correct projection missed by the pinned-table hybrid B.** This satisfies the specified stopping rule. No Stage 1 or held-out experiment was launched.

## Reconstruction coverage

“Success” below means CERTIFIED-BOUNDED **after** all four checks: bounded model existence SAT, alternative projection UNSAT, replay on the existing full RTL, and equality with the separate full-trace oracle.

| RTL / delay regime | Traces | A: compressed FIFO | B: pinned hybrid | C: closure-aware | Trace length, cycles |
|---|---:|---:|---:|---:|---:|
| Width adapter / below | 8 | 8 | 8 | 8 | 80–92 |
| Width adapter / near | 8 | 8 | 8 | 8 | 216–252 |
| Width adapter / above | 8 | 0 | 8 | 8 | 414–483 |
| Crossbar / below | 8 | 8 | 8 | 8 | 88–106 |
| Crossbar / near | 8 | 8 | 8 | 8 | 235–286 |
| Crossbar / above | 8 | 0 | 8 | 8 | 452–554 |
| **Total** | **48** | **32 / 48** | **48 / 48** | **48 / 48** | **80–554** |

Policy A's 16 unsuccessful cases were **INCOMPLETE**, not asserted provably ambiguous. This checker conservatively requires complete retained intervals for read-cone inputs. Policies B and C had no unsuccessful cases.

C minus B coverage: **0 percentage points**. C-only successes: **0**. Main-screen false certificates: **0**. TIMEOUT, MODEL-MISMATCH, and AMBIGUOUS main-screen results: **0**.

Machine-readable outputs: [summary.json](mission1/results/summary.json), [results.csv](mission1/results/results.csv). The 48 per-case result files include evidence/model hashes, solver answers, validation hashes, queue metrics, and memory accounting.

## What was actually simulated

Both unmodified supplied testbench selections passed first: **25 internal cocotb tests** for the adapter and **33** for the crossbar, including normal read/write correctness and stress cases. The final pinned simulator was Icarus 11. The tracked upstream source remained unchanged.

The screen then executed the existing full adapter with 32-bit upstream / 16-bit downstream data and the existing full 2×2 crossbar with 32-bit data. Existing cocotb AXI master and RAM-write models generated legal background writes.

The monitored transaction was one pending burst read on upstream port 0 / downstream port 0. The receiving master withheld read readiness. At the prescribed evidence-pressure point, a Python responder changed one held response field:

| Seed | Invalid boundary perturbation |
|---:|---|
| 101 | RDATA changes while valid and stalled |
| 211 | RID changes while valid and stalled |
| 307 | RRESP changes while valid and stalled |
| 401 | RLAST changes while valid and stalled |

These are intentionally invalid external inputs, **not discovered RTL bugs**. The common trigger was the observed held-response stability violation. An oracle audit verified legitimate write traffic in every trace and the exact intended changed response field. Adapter cases accepted 5–25 legal write addresses; crossbar cases accepted 7–35. [Workload audit](mission1/checks/workload_audit.json).

Delay was defined by emitted compressed records relative to A's usable capacity, rather than arbitrary elapsed idle time:

| Block | Source streams | Fixed common state | A record slots | Below / near / above closed-record targets |
|---|---:|---:|---:|---:|
| Adapter | 11 | 1,504 bytes | 465 | 162 / 418 / 790 |
| Crossbar | 21 | 2,464 bytes | 435 | 152 / 391 / 739 |

The actual trigger follows crossing that threshold and observing the perturbation. Final source runs are then flushed through the same two-slot queues. Every trace remained inside the frozen 2,048-cycle reconstruction horizon.

## Capture policies and total memory

Records encode exact unchanged-run intervals, not sampled or guessed values. A record is 32 bytes: an 8-byte timing/source/sequence header and a 24-byte packed signal payload, using the frozen schema.

All three policies reserve:

- 256 bytes of controller/header state.
- 128 bytes of monitor/obligation state.
- 64 bytes of integrity/counters.
- Per source, 32 bytes of current run state and two 32-byte ingress queue slots.

A uses its remaining capacity as a recent compressed FIFO. B reserves four 64-byte descriptors and an 8,192-byte historical read-domain store, with the remainder as a recent FIFO. C reserves four 96-byte root descriptors and four 32-byte shared nodes; each retained node costs 64 bytes including its record, ownership metadata, two dependency references, and padding. A lost read component invalidates coverage.

Every exported packed image is **exactly 16,384 bytes**. The checker verifies that each JSON-supplied record is present in that image; the interchange view cannot supply extra replay payload.

| Policy | Allocated modeled capacity | Observed peak live used bytes across cases |
|---|---:|---:|
| A | 16,384 bytes | 7,136–16,384 |
| B | 16,384 bytes | 15,584–16,384 |
| C | 16,384 bytes | 3,552–4,768 |

The difference in live use is not an ASIC efficiency result. B's fixed history reservation is charged even when mostly empty, and its recent FIFO also retains unrelated write evidence. The target read history itself was only **768 bytes on the adapter and 896 bytes on the crossbar** at 32 bytes per record. Both B and C preserve it; C adds ownership/dependency metadata. No additional budget or resized-policy experiment was run.

Ingress service was one 256-bit record per source per cycle, with two queue slots and one possible post-freeze drain cycle. Maximum queue depth was **2**; ingress drops were **0**. Capture did not drive DUT ready/valid or impose DUT backpressure. This validates the declared software service model, not physical SRAM timing or port feasibility.

## Bounded reconstruction and oracle separation

The formal models came from Yosys exports of the exact existing read modules, under the screening parameters. The full parent RTL instantiates read and write datapaths separately; write signals are not inputs to the read module. C therefore uses a conservative shared read-domain closure, with reset and a live transaction root as dependencies.

The checker:

1. Loads only the bounded evidence and frozen static model/schema.
2. Requires complete read-cone input intervals; incomplete capture is reported explicitly.
3. Symbolically evolves the exact RTL transition relation, retaining uninitialized state symbolically and applying RTL initializers/reset.
4. Requires a SAT bounded execution consistent with recorded outputs.
5. Adds an alternative valid-qualified transaction projection and requires UNSAT.
6. Constructs replay inputs only from retained evidence. Unrelated write inputs are independently set idle.

The evaluator alone reads the unrestricted raw trace. It compares accepted address/control/payload events, response identity/payload/last status, relevant valid/ready stall behavior, cycle offsets, reset, and the deterministic pending/age/stability monitor trajectory.

All **128 successful policy/case claims** were validated. There were **48 existing-RTL witness replay runs**; identical replay input plans across policies were verified by hash before reusing a replay. No replay used unrestricted oracle inputs.

All **256 stored SAT/UNSAT query artifacts** were independently re-executed using the standalone Z3 command. They had **24 distinct query contents** because functional RTL evaluation and simplification often produce identical reduced constraints; distinct trace and projection hashes remain preserved. [Independent query audit](mission1/checks/independent_z3_query_audit.json).

The largest observed per-policy checker time was **2.89 seconds**. The largest case-level checker subprocess time, including all three policies, was **6.84 seconds**. Checker processes had a 2 GiB virtual-address-space cap, a 60-second per-policy limit, and 10-second individual solver limits. Peak RSS was not separately measured. These are software verification timings, not hardware latency predictions.

## Reproducibility and scope

Source revision: **516bd5dadc3365b7f9e225d2af8fe0b8d804fe53**.

Manifest SHA-256: **d19107ff56615a569048ef21e61db411eec9c5a193457da57f3a7655a680331d**.

The [environment report](MISSION_1_ENVIRONMENT.md) gives exact rerun commands. Scripts, raw logs, raw trace containers, canonical trace hashes, bounded images, witness plans, query files, and result files are retained under mission1.

This is a small screen with one monitored read and independent legal write load. It does not establish general replay coverage, arbitrary shared-state handling, architectural novelty, or ASIC advantage. The decisive result is narrower and sufficient for the requested gate: **C never beats B on the frozen target.**
