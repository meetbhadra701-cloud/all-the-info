# REPRODUCTION — Wave 14 (E5 bit-parallel PnR, E6 bit-serial PnR)

## Environment

- **Host:** Linux; 4 CPUs and 15 GB RAM were used; Python 3 with numpy.
- **Docker.** If the daemon is not running, start it: `dockerd > /tmp/dockerd.log 2>&1 &`.
- **Container:** `openroad/orfs:latest`, image id `69df744e2b5c` (pulled 2026-09-26). It supplies Yosys, ABC, OpenROAD/OpenSTA, ORFS and the SKY130 HD platform. All EDA tools run inside it (isolation).
- **Independent simulator:** `13_FABLE_5_1_SCIENTIFIC_DISCOVERY/experiments/scripts/e2_run.py` (`read_aag`, `sim_aag`, `bus_index`), imported by path.

## Commands

Run everything from `14_FABLE_5_1_SCIENTIFIC_DISCOVERY/experiments`.

```bash
# E5 — bit-parallel, n = m = 32 (Amendment A1: area-oriented modules, 20 ns virtual clock)
python3 scripts/e5_build.py $(pwd)/results/E5 32 g1 ubp3 ubp4        # modules, top (all instances kept: A2), validation, configs
# (the session's UBP netlists were regenerated from the E5/E6 module netlists by: python3 scripts/reemit_a2.py <EDIR> <N> <design> [serial])
NO_DCE=1 scripts/e5_run.sh $(pwd)/results/E5 g1_n32:60 ubp3_n32:60 ubp4_n32:60 g1_n32:75 ubp3_n32:75 ubp4_n32:75
#   NO_DCE=1 mounts scripts/orfs_patch/synth_odb.tcl (eliminate_dead_logic disabled; A2). g1 is identical either way (0 dead instances).
#   Then <design>_n32:45 for any design not DRC-clean at 60.
python3 scripts/e5_collect.py results/E5 32 > results/E5_summary.md
python3 scripts/post_pnr_validate.py $(pwd)/results/E5 32 <design> <U>          # final routed netlist vs numpy (+ mutation control)
python3 scripts/select_wiring.py results/E5 32 <design> <U>                     # routed-wire decomposition from 6_final.def

# E6 — bit-serial, n = m = 64, 3.0 ns clock with CTS
python3 scripts/e6_build.py $(pwd)/results/E6 64 g1 ubp3 ubp4
NO_DCE=1 scripts/e5_run.sh $(pwd)/results/E6 g1_n64:60 ubp3_n64:60 ubp4_n64:60 g1_n64:75 ubp3_n64:75 ubp4_n64:75
python3 scripts/e5_collect.py results/E6 64 serial > results/E6_summary.md
python3 scripts/post_pnr_validate.py $(pwd)/results/E6 64 <design> <U> serial
python3 scripts/select_wiring.py results/E6 64 <design> <U> serial
```

**W-independence check (A2).** Verify both of these for every UBP run:
- `1_synth.log` has no `eliminate_dead_logic` line;
- `synth__design__instance__area` equals `build_n*.json → reemit_A2.yosys_stat_area_um2`.

## Determinism and inputs

- **W:** i.i.d. ternary, `numpy.random.default_rng(14)`, P(0) = 0.4. Saved as `results/E*/W_n*.npy`.
- **Validation vectors:**
  - E5: rng(7), 64 vectors;
  - E6: rng(3), 12 words;
  - post-PnR: rng(99).
- **Activations:** symmetric INT8 in [−127, 127].
- **Tool determinism:** Yosys/ABC module synthesis is deterministic for identical RTL. ORFS placement and routing are deterministic for a given thread count (NUM_CORES = 2 was used).

## Outputs

