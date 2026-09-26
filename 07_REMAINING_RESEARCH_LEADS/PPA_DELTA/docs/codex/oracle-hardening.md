# Oracle hardening and cache contract (C05)

Owner: Codex · Task C05 · 2026-09-09 · Interface version 1.0 · Evaluator version
`oracle-1.1` · Cache format `evaluation-cache-1.0`.

## Reusable identity and run identity

Every invocation receives a new immutable directory and `run_id`. Reuse is keyed separately by
the SHA-256 of canonical JSON containing all of the following:

- the stable-copied original manifest, rewritten replay manifest, before/after source bytes, and
  provenance-license bytes;
- the complete effective area configuration and frozen runtime document;
- evaluator version and an implementation hash over the oracle, public contracts, public
  schemas, and Claude-owned parser/size-counter implementation;
- the size-counter version, toolchain hash, library hash, semantics, metric, meaningful outputs,
  and absolute/relative predicate parameters.

A cache hit is rebound to the new run identity and timestamps. Copied logs point into the new run
directory, while the source-run ID and historical command argv remain explicit provenance.

## Stable input snapshot

The evaluator first stable-copies `pair.json`, validating equal hashes before/read/after. It then
does the same for every source and license file, with three bounded attempts. It writes a
replayable `input/pair.json` whose relative paths resolve entirely inside the run snapshot, and
retains the exact submitted bytes as `input/original-pair.json`. A changing source raises an
error; a pre-existing run directory is rejected so stale artifacts cannot be mistaken for output.

Manifest filename validation rejects absolute paths, traversal, shell metacharacters, separators,
and other values outside the frozen safe-name grammar. External programs are launched with argv
arrays; generated Yosys paths are quoted and reject newline, carriage-return, and quote injection.

## Cache publication and restoration

Complete runs are atomically published as ZIP archives beneath
`.cache/ppa-delta/evaluations-v1/`. The archive form avoids Windows path-length failures while
retaining every run artifact. Publication requires schema-valid `result.json` and `summary.txt`.
The inventory records every member's SHA-256 and byte length; symlinks, unsafe names, duplicate
entries, incomplete inventories, and changed bytes are rejected. Restoration validates the whole
archive before writing any artifact. Invalid entries are recoverably renamed with an
`.invalid.<uuid>.zip` suffix rather than silently deleted.

The cache records finished positive and negative classifications. It never converts any status
to `INTERESTING`: a hit must match candidate, effective-config, toolchain, library, thresholds,
content hashes, and cache key before it can be rebound.

## Fail-closed stage evidence

- Formal PASS requires at least one uniquely named, path-safe partition; a PASS status for every
  partition and selected strategy; the aggregate PASS marker; and both expected EQY completion
  messages. Missing, malformed, duplicate, UNKNOWN, or stale-only evidence returns
  `FORMAL_UNKNOWN`, never PASS.
- Area extraction requires finite nonnegative area, nonnegative integer cell totals, positive
  integer per-type counts whose sum matches the total, positive Liberty area for every mapped
  type, agreement between reported and recomputed area, and exact agreement with the mapped JSON
  top's cell types/counts. Empty, partial, malformed, negative, nonfinite, unsupported, and
  inconsistent reports return `INVALID_METRIC`.
- Timeout and executable-start failure remain distinct and preserve stdout/stderr. Unsupported
  syntax, latches/sequential cells, memories, X/Z, blackboxes, unresolved modules, bad interfaces,
  and degenerate outputs cannot reach `INTERESTING`.
- Canonical size is imported from `ppa_delta.coupled.size.DEFAULT`; the oracle does not maintain a
  competing AST-size definition.

## Verification evidence

- Unit/adversarial suite: `tests/codex/test_oracle_hardening.py`; 27/27 Codex tests pass in total.
  Stage outputs in those tests are mocks and are not EDA evidence.
- Peer parser/size suite: 15/15 Claude tests pass.
- Real cache control:
  `runs/codex/c05-cache-controls/7587e6e6541c43b9aced60e61212f0b8/matrix.json`.
  It records a cold `INTERESTING` miss, a validated hit with identical area/candidate/size, and a
  changed-config `INTERESTING` miss with a different config hash and cache key.
- Fresh real six-case matrix:
  `runs/codex/c03-controls/d7276d712d514771910495b63189684e/matrix.json`.
  All expected classifications match with caching disabled.
- Wheel audit:
  `runs/codex/c05-wheel/final/ppa_delta-0.1.0-py3-none-any.whl`, SHA-256
  `6c99e2f5c176e9668916ba403858262356acf66ef241ca8030de46580bf268cf`.
  It contains both `ppa_delta.oracle.cache` and the complete `ppa_delta.coupled` package.

Preserved failed controls are evidence, not superseded claims: the directory-form cache attempt
at `runs/codex/c05-cache-controls/22eea5b1a5c04aed99d12e08eec89d21/` exposed Windows
`MAX_PATH`; the sandbox-denied WSL attempt at
`runs/codex/c05-cache-controls/baed19fd918748d1b862f409b931eeff/` returned/cached
`TOOL_ERROR` rather than producing a false result. The final ZIP implementation and permissioned
WSL reruns above supersede those attempts.
