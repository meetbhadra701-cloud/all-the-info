# 20 — Week 1 development log: the parametric UBP generator (`ubpgen/`)

**Specification:** `19_FINAL_UBP_DECISION.md` §H, Week 1:
- a parametric generator (n, m, g, K; bands, taps and spines);
- A and P2 built with the same segmented access and the same sized spine drivers;
- the invariance, verification and collection scripts as the test suite;
- "reproduces the R3 tables from one command".

**Status: Week 1 complete** (§8). The generator reproduces the validated R3 designs bit-for-bit, from the netlist to the frozen physical base, and every routed program reproduces its historical record exactly.

## 1. Golden reference (preserved, not rewritten)

The validated R3 60% design came from this chain, all in `experiments/`:

| Step | Command |
|---|---|
| Modules | `e6_build.py` → `results/E6/ubp3_n64/{SGEN1,SGEN3,SNEG,STREE_L22}` |
| Cells | `g2_cells.py` |
| Logic base and programs | `g2_build.py base/program` → `results/G2/ubp3s` (seeds 1001–1005, 14) |
| R3 access | `r3_build.py cells/base/programs` → `results/G2/ubp3r3`, `cells/struct_ubp3r3.tcl`, `config_u60r.mk` |
| Base | `NO_DCE=1 e5_run.sh` → base ODB sha256 `70add1cd…` |
| Programs | `r3_run_program.sh` for each program, then `r3_collect.py 60` |

**Frozen as `ubpgen/golden/manifest.json`:**
- the sha256 of 95 historical files: scripts, modules, cells, bases, programs and R3 records;
- the parameters;
- the command chain.

The historical files are untouched. A test asserts they have not drifted.

## 2. What was implemented

`ubpgen/` is a Python package (`README.md` there has the parameter table). Its stages:

| Module | Stage |
|---|---|
| `config.py` | configuration |
| `arch.py` | architecture |
| `rtl.py` | modules and spine-driver sizing |
| `netlist.py` | W-independent base emitter |
| `access.py` | R3 taps, cells and W-blind plan |
| `programs.py` | weights with provenance, and programs |
| `orfs.py` | physical flow |
| `verify.py` | numpy oracle and two mutation controls |
| `invariance.py` | frozen-base checks |
| `pipeline.py` | orchestration and records |
| `golden.py` | historical comparison |
| `tables.py` | R3 tables from one command |

**Architectural parameters supported** (only those justified by the thesis or §H):
- fabric ∈ {ubp (B), g1 (A), pc2 (P2)};
- n, m (m ≠ n allowed);
- g ∈ 2..4 (validated g = 3);
- K taps per line, where K divides m;
- utilization, aspect, margin, clock;
- spine_driver ∈ {as_synthesized, drive4}, applied by the same rule to every fabric;
- weight programs, seeded or from file.

**Rejected combinations** are listed in the README; each has a test.

**Reuse:** `_legacy.py` imports the validated components unchanged:
- module RTL generators;
- the synthesis recipe;
- the AIGER simulators;
- cell builders;
- the R3 placer;
- program routing;
- the invariance check.

## 3. Tests (`python3 -m pytest -q ubpgen/tests`)

| Test file | Content | Result |
|---|---|---|
| `test_config_arch.py` | 18 illegal configurations rejected; defaults and round trip; shipped configs load; golden counts (548 lines, 2,192 taps, 1,408 sites, 22 bands, latency 8); canonical-pattern coverage for g = 2..4; exactness of the selection rule (arithmetic model vs W@x, 5 points × 3 densities); band order | 34 pass |
| `test_generate.py` (container) | 5 points spanning all fabrics (g = 2/3/4, K = 1/2/4, m ≠ n), each × 4 programs: pre-PnR W@x, oracle mutation and program mutation all detected; determinism (byte-identical regeneration); base netlist, plan and config independent of the programs; R3 per-segment access rule and structural counts; drive-4 sizing changes exactly the two line-driver cells and still computes W@x | 14 pass |
| `test_golden.py` | reference not drifted; generator vs history for UBP3 at 60% and 52%, P2-R3 at 67% and the A logic base; invariance of the 5 historically routed 60% programs against the generated programs; negative controls (moved cell, base-layer routing, foreign pin) | 11 pass |

## 4. Golden reproduction (generation level)

`python3 -m ubpgen.golden` compares each generated file with its historical counterpart:

