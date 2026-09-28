# 23 — Reusable research assets (UBP closeout, Phase A2)

UBP is closed (`22_UBP_PROJECT_CLOSEOUT.md`). This inventory separates what was specific to UBP from infrastructure a new thesis can reuse.

**Policy.** Nothing in `ubpgen/` or `experiments/scripts/` was moved, renamed or edited. The historical tests, goldens and records still pass unchanged (see §4).

Generic components that could be decoupled safely were **copied** into a new package, `SUPPORTING_ARTIFACTS/research_harness/harness/`:
- the dependency on UBP's `_legacy.py` import shim was replaced by explicit parameters;
- the harness tests check each copy against its original, on committed data and on the UBP runs.

Everything else is documented here with its path and left where it works.

Paths are relative to the repository root. "UBP" below means `14_FABLE_5_1_SCIENTIFIC_DISCOVERY/`.

---

## 1. UBP-specific assets (keep for the record; do not reuse as architecture)

| Asset | Path | Purpose | Why it is UBP-specific |
|---|---|---|---|
| Architecture model | UBP/ubpgen/arch.py | Patterns, lines, bands, leaves, latency, output width | Encodes the UBP-g block-pattern fabric |
| RTL generators | UBP/ubpgen/rtl.py; UBP/experiments/scripts/e6_build.py (`gen_rtl`, `negline_rtl`, `tree_rtl`); g3_build.py (`ctrl_rtl`, `pline_rtl`, `prow_rtl`) | Bit-serial UBP modules, the negator, the serial adder tree, and the P2 bit-plane popcount | Arithmetic of this fabric and its two baselines |
| Base-netlist emitter | UBP/ubpgen/netlist.py; UBP/experiments/scripts/g2_build.py | W-independent top netlist with via sites and line taps | Regime-V programmable boundary |
| Weight programs | UBP/ubpgen/programs.py; UBP/experiments/scripts/g2_build.py | W → via-site connections / master swaps (met4/met5 program) | Weight programming by upper-layer vias |
| Access modes and placement | UBP/ubpgen/access.py; r3_build.py; g2_struct.py; r3_design_model.py; g2_track_model.py | R2 single tap, R3 segmented taps, W-blind band placement, placer TCL, the track-demand model | The UBP layout co-design |
| Custom cells | UBP/experiments/scripts/g2_cells.py; r3_build.py (`LTAP2_LEF`); access.py (`w2_lef`, `w2_lib`) | Via-site, LTAP, LTAP2 and LTAPB/LTAPBW abstractions | Cells that model UBP's programmable boundary |
| Tap-class rule | UBP/ubpgen/drivers.py | `w2_load_rule`: the smallest buf_k meeting slew S at the W-independent worst-case load | The load formula is UBP geometry. The method (worst-case load from a W-blind plan + NLDM lookup) is generic; see §3 |
| Program routing | UBP/experiments/scripts/g2_program.tcl | Delete base nets, apply the program, route met4–met5 only | UBP's two-tier base / program flow |
| UBP invariance extras | UBP/ubpgen/invariance.py (`program_connectivity`) | Only `lt_*/Z` and `vs_*/A` pins on `pgm_*` nets | Names UBP's cells |
| Week 1 / Week 2 summaries | UBP/ubpgen/tables.py; week2.py (`design`, `axt`, `markdown`) | UBP tables and the Week 2 A×T variants | The rows are UBP designs; the decision core is generic (§2) |
| Historical collectors | UBP/experiments/scripts/e5_collect.py; g2_r2_collect.py; r3_collect.py; r3_fairness.py | Per-gate pre-registered criteria | Gate-specific |

---

## 2. Generic infrastructure

Legend (reuse status):
- **E**: extracted into `research_harness`, decoupled and equivalence-tested.
- **D**: directly reusable in place (no UBP imports, or trivially parameterized).
- **G**: needs generalizing before reuse; the needed change is stated.

