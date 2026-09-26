---
agent: codex
type: experiment
created: 2026-09-10T22:43:03+00:00
---

# C12 source-free release replay passes ten of ten

# C12 completed: source-free wheel replay and local release candidate

Classification: **OBSERVED** (real WSL2 EDA, wheel installation, checksum audit).

## Result

The definitive unpublished release kit is
`runs/codex/c12-release-candidate-20260910T192551Z-final/`. Its 962-file
SHA-256 inventory and all ten nested bundle inventories verify. Wheel SHA-256 is
`032edb059c3d4b318ff76a89e14b3e1dd173c8f73d0aab85956f671c3e6cd89f`;
the wheel contains the coupled reducer, oracle, bugpoint predicate, replay code,
and packaged schemas.

The kit was copied into the source-free root
`runs/codex/c12-clean-room-20260910T193000Z/`. A new Python 3.12 venv installed
the six exact dependency pins and only the release wheel. The imported
`ppa_delta` came from that venv's `site-packages`; no source tree was present.

The wheel-installed doctor matched OSS CAD Suite 20260816, the suite manifest,
Yosys, EQY, ABC, Z3, Boolector, the frozen config/toolchain identity, and the
included Nangate45 Liberty hash. The clean driver replayed all ten bundles with
cache disabled: **10/10 PASS**, each `INTERESTING`, formal `PASS`, and exact on
candidate/source hashes, area, and AST size. Runtime was 57.281 driver seconds.
No witness was invalidated; L12 does not need recomputation.

## Release behavior

The project/support root, WSL mapping, and exact EDA artifact location are now
relocatable by explicit environment variables. Doctor hashes the effective tool
files before replay. Standalone evaluate/reduce/replay/compare can use
`--no-publish`, which suppresses only the unavailable project vault, not any
scientific stage. Bugpoint now resolves the installed predicate/Python and
effective EDA root. README, supported subset, limitations, licensing/provenance,
and an opt-in CI workflow are included.

## Verification

- 10 control-helper tests PASS.
- 58 Codex unit/integration-contract tests PASS.
- 43 Claude tests PASS unchanged.
- `scripts/check_pack.py` PASS.
- Release audit PASS:
  `runs/codex/c12-release-audit-20260910T193300Z/audit.json`.
- Clean replay matrix PASS:
  `runs/codex/c12-clean-room-20260910T193000Z/runs/codex/c12-clean-replay/replay-matrix.json`.
- Full report: `docs/codex/c12-clean-replay-release.md`.

## Failures and limits

An initial sandboxed dependency installation lacked network access; the approved
retry installed the exact pins. One superseded package-assembly attempt stopped
before bundle copying because its elevated-build wheel was unreadable in the
sandbox. Neither is scientific evidence or the final artifact.

The literal 70%-original-reduction Week-4 bar remains 0/10, every benchmark is
synthetic, and no external maintainer review occurred. C12 verifies packaging
and reproducibility only; it does not alter L12's interpretation, publish
anything, or authorize month two.

Next: Claude L13 scores maintainer relevance and casts its Week-4 vote. Codex
then performs C13 against the raw artifacts and stops at the month-one decision.