| Artifact | UBP3 at 60% / 52% | P2-R3 at 67% | A (logic only) |
|---|---|---|---|
| module RTL and gate-level netlists | BYTE | BYTE | BYTE |
| cells (LEF / Liberty / hooks / PDN) | BYTE | BYTE | BYTE |
| logic base netlist (one tap per line) | BYTE | BYTE | BYTE |
| R3 base netlist (`netlist_base.v`) | BYTE | BYTE | — (never built historically) |
| mapping.json | BYTE | BYTE | SEMANTIC (vs the single-tap mapping) |
| placement plan | SEMANTIC | SEMANTIC | — |
| ORFS config | SEMANTIC | SEMANTIC | — |
| SDC | BYTE | BYTE | — |
| W and program nets | SEMANTIC (identical arrays and nets) | SEMANTIC | SEMANTIC (segments merged) |
| program TCL | BYTE | BYTE | — |

**The SEMANTIC items, and why they are behaviour-free:**
- **Placement plan:** identical entries, band count and placer TCL. Only the comment line naming the generator differs.
- **ORFS config:** identical variables and values. Paths differ only by the mount layout (`/work/netlist/…` instead of `/work/ubp3r3/…`).
- **W arrays:** the arrays are equal; the `.npy` headers are not compared.
- **Program JSON:** the nets, zeros and ones are identical. The JSON carries different descriptive keys (`derived_from`).

**Pre-PnR functional check of the golden 60% design:** 6 of 6 programs (W1–W5, W14) match numpy, and the oracle and program mutations are both detected for each.

## 5. Physical reproduction

**Command:**

```
python3 -m ubpgen.tables ubpgen/configs/suite_r3_tables.json --run
```

This is the §H "one command". It runs every step: generate → golden compare → pre-PnR verify → frozen base → programs → table. The committed snapshot is `ubpgen/results/week1_r3_tables/`. It holds `tables.md` and `tables.json`, and per design the `config.json`, `generation.json` (provenance and file hashes) and `records/`.

**Frozen bases, regenerated from configuration by the generator:**

| Design | Base ODB sha256 = historical | Components differing | Routed base nets | Base DRC | Setup / hold (ns) |
|---|---|---|---|---|---|
| UBP3 R3, 60% | **identical** (`70add1cd…`) | 0 of 14,078 | identical | 0 | +1.022 / +0.293 |
| UBP3 R3, 52% | **identical** (`aefbdaff…`) | 0 of 14,027 | identical | 0 | +0.976 / +0.268 |
| P2-R3, 67% | **identical** (`afde9bb0…`) | 0 of 31,304 | identical | 0 | −0.846 / +0.024 |

**Programs:**
- 12 programs were routed on met4–met5 at the 64-iteration default: UBP3 W1–W5 at 60% and 52%, and P2-R3 W1 and W4.
- Each program's DRT iterations, met4/met5 wirelength, via count, setup WS and programmable-path WS equal the historical record: **0 differences** over every compared value (`tables.md`).
- Every program: 0 DRT violations; post-PnR netlist = numpy W@x with the mutation detected; every invariant holds, including the new programmable-connectivity check.

**A×T (established rule):**
- UBP3: 9.2625e6 at 52% (**1.538×** vs A at 75%, credited) and 8.5660e6 at 60% (**1.663×**). These are the validated values.
- P2-R3: 17.885e6.

**New Week 1 point (§H: A with the same segmented access): A with R3 access at 75% (`r3_g1_u75`).**
- The base has DRC 0, setup / hold +0.775 / +0.065 ns, and cell area 356,417 µm²: the taps are area-neutral.
- All five programs route DRC-clean in 8 / 8 / 5 / 10 / 1 iterations. All are correct and invariant.
- A×T 14.80e6, against 14.25e6 for the credited single-tap A at 75%. As the R3 pre-registration expected ("A's period is set by its base"), segmented access does not strengthen A: its base is slightly slower (+0.775 vs +0.853 ns).
- The strongest competitor therefore remains the credited single-tap A.
- UBP3 vs A-R3: **1.598× (52%)** and **1.728× (60%)**.

**Sized spine drivers.** The generator implements `spine_driver = drive4` identically for every fabric, and it is verified pre-PnR (tests). §H puts the placed-and-routed evaluation of sized drivers in Week 2, so no physical drive-4 run was made in Week 1.

## 6. Deviations from the original R3 scripts

