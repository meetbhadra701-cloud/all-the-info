# MUXWISE Experiment 4

This experiment audits the FIR4 arith_tree counterexample reported by
Experiments 2 and 3. It does not implement an optimization pass.

The decisive checks are:

1. results/correctness_matrix.csv: clean RTL self-equivalence and wrong-RTL
   negative control.
2. results/export_correctness.csv: original RTL against re-imported,
   fixed-width normal and arithmetic-tree exports.
3. results/rtlil_stage_correctness.csv: original RTL against direct RTLIL
   stage snapshots, before Verilog export.
4. results/replay.csv and results/reference_vectors.csv: independent Icarus
   replay and a separate two's-complement reference model.
5. results/configuration_formal.csv and
   results/configuration_w8_formal.csv: documented arith_tree option
   isolation.

The bundled OSS CAD Suite is reused from Experiment 2. The tested Yosys
binary is 0.69+77, commit 9ff27d29c, with a -dirty build suffix. A clean
rebuild of the cloned upstream source was not possible because this WSL
environment has no make or compiler. That provenance limitation is part of
the conclusion.
