# C12 clean replay and local release

Owner: Codex · Date: 2026-09-10 · Classification: **OBSERVED** (real EDA and
wheel-install evidence).

## Release artifact

The final unpublished kit is
`runs/codex/c12-release-candidate-20260910T192551Z-final/`. It contains 962
checksummed files: the 0.1.0 wheel, exact dependency lock, frozen runtime/config,
Apache-2.0 Nangate45 library and notices, original ten-pair suite, ten final
replay bundles, supported-subset/usage documentation, clean replay driver, and
the opt-in CI workflow. The external OSS CAD Suite archive is not redistributed.

Wheel SHA-256:
`032edb059c3d4b318ff76a89e14b3e1dd173c8f73d0aab85956f671c3e6cd89f`.
The release inventory, every nested bundle inventory, and the required wheel
modules/schemas match in
`runs/codex/c12-release-audit-20260910T193300Z/audit.json`.

## Clean installation and runtime check

Codex copied the kit to a new source-free directory,
`runs/codex/c12-clean-room-20260910T193000Z/`, created a fresh Windows Python
3.12 venv, installed the six exact `requirements.lock` dependencies, then
installed only the built wheel. The loaded package path was under that venv's
`site-packages`; no `src/` tree existed in the clean root.

The wheel-installed public `ppa-delta doctor` returned `ok: true` after checking:

- suite release `20260816`;
- exact hashes for the OSS CAD Suite manifest, Yosys, EQY, ABC, Z3, and
  Boolector;
- the frozen config/toolchain identity; and
- the included Nangate45 library hash.

The runtime/config hashes and scientific thresholds were not changed. Relocation
variables alter paths only, and doctor rejects nonmatching artifact bytes.

## Ten final uncached replays

The clean driver ran each bundle through a new evaluator directory with cache
disabled. All ten are `INTERESTING`, formal `PASS`, and exact on candidate/source
hashes, area, and size:

| Pair | Final AST | Area before → after | Relative gap |
|---|---:|---:|---:|
| f1-mux-share-add | 30 | 47.614 → 57.988 | 21.79% |
| a2-share3-add | 39 | 47.614 → 57.988 | 21.79% |
| a3-share-sub | 35 | 66.234 → 79.002 | 19.28% |
| a5-share3-sub | 44 | 66.234 → 79.002 | 19.28% |
| a6-share2-add-w6 | 30 | 36.176 → 42.028 | 16.18% |
| m1-share2-mult4 | 32 | 82.194 → 93.366 | 13.59% |
| f2s-factor-mult4 | 28 | 125.020 → 162.526 | 30.00% |
| a4-share4-add (held-out) | 48 | 47.614 → 57.988 | 21.79% |
| m2-share3-mult4 (held-out) | 43 | 82.194 → 93.366 | 13.59% |
| f3s-factor3-mult4 (held-out) | 32 | 125.020 → 162.526 | 30.00% |

Aggregate: **10/10 PASS**, zero cache hits, 57.281 driver seconds. Primary
evidence is
`runs/codex/c12-clean-room-20260910T193000Z/runs/codex/c12-clean-replay/replay-matrix.json`;
each row links its own `replay.json` and full raw EQY/Yosys logs.

No witness was invalidated, so Claude's L12 analysis does not need recomputation.

## Release-facing changes

- Wheel/source execution discovers a support root or accepts
  `PPA_DELTA_PROJECT_ROOT`; WSL and EDA roots are relocatable explicitly.
- `doctor` now probes and hashes the real WSL tool files rather than checking
  only JSON agreement.
- `--no-publish` permits standalone evaluate/reduce/replay/compare while leaving
  the normal project-vault publication default intact.
- Bugpoint resolves its installed predicate module, current Python executable,
  and effective EDA root instead of hardcoded checkout paths.
- Root README, syntax/metric limits, provenance, install/replay commands, and an
  opt-in CI workflow are included.

## Failures and boundaries

One sandboxed dependency-install attempt could not access the package index; the
approved retry installed the exact pins. An earlier package assembly attempt
could not read a wheel created under the elevated build context; it stopped
before bundle assembly and is not the release artifact. Both are packaging
environment failures, not EDA evidence, and neither is used by the final audit.

C12 does not change L12's scientific interpretation: the literal 70%-reduction
bar remains 0/10, all pairs remain synthetic, and external maintainer relevance
remains unresolved. The CI EDA job is a draft requiring a configured self-hosted
Windows+WSL2 runner; it is separately selected as `controls` or `month-one` and
was not published or remotely executed.
