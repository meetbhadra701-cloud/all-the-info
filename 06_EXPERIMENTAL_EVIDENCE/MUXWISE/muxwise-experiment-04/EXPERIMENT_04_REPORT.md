# Experiment 4 — Yosys arith_tree formal counterexample prosecution

## Executive result

The Experiment 2 reporting error was confirmed. Its manifest treated
Yosys process exit code zero as proof success; Yosys can return zero after
printing a SAT counterexample. The FIR4 arithmetic-tree failure is not
explained by that bookkeeping error or by the original miter alone.

An independent explicit output-comparison miter, direct RTLIL snapshots,
Icarus replay, and an independent fixed-width reference model all agree:

- normal synthesis is equivalent to the original FIR4;
- default arith_tree synthesis is not equivalent;
- the first divergence is immediately after arith_tree;
- techmap and ABC preserve, rather than create, the mismatch;
- arith_tree -no-fma passes at W=4 and W=8;
- compressor and final-adder options do not repair the default failure
  unless -no-fma is also used.

Disposition: **C — GENUINE SYNTHESIS DEFECT CONFIRMED**, qualified by the
dirty binary provenance. This is a correctness finding in the tested Yosys
binary, not a MUXWISE optimization opportunity and not a claim of novelty.

## Environment and provenance

The experiment reused the Experiment 2 OSS CAD Suite:

| Item | Observed |
|---|---|
| Host execution | Windows 11 through WSL2 |
| WSL kernel | 6.18.33.2-microsoft-standard-WSL2 |
| Distribution | Ubuntu 26.04.1 LTS |
| Python | 3.14.4 |
| Git | 2.53.0 |
| CPU/RAM | 8 CPUs, 15 GiB RAM, 4 GiB swap |
| Docker | Docker Desktop docker.exe 29.8.0, Linux daemon reachable |
| Yosys | 0.69+77, git 9ff27d29c-dirty |
| ABC | 1.01, compiled Sep 21 2026 |
| Icarus | 14.0 development build |
| Verilator | 5.053 development build |

The official Yosys repository was shallow-cloned at commit
9ff27d29c672cc5274ce69106145a8aed7c9ba3d, which is the same commit
embedded in the binary. The suite binary has the -dirty suffix and its
source tree was not supplied, so local modifications cannot be ruled out.
A clean rebuild was attempted but was blocked because this WSL environment
has no make and no compiler. No OpenROAD or physical-design work was
needed or performed: correctness failed before any PPA interpretation was
appropriate.

Full environment output: logs/environment.txt.

## Harness audit

The Experiment 2 formal script in audit/exp02_formal_equiv.py classified
outcomes using only returncode == 0. That is insufficient. The actual
FIR4 W4 arithmetic-tree log contains:

SAT proof finished - model found: FAIL!

while formal_manifest.csv says PASS.

The repaired harness:

- uses an explicit mismatch = |(gold_y ^ gate_y) output property;
- uses sat -prove mismatch 0 -verify -set-def-inputs;
- requests ports, JSON, and VCD witnesses;
- parses the proof verdict and rejects setup errors;
- keeps missing, interrupted, and timeout states distinct;
- imports fixed-width candidate netlists under a distinct module name;
- sets the miter parameter explicitly.

There was one additional harness trap during this audit: parameterized
module resolution could select the original parameterized module after
synthesis. Those diagnostic in-process rows were discarded from the final
correctness result. The accepted synthesis results are from fixed-width
Verilog re-imports and direct RTLIL re-imports.

### Corrected previous audits

The complete reconciliation is in:

- audit/experiment_02_formal_audit.csv
- audit/experiment_03_formal_audit.csv
- audit/formal_reconciliation.csv

Experiment 2 had seven formal records. Six are supported by their logs.
One is corrected:

| Check | Manifest | Actual log |
|---|---:|---:|
| FIR4 W4 normal mapped vs RTL | PASS | PASS |
| FIR4 W4 arith_tree mapped vs RTL | PASS | **FAIL** |

The other five Experiment 2 checks were actual PASS records. In Experiment
3, FIR4 W8 normal is PASS and FIR4 W8 arith_tree is FAIL. The FIR4 W16
normal run has no completion marker and remains inconclusive, not PASS.

## Clean formal controls

| Check | Expected | Observed | Exit |
|---|---|---|---:|
| RTL FIR4 vs identical RTL, W8 | PASS | PASS | 0 |
| Original FIR4 vs deliberate +5 to -5 variant, W8 | FAIL | FAIL | 1 |

Evidence: results/correctness_matrix.csv, logs/clean_miter/rtl_self.log,
and logs/clean_miter/wrong_rtl.log.

## Clean formal comparison

The candidate is the generated fixed-width Verilog export, re-imported as
fir4_gate_flat; it is not compared by text or by cell count.

