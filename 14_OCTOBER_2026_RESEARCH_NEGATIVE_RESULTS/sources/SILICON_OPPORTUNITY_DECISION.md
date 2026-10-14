# Silicon opportunity decision

**INSUFFICIENT EVIDENCE: Further profiling is necessary before an architectural opportunity can be established.**

This decision withholds silicon-design advancement. The experiments locate real software hotspots and demonstrate strong conventional alternatives, but do not establish the physical resource causing a persistent residual bottleneck. They do not prove that SAT, synthesis or processor verification workloads are efficiently served by today's CPUs. A positive opportunity requires a persistent residual against conventional alternatives, a measured limiting resource and credible dataflow/scaling evidence; that combination was not established here.

## Findings that drive the decision

1. **SAT verification has real hotspots, but solver choice matters more than a single hotspot fraction.** Kissat spends about half its sampled user CPU time in watched-literal propagation on gm28. MiniSAT solves the same published UNSAT input in 0.783 median wall seconds versus 10.739. CPU medians are 0.510 versus 10.040. BMC profiles show different operation mixes and preprocessing effects. A propagation-engine hypothesis was examined and rejected for advancement on this evidence.
2. **RTL simulation admits a strong conventional implementation change.** At 1000 iterations, median Icarus wall/CPU times are 31.706/29.590 seconds; tuned Verilator is 2.326/0.510. Observed firmware counters/check values match. This comparison applies to initialized Dhrystone on one small real core, not all four-state verification. Two-worker simulation is slower and consumes more CPU in this case.
3. **Mapping exposes cut work, with existing algorithmic and GPU alternatives still open.** Hypotenuse defaults to 3.580 CPU seconds and 44,508 LUTs; four retained cuts use 1.660 CPU seconds and 45,293 LUTs at the same depth. That is a quality tradeoff, not a free speedup. Prior GPU mapping addresses this kernel; no matched local GPU comparison was possible.

## What was completed and what is uncertain

- Three substantial public workload families executed; 13 industrial SAT instances screened; four BMC and three modern same-architecture multiplier sizes repeatedly compared; six arithmetic graphs mapped; original processor RTL ran three firmware lengths.
- **126 final native runs**, 42 case/configuration combinations, three successful repetitions each. Models/output, commands, version/flag/hash records, native samples, instrumented profiles, failures and generated artifacts are retained.
- The correctness ledger records 103 run checks, combining independent SAT-model and firmware checks with solver-status agreement checks. UNSAT results agree across solvers and published labels; independently checked UNSAT proofs were not generated. Mapping equivalence confirmed for 10 of 12 case/variant outputs; individual transcripts report any unconfirmed result.
- Hardware perf events are unsupported under this WSL guest. Actual DRAM bandwidth, hardware pipeline stalls/IPC, energy and residual SIMD/GPU efficiency remain unmeasured. Cache/branch-model values are explicitly estimates. The current desktop was not isolated; ranges expose timing variability.
- Two Callgrind runs, modern 24-bit SAT and ABC hypotenuse, hit their 360-second limits; partial traces are preserved. Both hypotenuse mapping-equivalence checks hit their 180-second limits and remain unconfirmed. All selected native baselines completed. Historical EPFL LUT scores and published PicoRV32 DMIPS/CPI were not reproduced exactly. Divisor mapping produces 22,030 LUTs versus the published 9,311; a packaged ABC comparator and three input-format/normalization diagnostics reproduce our result, leaving the cause unresolved. The documented recipes/configuration and all discrepancies are reported.

The measured changes reject advancement of the propagation-only and interpreted-simulation candidates on the corresponding inputs. The absent physical counters, partial largest-case profiles, unconfirmed largest-graph equivalence and unmeasured matched-quality GPU alternatives also prevent a confident general NO-GO conclusion. This mission therefore ends with insufficient evidence, rather than converting software hotspots into an ASIC opportunity or treating limited coverage as proof that none exists.

## Smallest useful next investigation

First finish complete physical-resource profiles of the fastest conventional baselines, rather than only the slower solver/interpreter: same-input MiniSAT/Kissat and ABC on an already accessible native machine with working PMU events, including cache/branch/stall and traffic evidence. Resolve the largest mapping-equivalence checks and compare a quality-matched GPU mapper if an existing compute runtime is accessible. Only then broaden to larger current industrial CNFs and real large processor/SoC verification inputs; quantify mutable-state transfers and proof/simulation semantics. Show that a stable residual operation remains important after alternatives. These are profiling experiments, not a request to purchase hardware. No RTL, physical design, equipment purchase or fabrication is authorized by this report.

## Reports and reproduction

| Artifact | Purpose |
| --- | --- |
| [REAL_WORKLOAD_INVENTORY.md](</mnt/c/Users/meetb/Documents/ChatGPT/idea new strat/REAL_WORKLOAD_INVENTORY.md>) | Real inputs, source provenance, sizes and scope |
| [REPRODUCIBLE_BASELINES.md](</mnt/c/Users/meetb/Documents/ChatGPT/idea new strat/REPRODUCIBLE_BASELINES.md>) | Machine, compiler, flags, hashes, recipes and blockers |
| [PERFORMANCE_PROFILES.md](</mnt/c/Users/meetb/Documents/ChatGPT/idea new strat/PERFORMANCE_PROFILES.md>) | Native times/hotspots, instruction/access traces and model limits |
| [HARDWARE_BOTTLENECK_ANALYSIS.md](</mnt/c/Users/meetb/Documents/ChatGPT/idea new strat/HARDWARE_BOTTLENECK_ANALYSIS.md>) | Exact operations and rejected propagation hypothesis |
| [CONVENTIONAL_ALTERNATIVES.md](</mnt/c/Users/meetb/Documents/ChatGPT/idea new strat/CONVENTIONAL_ALTERNATIVES.md>) | Measured comparisons and primary research |

Raw evidence index: [raw/commands.jsonl](</mnt/c/Users/meetb/Documents/ChatGPT/idea new strat/raw/commands.jsonl>). Summary: [results/native_summary.csv](</mnt/c/Users/meetb/Documents/ChatGPT/idea new strat/results/native_summary.csv>). Full results: [results/run_metrics.json](</mnt/c/Users/meetb/Documents/ChatGPT/idea new strat/results/run_metrics.json>). Failure ledger: [raw/build/MANUAL_FAILURES.md](</mnt/c/Users/meetb/Documents/ChatGPT/idea new strat/raw/build/MANUAL_FAILURES.md>). Reproduction: [scripts/reproduce.sh](</mnt/c/Users/meetb/Documents/ChatGPT/idea new strat/scripts/reproduce.sh>). Input hashes: [results/input_hashes.sha256](</mnt/c/Users/meetb/Documents/ChatGPT/idea new strat/results/input_hashes.sha256>).

**INSUFFICIENT EVIDENCE.** No custom silicon architecture advances from the measured evidence.
