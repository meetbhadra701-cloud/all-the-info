# ubpgen: parametric generator for the weight-independent UBP fabric

> **Status (2026-09-28): UBP is CLOSED** (`../22_UBP_PROJECT_CLOSEOUT.md`).
> - `ubpgen` is kept unchanged as the reproducible record of Weeks 1–2.
> - New work should use the extracted, architecture-free harness in `../../SUPPORTING_ARTIFACTS/research_harness/`.

`ubpgen` builds, from one JSON configuration, every artifact needed to verify and physically implement a weight-independent fixed-base matrix–vector fabric:

- the bit-serial UBP-g fabric (B);
- the per-input serial baseline (A);
- the bit-plane popcount baseline (P2).

All three use the R3 segmented-access layout methodology; `access.mode = r2` also gives the historical single-tap (R2) access of the per-input baselines. The specification is `../19_FINAL_UBP_DECISION.md` §H: Week 1 (the generator, `../20_WEEK1_DEVLOG.md`) and Week 2 (physical driver sizing and three-corner extracted sign-off, `../21_WEEK2_TIMING_CLOSURE.md`).

The validated R3 implementation is the golden reference. `golden/manifest.json` freezes it. The generator reproduces it byte-for-byte: module netlists, cells, base netlists and program TCL (`tests/test_golden.py`).

## Quick start

Run from `14_FABLE_5_1_SCIENTIFIC_DISCOVERY/`. The ORFS image must be `openroad/orfs:latest` with id `sha256:69df744e…`. If the Docker daemon is down, start it with `dockerd &`.

```
python3 -m ubpgen params                                     # documented parameter table
python3 -m ubpgen generate ubpgen/configs/golden_r3_ubp3_u60.json   # all artifacts, seconds
python3 -m ubpgen verify   ubpgen/configs/golden_r3_ubp3_u60.json   # pre-PnR W@x + 2 mutation controls per program
python3 -m ubpgen.golden   ubpgen/configs/golden_r3_ubp3_u60.json   # compare with the historical implementation
python3 -m ubpgen base     ubpgen/configs/golden_r3_ubp3_u60.json   # ORFS flow of the frozen base (~20 min)
python3 -m ubpgen program  ubpgen/configs/golden_r3_ubp3_u60.json --tags w1,w2   # route/STA/post-PnR/invariance/sign-off
python3 -m ubpgen.pdk fetch                                  # once: the pinned ss / ff corner libraries (sha256-checked)
python3 -m ubpgen signoff  ubpgen/configs/golden_r3_ubp3_u60.json --tags w1   # OpenRCX + tt/ss/ff STA of a routed program
python3 -m ubpgen base     ubpgen/configs/w2_b60.json --prune   # Week 2: sized design; --prune drops intermediate ODBs
python3 -m ubpgen.week2                                      # Week 2 decision table from the records of suite_week2
python3 -m ubpgen summary  ubpgen/configs/golden_r3_ubp3_u60.json   # table + A x T
python3 -m ubpgen all      CONFIG                            # everything, in order; non-zero exit on any failure
python3 -m pytest -q ubpgen/tests                            # regression suite (~6 min; docker for most tests)
python3 -m ubpgen.tables ubpgen/configs/suite_r3_tables.json --run   # the R3 tables from one command (resumable; hours)
python3 -m ubpgen.snapshot ubpgen/configs/suite_r3_tables.json ubpgen/results/<dir>   # commit-sized provenance snapshot
```

Outputs go to `ubpgen_runs/<name>/`, which is not committed. `pipeline.py` documents the layout. Each output directory holds `config.json`, a resolved configuration with every default explicit. It also holds `generation.json`, which records:

- git commit;
- tool versions and image id;
- config sha256;
- structural counts;
- the sha256 of every generated file.

Every verification and physical event appends a provenance-stamped record to `records/`.

## Parameters

