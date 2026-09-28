# Research harness

Architecture-free infrastructure for hardware/EDA research. It was proven in the UBP project, which was closed by its pre-registered Week 2 test (`14_FABLE_5_1_SCIENTIFIC_DISCOVERY/22_UBP_PROJECT_CLOSEOUT.md`).

A new thesis imports **this** package, not `ubpgen`:
- `ubpgen` is left untouched and keeps reproducing the UBP history;
- every module here is a decoupled copy, tested for equivalence against its original;
- the inventory of what was and was not extracted is in `14_FABLE_5_1_SCIENTIFIC_DISCOVERY/23_REUSABLE_RESEARCH_ASSETS.md`.

```
cd SUPPORTING_ARTIFACTS/research_harness
python3 -m pytest -q -p no:cacheprovider tests      # 24 tests; docker/cache tiers skip cleanly when absent
python3 -m harness.sky130 fetch                     # SKY130 ss/ff corner libraries, sha256-pinned (once)
```

Requirements:
- Python 3.10+ and numpy;
- `zstandard` for the corner fetch only;
- docker with `openroad/orfs:latest` (the image id every UBP result used: `sha256:69df744e…`; check it with `harness.orfs.image_id()`).

## The stage interface

A thesis is a sequence of ten stages. Each stage reads the configuration and earlier records, and appends one record (`harness.records.record` → `append`). Nothing is rewritten. A stage that is already recorded is not re-run, so the suite is resumable.

| # | Stage | The thesis provides | The harness provides | Record |
|---|---|---|---|---|
| 1 | **config** | A JSON config per design point (candidate and every baseline), with a PARAMS table of documented defaults; unknown keys are an error | `records.config_sha256` (the identity of the config) | `config.json` |
| 2 | **generate** | The generator (RTL / netlist / script) | `records.sha256_file` for every generated file; `records.git_state` (a dirty generator tree is flagged) | `generation.json` |
| 3 | **independent verify** | An oracle that shares no code with the generator; stimulus and decode adapters | `oracle.netlist_to_aag` (Yosys, via the Liberty functions), `oracle.read_aag_seq`, `oracle.simulate`, `bus`, `serial_word` | `verify.jsonl` |
| 4 | **mutation control** | At least one design mutant and one reference mutant | `oracle.checked` / `oracle.verdict`: PASS requires a match **and** every mutant rejected | (inside `verify.jsonl`) |
| 5 | **baseline** | The strongest known competitor, implemented through the *same* stages 1–10. It is named before any candidate result (see the rules) | The same functions; `decision.ratio_rule(required=[...])` returns INCOMPLETE until every required baseline is complete | The same record types, per baseline |
| 6 | **physical flow** | The ORFS `config.mk` variables | `orfs.write_config`, `orfs.run_flow`, `orfs.metrics`, `orfs.gds_status`, `orfs.drt_metrics`, `orfs.grt_failure`, `orfs.prune` | `base.json` / `physical.jsonl` (with the ODB sha256) |
| 7 | **extract** | — | `resources/extract.tcl` via `sta.openroad`; `sta.parse_extract` | `signoff.jsonl` |
| 8 | **multi-corner timing** | The custom-cell spec, if any (cloned to every corner) | `sky130.fetch/lib_path`, `liberty.clone_library`, `sta.multi_corner` (tt/ss/ff), `sta.parse_sta`, `sta.period` | `signoff.jsonl` |
| 9 | **metrics** | The figure of merit, fixed in the pre-registration | `accounting.flow_changes` (what the flow added after the floorplan metric), `liberty` NLDM lookups, `decision.sensitivities` | `accounting.json`, summary |
| 10 | **decision** | The pre-registered threshold and the required competitors | `prereg.audit` (the rule was committed before the results), then `decision.ratio_rule` | `decision.json`: PASS / KILL / INCOMPLETE |

The stages the harness cannot provide are the thesis: the generator (2), the oracle (3), the mutants (4) and the physical configuration (6). Everything else is shared.

## Modules

| Module | Origin (unchanged in UBP) | Contents |
|---|---|---|
| `records` | ubpgen/config.py, provenance.py, pipeline.py | canonical config hash, git state, tool versions, append-only JSONL, latest-by-key |
| `decision` | ubpgen/week2.py `decide` | `ratio_rule` (min over competitors vs threshold; INCOMPLETE / KILL / PASS), `sensitivities` |
| `prereg` | new | `audit`: the pre-registration commit is an ancestor of every result commit; `first_version` |
| `oracle` | e6_build.py, ubpgen/verify.py | Yosys → AIGER, cycle simulator, bus decoding, mutation-control verdicts |
| `sky130` | ubpgen/pdk.py | pinned volare ss/ff + ORFS tt, `fetch`, `provenance` |
| `liberty` | ubpgen/liberty.py, access.py, g2_cells.py | reader (area, caps, NLDM, interpolation), `clone_library`, `set_input_max_transition` (replaces the attribute; read it back with `pin_attribute_values`), `cell_areas`, `lef_sizes` |
| `sta` | ubpgen/signoff.py + resources | `openroad` (docker), `multi_corner`, `parse_sta`, `parse_path` (critical-path stages, largest stage), `parse_extract`, `period` |
| `accounting` | ubpgen/accounting.py | `flow_changes`, `area_table`, `flatten`, `def_components` |
| `orfs` | ubpgen/orfs.py | `write_config`, `run_flow`, `paths`, `metrics`, `prune`, `gds_status`, `drt_metrics`, `grt_failure` |

## What the tests establish

- **Committed tier.** No docker is needed:
  - the config hashes equal ubpgen's for every UBP config;
  - every committed Week 2 record hashes its own config;
  - `decision.ratio_rule` reproduces the Week 2 KILL (R = 1.473, strongest competitor A-R2) and every sensitivity;
  - `sta.parse_sta` equals ubpgen's parser on all 147 committed STA logs, and the committed records;
  - `prereg.audit` proves that the Week 2 pre-registration (commit 3274c4c) precedes its results, and rejects the reverse order.
- **Cache tier.** The Liberty reader and editors equal their originals on the ss/ff libraries, including the "last `max_transition` wins" defect control.
- **Runs tier** (docker plus the UBP run directories, which are regenerable and not committed):
  - `accounting.flow_changes` reproduces the committed B60 accounting record exactly;
  - the DRT/GRT parsers and the GDS-failure classifier equal their originals;
  - `extract.tcl` + `sta_corner.tcl` reproduce the ORFS final report's tt worst setup/hold slack of the frozen B60 base;
  - the generic oracle with a 15-line adapter reproduces ubpgen's functional verdict, with the oracle mutant detected, on a real UBP netlist.

## Rules of use

The full list is in `../NEXT_THESIS_RESEARCH_RULES.md`.

- Every result is a record with a config hash and a git state. A number without a record is not a result.
- The decision function runs only on records, and only after `prereg.audit` passes.
- The candidate and the baselines go through the same stages with the same flow, corners and metric. A missing baseline makes the decision INCOMPLETE, never a pass.
- Keep regenerable databases (ODB, DEF, SPEF, GDS) out of git. Commit configs, records, logs and small reports.