| Width | Normal export | arith_tree export | Formal witness |
|---:|---|---|---|
| 4 | PASS, 2.934 s | **FAIL**, 0.373 s | witnesses/arith_tree_w4_export.* |
| 8 | PASS, 108.858 s | **FAIL**, 0.428 s | witnesses/arith_tree_w8_export.* |

The W4 witness is:

| Signal | Value |
|---|---:|
| x0 | 7 (0111) |
| x1 | 12 (1100, signed -4) |
| x2 | 9 (1001, signed -7) |
| x3 | 6 (0110) |
| gold_y | 0x00000 |
| gate_y | 0x00180 |
| mismatch | 1 |

The W8 witness is:

| Signal | Value |
|---|---:|
| x0 | 234 (0xea, signed -22) |
| x1 | 22 |
| x2 | 100 |
| x3 | 0 |
| gold_y | 0x000186 |
| gate_y | 0x001986 |
| mismatch | 1 |

Canonical W4 files:

- witnesses/counterexample.json
- witnesses/counterexample.vcd

Complete comparison table: results/export_correctness.csv.

## Independent replay and reference model

The bundled Icarus executable independently simulated the original RTL and
each exported candidate. The reference model performs signed input
interpretation, multiplication by (3, -2, 5, 1), modulo 2^(W+16)
accumulation, and reports the output bit vector.

| Width | Configuration | Reference | RTL gold | Candidate | Replay |
|---:|---|---|---|---|---|
| 4 | normal | 0x00000 | 0x00000 | 0x00000 | PASS |
| 4 | arith_tree | 0x00000 | 0x00000 | 0x00180 | **FAIL** |
| 8 | normal | 0x000186 | 0x000186 | 0x000186 | PASS |
| 8 | arith_tree | 0x000186 | 0x000186 | 0x001986 | **FAIL** |

Evidence: results/replay.csv, results/reference_vectors.csv,
replay/reference_model.py, replay/testbench/tb_fir4.v, and logs/replay/.

This eliminates a SAT-only interpretation and supports the intended
two's-complement width semantics. The original RTL's reference outputs agree
with the independent model.

## Stage isolation

The documented synth sequence was replayed with snapshots before
arith_tree, after arith_tree, after techmap, and after ABC. Direct RTLIL
checks are the strongest isolation because they occur before Verilog export.

| Width | Configuration | Pre-arith_tree | Post-arith_tree | Post-techmap | Post-ABC |
|---:|---|---|---|---|---|
| 4 | normal | PASS | PASS | PASS | PASS |
| 4 | arith_tree | PASS | **FAIL** | FAIL | FAIL |
| 8 | normal | PASS | PASS | PASS | PASS |
| 8 | arith_tree | PASS | **FAIL** | FAIL | FAIL |

The same pattern occurs in both direct RTLIL and re-imported Verilog stage
checks. Therefore the Verilog writer, Liberty modeling, techmap, and ABC
are not the earliest cause.

The arithmetic-tree snapshot contains $fa compressor cells and a final
adder. The exported failing structure assigns the upper output bits to a
constant 12'h001 for both W4 and W8, whereas normal synthesis sign-extends
the computed sign bit. This is an observed structural symptom. The exact
internal arithmetic proof obligation that produces that constant has not
been reduced to a one-cell source-level explanation.

Evidence: results/rtlil_stage_correctness.csv, results/stage_isolation.csv,
results/stage_correctness.csv, and intermediate/.

## Configuration isolation

The Yosys help output documents:

- -strategy fa|42;
- -final auto|ripple|prefix;
- -no-fma.

The options were applied to the explicit documented arith_tree pass.
They are not accepted as options to synth itself; an initial attempt using
synth -arith_tree -strategy ... was correctly recorded as a setup error,
then replaced by the documented explicit flow.

| Configuration | W4 | W8 |
|---|---|---|
| default | FAIL | FAIL |
| strategy fa | FAIL | not run |
| strategy 42 | FAIL | not run |
| final ripple | FAIL | not run |
| final prefix | FAIL | not run |
| fa+ripple, fa+prefix | FAIL | not run |
| 42+ripple, 42+prefix | FAIL | not run |
| no-fma | PASS | PASS |
| no-fma+ripple, no-fma+prefix | PASS | not run |

The documented -no-fma switch is an existing configuration workaround,
not a new algorithm. Evidence: results/configuration_formal.csv,
results/configuration_w8_formal.csv, and results/configuration_isolation.csv.

## Answers to the final questions

### Q1. Was the Experiment 2 PASS reporting error confirmed?

Yes. The script used process exit status as the proof result. The FIR4 W4
arith_tree log explicitly says model found: FAIL even though the manifest
records PASS.

### Q2. Does a clean formal harness reproduce the FIR4 counterexample?

