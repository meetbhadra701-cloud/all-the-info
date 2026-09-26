# C6 decisive experiment: pre-registration

Written 2026-09-25, after C1 was killed and before any C6 treatment data existed.

## Object

OpenROAD `rmp` search-based post-placement resynthesis (Antmicro, 2025, in OpenROAD mainline):
- **`resynth_annealing`** runs simulated annealing over ABC operation sequences. A neighbour adds, removes or swaps one operation, and the objective is worst slack.
- **`resynth_genetic`** is the genetic-algorithm variant.

Both are applied to logic below `-slack_threshold` (default 0), on a placed design.

## Exact claim (PAPER: Antmicro blog, 2025-11)

AES on ASAP7: WNS goes from −30.92 ps to +20.59 ps. The blog gives no baseline, no area or runtime, and no equivalence check.

## A. Hypothesis

`resynth_annealing` improves post-placement setup WNS on asap7/aes beyond what standard post-placement timing repair achieves. The gain must hold across seeds, cost acceptable area, and yield functionally equivalent netlists.

## B. Baselines

All start from the identical ORFS `3_place.odb` + `3_place.sdc`, with the placement parasitics estimate.
1. `none`: WNS as placed.
2. `resynth`: the fixed-script rmp resynthesis.
3. `repair_timing -setup`: OpenROAD's standard setup repair.

## C. Variable

The treatment (seeds 1..5 for annealing and genetic).

## D. Observables

WNS, TNS, design area, instance count and runtime before and after each treatment (`c6_treat.tcl` → `metrics.json`).

## E. Independent validation

- Functional equivalence of `after.v` vs `before.v`: Yosys with ASAP7 liberty functional models, `equiv_make` / `equiv_simple` / `equiv_induct`, with registers matched by name. The checker is first validated on a mutated netlist (negative control).
- Seed-to-seed spread.

## F. Kill

Any one of the following kills the hypothesis:
- median-over-seeds WNS after `resynth_annealing` is not better than `repair_timing -setup` by more than 5 ps;
- the gain changes sign across seeds;
- the gain costs more than 5% area;
- any treated netlist is NEQ. This would be a bug: engineering-grade, and it also kills the research reading.

## G. Advance

All of the following:
- median WNS better than `repair_timing` by more than 10 ps;
- the gain is additive, i.e. `resynth_annealing` then `repair_timing` beats `repair_timing` alone by more than 10 ps;
- at most 2% area cost;
- every seed equivalent.

Only then: prior art on ABC-script search for timing (FlowTune, DRiLLS, Bulls-Eye and others; expected to be heavily occupied) and a mechanism study.

## Scope note

This is a single-design reproduction of the single published example. A kill here says the published example does not demonstrate the claimed benefit. It does not say the method can never help.

## Amendment 1 (2026-09-25, after the first post-placement annealing result, before any unplaced run)

On re-reading the blog, its AES example loads an **unplaced** netlist: `read_liberty`, `read_lef`, `read_verilog aes_asap7.v`, `link_design`, `read_sdc`, from "one of the simulated annealing tests in OpenROAD". It then runs `resynth_annealing` with no parameters and measures slack with ideal wires. The post-placement arm above tests the command's documented use. It does not reproduce the published example's own setting.

The added arm is **R6**:
- the same load sequence, applied to the local ORFS asap7/aes `1_synth.v` + `1_synth.sdc` (no placement, no parasitics estimate);
- modes: none; `resynth_annealing` seeds 1–3 (defaults); `repair_timing -setup`.

R6 only tests whether the published number is reproducible in its own setting, on the ORFS netlist rather than the test's `aes_asap7.v`, which was not downloaded. F and G remain defined on the post-placement arm.

## Amendment 2 (2026-09-25): equivalence checker v1 → v2, before any treated-netlist verdict was used

Checker v1 matched every same-named wire after flattening, including the liberty cells' `<instance>.<pin>` wires. On the `repair_timing` netlist it reported EQUIV_NOT_PROVEN, and every unproven point was a cell *input pin* (`u4193.A2`, `u3946.B`, `u7005.A`). `repair_timing` pin-swapping legitimately changes which net sits on a commutative pin, so these name matches are not meant to hold. This is a checker artifact, not evidence of non-equivalence.

**v2 change.** After flattening, v2 hides those pin wires (`rename -hide w:*.*`) and matches only top-level net and port names. It remains fail-closed: every matched point, including all primary outputs and register nets, must be proven.

**Validation.** v2 is re-validated on the same controls: identical must PASS, and the mutated netlist must NOT pass.

**Records.** The v1 outputs are archived in `experiments/outputs/c6/equiv_v1_superseded/`. v1 completed only on `repair_timing_s1`; its runs on resynth_s1, annealing s2–s4 and genetic s1 were stopped before finishing.

## Amendment 3 (2026-09-25): additive arm fix

`annealing_repair` as first written (`resynth_annealing; repair_timing -setup`) aborts in OpenROAD with `[ERROR EST-0104] inconsistent parasitics state`: the resynthesis leaves parasitics stale. The mode now re-runs `estimate_parasitics -placement` between the two commands.

The failed run is kept in `experiments/outputs/c6/failed_runs/annealing_repair_s2_EST-0104/`. Its annealing part reproduced seed 2's −88.79 ps exactly, so the tool is deterministic per seed. Affected runs are redone.

## Amendment 4 (2026-09-25): equivalence checker v3 (ABC) becomes the primary checker; v2 abandoned for throughput

Checker v2 (Yosys `equiv_*`) was sound but needed about 10k SAT calls per netlist, i.e. hours on an oversubscribed CPU.

**v3** (`c6_equiv_abc.sh`):
- Yosys lowers each netlist (liberty functional models, flattened) to BLIF, with flops as `.latch` named by their Q net.
- ABC `cec -T 3000 -C 1000000` compares all outputs and latch inputs, with latches matched **by name** (530 on both sides).

**Controls** (`experiments/logs/c1/c6_equiv_abc_selftest.out`):
- identical: PASS, 13 s;
- mutated: a concrete counterexample on the cone of register `u9891`, the same register v2 localized. The first parse filed it as UNDECIDED, and the parser was fixed to treat an explicit counterexample ("Verification failed" / "Value in Network1") as NEQ;
- `repair_timing_s1`: PASS, confirming that v1's NOT_PROVEN on that netlist was the pin-name artifact.

**Verdict rule.** Fail-closed: PASS only on "Networks are equivalent", NEQ only on explicit mismatch evidence, otherwise UNDECIDED. Partial v2 logs are kept in `experiments/outputs/c6/equiv_v2_abandoned/`.
