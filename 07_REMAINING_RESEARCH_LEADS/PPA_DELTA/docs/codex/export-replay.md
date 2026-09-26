# Export, replay, and automatic experiment notes

C07 adds an immutable replay bundle and durable automatic vault publication for
`evaluate`, `reduce`, and `replay` commands.

## Commands

Export a completed evaluation or reduction whose final validation is uncached,
formal `PASS`, and `INTERESTING`:

```text
ppa-delta export --run runs/codex/RUN --bundle exports/BUNDLE
```

Verify every bundled checksum and rerun using only the bundled pair and
configuration, with the evaluator cache disabled:

```text
ppa-delta replay --bundle exports/BUNDLE --out runs/codex/FRESH-RUN --agent codex
```

For a standalone release kit with no coordination vault, add `--no-publish`.
That option skips only documentation publication; bundle verification and the
fresh cache-free evaluator run are unchanged.

Retry only vault publication after a documentation failure:

```text
ppa-delta publish --run runs/codex/RUN --agent codex
```

Use `--agent claude` for commands run in Claude's lane. The agent value controls
the run note's vault destination; it does not change scientific evaluation.

## Bundle contract

Each bundle contains:

- `pair/`: the exact final `pair.json`, RTL sources, and declared license file;
- `evidence/final-validation/`: the complete uncached formal and mapped-area run,
  including raw stage logs and reports;
- `config.json` and `runtime.json`: the effective evaluator configuration and
  frozen runtime identity used by that validation;
- `records/`: the primary result plus available reduction trace, budget,
  summary, and publication records;
- `bundle.json`: expected candidate/content hashes, formal and area outcome,
  size vector, toolchain/config/library identities, and replay command; and
- `inventory.json`: SHA-256 and byte count for every other bundled file.

Export is atomic: it is assembled in a unique sibling temporary directory,
verified, and renamed into place. Existing destinations are never overwritten.
Replay rejects a changed, missing, extra, unsafe, or symlinked artifact before
EDA starts. It also requires the active runtime manifest to equal the bundled
runtime manifest exactly. A replay is a pass only when the fresh uncached result
exactly matches the expected candidate/content hashes, status, formal result,
area vector, size vector, and frozen identity hashes.

The bundle is independent of the original benchmark directory and evaluator
cache. It intentionally does **not** copy the large OSS CAD Suite distribution.
C12's local release kit supplies the exact Nangate45 library and supports
relocation through `PPA_DELTA_PROJECT_ROOT`, `PPA_DELTA_EDA_ROOT`, and optional
`PPA_DELTA_WSL_PROJECT_ROOT`. The strengthened doctor compares the effective
suite release and every frozen binary/manifest hash before replay.

## Automatic publication and failure behavior

The CLI first persists the scientific command result atomically. It then invokes
the coordination helper with an argument vector to create a short experiment
note linking that result. Publication outcome is separately recorded in
`publication.json`.

If publication fails, the CLI returns a distinct documentation-failure code and
prints the `ppa-delta publish` retry command. It does not alter or rerun the EDA
result. Setup failures for newly created output directories are also saved as
`command-result.json` before publication is attempted. A successful
`publication.json` is idempotent: retrying returns the existing record instead
of creating a duplicate note.

## C07 evidence

- Export bundle: `exports/c07-edit-only-f2s/`
- Bundle manifest: `exports/c07-edit-only-f2s/bundle.json`
- Checksum inventory: `exports/c07-edit-only-f2s/inventory.json`
- Fresh cache-free replay under the final implementation:
  `runs/codex/c07-final-replay-approved-20260909T210100Z/replay.json`
- Automatic evaluator publication: `runs/codex/c07-auto-evaluate-20260909T185400Z/publication.json`
- Automatic reducer publication: `runs/codex/c07-auto-reduce-20260909T185800Z/publication.json`
- Persisted setup failure and publication: `runs/codex/c07-auto-failure-20260909T185500Z/`
- Packaged wheel: `runs/codex/c07-wheel/ppa_delta-0.1.0-py3-none-any.whl`
  (SHA-256 `2594e3278a782078aa3e5c59a7d6cc06aa84b3a27f55914e4aa7ee5ae6174d76`)

The exported witness is the smaller edit-only `f2s` pair. Its replay retained
formal `PASS`, `INTERESTING`, mapped area `128.212 -> 186.732`, the exact size
vector, all identity hashes, and `cache_hit: false`.

One preceding attempt at
`runs/codex/c07-final-replay-20260909T190500Z/` was denied by the Windows WSL
service (`Wsl/Service/E_ACCESSDENIED`) in the command sandbox. It was preserved
and automatically published as a fail-closed `TOOL_ERROR`; no claim relies on
it. The permission-approved rerun above is the C07 acceptance replay.

## C12 portability closure

The final local kit and a source-free wheel installation replayed all ten
month-one bundles exactly. See `docs/codex/release-candidate.md` and
`runs/codex/c12-release-audit-20260910T193300Z/audit.json`. Newly exported bundle
commands include `--no-publish` so a user without this repository's Obsidian
vault gets a scientific PASS/FAIL exit code rather than a documentation error.
