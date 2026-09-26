---
agent: codex
type: experiment
created: 2026-09-09T10:13:24+00:00
---

# C01 runtime and real EDA smoke verified

# C01 runtime and environment complete

Classification: OBSERVED. Date: September 9, 2026.

## Outcome

C01 acceptance is met on the selected WSL2 route. A real EQY proof and real
Yosys/ABC mapped-area measurement both ran successfully. The frozen metadata
is in `coordination/runtime.json`; raw evidence is in
`runs/codex/c01-smoke-20260909T101000Z/`.

No subagents, additional model sessions, model APIs, or delegating workflows
were used.

## Host and route

- Host: Microsoft Windows NT 10.0.26200.0; PowerShell 7.6.5.
- Host Python alias observation: neither `python` nor `py` is on PATH.
- Bootstrap Python: 3.12.14 at the delivery-time absolute path recorded in
  `coordination/runtime.json`.
- Project environment: `.venv\Scripts\python.exe`, Python 3.12.14, pip 25.0.1.
- Git executable: 2.55.0.windows.3. This project is not currently inside a Git
  repository; no nested repository was created.
- Docker client: 29.6.1. The daemon is not running, so Docker is explicitly
  not the selected route.
- Selected EDA route: WSL 2.7.10.0, Ubuntu 26.04 LTS, kernel
  6.18.33.2-microsoft-standard-WSL2.
- Windows/WSL shared-tree check: `AGENTS.md` had SHA-256
  `3cea049fa25330a0b64ead7ea2896e7d63951c55d71a6269f6d13278dddc232d`
  through the `/mnt/c/...` view.

## Frozen EDA identity

- OSS CAD Suite release: 20260816.
- Yosys: 0.68+71, git sha1 `dbe5b7c03-dirty`.
- EQY: 0.68.
- ABC: 1.01, compiled August 16, 2026 02:10:07.
- Z3: 4.15.5; Boolector: 3.2.4.
- Aggregate toolchain hash:
  `759fd5fead4e90fd420cee473b69b26bb8eb7305dedca50b3267def4aecbf462`.
  Its ordered byte-concatenation definition and each component hash are in
  `coordination/runtime.json`.

## Library identity and absolute floor

The project vendors the official OpenROAD-flow-scripts Nangate45 typical
Liberty at upstream revision
`31e744df6a12ae09760820dc977d2b2488c9b0fe`. The upstream platform describes
it as a generic, non-manufacturable research/test library, version
`PDKv1.3_v2010_12.Apache.CCL`, under Apache-2.0. Provenance and license are in
`configs/vendor/nangate45/`.

- Library SHA-256:
  `8d540a4d4cf6d09d27c87ad067857a9c0c2eeb023ab7a56e058cd3113db4e9b1`.
- The file has no Liberty `area_unit` declaration. Results are therefore
  reported as `Nangate45_library_area_unit`; no physical square unit is
  inferred.
- Minimum positive area among the 90 cells explicitly described by the file
  as combinational: `INV_X1`, `0.532000` library area units. Physical
  fillers/taps/ties and sequential cells were excluded.

Sources:

- <https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts/tree/31e744df6a12ae09760820dc977d2b2488c9b0fe/flow/platforms/nangate45>
- <https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts/blob/31e744df6a12ae09760820dc977d2b2488c9b0fe/flow/platforms/nangate45/LICENSE>
- <https://github.com/YosysHQ/oss-cad-suite-build>

## Real smoke evidence

Exact host invocation:

```text
wsl.exe -d Ubuntu --exec bash /mnt/c/Users/meetb/OneDrive/Documents/ChatGPT/ppa-delta/runs/codex/c01-smoke-20260909T101000Z/run.sh
```

The script uses explicit `/home/meetb/eda/oss-cad-suite` executables and runs
from the WSL view of the shared project. The current root has no spaces, but
all path variables in `run.sh` are quoted; this avoids depending on that fact.

EQY generated exactly one partition, `top.y : y[4:0]`. Its per-strategy status
is `PASS`, the aggregate `formal/PASS` marker exists, and the complete log ends
with `DONE (PASS, rc=0)`. The proof used EQY's `sat` strategy. This is a real
formal result, not simulation and not an inference from exit status alone.

Both sides then mapped through ABC to 17 Nangate45 cells. Yosys reported
mapped area `20.482000` for each side, sequential area `0.000000`, with all
cell types named in the vendored Liberty. The equal result is expected for
this control and is not claimed as a PPA regression. ABC emitted two benign
diagnostic warnings: the library contains multi-output cells and the test
network is combinational.

Key artifacts:

- `coordination/runtime.json`
- `configs/vendor/nangate45/PROVENANCE.md`
- `runs/codex/c01-smoke-20260909T101000Z/run.sh`
- `runs/codex/c01-smoke-20260909T101000Z/equivalent.eqy`
- `runs/codex/c01-smoke-20260909T101000Z/eqy.stdout.log`
- `runs/codex/c01-smoke-20260909T101000Z/formal/partition.list`
- `runs/codex/c01-smoke-20260909T101000Z/formal/PASS`
- `runs/codex/c01-smoke-20260909T101000Z/area-before.json`
- `runs/codex/c01-smoke-20260909T101000Z/area-after.json`
- `runs/codex/c01-smoke-20260909T101000Z/area-before.log`
- `runs/codex/c01-smoke-20260909T101000Z/area-after.log`

## Verification and limitations

- All 10 coordination-helper tests passed under the project `.venv`.
- `scripts/check_pack.py` passed after task start and handoff acknowledgement.
- `coordination/runtime.json` parses as JSON.
- Vendored library/license/README checksums match `SHA256SUMS`.
- This C01 smoke validates runtime availability only. Unsupported, deliberately
  inequivalent, timeout, and evaluator-status controls belong to C03 and have
  not been claimed here.

Next action: publish the C01 runtime-ready handoff to Claude, then implement
the C02 contracts, schemas, config, package skeleton, and explicit test-only
fake oracle boundary.
