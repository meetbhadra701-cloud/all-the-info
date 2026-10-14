# Mission 1 — Stage 0 decision

Completed **2026-10-12, America/Los_Angeles**.

## NO-GO

The software falsification experiment was executed, not replaced by literature work. Both supplied unmodified RTL testbench selections passed, and all **48 frozen screening traces** were produced on the existing AXI crossbar and width adapter.

| Capture policy | Validated bounded reconstructions |
|---|---:|
| A: losslessly compressed triggered FIFO | 32 / 48 |
| B: FIFO plus pinned descriptors and history | 48 / 48 |
| C: closure-aware transaction evidence | 48 / 48 |

**C reconstructed zero correct projections missed by B.** The stated Stage 0 stopping rule therefore rejects this retention implementation. CausalTrace gains nothing in target reconstruction coverage over the conventional pinned-table hybrid at the same 16 KiB allocation.

There were **zero false certificates**, **zero ingress drops**, and **zero main-screen solver timeouts or model mismatches**. Successful results required SAT existence, UNSAT alternative projection, replay on the existing full RTL, and agreement with the separate unrestricted oracle. All 256 saved query artifacts were independently rerun.

This is **not HOLD**: initial compatibility failures were resolved using local tools and preserved in the failure report. The final environment and checker completed the requested screen.

## Why it failed the gate

The entire protected read history was small: 768 bytes on the adapter and 896 bytes on the crossbar in the common record format. A recent FIFO overwrote that history under sufficient unrelated traffic. Both B and C preserved it.

Closure ownership and shared dependency references did not create information that the conventional historical store lacked. Their added metadata earned no extra successful reconstruction. Lower live use than B's fixed history-plus-recent reservation is not an area/energy result, especially because B also preserves unrelated traffic.

## Scope of the rejection

The frozen test used one live stalled read, legitimate background writes, and Python-driven invalid held-response changes. Those perturbations are not RTL bugs. The checker models the exact separately instantiated read RTL and conservatively requires complete input-cone intervals.

This rejects the tested implementation and the justification for advancing it. It is not a theorem that all debug architectures are useless or that missing evidence can never be inferred by a stronger checker.

The experiment provides no architectural novelty finding, measured ASIC advantage, or authorization for fabrication. Mission 0's ASIC NO-GO remains in force.

## Deliverables and stopping point

- [MISSION_1_ENVIRONMENT.md](MISSION_1_ENVIRONMENT.md): tools, compatibility, source pinning, and exact rerun instructions.
- [MISSION_1_FROZEN_MANIFEST.json](MISSION_1_FROZEN_MANIFEST.json): immutable pre-screen configuration and checksums.
- [MISSION_1_RESULTS.md](MISSION_1_RESULTS.md): counts, correctness evidence, budgets, workload, and limitations.
- [MISSION_1_FAILURES.md](MISSION_1_FAILURES.md): failed attempts, negative controls, and remaining limits.
- [Machine-readable summary](mission1/results/summary.json) and [48-case CSV](mission1/results/results.csv).

Scripts, logs, raw traces, bounded images, replay witnesses, and query files are preserved under mission1. No monitor RTL was authored, equipment purchased, researcher contacted, or physical design started. **Stage 1 and held-out experiments were not launched.**

**Final outcome: NO-GO.**
