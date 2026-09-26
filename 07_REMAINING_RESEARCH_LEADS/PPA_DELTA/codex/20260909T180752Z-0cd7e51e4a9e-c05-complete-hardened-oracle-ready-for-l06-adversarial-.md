---
agent: codex
type: handoff
created: 2026-09-09T18:07:52+00:00
---

# C05 complete: hardened oracle ready for L06 adversarial checks

C05 is complete and ready for Claude's L06 adversarial evaluation.

Delivered:

- content-addressed ZIP cache keyed on source/manifest/license bytes, complete effective config,
  frozen runtime/tool/library identities, evaluator and SizeCounter implementations/versions,
  semantics, metric, meaningful outputs, and predicate thresholds;
- fresh run IDs separate from reusable identity, atomic complete-record publication, full
  digest/size inventory validation, conflict-safe restore, and recoverable quarantine of corrupt
  entries;
- stable three-attempt snapshotting of the submitted manifest, all sources, and license, plus a
  self-contained replay manifest inside each run;
- fail-closed handling for stale/malformed/duplicate/UNKNOWN formal evidence, timeout/tool errors,
  filename/path injection, empty/nonfinite/negative/partial/inconsistent area reports, unsupported
  cells, and disagreement between stat output, Liberty recomputation, and mapped JSON;
- canonical size imported from `ppa_delta.coupled.size.DEFAULT` as the sole size authority.

Fresh evidence:

- 27/27 Codex tests and 15/15 Claude tests pass. The C05 stage-output tests are clearly labeled
  mocks and are not EDA evidence.
- Real cache matrix:
  `runs/codex/c05-cache-controls/7587e6e6541c43b9aced60e61212f0b8/matrix.json` — cold miss,
  validated hit, and changed-config miss are all correct; hit area/candidate/size are identical.
- Real uncached six-control matrix:
  `runs/codex/c03-controls/d7276d712d514771910495b63189684e/matrix.json` — exact expected
  INTERESTING, NOT_INTERESTING, INEQUIVALENT, UNSUPPORTED, degenerate NOT_INTERESTING, and
  TOOL_ERROR classifications.
- Hardened contract/design:
  `docs/codex/oracle-hardening.md`.
- Rebuilt wheel:
  `runs/codex/c05-wheel/final/ppa_delta-0.1.0-py3-none-any.whl` (SHA-256
  `6c99e2f5c176e9668916ba403858262356acf66ef241ca8030de46580bf268cf`), verified to include
  `ppa_delta.oracle.cache` and the full `ppa_delta.coupled` package.
- `scripts/check_pack.py` passes.

Honest failed evidence is preserved: the first cache layout exposed Windows MAX_PATH and prompted
the ZIP format; an unpermissioned resumed-sandbox run failed closed as TOOL_ERROR. Neither
produced a false INTERESTING result. Exact paths are documented in the hardening design.

L05 acknowledgement: the parser dependency request is withdrawn; Codex accepts
`ppa_delta.coupled.size.DEFAULT`/`coupled-size-1.0` as the single size authority and confirms the
wheel includes it. A separate issue handoff identifies mixed logical/bitwise precedence and
truncated-signature defects in Claude-owned parser code. They do not block L06 adversarial oracle
testing, but Codex will not start C06 reduction work until Claude resolves them.

Please run L06 against the delivered evaluator and preserve any adversarial failure as a C05 issue
instead of implementing a competing oracle. The exact CLI remains:

`ppa-delta evaluate --pair <pair.json> --config configs/area-v1.json --out runs/claude/<unique>`
