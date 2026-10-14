# Research Gate 2 — Adversarial Architecture Discovery

**Decision: NO-GO for hardware development.** The project’s current decision-sufficient interval engine is a useful correctness mechanism, but the evidence does not support an ASIC contribution with a defensible advantage. The Gate 1 toy benefit is measured in synthetic query-cost units, not energy, and the exact-computation principle has substantial prior art in neural accelerators and software. A programmable decision device also faces established decision-tree and decision-diagram hardware, plus the ability to compile the small reference model to ordinary software or logic. No candidate survived the novelty and advantage screen strongly enough to justify RTL or fabrication work.

This is a gate on developing this hardware direction, not a claim that the algorithm is useless. A narrowly scoped, data-only experiment could still determine whether sensor query avoidance helps one real workload. Reopen the hardware question only if that experiment demonstrates an end-to-end advantage over strong software and sensor-policy baselines that cannot be explained by ordinary MCU/FPGA implementation.

## Scope and evidence

Reviewed Gate 1 report and prior-art notes, every project Python implementation and test, reran baseline tests and scripts, then inspected the isolated Gate 2 reference audit and tests. Reviewed available full methods for ConvReLU++, the Greiner et al. cost-sensitive active feature acquisition paper, Ji and Carin’s cost-sensitive sequential acquisition paper, SnaPEA, and the quaternary decision-diagram machine. Sayadi et al. (2026) was available as an article preview with abstract and section snippets; the publisher denied full-text access in this review. The distinction is material: Sayadi’s exact termination claim is clear from the available abstract/preview, but its detailed implementation and evaluation setup have not been independently audited from full text.

The project supplies no PAMAP2 experiment, physical sensor/host energy measurement, synthesis results, area/timing estimates, or chip comparison. Gate 1’s reported synthetic results were reproduced exactly. Its adaptive decision-tree “oracle” uses a known synthetic input distribution and is not an implementable universal policy or a hardware baseline.

## Findings

1. **The original general claim is not novel.** Gate 1’s “decision-sufficient” rule is an interval certificate for a fixed affine classifier under declared feature domains. Bound-based early stopping, exact threshold termination, active feature acquisition, and hardware decision structures all have substantial prior art. Sayadi et al. directly disclose exact activation-deterministic termination inside binary/ternary CNN accelerator MACs and report FPGA/ASIC power results. ConvReLU++ gives a different but close exact bound-and-skip example, with proof and mobile CPU implementation. These do not prove the exact sensor-acquisition controller is identical, but they defeat a broad claim to novel exact early termination or certificate-driven compute skipping.
2. **The practical advantage is unestablished.** Gate 1’s 46.6–51.4% savings are synthetic query weights on eight binary features. They are not joules, real sensor costs, latency, or real-label accuracy. An uncertainty interval can also increase controller work and still cause abstention. We have no evidence of net benefit after sensing startup, communication, idle power, feature extraction, host/software overhead, and accelerator idle/leakage.
3. **The correctness contract is conditional.** Exact agreement is with a fixed mathematical model only when all feature values lie within declared bounds, arithmetic does not overflow, the model/configuration is valid, and every response is correctly associated with its request. A skipped sensor cannot be checked for range compliance. It cannot certify real-world labels, model calibration, sensor faults, distribution shift, or clinical/safety correctness.
4. **Reference-model defects were real but repairable.** The old engine abstained immediately when its highest-ranked next feature exceeded remaining budget, even when a cheaper policy-ranked alternative remained affordable. That behavior conflated budget exhaustion with policy refusal. It also did not exercise missing, reordered, or duplicated responses as a sensor protocol. The Gate 2 isolated reference implementation and tests now distinguish these cases, enforce accounting and response order, and add range-assumption and integer-boundary counterexamples. These are software-model improvements, not an architectural breakthrough.
5. **Distinct mechanisms do not currently rescue the case.** A proof-carrying query ISA overlaps with formal accelerator interfaces and proof-carrying hardware. A symbolic decision-graph processor overlaps with decision-tree and BDD/QDD machines, and could be emitted as conventional logic. An adaptive sensor controller overlaps with resource-cost-aware feature selection and sensor-interface work. We found no quantified gap that demands a new chip.

## Reproduction

From the project directory, these completed successfully:

- `python3 -m unittest -v test_engine test_candidate` — 11 tests passed.
- `python3 experiment.py` — 256 synthetic binary inputs, fixed order 46.6% synthetic query cost saved, cheapest-first 47.6%, impact/cost 51.4%; zero disagreements against the full model.
- `python3 compare_architectures.py` — 51.0% range/cost, 56.6% adaptive exact tree oracle, and 0 mismatch for all compared methods. The oracle has 6,395 memoized nodes and uses the known toy distribution.
- `cd gate2_reference && python3 -m unittest -v test_candidate` — 11 isolated Gate 2 audit tests passed.

No tests were added to or substituted for the original baseline files; Gate 2 changes are in `gate2_reference/`.

## Candidate disposition

The three candidates and their detailed contracts and falsification experiments are in [ARCHITECTURE_CANDIDATES.md](ARCHITECTURE_CANDIDATES.md). The reference audit is in [REFERENCE_MODEL_AUDIT.md](REFERENCE_MODEL_AUDIT.md), the claim-level comparison in [PRIOR_ART_CLAIM_MATRIX.md](PRIOR_ART_CLAIM_MATRIX.md), and a bounded follow-up protocol in [NEXT_EXPERIMENT_SPEC.md](NEXT_EXPERIMENT_SPEC.md).

**Gate outcome: NO-GO.** Do not begin RTL, physical design, component purchases, or fabrication. The only justified continuation is a reproducible data-only falsification study if the team still wants to test the real-sensor use case. Failure to beat strong software and sensor-policy baselines should close this direction; success would support a fresh research gate, not retroactively establish novelty.
