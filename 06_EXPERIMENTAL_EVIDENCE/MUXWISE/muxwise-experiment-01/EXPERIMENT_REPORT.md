# MUXWISE Experiment 01 — Zero-Commitment EDA Feasibility and Baseline Investigation

Date: 2026-09-20  
Toolchain: Yosys 0.23 (git sha1 `7ce5011c24b`), Berkeley ABC 1.01  
Disposition: **A — BASIC IDEA ALREADY COVERED**

This is a negative-result experiment. It evaluates whether the basic mutually-exclusive add-sharing idea survives existing open-source synthesis. It does not claim that every timing-constrained sharing problem is solved by Yosys, and it does not measure physical design.

## 1. Environment and integrity

The host is Windows 11 accessed through WSL2. The active Linux environment reports WSL2 kernel `6.18.33.2-microsoft-standard-WSL2`, Python 3.14.4, Git 2.53.0, 8 logical CPUs, and 15 GiB total memory. Docker Desktop was installed and its Linux daemon was reachable through `docker.exe` version 29.8.0. Host-side Yosys, ABC, and OpenROAD were not available. Yosys and ABC were installed only inside a dedicated Debian Bookworm Docker image. The complete inventory is in `logs/environment.txt`.

The workspace is not a Git checkout, so no experiment commit hash exists. Exact commands are saved as generated Yosys scripts in `work/ys_scripts/`; each run has a log in `logs/synthesis/` and a JSON/RTLIL output in `work/flows/`. The first two setup mistakes are retained in `logs/setup_mount_failure.log`; they were corrected before collecting the 99 final synthesis runs. Final synthesis run status: 99/99 completed with return code 0.

## 2. Formal equivalence

Method: Yosys `equiv_make`, `equiv_simple`, and `equiv_status -assert` on combinational bit-vector designs. Inputs were unconstrained; no random simulation was used and no timing or environmental assumptions were added.

| Check | Result | Runtime | Evidence |
|---|---:|---:|---|
| `unshared` vs `shared`, W=16 | PASS | 0.95 s | `logs/formal_equivalent.log`, `logs/formal_equivalent.status` |
| `unshared` vs deliberately incorrect subtraction variant | FAIL as required | 0.99 s | `logs/formal_incorrect.log`, `logs/formal_incorrect.status` |

The correct proof resolved all 16 output-bit equivalence cells. The negative control proved only one trivially matching bit and left 15 unproven; `equiv_status -assert` returned nonzero. This validates the proof setup for this experiment.

## 3. Baseline synthesis evidence

The table reports `(total cells, muxes, arithmetic operators)` for unshared and shared forms. `same` is the name-independent connectivity signature, not merely equal counts.

| W | Stage | Unshared | Shared | Same structure? |
|---:|---|---:|---:|:---:|
| 8 | early RTLIL | (3, 1, 2) | (2, 1, 1) | no |
| 8 | `opt_share` | (3, 2, 1) | (2, 1, 1) | no |
| 8 | `opt_share; opt` | (2, 1, 1) | (2, 1, 1) | yes |
| 8 | normal `synth -noshare` | (48, 8, 0) | (48, 8, 0) | yes |
| 8 | normal `synth` | (48, 8, 0) | (48, 8, 0) | yes |
| 16 | early RTLIL | (3, 1, 2) | (2, 1, 1) | no |
| 16 | `opt_share` | (3, 2, 1) | (2, 1, 1) | no |
| 16 | `opt_share; opt` | (2, 1, 1) | (2, 1, 1) | yes |
| 16 | normal `synth -noshare` | (118, 16, 0) | (118, 16, 0) | yes |
| 16 | normal `synth` | (118, 16, 0) | (118, 16, 0) | yes |
| 32 | early RTLIL | (3, 1, 2) | (2, 1, 1) | no |
| 32 | `opt_share; opt` | (2, 1, 1) | (2, 1, 1) | yes |
| 32 | normal `synth` | (262, 32, 0) | (262, 32, 0) | yes |
| 64 | early RTLIL | (3, 1, 2) | (2, 1, 1) | no |
| 64 | `opt_share; opt` | (2, 1, 1) | (2, 1, 1) | yes |
| 64 | normal `synth` | (559, 64, 0) | (559, 64, 0) | yes |

At W=16, the normal mapped cell histogram is identical for both descriptions:

