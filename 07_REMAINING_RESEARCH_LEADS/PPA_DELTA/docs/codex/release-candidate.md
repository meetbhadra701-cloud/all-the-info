# C12 local release candidate

Owner: Codex · Scope: local, unpublished month-one prototype.

## Contents

The release kit contains the `ppa_delta-0.1.0-py3-none-any.whl`, exact dependency
lock, runtime/config manifests, Apache-2.0 Nangate45 Liberty file, ten immutable
replay bundles, setup documentation, and the clean-room replay driver. The OSS
CAD Suite binary distribution is referenced by exact release and hashes but is
not redistributed.

Each bundle contains the final before/after RTL, pair manifest and license,
frozen config/runtime identity, uncached proof and area evidence, transformation
trace when available, and SHA-256 inventory. Replay verifies that inventory
before EDA and compares candidate/content hashes, status, formal result, area,
size, config, toolchain, and library identity exactly.

## Frozen technical result

- ten of ten coupled final witnesses are valid in the C11 matrix;
- coupled is smaller than the best non-coupled baseline on ten of ten;
- median final-size advantage is 23.08%;
- all three held-out cases show an advantage;
- scaffold matching improves the two held-out scaffold cases, a4 and m2;
- coupled cost was 247 proposals, 267 evaluations/EDA executions, 1,863 tool
  commands, and 1,402 aggregate method-seconds.

The full machine-derived table is in `analysis/month-one-report.md` and the raw
matrix is under `runs/codex/c11-month-one-six-method-20260910T174500Z/` in the
development checkout.

## Honest decision boundaries

The literal requirement “at least 70% original pair AST reduction” is 0/10 and
therefore fails. Seven of ten end at or below 70% of their original size, but
that alternative interpretation is reported separately and does not rewrite the
pre-registered gate. All ten examples are synthetic and no synthesis maintainer
has reviewed them, so practical relevance is unresolved.

The clean-room C12 replay verifies reproducibility and packaging only. It does
not repair those scientific limitations, tune the frozen reducer, or authorize
publication or month-two work.

## Relocation contract

`PPA_DELTA_PROJECT_ROOT` selects the support root containing `coordination/`,
`configs/`, `bundles/`, and `runs/`. `PPA_DELTA_EDA_ROOT` relocates the exact OSS
CAD Suite bytes. `PPA_DELTA_WSL_PROJECT_ROOT` is an optional override when the
automatic Windows-drive mapping is unsuitable. `ppa-delta doctor` validates the
effective roots and every frozen component hash before replay.

Standalone commands should pass `--no-publish`; this skips only project-vault
documentation and never skips or changes scientific validation.

## C12 verification

The definitive wheel is SHA-256
`032edb059c3d4b318ff76a89e14b3e1dd173c8f73d0aab85956f671c3e6cd89f`.
It was installed with the locked dependencies into a new venv in a source-free
support root. The wheel-installed doctor matched OSS CAD Suite 20260816, all six
recorded executable/manifest hashes, the frozen config, and the Liberty hash.

That install replayed all ten bundles with cache disabled in 57.281 aggregate
driver seconds. All ten returned `INTERESTING` with formal `PASS`; candidate
hash, source hashes, area vector, and AST-size vector matched their bundle
expectations exactly. The aggregate audit also verified all 962 release-file
checksums, all ten bundle inventories, packaged schemas/coupled/oracle modules,
source-free installation, and standalone `--no-publish` commands.

Evidence:

- `runs/codex/c12-release-candidate-20260910T192551Z-final/`
- `runs/codex/c12-clean-room-20260910T193000Z/runs/codex/c12-clean-replay/replay-matrix.json`
- `runs/codex/c12-release-audit-20260910T193300Z/audit.json`
