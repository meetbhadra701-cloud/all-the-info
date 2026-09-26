# MUXWISE Experiment 3 — Physical-Design Prosecution of F-AT-01

Date: 2026-09-21  
Disposition: **E — INCONCLUSIVE** for a research-grade conclusion.

The physical pilot itself completed through placement and global routing for three representative designs. It found no timing benefit from `-arith_tree`; however, the required equivalence validation was not complete, and one arithmetic-tree formal check produced a real counterexample. Therefore these physical measurements are reported as conditional implementation evidence, not as a validated optimization opportunity.

## Scope and exact inputs

The RTL was copied without modification from Experiment 2:

- `reproducers/fir4.v`, top `fir4`, W=8 and W=16.
- `reproducers/mixed_arith.v`, top `mixed_left`, W=16 and W=32.
- `reproducers/add_chain.v`, top `add_chain`, W=16 and W=64.

The final comparison variable was the Yosys arithmetic-tree option. The controlled mapping script used:

```text
read_verilog -sv <RTL>
hierarchy -top TOP
chparam -set W WIDTH TOP
synth -top TOP -noabc                  # normal
synth -top TOP -noabc -arith_tree      # arithmetic-tree
write_verilog <premap netlist>
abc -liberty NangateOpenCellLibrary_typical.lib -script scripts/abc_seeded.script
write_verilog <mapped netlist>
```

The explicit `-noabc` boundary prevents an earlier generic ABC mapping before the target Liberty mapping. The ABC script is the Yosys Liberty default script with `set random_seed 1` added. Two complete seeded mapping runs matched exactly for all 12 rows. An earlier unseeded repeat changed results, including the direction of the add-chain W64 area difference; that repeatability issue is retained in `logs/` and is itself an experimental limitation.

## Environment

| Item | Observed value |
|---|---|
| Host | Windows 11 with WSL2 shell |
| CPU/RAM | Intel Core Ultra 7 258V, 8 CPUs, approximately 15 GiB RAM visible |
| Docker | Docker Desktop 4.91.0, Engine 29.8.0; daemon responded successfully |
| Yosys/ABC for controlled mapping | Yosys 0.69+77, git `9ff27d29c-dirty`; ABC 1.01 compiled 2026-09-21 |
| Liberty/LEF | ORFS Nangate45 `NangateOpenCellLibrary_typical.lib` and matching LEF |
| ORFS source | `3a964e13f11a4e435aac01ffa14db0a7d2853720` |
| OpenROAD image | `openroad/orfs:latest`, digest `sha256:573c1716efa0e286c4f641c26d343e20929d58d27fffbb22be2d0b93f09764f6`; embedded OpenROAD reported `unknown` version |

The official ORFS Docker-shell workflow and Nangate45 tutorial were used as compatibility references: <https://openroad-flow-scripts.readthedocs.io/en/latest/user/DockerShell.html> and <https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts/blob/master/docs/tutorials/FlowTutorial.md>.

## Standard-cell mapping

Area is Liberty cell area in µm², not generic gate count. Percent change is `(arith_tree - normal) / normal * 100`.

| Design | W | Normal area | Tree area | Δ area | Normal cells | Tree cells |
|---|---:|---:|---:|---:|---:|---:|
| add_chain | 16 | 621.642 | 625.898 | +0.685% | 536 | 536 |
| add_chain | 64 | 2583.658 | 2574.348 | -0.360% | 2273 | 2246 |
| fir4 | 8 | 323.722 | 399.532 | +23.418% | 271 | 345 |
| fir4 | 16 | 609.672 | 827.792 | +35.777% | 529 | 717 |
| mixed_left | 16 | 443.422 | 498.750 | +12.478% | 375 | 439 |
| mixed_left | 32 | 906.262 | 1028.090 | +13.443% | 775 | 915 |

## Liberty STA under final constraints

The measured preliminary maximum mapped delay was used to choose 10 ns relaxed and 1.5 ns aggressive virtual-clock periods. Input and output delays were both 0.1 ns. The table below shows the aggressive 1.5 ns result; the complete 36-row table, including preliminary and relaxed runs, is in `results/timing_comparison.csv`.

| Design | W | Normal delay ns | Tree delay ns | Δ delay | Normal WNS ns | Tree WNS ns |
|---|---:|---:|---:|---:|---:|---:|
| add_chain | 16 | 1.1127 | 1.0744 | -3.442% | 0.2873 | 0.3256 |
| add_chain | 64 | 2.4382 | 2.4302 | -0.328% | -1.0382 | -1.0302 |
| fir4 | 8 | 1.0328 | 0.9760 | -5.500% | 0.3672 | 0.4240 |
| fir4 | 16 | 1.2442 | 1.3367 | +7.434% | 0.1558 | 0.0633 |
| mixed_left | 16 | 0.9635 | 1.0670 | +10.742% | 0.4365 | 0.3330 |
| mixed_left | 32 | 1.4813 | 1.5604 | +5.340% | -0.0813 | -0.1604 |

The tree configuration improved standalone mapped delay for add-chain and FIR4 W8, but its area-delay product still increased for FIR4 W8 because the area increase dominated. It worsened both area and delay for FIR4 W16 and both mixed cases. These are synthesis/STA results, not routed timing.

## Placement and global-route pilot

The bounded physical pilot used the same Liberty/LEF, floorplan utilization 20%, core margin 10, pin layers metal5/metal6, global-placement density 0.20, Nangate45 RC settings, 1.5 ns virtual clock, and global routing. It covered FIR4 W16, mixed W32, and add-chain W64.