```text
$_ANDNOT_:27; $_AND_:1; $_MUX_:16; $_NAND_:10; $_NOR_:11;
$_NOT_:4; $_ORNOT_:2; $_OR_:16; $_XNOR_:14; $_XOR_:17
```

The saved mapped RTLIL shows the same per-bit connectivity pattern: each bit begins with a mux between `c` and `b`, followed by the same Boolean implementation using `a`. Names and source attributes differ, as expected; the structural signature and cell histogram agree. This is stronger evidence than cell-count equality alone, but it is still not a formal proof of the mapped netlists.

The hand-built `coarse_share` flow did not converge: at W=16 it left two `$alu` cells for the unshared form and one `$alu` for the shared form. The hand-built `mapped_manual` flow also differed substantially at W=16 (212 versus 114 cells). This is an important control: not every arbitrary partial flow erases the input difference. The normal Yosys flow's later fine optimization and ABC mapping do erase it for this benchmark.

## 4. Width sweep

Widths 8, 16, 32, and 64 produced the same qualitative behavior:

- Early RTLIL preserved the description difference.
- `opt_share` recognized the common-operand opportunity in the unshared form at every width.
- `opt_share; opt` converged to the shared-style two-cell structure at every width.
- Normal `synth` and normal `synth -noshare` produced the same mapped structure and cell histogram at every width.
- Counts scaled with width; the convergence decision did not change.
- Runtime varied by roughly normal container/process noise rather than showing a monotonic width-dependent decision change. Exact per-run runtimes are in `results/baseline.csv`.

No width-specific exception was observed.

## 5. Multiple-operator experiment

`rtl/multi_operator.v` contains mutually exclusive addition, subtraction, comparison, and shift opportunities, plus an additional add pair and a mix mux. It is combinational, uses explicit widths and unsigned operators, and has no keep/don't-touch constraints.

| Flow | Cells | Muxes | Arithmetic operators | Relevant types |
|---|---:|---:|---:|---|
| early | 16 | 6 | 10 | `$add:4; $sub:2; $lt:2; $shl:1; $shr:1; $mux:6` |
| `opt_share` | 16 | 10 | 6 | `$add:2; $sub:1; $lt:1; $shl:1; $shr:1; $mux:10` |
| `share` default | 16 | 6 | 10 | unchanged from early |
| `share -aggressive` | 24 | 14 | 10 | `$add:2; $sub:1; $lt:1; $eq:4; $shl:1; $shr:1; $mux:14` |
| `share -force -aggressive` | 24 | 14 | 10 | same as `-aggressive` here |
| `opt_share; opt` | 12 | 6 | 6 | `$add:2; $sub:1; $lt:1; $shl:1; $shr:1; $mux:6` |
| normal `synth -noshare` | 660 | 179 | 0 | mapped gate histogram saved in CSV |
| normal `synth` | 660 | 179 | 0 | identical to `-noshare` |

Observed pass behavior:

- `opt_share` logged four common-operand transformations: the add pair, subtract pair, compare pair, and second add pair. It reduced the operator count but introduced additional mux structure until a subsequent `opt` cleanup.
- Default `share` examined only the shift pair in this design and found no shareable candidate. Its default heuristics did not consider the smaller arithmetic resources at this point.
- `share -aggressive` and `share -force -aggressive` considered 10 cells, used SAT to prove candidate sharing for arithmetic/compare pairs, removed eight operator cells, and added control logic. The resulting intermediate netlist had more total cells and muxes than the early form. This is a real surviving intermediate sharing choice, but it is not evidence of a useful area/timing trade-off.
- The normal `synth` flow invokes SAT-based `share` after `alumacc`, then runs repeated `opt_share` passes later. `synth -noshare` suppresses the SAT-based `share` pass but still runs the later `opt_share` steps. In this design, both paths reached the same mapped result.

## 6. Yosys behavior prosecution

Observed in Yosys 0.23, corroborated by help output and logs:

