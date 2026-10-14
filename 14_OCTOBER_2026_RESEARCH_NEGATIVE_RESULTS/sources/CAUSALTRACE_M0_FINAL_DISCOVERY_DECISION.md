# Silicon Discovery Lab — Mission 0: final decision

Research date: **2026-10-11, America/Los_Angeles**.

## Decision

**NO-GO for ASIC development. Retain one narrowly defined CausalTrace experiment; reject the other five current architecture proposals.**

This mission has not established a new architecture with a compelling measured advantage. No benchmark, synthesis, FPGA, energy, or area result was produced. The surviving question is a research opportunity, not a chip recommendation or a novelty finding.

The previous Decision-Sufficient Silicon rejection remains in force. It was not resurrected.

## What survived

**H1: closure-aware retention of aged transaction evidence.** The possible improvement is higher coverage of uniquely reconstructible observed transaction failures under the same total storage, observation access, and ingress service capacity as conventional debug hardware.

The proposed difference is a transaction-owned evidence store that tracks shared replay dependencies and invalidates incomplete components, allowing old live-obligation evidence to outlast a recent-event ring. The strongest falsifier is a **pinned request/state table plus a compressed, age-partitioned trace FIFO**. If that conventional hybrid matches the result, the architecture is NO-GO.

An offline uniqueness check must establish that reconstructed evidence corresponds to the observed bounded transaction projection. Merely finding a plausible failure trace does not count.

The experiment has a 48-trace screening step using existing open RTL, followed only conditionally by a held-out comparison. Its frozen advancement target is at least a 15-percentage-point coverage gain on each of two RTL blocks at 16 KiB, with zero false certificates and additional resource/robustness requirements. These are chosen falsification thresholds, **not predicted results**.

Novelty confidence remains low: the closest transaction-pattern and NoC debug full papers were not successfully retrieved, and patent-family questions remain open. Success cannot establish novelty without resolving those comparisons.

## What was rejected

| Hypothesis | Current verdict | Decisive reason |
|---|---|---|
| H1 broad CausalTrace | **NO-GO as a novelty claim** | Hardware monitors, selective tracing, formal reconstruction, replay determinants, and short counterexamples already exist |
| H1 specific retention structure | **EXPERIMENT-ONLY** | Identifiable structure and cheap falsifier; benefit, physical feasibility, and novelty unresolved |
| H2 hint-directed proof-memory engine | **NO-GO** | LRAT hints, FPGA proof checking, and streaming checking already supply the core mechanisms; no useful distinct cache/dataflow contribution established |
| H3 paired syndrome reconciliation | **NO-GO** | IBLT, FlowRadar, and LossRadar already implement the proposed coding-to-telemetry mechanism |
| H4 keyed exact reduction | **NO-GO** | Specialized accumulators and optimized grouped numerical software are established; no distinct traffic/capacity mechanism or end-to-end advantage demonstrated |
| H5 factor-DAG mutation | **NO-GO** | Provenance/factorized incremental methods are mature; the proposed hardware mapping supplies no defensible improvement beyond banking/fusion |
| H6 sparse numerical recovery sidecar | **NO-GO** | ABFT and sparse hardware checksum circuitry already provide the mechanism; no new code, routing, or fault contract supplied |

These are decisions about the proposed claims. They do not imply the underlying technologies are useless or that all future architectures in those fields are exhausted.

## What was learned

Eight fields were investigated, including semiconductor architecture and seven fields outside semiconductor implementation. The strongest cross-domain connections were often already realized in older work or current software. That is a useful negative discovery.

The remaining hardware opportunity is about **preserving otherwise lost information at an internal observation boundary**. Its difficulty is equally concrete: dependencies, snapshots, ordering, and queue state can consume the entire budget. No model-free “minimum debugging evidence” exists.

Arithmetic and graph accelerators face a different obstacle: existing software can use the same representation, and memory movement or entire-workflow overhead can dominate. A new label, a stronger output contract, or moving a known algorithm into gates is insufficient.

## Next action and stopping rules

The next justified action is the software retention screen specified in the experiment report, using existing RTL and software models. No new RTL is part of that screen. Tool installation/compatibility is a prerequisite: the required simulators and formal tools were not on the local PATH during this mission.

Stop the current H1 architecture if the hybrid baseline matches, if full accounting erases the gain, if common shared-state coupling defeats bounded retention, or if a certificate is false. A tooling or literature-access blocker remains a named HOLD, not evidence of success.

Only a fresh research gate after positive evidence could justify monitor RTL, FPGA measurements, or ASIC analysis. Fabrication is conditional on a useful advantage across designs; a working chip alone would fail this mission.

## Deliverables

1. [DISCOVERY_LITERATURE_MAP.md](DISCOVERY_LITERATURE_MAP.md) — primary sources, eight-field coverage, access levels, patents, unsuccessful assumptions, and search gaps.
2. [CROSS_DOMAIN_CONNECTIONS.md](CROSS_DOMAIN_CONNECTIONS.md) — mechanistic bridges, transferable assumptions, and disconfirmation.
3. [SIX_ARCHITECTURE_HYPOTHESES.md](SIX_ARCHITECTURE_HYPOTHESES.md) — ten required specifications for each candidate and detailed CausalTrace analysis.
4. [CLAIM_TO_PRIOR_ART.md](CLAIM_TO_PRIOR_ART.md) — adversarial claim matrix, verdicts, strongest attacks, and unresolved patent questions.
5. [TOP_CANDIDATE_EXPERIMENTS.md](TOP_CANDIDATE_EXPERIMENTS.md) — one provisional experiment, strongest baselines, correctness oracle, physical models, thresholds, and conditional development path.
6. [FINAL_DISCOVERY_DECISION.md](FINAL_DISCOVERY_DECISION.md) — this decision.

No researchers were contacted, equipment purchased, or fabrication initiated. No new RTL was written.