| Design | W | Normal placed area | Tree placed area | Δ area | Normal global-route delay | Tree global-route delay | Normal WNS | Tree WNS | Wirelength normal/tree µm |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fir4 | 16 | 611 | 833 | +36.334% | 1.3554 | 1.4207 | +0.0446 | -0.0207 | 6703.2 / 8544.3 |
| mixed_left | 32 | 937 | 1087 | +16.009% | 1.4749 | 1.5839 | -0.0749 | -0.1839 | 15840.3 / 17752.65 |
| add_chain | 64 | 3099 | 3060 | -1.258% | 2.3816 | 2.4668 | -0.9816 | -1.0668 | 55985.4 / 57575.7 |

No detailed routing, CTS, or routed-signoff timing was executed. The global-route values above must not be called routed timing. The full logs are in `logs/physical/`; the machine-readable table is `results/physical_design.csv`.

Observed physical pattern: arithmetic-tree was physically larger and slower for FIR4 W16 and mixed W32. For add-chain W64 it was slightly smaller but slower, with worse slack. This is a measured area/timing trade-off in one pilot pair, not evidence of a new algorithmic gap.

## Formal-validation audit

This experiment found an integrity problem in the inherited formal interpretation. A Yosys process exit code of zero is not sufficient to classify `sat` as PASS. The log must contain `SAT proof finished - no model found: SUCCESS!`; `SAT proof finished - model found: FAIL!` is a counterexample.

The inherited Experiment 2 log for `fir4_arith_tree_mapped_vs_rtl_w4` contains `model found: FAIL`, although the earlier manifest called it PASS. The Exp3 audit therefore does not repeat that PASS claim.

Exp3 direct proof evidence:

| Check | Result | Evidence |
|---|---|---|
| FIR4 W4 arithmetic-tree control | FAIL, counterexample | `logs/formal/fir4_w4_default_arith_tree.log` |
| FIR4 W8 normal synthesized configuration | PASS, 51.85 s | `logs/formal/fir4_w8_normal.log` |
| FIR4 W8 arithmetic-tree configuration | FAIL, counterexample | `logs/formal/fir4_w8_arith_tree.log` |
| FIR4 W16 normal | INCONCLUSIVE, interrupted during SAT | `logs/formal/fir4_w16_normal.log` |
| Remaining priority widths/configurations | NOT COMPLETED | `results/formal_comparison.csv` |

Thus the physical results are not equivalence-qualified for the full priority set. In particular, an arithmetic-tree implementation that fails formal equivalence cannot be treated as a legitimate alternative implementation without first determining whether the failure is a signed-width/tool-flow defect.

## Answers to the required questions

1. **Did standard-cell mapping preserve the Experiment 2 differences?** Yes. All six final pairs differed in Liberty area and/or cell distribution; differences were not merely generic cell counts.
2. **Was arithmetic-tree physically larger, smaller, faster, or slower?** Larger and slower in the FIR4 W16 and mixed W32 physical pilot. Slightly smaller but slower for add-chain W64.
3. **Did preference vary by family?** Yes, conditionally. The area direction differed for add-chain W64, but the tree was not faster after global routing in any physical pilot pair.
4. **Did timing constraints change the preferred implementation?** The 1.5 ns target exposed small slack differences and additional failures, but did not make arithmetic-tree the timing-feasible choice in any physical pair.
5. **Were configurations Pareto-dominated?** Yes: tree was area- and delay-dominated in the two larger physical pairs. Add-chain W64 was a small area-versus-delay trade-off, with both configurations missing the aggressive target.
6. **Did physical optimization erase the structural difference?** No. Placement/global routing preserved area, timing, slack, and wirelength differences.
7. **Most consequential result:** FIR4 W16 tree area increased 36.334% and global-route delay increased 4.818%, moving WNS from +0.0446 ns to -0.0207 ns.
8. **Strongest reason this is not a novel research opportunity:** the behavior is an existing Yosys `-arith_tree` configuration choice, while the arithmetic-tree alternatives used here are not fully formally validated; the strongest observed physical result is either dominated or a small, unvalidated trade-off.
9. **Does this justify an adaptive synthesis-selection algorithm?** No. The evidence is insufficient because equivalence failed/incomplete and only three pairs reached global routing.
10. **Exact next technical question:** Can current Yosys produce a formally equivalent, deterministic arithmetic-tree implementation for the signed/truncated FIR and mixed-width cases, and—after that proof succeeds—does the area/timing trade-off reproduce across repeated full place-route runs?

## Research gate

**E — INCONCLUSIVE.** This is not a recommendation to build MUXWISE. The physical pilot is a useful negative result: `-arith_tree` did not produce a validated timing advantage, and its clearest physical effects were area increases or a small area reduction coupled to worse timing. The formal counterexample and inherited PASS-labeling defect must be resolved before promoting F-AT-01 to a research opportunity.

## Reproduction and artifact index

- Mapping: `scripts/run_mapping.sh`; logs in `logs/mapping/`; netlists in `netlists/` and `netlists/premap/`.
- STA: `scripts/run_openroad_sta.sh`; constraints in `constraints/`; logs in `logs/sta/`.
- Physical pilot: `scripts/run_physical_pilot.sh`; logs and DEF/route artifacts in `logs/physical/` and `work/physical/`.
- Formal audit: `scripts/audit_formal_results.py`; evidence in `logs/formal/`.
- Results: `results/standard_cell_mapping.csv`, `results/timing_comparison.csv`, `results/physical_design.csv`, `results/formal_comparison.csv`.