1. `opt_share` identifies mutually exclusive same-type cells that share an operand and drive the same mux. It moves the mux to the non-shared inputs, creating one merged operator. It does not, by itself, guarantee cleanup of the redundant outer mux in this exact invocation.
2. `share` is SAT-based resource sharing. Its default candidate selection is narrowed by cell types and heuristics; `-aggressive` disables a size heuristic, `-force` considers all selected cells, `-fast` limits control reasoning, and `-limit N` bounds merges. In this experiment `-force` did not change the `-aggressive` result.
3. The documented normal `synth` coarse flow includes `alumacc`, `share`, `opt`, memory handling, and later fine optimization. The fine flow includes repeated `opt_share` and ABC technology mapping. `-noshare` removes SAT-based resource sharing but does not remove every later optimization pass.
4. The exact transformed result depends on the flow context. A bare `opt_share`, a bare `share`, a normal synthesis, and a manually assembled partial flow are observably different. Therefore the conclusion is not “every Yosys flow always produces the same netlist”; it is that the standard flow already covers this basic sharing problem and the tested differences do not survive it.

## 7. Physical-design pilot

**NOT EXECUTED — ENVIRONMENT LIMITATION.** OpenROAD was not available on the host or in an already accessible compatible environment. No Nangate45 installation was performed. Consequently there are no measured standard-cell area, routed delay, or select-arrival sensitivity results. Mapped gate counts are not reported as physical area, and no synthesis estimate is called routed timing.

## 8. Exact questions

**Q1. Did the shared and unshared designs prove equivalent?** Yes. Yosys proved all 16 output bits equivalent under unconstrained combinational inputs.

**Q2. Did the deliberately incorrect design fail the equivalence check?** Yes. `equiv_status -assert` failed; 15 of 16 output-bit equivalences remained unproven.

**Q3. Does Yosys automatically perform our proposed basic resource-sharing transformation?** Yes. `opt_share` recognizes the exact common-operand transformation. The normal `synth` flow also performs related sharing/optimization passes automatically.

**Q4. At what synthesis stage do the two descriptions converge?** In the diagnostic flow, after `opt_share; opt`. In the normal flow, they converge at the final ABC-mapped netlist; the normal flow also converges with `synth -noshare` for this benchmark.

**Q5. Do different bit widths change this behavior?** No for W=8, 16, 32, and 64. Counts and runtimes scale, but sharing recognition and convergence do not change.

**Q6. Are there real cases in the multiple-operator experiment where sharing choices remain?** Yes, at intermediate RTLIL stages. `opt_share` shares add/subtract/compare pairs, and aggressive SAT-based `share` creates a different control-heavy shared structure. These are genuine observed choices, not keep/don't-touch artifacts.

**Q7. Does technology mapping eliminate those differences?** In the normal Yosys+ABC flow, yes for both baseline descriptions and for the multi-operator design: normal and `-noshare` produced the same mapped histograms/signatures. A manually truncated coarse→techmap→ABC flow did not converge, so the evidence points to the complete normal flow, not ABC in isolation.

**Q8. What does `opt_share` already accomplish?** It merges mutually exclusive same-type operators that share an operand and move the controlling mux onto the other inputs. It handled all four compatible pairs in the multi-operator example.

**Q9. What does `share` already accomplish?** It uses SAT-derived mutual exclusivity/control reasoning to merge shareable resources, with documented `-force`, `-aggressive`, `-fast`, and `-limit` controls. In the multi-operator experiment, aggressive mode found several arithmetic/compare sharing candidates but added mux/equality control overhead.

**Q10. Did we find evidence of a useful optimization decision that a future algorithm could control?** No. We found controllable intermediate structures, but no measured timing/area benefit and no final mapped difference under the normal flow. H3 is not proven.

**Q11. What evidence is still missing?** Physical implementation with a fixed standard-cell library and constraints; routed area and timing; select-arrival sensitivity; larger sequential/datapath benchmarks; and comparisons against timing-aware baseline flows. These omissions prevent a claim about physical trade-offs.

**Q12. What is the strongest reason NOT to build MUXWISE?** The core transformation is already recognized by Yosys, and complete normal synthesis plus ABC erased the tested representation differences—even when SAT-based `share` was disabled. A new project would risk reimplementing existing behavior without a demonstrated residual timing/area opportunity.

## 9. Final disposition

**A. BASIC IDEA ALREADY COVERED.** The experiment is sufficient to reject the basic “rewrite two mutually exclusive adds into one shared add” idea as a standalone research opportunity in this scope. The result does not prove that no timing-aware or physical-design-specific extension could matter; it says that such an extension needs a stronger, benchmark-backed hypothesis before implementation work is justified.

