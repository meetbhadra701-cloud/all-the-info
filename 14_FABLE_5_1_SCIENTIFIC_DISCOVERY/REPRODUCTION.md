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
python3 scripts/e5_build.py $(pwd)/results/E5 32 g1 ubp3 ubp4        # modules, top, validation, configs
scripts/e5_run.sh $(pwd)/results/E5 g1_n32:60 ubp3_n32:60 ubp4_n32:60 g1_n32:75 ubp3_n32:75 ubp4_n32:75
#   (then <design>_n32:45 for any design not DRC-clean at 60)
python3 scripts/e5_collect.py results/E5 32 > results/E5_summary.md
python3 scripts/post_pnr_validate.py results/E5 32 <design> <U_max>   # final routed netlist vs numpy

# E6 — bit-serial, n = m = 64, 3.0 ns clock with CTS
python3 scripts/e6_build.py $(pwd)/results/E6 64 g1 ubp3 ubp4
scripts/e5_run.sh $(pwd)/results/E6 g1_n64:60 ubp3_n64:60 ubp4_n64:60 g1_n64:75 ubp3_n64:75 ubp4_n64:75
python3 scripts/e5_collect.py results/E6 64 serial > results/E6_summary.md
python3 scripts/post_pnr_validate.py results/E6 64 <design> <U_max> serial
```

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
- `results/E*/post_pnr_validation.jsonl`.
- The per-design `netlist.v`, `top.v`, module netlists, configs and ORFS logs `orfs_u*.log`.

**Not committed** (size; regenerable): `results/E*/orfs/` (ORFS work trees: ODB/DEF/GDS-level data), AIGER files, raw netlists (see `.gitignore`).

## Runtime (this machine)

A 32×32 bit-parallel or 64×64 bit-serial PnR job takes roughly 20–60 min with 2 threads. Detailed routing dominates.