| # | Asset | Current path (original) | Harness path | Purpose | Architecture-specific dependency | Status | What would need generalizing |
|---|---|---|---|---|---|---|---|
| 1 | ORFS / OpenROAD runner | UBP/ubpgen/orfs.py (`_docker`, `build_base`, `_freeze`, `prune_base`, `base_metrics`) | harness/orfs.py (`docker`, `write_config`, `run_flow`, `metrics`, `prune`, `paths`) | Docker ORFS flow with rc capture, freeze by ODB sha256, stage metrics, pruning of regenerable databases | `config_mk` builds UBP's config.mk (custom LEF/LIB, POST_PDN placer, dont_touch hook) | E | The caller supplies the config.mk variables. The pinned image id must be re-checked (`orfs.image_id()`). |
| 2 | Expected-failure classifier | UBP/ubpgen/orfs.py (`gds_status`) | harness/orfs.py (`gds_status`) | The GDS merge fails only because of abstract (LEF-only) cells; anything else is a real failure | UBP cell names | E | Abstract cells are a parameter |
| 3 | Routing / DRC / congestion parsers | UBP/ubpgen/orfs.py (`route_metrics`, `base_metrics`) | harness/orfs.py (`drt_metrics`, `grt_failure`, `metrics`) | DRT trajectory, final violations, GRT usage and overflow per layer, wire length, vias, GRT error codes | `G2_RESULT` marker of g2_program.tcl | E | none |
| 4 | OpenRCX extraction | UBP/ubpgen/resources/signoff_extract.tcl; signoff.py (`run`) | harness/resources/extract.tcl; harness/sta.py (`openroad`, `parse_extract`) | Platform-rules extraction, exactly as the ORFS final report | Counted `pgm_*` nets | E | Net prefix optional |
| 5 | Multi-corner STA | UBP/ubpgen/resources/signoff_sta.tcl; signoff.py (`parse_sta`, `parse_path`, `corner_libs`) | harness/resources/sta_corner.tcl; harness/sta.py (`multi_corner`, `parse_sta`, `parse_path`, `period`) | One OpenSTA session per corner, with each corner's standard + custom libraries; critical-path decomposition | Tap/via-site slew probes and spine-driver histogram | E | The UBP probes are dropped; "through" cell class and net/pin classes are parameters |
| 6 | Merged-DEF builder | UBP/ubpgen/signoff.py (`merge_def`) | — | Base DEF + program COMPONENTS + `pgm_*` nets for extraction | Two-tier base/program designs only | D (in place) | Only needed for a two-tier design; reuse as-is if one recurs |
| 7 | SKY130 corner acquisition and hashing | UBP/ubpgen/pdk.py | harness/sky130.py | volare ss/ff pinned by tarball and file sha256; the ORFS tt pinned | Cache path under UBP | E | Cache is a parameter (`RESEARCH_HARNESS_SKY130`); the UBP cache verifies as-is |
| 8 | Liberty reader | UBP/ubpgen/liberty.py | harness/liberty.py | Cell/pin blocks, area, pin caps, NLDM tables, bilinear interpolation, output transition | Loads via `_legacy.IMAGE`/`pdk` | E | Functions take text; `image_file` loads from the image |
| 9 | Liberty editing and corner cloning | UBP/experiments/scripts/g2_cells.py (`extract_cell`, `lib_cell`); ubpgen/access.py (`_lib_header`, `_set_input_max_transition`, `clone_*_lib`) | harness/liberty.py (`clone_cell`, `header`, `set_input_max_transition`, `clone_library`, `pin_attribute_values`) | Custom cells defined from standard cells at every corner; attribute edits that replace rather than shadow | UBP cell list | E | `clone_library` takes a cell spec list |
| 10 | Physical area accounting | UBP/ubpgen/accounting.py | harness/accounting.py (`flow_changes`, `area_table`, `flatten`, `def_components`) | What the flow resized/inserted/removed after the floorplan metric; excluded classes listed | `access.custom_libs` paths | E | Inputs are texts plus an area table |
| 11 | Configuration: explicit, validated, hashable | UBP/ubpgen/config.py | harness/records.py (`config_sha256`) | Canonical JSON sha256 as config identity; PARAMS table with defaults; unknown keys rejected | PARAMS are UBP parameters | E (hash) / G (schema) | The PARAMS/validate/with_overrides pattern should be re-instantiated per thesis (copy the 60-line skeleton, new PARAMS) |
| 12 | Provenance records | UBP/ubpgen/provenance.py; pipeline.py (`_append`, `file_hashes`) | harness/records.py (`git_state`, `tool_versions`, `record`, `append`, `latest_by`, `sha256_file`) | Every record: time, command, commit, dirty flag, tool versions, config hash, result; append-only JSONL | Tracked paths and image fixed | E | Parameters |
| 13 | Pre-registered decision rule | UBP/ubpgen/week2.py (`decide`) | harness/decision.py (`ratio_rule`, `sensitivities`) | min over the complete competitors of metric ratio vs threshold; INCOMPLETE if a required competitor is missing; candidate validity; sensitivities reported but never decisive | UBP design keys | E | none |
| 14 | Pre-registration audit | (manual in UBP: 09_PREREGISTRATION.md, 21 §1, configs/suite_week2.json committed before builds) | harness/prereg.py (`audit`, `first_version`) | Git proof that the rule was committed before its results; the rule of record is the first version | — | E (new) | none |
| 15 | Independent functional oracle | UBP/ubpgen/verify.py (`to_aag`, `simulate`); experiments/scripts/e6_build.py (`read_aag_seq`, `sim_seq`); g3_build.py (`sim_bitplane`) | harness/oracle.py (`netlist_to_aag`, `read_aag_seq`, `simulate`, `bus`, `serial_word`) | Netlist → Yosys (Liberty functions) → AIGER → own cycle simulator vs an independent oracle | UBP stimulus / decode | E | Stimulus and decode are callables. A 15-line adapter reproduces the UBP check (test `test_oracle_reproduces_ubp_functional_check_on_a_real_netlist`) |
| 16 | Mutation controls | UBP/ubpgen/verify.py (`oracle_mutation`, `program_mutation`) | harness/oracle.py (`verdict`, `checked`) | A check must reject every mutant; a blind check fails even if it matched | Mutations of W / of the program | E (framework) / G (mutants) | Mutants are design-specific and must be written per thesis |
| 17 | Frozen-artifact invariance | UBP/experiments/scripts/r3_invariance.py; ubpgen/invariance.py | — | ODB sha256 unchanged, placement identical, masters, layers, special nets identical after a later step | Regime-V layer rules | G | The pattern (hash + section diff of DEF COMPONENTS/SPECIALNETS) is generic; the layer and master rules are UBP's |
| 18 | Golden reproduction | UBP/ubpgen/golden.py; ubpgen/golden/manifest.json | — | Generated vs historical: BYTE, SEMANTIC (documented normalization), or FAIL; nothing accepted silently | Compares UBP files | G | The three-way comparison and manifest format are reusable; the normalizers are UBP's |
| 19 | Parameterized runner / resumable suites | UBP/ubpgen/pipeline.py; tables.py; __main__.py | — | config → generate → verify → base → programs → sign-off → summary; resumable (recorded steps not re-run) | UBP stages | G | The stage interface is written up in SUPPORTING_ARTIFACTS/research_harness/README.md; a new thesis implements its own stages |
| 20 | Results snapshot | UBP/ubpgen/snapshot.py | — | Copy only small, provenance-bearing outputs into git (no ODB/DEF/netlists) | UBP record names | D | Paths |
| 21 | Result tables | UBP/ubpgen/tables.py (`markdown`); week2.py (`markdown`) | — | Every measured value next to its historical or pre-registered reference; differences listed | UBP columns | G | Columns |
| 22 | Baseline accounting conventions | UBP/ubpgen/week2.py (`axt`, `counterpart_sizing`); 21_WEEK2_TIMING_CLOSURE.md §1.7 | harness/decision.py (sensitivities), harness/accounting.py | Same metric, same flow, same corner for every design; physical costs counted for all; conservative vs nominal readings pre-declared | A×T definition | G | The discipline, not the code, transfers: see 24 lessons 1–2 |
| 23 | Failure-mode handling | UBP/ubpgen/orfs.py (`gds_status`); week2.json `failed_points`; configs/suite_week2.json (fallbacks) | harness/orfs.py | Classify expected vs unexpected failures; record failed pre-registered points with their error code; apply the pre-registered fallback, never an ad-hoc one | — | E (classifier) / D (records) | none |
| 24 | Deterministic regression tests | UBP/ubpgen/tests/ (106 tests: golden byte-compare, functional, mutation, invariance, illegal params, Week 2) | SUPPORTING_ARTIFACTS/research_harness/tests/test_harness.py | Every claim backed by a test that fails when the claim breaks | — | D (pattern) | — |
| 25 | Wiring decomposition | UBP/experiments/scripts/select_wiring.py | — | Routed wirelength split into select vs module-internal wiring from a finished ORFS run | Module naming | G | Instance-prefix classes as parameters |
| 26 | Post-hoc what-if TCL | UBP/experiments/scripts/r3_whatif_drivers.tcl; r3_sta_extracted.tcl; r3_prog_spef.py | — | Sensitivity studies kept separate from the decisive test | UBP cells | G | Reference only |

