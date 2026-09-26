# Counterexamples — Wave 10

**None found in any object under test.**

- C1 D1: all 1,855 mapped netlists are `SIM_AGREE` and CEC `PASS`. This covers 3 evolved-operator variants plus 8 baseline families over 53 circuits.
- C1 D2: all 168 ablation netlists are `SIM_AGREE` and CEC `PASS`.

The only counterexamples produced in this wave are **synthetic**. They come from the negative control T1, which deliberately mutated a netlist to prove the checker can fail:

| mutated netlist | mutation | simulation counterexample | ABC |
|---|---|---|---|
| ctrl E:initial | first NAND2x1 → NOR2x1 | PO y1 (index 1), inputs `0100010`, ref 0, mapped 1 | NOT EQUIVALENT |
| i2c E:initial | first NAND2x1 → NOR2x1 | PO y16, pattern bit 4 (full input vector in the log) | NOT EQUIVALENT |

Source: `experiments/logs/c1/t1_negative_control.log`, script `experiments/scripts/c1/t1_negative_control.sh`.

For C6, see the equivalence results in `04_EXPERIMENTAL_INVESTIGATION.md` §7. This file will be updated if a treatment produces a non-equivalent netlist.