| Key | Default | Meaning |
|---|---|---|
| `name` | required | design name (output directory; default ORFS nickname `ubpgen_<name>`) |
| `fabric` | required | `ubp` = bit-serial UBP-g (B); `g1` = per-input bit-serial (A); `pc2` = pipelined bit-plane popcount (P2) |
| `n` | required | inputs (columns of W) |
| `m` | `n` | outputs / rows |
| `g` | — | UBP block size 2..4 (`ubp` only; validated g = 3). Rejected for `g1` / `pc2` |
| `activation_bits` | 8 | symmetric INT8; the only supported value |
| `clock_ns` | 3.0 | SDC clock |
| `access.taps_per_line` | 4 | K taps per line; rows split into K equal segments; K must divide m |
| `layout.util` | 60 | ORFS core utilization (%) |
| `layout.core_aspect_ratio`, `layout.core_margin` | 1, 2 | ORFS floorplan |
| `spine_driver` | `as_synthesized` | `drive4`: every line (spine-root) driver upsized to drive 4, identically for every fabric (the Week-1 netlist-level option; not with `w2_load_rule`) |
| `access.mode` | `r3` | `r3` = K taps per line on a base spine, R3 track-aligned placer; `r2` = one tap per line (K must be 1), the historical R2 structured placer |
| `drivers.policy` | `historical` | `historical` = the validated abstract taps (R3 `LTAP2`: 2 sites with `buf_4` timing; R2 `LTAP`: 8 sites); `w2_load_rule` = Week 2: physical taps `LTAPB<k>` / `LTAPBW<k>` (2-site pad + `buf_<k>`), class chosen by the W-independent rule of `drivers.py`, tap A-pin `max_transition` = S enforced on the spines by the flow's `repair_design` |
| `drivers.slew_target_ns` | 0.30 | S: the transition target (tt) of the rule |
| `drivers.tap_class` | null | `w2_load_rule` only: the class; null = resolved at generation; if given it must equal the rule's choice |
| `programs` | `[]` | `[{tag, seed, p0, same_rows?}]`: i.i.d. ternary with P(0) = p0. Or `[{tag, file}]`: a .npy m × n ternary matrix |
| `flow.*` | see `params` | image id pin, NUM_CORES (determinism), DRT iteration cap (64), NO_DCE, nickname |
| `verify.words`, `verify.seed` | 12, 3 | simulator stimulus |

**Illegal combinations raise `ConfigError`:**
- unknown keys;
- `g` outside 2..4 for `ubp`, or any `g` for the baselines;
- `g` > n;
- K not dividing m;
- `pc2` with n > 64 (its 14-bit output word);
- duplicate or ill-formed program tags;
- `p0` outside [0, 1];
- an unsupported activation width;
- utilization outside 5–90%;
- `access.mode = r2` with K ≠ 1, an unknown access mode or driver policy, a tap class without `w2_load_rule` or outside the candidates, `drive4` with `w2_load_rule`, S outside [0.05, 1.5] ns.

## Components

| Module | Role |
|---|---|
| `config.py` | parameters, defaults, validation, hashing |
| `arch.py` | blocks, canonical patterns, line names, bands, the W → leaf selection rule, counts, latency |
| `rtl.py` | which modules a configuration needs; Yosys synthesis (reused); spine-driver sizing |
| `netlist.py` | the W-independent base top emitter; Yosys link (every instance kept); mapping |
| `access.py` | R3 (K taps per line) and R2 (one tap per line) access; tap masters; custom cells incl. the Week-2 physical taps and per-corner clones; W-blind placement plans + placers |
| `drivers.py` | Week 2 `w2_load_rule`: the tap class from the worst-case W-independent load, and its re-check on the built base |
| `pdk.py`, `liberty.py` | pinned ss / ff sign-off libraries (uncommitted cache); minimal Liberty reader |
| `signoff.py` | merged base + program DEF, OpenRCX extraction, OpenSTA at tt / ss / ff (one session per corner) |
| `accounting.py` | exact flow-sizing area: resized input cells + resizer-inserted cells, priced from Liberty |
| `week2.py` | Week 2 per-design summary and the kill / pass decision (`configs/suite_week2.json`) |
| `programs.py` | W generation / loading with provenance; program = per-segment nets + master swaps; TCL |
| `orfs.py` | ORFS config / SDC; base build + freeze (sha256); program route (met4–met5) and STA; metrics |
| `verify.py` | Yosys → AIGER → own simulators vs numpy; oracle and program mutation controls |
| `invariance.py` | frozen-base checks (validated R3 check + programmable-connectivity check) |
| `pipeline.py` | generate → verify → base → programs → summary, with records |
| `golden.py` | comparison with the historical implementation (BYTE / SEMANTIC / DIFF), incl. the frozen physical base |
| `tables.py`, `snapshot.py` | suite runner + R3 tables vs historical records; provenance snapshot |
| `_legacy.py` | the single import point of the validated research code (reused, never modified) |

**Reuse policy.** The following components were validated in the R3 run, so `_legacy.py` imports them unchanged:
- module RTL generators;
- the synthesis recipe;
- the AIGER simulators;
- cell builders;
- the R3 placer;
- the program-routing TCL;
- the invariance script.

New code covers the parts that were one-off text transforms: the base emitter, access expansion, plans, configs and orchestration. It is golden-tested against the historical outputs.
