---
agent: codex
type: evidence
created: 2026-09-09T16:09:01+00:00
---

# C03 real evaluator verified

# C03 real smoke evaluator complete

Classification: OBSERVED and IMPLEMENTED. Date: September 9, 2026.

## Delivered

- `src/ppa_delta/oracle/process.py` launches only explicit argv arrays with
  `shell=False`, closed stdin, per-stage timeout, and separate raw stdout and
  stderr logs. Missing executables and timeouts remain distinct outcomes.
- `src/ppa_delta/oracle/evaluator.py` snapshots sources immutably, verifies
  source/config/runtime/library hashes, and executes inspectable parse/check,
  formal, synthesis, and predicate stages.
- Explicit top/interface checks reject unsupported latches, memories,
  blackboxes, inouts, unknown-state constants, width/direction mismatches,
  hierarchy errors, and structurally unsafe sources before qualification.
- The EQY adapter requires a nonempty partition list, PASS for every
  partition, the aggregate PASS artifact, and both complete-success log
  markers. It does not infer equivalence from exit status alone.
- Mapped area is recomputed from every mapped cell against the frozen
  Nangate45 Liberty. Missing cells, partial mapping, malformed/negative/
  nonfinite/contradictory metrics, and zero-area inconsistencies fail closed.
- The meaningful-output backward-cone guard requires a mapped cell and an
  actual input dependency. A genuine zero-cell Yosys report is normalized
  only to permit this guard to classify it NOT_INTERESTING; no zero-area
  witness can become INTERESTING.
- Every invocation uses a new directory under `runs/codex/` or
  `runs/claude/`, writes atomic `result.json` plus `summary.txt`, preserves raw
  logs/scripts/reports, and records unique project-relative run and artifact
  paths.
- `ppa-delta doctor` and `ppa-delta evaluate` are active. Future
  reduce/replay/compare commands continue to fail closed until their tasks.
- C03 intentionally performs no reusable caching; `cache_hit` is false. C05
  owns content-addressed cache hardening.
- AST fields remain explicitly labeled `UNAVAILABLE_PRE_L05` while source
  bytes are exact. Claude owns the canonical `SizeCounter` implementation at
  L05; this does not affect L03 area/equivalence qualification.

## Real control matrix

Fresh run: `runs/codex/c03-controls/03e864eea5454ff89a233745fa4b8c56/matrix.json`.

| Control | Expected | Observed | Formal | Area before -> after |
|---|---|---|---|---|
| equivalent regression | INTERESTING | INTERESTING | PASS | 35.378 -> 48.412 |
| equal area | NOT_INTERESTING | NOT_INTERESTING | PASS | 20.482 -> 20.482 |
| inequivalent | INEQUIVALENT | INEQUIVALENT | FAIL | not measured |
| unsupported latch | UNSUPPORTED | UNSUPPORTED | NOT_RUN | not measured |
| degenerate constant | NOT_INTERESTING | NOT_INTERESTING | PASS | rejected by meaningful-output guard |
| missing synthesis tool | TOOL_ERROR | TOOL_ERROR | NOT_RUN | not measured |

The integration script additionally asserts the formal status and that run
IDs/log paths are unique and project-relative. The earlier diagnostic run
`runs/codex/c03-controls/438ee5f173c14bc68979c0cc774aef6d`
is retained: it exposed Yosys's omitted area member for a zero-cell design and
was not rewritten or deleted.

## Verification

- Real final EDA matrix: 6/6 expected classifications and formal statuses.
- Installed CLI end to end:
  `runs/codex/c03-cli-evaluate-20260909T161000Z/result.json` is INTERESTING,
  formal PASS, area 35.378 -> 48.412.
- Host contract/process/schema tests: 18/18 PASS.
- Coordination helper tests: 10/10 PASS.
- Actual timeout and missing-executable tests: PASS.
- `compileall`: PASS.
- `pip check`: no broken requirements.
- `ppa-delta doctor`: runtime/config/library/toolchain identities agree.

C03 acceptance is satisfied. Next: hand Claude the exact L03 evaluator argv
and wait for qualified pair manifests before C04.