**Committed:**
- `results/E*/build_n*.json`: validation, mutation control, module timing/area, latency.
- `results/E*_summary.md`: collected metrics and the pre-registered decision.
- `results/E*/post_pnr_validation.jsonl`, `results/E*/select_wiring.jsonl`.
- `results/E*/orfs_metrics/<run>/`: ORFS per-stage metric JSONs and 1_synth.log, the inputs of the collector.
- Superseded pruned runs (A2): `results/E*/pruned_A1_runs/` and `results/E*_pruned_A1_summary.md`.
- The per-design `netlist.v`, `top.v`, module netlists, configs and ORFS logs `orfs_u*.log`.

**Not committed** (size; regenerable): `results/E*/orfs/` (ORFS work trees: ODB/DEF/GDS-level data), AIGER files, raw netlists (see `.gitignore`).

## Runtime (this machine)

A 32×32 bit-parallel or 64×64 bit-serial PnR job takes roughly 20–60 min with 2 threads. Detailed routing dominates.

## Gates G2 / G3 / R2 (2026-09-27)

All commands run from `experiments/`. EDA runs inside `openroad/orfs:latest`, image 69df744e2b5c.

### G3: frontier popcount competitors and the DA model

```
python3 scripts/g3_build.py $PWD/results/G3 64 pc pc2           # (and N = 8 for quick checks); validated vs numpy
NO_DCE=1 scripts/e5_run.sh $PWD/results/G3 pc_n64:60c5 pc2_n64:60   # routed runs used (D-G3.1: pc at 5.0 ns)
python3 scripts/g3_post_validate.py $PWD/results/G3 pc2 g3_pc2_n64_u60
python3 scripts/g3_da_model.py $PWD/results/G3/da_model          # → da_model.json
```

### G2: the fixed base, generic placement (pre-registered)

1. Build the cells, the bases and the programs:

   ```
   python3 scripts/g2_cells.py $PWD/results/G2/cells                  # via-site / line-tap LEF + liberty
   python3 scripts/g2_build.py base    $PWD/results/G2 ubp3s $PWD/results/E6/ubp3_n64   # g1s: E6/g1_n64; pc2: G3/pc2_n64
   python3 scripts/g2_build.py program $PWD/results/G2 ubp3s w1 1001 0.4
   ```

   - W1/W2 use seeds 1001/1002; W3 1003 with p0 0.8; W4 1004 with p0 0.1; W5 1005 with identical rows.
   - Repeat the `program` step for pc2 and g1s.

2. Build a base at utilization U: `NO_DCE=1 scripts/e5_run.sh $PWD/results/G2 ubp3s:60`.
3. Screen each program with GRT on met4–met5: `scripts/g2_grt_screen.sh $PWD/results/G2 ubp3s 60 w1`.
4. Route it (20 iterations), take the modeled STA and write the programmed netlist, then check it against numpy: `DRT_ITERS=20 scripts/g2_run_program.sh $PWD/results/G2 ubp3s 60 w1`.

### R2: the structured W-blind crossbar base

1. Write the plan and the `config_u<U>s.mk` files: `python3 scripts/g2_struct.py $PWD/results/G2 ubp3s 60 52 45` (then pc2 60 67, g1s 60 75). Rename the configs to `config_u<U>s.mk`.
2. Build the bases: `NO_DCE=1 scripts/e5_run.sh $PWD/results/G2 ubp3s:60s pc2:60s ubp3s:52s g1s:60s ubp3s:45s pc2:67s g1s:75s`.
3. Screen, route and verify: `scripts/g2_grt_screen.sh $PWD/results/G2 ubp3s 60s w1`, then `DRT_ITERS=20 scripts/g2_run_program.sh $PWD/results/G2 ubp3s 60s w1`.
4. Collect the table: `python3 scripts/g2_r2_collect.py results/G2` → `results/G2/g2_r2_summary.json`.
5. Track model (DERIVED): `python3 scripts/g2_track_model.py results/G2`.

**Integrity checks:**
- `sha256sum results/G2/orfs/results/sky130hd/g2_*/base/6_final.odb` must equal `results/G2/base_odb_sha256_before_programs.txt`.
- Program DEFs contain only met4/met5 wiring.

**Committed outputs:**
- `results/G2/g2_grt_screen.jsonl` and `g2_verification.jsonl`;
- `g2_r2_summary.json` and `g2_track_model.json`;
- per-run logs;
- gzipped congestion and DRC reports (`*.rpt.gz`).