### What is deliberately NOT extracted

- **`ubpgen/_legacy.py` and its imports.** They are the reason the originals cannot be imported without the UBP scripts. Rewriting them would risk historical reproducibility for no gain.
- **`merge_def` (row 6).** It is only meaningful for a base/program two-tier design.
- **The `w2_load_rule`.** The generic idea is written into 24 (lesson 2) instead.

---

## 3. Generic methods (no code to copy, but proven)

- **Worst-case, input-independent sizing.** Size shared drivers at the worst-case load that any input can present. Compute that load from an input-blind plan, not from one instance, and enforce it in the flow through a Liberty attribute (`max_transition` on the load pin) rather than hand-inserted buffers (21 §1.4).
- **One sign-off definition for every design.** Use the same extraction, the same corners and the same metric for the candidate and every baseline. Re-time the historical rows with the same sign-off before comparing (21 §1.6, §2.2).
- **Kill rule = the strongest competitor, conservative corner.** Nominal readings are reported beside it and are never the headline (22 §6).
- **Resumable suites with append-only records.** A failed or interrupted run leaves every recorded step intact. The summary tabulates only what is recorded and reports missing points as missing.

---

## 4. Reproducibility after this extraction

| Check | Command | Result (this closeout) |
|---|---|---|
| Historical ubpgen suite (unchanged code) | `cd 14_FABLE_5_1_SCIENTIFIC_DISCOVERY && python3 -m pytest -q -p no:cacheprovider ubpgen/tests` | **106 passed** (272 s), after the extraction and the notices |
| Harness (equivalence with the originals) | `cd SUPPORTING_ARTIFACTS/research_harness && python3 -m pytest -q -p no:cacheprovider tests` | **24 passed** (committed, cache and runs tiers) |
| Goldens | `ubpgen/tests/test_golden.py` (inside the suite) | Byte/semantic comparison against `ubpgen/golden/manifest.json`: passed (inside the 106) |

The harness's docker-tier tests re-derive, from the frozen W2 B60 base and with the harness's own TCL templates:
- the OpenRCX extraction;
- the tt worst setup/hold slack of the ORFS final report;
- the committed Week 2 accounting record, byte-for-byte as JSON;
- the committed functional verdict on a real UBP netlist;
- all 147 committed sign-off corner records.

Three of those records, the first sign-off run `golden_r3_ubp3_u60/w1`, were written by an earlier path parser without per-stage rows; every number in them still matches.