1. The base top is emitted directly from the configuration. The history built a W-hardwired top (E6), then removed every W-dependent connection by text substitution (G2). The emitted top omits two dead leftovers of that removal (an unused `wire zero;` and the tie cell's line residue). Yosys drops them, so the linked netlist is byte-identical.
2. The tap expansion is a named stage (`netlist_logic.v` → `netlist_base.v`), no longer a rewrite of another design's directory.
3. Pre-PnR verification adds a **program mutation** control (one leaf re-routed to another line of its band), on top of the historical oracle mutation.
4. Invariance adds **programmable connectivity**: the routed pgm nets equal the program, and every pin on them is a tap Z or a site A.
5. Invariance runs on the unmodified `r3_invariance.py`: its printed record is captured, and the script is not edited.
6. `spine_driver = drive4` implements the §H fairness rule at the netlist level. The cells driving a line port of SNEG / PLINE become drive 4 (same rule as the D-R3.4 what-if). Physical evaluation is Week 2.
7. Output layout is one directory per configuration, mounted at `/work`. The ORFS nickname can be pinned; the golden configs pin the historical nicknames.

## 7. Regressions encountered

- A test expectation for the band order was wrong: it assumed 0, 1, 10, … instead of the string order 0, 10, 11, …. The generator was right; the golden plan comparison had already shown identity. The test was fixed.
- **Base freeze rejected a complete run (fixed).** The first golden base run was refused by the new flow wrapper because ORFS exited with rc 2. The cause is KLayout's final GDS merge: the abstract via-site and tap cells have no GDS. The historical R3 runs had the same rc 2, and `6_final.odb/def` and `6_report` are written before the merge.
  - The wrapper now accepts exactly that failure and records it (`gds_merge: expected-failure`). Any other ORFS error still fails.
  - A resume path freezes an already-completed run instead of re-running it.
- **Bookkeeping bug (fixed).** `all_programs_pass` compared against every program in the config (including W14) instead of the programs the suite routes.
- **Table bug (fixed).** The table showed a meaningless "vs strongest" ratio for competitor rows.
- **No generator regression against the golden reference was observed.** Every generated file and every physical result matched.

## 8. Week 1 success criteria

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | The generator produces a UBP design from configuration | **met** | `python3 -m ubpgen generate CONFIG`; 3 fabrics; g = 2..4; K = 1/2/4; m ≠ n |
| 2 | Generated designs compute W@x | **met** | pre-PnR: 5 small points × 4 programs, plus golden 6 + A 5 + P2 2 programs; post-PnR: 17 routed programs |
| 3 | Mutation controls work | **met** | oracle and program mutation detected in every pre-PnR check; oracle mutation in every post-PnR check |
| 4 | Base invariants are checked automatically | **met** | `invariance.check` after every routed program: hash, placement, masters, layers, power grid, programmable connectivity; negative controls in the tests |
| 5 | The validated R3 design is reproduced | **met, exactly** | byte-identical netlists; bit-identical base ODBs at 60% and 52% (and P2-R3 at 67%); 0 differences on 12 routed programs |
| 6 | Config → generation → verification → physical flow is documented and executable | **met** | `ubpgen/README.md`; `python3 -m ubpgen all CONFIG`; `python3 -m ubpgen.tables SUITE --run` |
| 7 | Failures are explicit | **met** | `ConfigError` on illegal parameters; image-id pin; non-zero exit on any failed check; GDS-merge rc classified, never ignored; every difference listed |
| §H | A and P2 with the same segmented access | **met** | P2-R3 (golden) and A-R3 (new) built and routed |
| §H | A and P2 with the same sized spine drivers | **generator done; physical evaluation is Week 2 per §H** | `spine_driver = drive4`, same rule for every fabric, verified pre-PnR |
| §H | Invariance / verification / collection as the test suite | **met** | 59 tests (`python3 -m pytest -q ubpgen/tests`, about 2 min) |
| §H | Reproduces the R3 tables from one command | **met** | `ubpgen/results/week1_r3_tables/tables.md` |

## 9. Remaining (Week 2 onward, per §H; not Week 1)

- Place and route the drive-4 spine-driver variants of B, A and P2, and settle the post-hoc 1.48× point.
- Extracted-parasitic STA of merged base + program as a pipeline stage. `r3_prog_spef.py` and `r3_sta_extracted.tcl` exist but are not wired into ubpgen yet.
- Real weights (`programs: [{tag, file}]` is supported; weights must be supplied locally).
- Scale points (256 × 256) through the same suite runner.