Yes. The explicit output miter fails for re-imported arithmetic-tree exports
at W4 and W8 and passes for normal exports.

### Q3. Do the negative controls behave correctly?

Yes. Identical RTL passes; the deliberate +5 to -5 RTL variant fails.

### Q4. What exact input assignment causes the first verified mismatch?

The W4 witness is x0=7, x1=12, x2=9, x3=6, producing gold 0x00000
and arithmetic-tree 0x00180. The W8 witness is 234, 22, 100, 0,
producing gold 0x000186 and candidate 0x001986.

### Q5. Does independent simulation reproduce it?

Yes. Icarus reproduces both mismatches and agrees with the independent
reference model.

### Q6. Is the original RTL correct under intended width and signedness?

Yes for the tested witnesses and formal reference comparison. Inputs are
signed W-bit values, sign-extended to W+16, and the output is W+16 bits.
The independent model gives 0 for W4 and 0x186 for W8.

### Q7. What is the earliest divergent stage?

Immediately after arith_tree. Pre-arith_tree RTLIL is formally equivalent;
post-arith_tree RTLIL is not. Techmap and ABC preserve the mismatch.

### Q8. What is the minimum RTL reproducer?

The original parameterized FIR4 in rtl/original/fir4.v is already the
smallest retained reproducer. It requires four signed inputs, explicit
W+16 sign extension, signed constant products, and their sum. W4 and W8
both reproduce it. No smaller source-level reduction was claimed.

### Q9. Which arithmetic-tree configurations fail?

Default, -strategy fa, -strategy 42, -final ripple, -final prefix,
and their tested combinations fail at W4. Default fails at W8. -no-fma
passes at W4 and W8; its tested final-adder combinations also pass at W4.

### Q10. Is the issue present in the latest available official Yosys version?

It is present in the latest available tested OSS CAD Suite binary,
Yosys 0.69+77 at commit 9ff27d29c, which is also the current upstream
commit cloned during this experiment. Because the binary is marked -dirty
and a clean rebuild was blocked, this is not yet a clean-upstream binary
claim.

### Q11. Is this already a documented upstream issue?

No matching official arith_tree/FIR4 issue was found in the bounded search of
the Yosys issue and pull-request records. The upstream source includes
signed-FMA arithmetic-tree tests, but those tests do not cover this exact
explicit sign-extension plus signed-constant FIR4 shape. This is not a claim
that no related issue exists.

### Q12. Does the evidence establish a genuine synthesis correctness bug?

Yes, conditionally on the tested binary provenance. Independent formal
comparison, direct RTLIL isolation, executable replay, and an independent
reference agree, and the first divergence is the arith_tree transformation.

### Q13. Is the evidence sufficient to begin developing an upstream fix?

It is sufficient to file a narrowly scoped upstream bug report and add this
reproducer as a regression candidate. It is not sufficient to implement or
validate a fix here, because the clean upstream build remains untested.

### Q14. What is the strongest alternative explanation not eliminated?

The strongest remaining alternative is an unobserved local modification in
the -dirty Yosys binary, or a version-specific interaction in the arith_tree
FMA path. A clean build from the same upstream commit is required to
eliminate that provenance explanation.

## Final disposition

**C. GENUINE SYNTHESIS DEFECT CONFIRMED**, with a version/provenance
qualification. The result is a compiler-correctness finding, not evidence
for reviving MUXWISE or for designing a new optimization engine.

The strongest negative evidence against treating this as a research
optimization opportunity is that the documented -no-fma configuration
already avoids the defect, while the failing default path is incorrect
rather than an area/timing trade-off. No PPA or physical-design conclusions
are valid until a clean current build confirms and repairs correctness.

## Reproduction commands

From this experiment directory:

    python3 scripts/clean_miter.py
    python3 scripts/stage_isolation.py
    python3 scripts/stage_miter.py
    python3 scripts/rtlil_stage_miter.py
    python3 scripts/run_replay.py
    python3 replay/reference_model.py
    python3 scripts/configuration_isolation.py
    python3 scripts/configuration_formal.py
    python3 scripts/configuration_w8.py
    python3 scripts/audit_previous.py

The exact generated Yosys scripts are under work/; complete logs are under
logs/.

## Official references checked

- Yosys repository: https://github.com/YosysHQ/yosys
- Tested upstream commit:
  https://github.com/YosysHQ/yosys/tree/9ff27d29c672cc5274ce69106145a8aed7c9ba3d
- arith_tree implementation:
  https://github.com/YosysHQ/yosys/blob/9ff27d29c672cc5274ce69106145a8aed7c9ba3d/passes/techmap/arith_tree.cc
- upstream arith_tree FMA tests:
  https://github.com/YosysHQ/yosys/blob/9ff27d29c672cc5274ce69106145a8aed7c9ba3d/tests/arith_tree/arith_tree_fma.ys
