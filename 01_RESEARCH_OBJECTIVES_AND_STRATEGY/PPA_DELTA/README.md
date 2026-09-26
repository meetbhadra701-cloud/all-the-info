# PPA-Delta

PPA-Delta is a research prototype that minimizes two equivalent combinational
Verilog descriptions together while preserving a reproducible mapped-cell-area
regression. It emits a small diagnostic witness with formal proof, area reports,
lineage, tool identities, and a cache-free replay command.

This is a local month-one release candidate, not a published package and not an
RTL optimizer. A retained area difference demonstrates a reproducible synthesis
witness; it does not prove the optimizer's internal cause or a silicon PPA change.

## Host and tool prerequisites

The tested release route is Windows with WSL2 distribution `Ubuntu` and:

- Python 3.11 or newer on Windows (tested with 3.12.14);
- OSS CAD Suite release `20260816` in WSL, including Yosys/EQY 0.68, ABC,
  Z3, and Boolector; and
- the included Nangate45 Liberty file, Apache-2.0 licensed.

Docker is not used. The OSS CAD Suite archive is too large to bundle. Obtain the
exact dated release from the official YosysHQ `oss-cad-suite-build` releases,
unpack it in WSL, and let `ppa-delta doctor` verify every executable hash. The
doctor fails closed if the release, tool bytes, config, or library differs.

## Install from this checkout

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m pip install --no-deps --editable .
$env:PPA_DELTA_PROJECT_ROOT = (Resolve-Path .).Path
$env:PPA_DELTA_EDA_ROOT = "/absolute/wsl/path/to/oss-cad-suite"
.\.venv\Scripts\ppa-delta.exe doctor --config configs\area-v1.json
```

For the packaged kit, replace the editable install with:

```powershell
.\.venv\Scripts\python.exe -m pip install .\dist\ppa_delta-0.1.0-py3-none-any.whl
```

`PPA_DELTA_EDA_ROOT` may be omitted when the suite is at the frozen path in
`coordination/runtime.json`. `PPA_DELTA_WSL_PROJECT_ROOT` is also optional; the
Windows project root is normally translated to `/mnt/<drive>/...` automatically.
These overrides relocate identical artifacts and do not change their recorded
hash identities.

## One-command replay

The release kit contains ten immutable bundles. From its root:

```powershell
$env:PPA_DELTA_PROJECT_ROOT = (Resolve-Path .).Path
$env:PPA_DELTA_EDA_ROOT = "/absolute/wsl/path/to/oss-cad-suite"
.\.venv\Scripts\ppa-delta.exe replay `
  --bundle bundles\a4-share4-add `
  --out runs\codex\a4-fresh `
  --agent codex `
  --no-publish
```

A successful replay exits zero and writes `replay.json` with `status: PASS`,
`cache_hit: false`, exact expected/observed candidate and content hashes, formal
`PASS`, and identical area and size vectors. `--no-publish` is intended for a
standalone kit with no project Obsidian vault; normal checkout runs still publish
evidence automatically.

Replay all ten bundles with the included driver:

```powershell
.\.venv\Scripts\python.exe tools\c12_clean_room.py `
  --root . `
  --eda-root "/absolute/wsl/path/to/oss-cad-suite"
```

## Other commands

```text
ppa-delta evaluate --pair PAIR/pair.json --config configs/area-v1.json --out runs/codex/RUN --agent codex --no-cache
ppa-delta reduce --pair PAIR/pair.json --config configs/area-v1.json --method coupled --out runs/codex/RUN --agent codex --no-cache
ppa-delta compare --suite benchmarks/suites/month-one.json --out runs/codex/RUN --agent codex
ppa-delta export --run runs/codex/RUN --bundle exports/BUNDLE
ppa-delta replay --bundle exports/BUNDLE --out runs/codex/FRESH --agent codex
```

Supported reduction methods are `edit-only`, `independent`, `bugpoint`,
`coupled`, and `coupled-no-matching`. Every proposed witness is accepted only by
the shared compile → EQY equivalence → Nangate45 mapped-area oracle. The frozen
predicate requires a 5% relative increase and an absolute increase of 0.532
library-area units (one `INV_X1`).

See [supported-subset.md](docs/codex/supported-subset.md) for exact syntax and
semantic exclusions, [release-candidate.md](docs/codex/release-candidate.md) for
results and replay structure, and [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md)
for provenance.

## Month-one result and limits

On the frozen synthetic suite, coupled reduction produced a smaller valid final
witness than the best non-coupled baseline on 10/10 pairs, with 23.08% median
final-size advantage and held-out advantage on 3/3. All ten final witnesses are
formally equivalent and retain the measured area regression.

The result has important boundaries:

- all ten pairs are synthetic; public-design relevance and maintainer feedback
  remain unresolved;
- the literal pre-registered Week-4 requirement of removing at least 70% of the
  original AST is met on 0/10 (the alternative “final size at most 70%” reading
  is 7/10, reported but not substituted);
- only combinational, two-state, single-top Verilog in the documented subset is
  supported;
- the metric is mapped standard-cell library area, not timing, power, placement,
  routing, or silicon behavior; and
- scaffold matching helps only the multi-select structures that contain the
  relevant shared control cone; it is null on the other six cases.

The project is Apache-2.0 licensed. It has not been published or externally
reviewed. Month two must not begin without an explicit user decision.