The ORFS trees (`results/G2/orfs/`) and the programmed netlists and DEFs are regenerable and not committed.

## R3: the final layout revision (segmented line taps)

All commands run from `experiments/`.

1. **Cells, base, programs, placement plan and configs.**

   ```
   python3 scripts/r3_build.py cells    $PWD/results/G2
   python3 scripts/r3_build.py base     $PWD/results/G2 52 60
   python3 scripts/r3_build.py programs $PWD/results/G2 w1 w2 w3 w4 w5 w14
   ```

   - `cells` writes the LTAP2 LEF/Liberty and `dont_touch_r3.tcl`.
   - `base` writes `ubp3r3/` and `cells/struct_ubp3r3.tcl`.
   - `programs` re-derives each program from W and asserts it equals the G2 program.
   - For the P2-R3 fairness point, append `pc2` to the `base` and `programs` commands, e.g. `... base $PWD/results/G2 67 pc2`.
   - Design model (DERIVED, development matrices only): `python3 scripts/r3_design_model.py results/G2/r3`.
2. **Pre-PnR functional check:** `python3 scripts/g2_verify.py $PWD/results/G2 ubp3r3 w14`.
3. **Bases:** `NO_DCE=1 scripts/e5_run.sh $PWD/results/G2 ubp3r3:52r ubp3r3:60r pc2r3:67r`, then `sha256sum .../g2r3_ubp3r3_uU/base/6_final.odb > results/G2/r3/base_sha256_ubp3r3_uU.txt`.
4. **Per program:** `scripts/r3_run_program.sh ubp3r3 52 w1`, and likewise for w2–w5 and for U = 60.
   - It routes met4–met5 at 64 iterations, runs the modeled STA, writes the programmed netlist and checks it against numpy with the mutation control.
   - It then runs `r3_invariance.py` and appends a record to `results/G2/r3/r3_results.jsonl`.
5. **Scoring against the pre-registered criteria:** `python3 scripts/r3_collect.py 52`, and likewise for 60. Writes `results/G2/r3/r3_summary_uU.json`.
6. **Routed-parasitic timing (post-hoc rigor check):**
   - `python3 scripts/r3_prog_spef.py <program DEF> <out.spef>`.
   - Then `openroad scripts/r3_sta_extracted.tcl`, with env BASE_ODB, BASE_SDC, BASE_SPEF, PROG_TCL and PROG_SPEF set.
   - Summary: `results/G2/r3/sta_extracted_summary.json`.
7. **P2-R3 fairness point (pre-registered), after its base (step 3):**
   - `sha256sum .../g2r3_pc2r3_u67/base/6_final.odb > results/G2/r3/base_sha256_pc2r3_u67.txt`.
   - GRT for all five W: `scripts/g2_grt_screen.sh $PWD/results/G2 pc2r3 67r wN`.
   - The largest-WL program, routed, timed, verified and invariance-checked: `scripts/r3_run_program.sh pc2r3 67 w4`.
   - W1 modeled timing and verification: `MODES=sta scripts/g2_run_program.sh $PWD/results/G2 pc2r3 67r w1`.
   - Critical-path report: rerun that STA with `REPORT_PATHS=1` (saved as `results/G2/r3/p2r3_w1_critical_path_u67.log`).
8. **Spine-driver sizing sensitivity (post hoc, D-R3.4), STA only:**
   - Run `openroad scripts/r3_whatif_drivers.tcl`, with env BASE_ODB, BASE_SDC and PROG_TCL set to a base and program.
   - Runs used: pc2r3 67 w1 / w4; ubp3r3 52 w1 / w5; ubp3r3 60 w1 / w4 / w5. Logs go to `results/G2/r3/whatif_drivers_<design>_<W>_u<U>.log`.
   - Then `python3 scripts/r3_fairness.py`, which writes `results/G2/r3/fairness_summary.json` and prints the fairness table of 16 §6.6.
