# Fair comparison harness v1

Owner: Codex · C08 · implementation `comparison-harness-1.0`.

## Frozen suite contract

The suite JSON is validated by `comparison-suite.schema.json` and then by path,
pair-ID, and manifest checks. Version 1 freezes:

- evaluator config `configs/area-v1.json`;
- cache policy `disabled` for every method (a stricter form of an initially
  cold per-method cache, preventing cross-method reuse);
- 200 proposed candidates or 1,800 seconds per pair/method;
- one unique manifest per pair ID; and
- required rows for `unreduced`, `edit-only`, `independent`, and `coupled`.

The registry also reserves `bugpoint` and `coupled-no-matching`, both required by
the Week 3 experiment even though the minimum C08 schema set predates their
integration. The checked-in smoke suite lists all six methods.

Every pair is copied once into `inputs/<pair-id>/` and assigned the evaluator's
canonical candidate hash and `coupled-size-1.0` vector. Every method receives
that exact immutable manifest, hash, size, config, budget, and cache policy.
Method output is rejected as `HARNESS_ERROR` if it claims a different start.

## Method registration boundary

`MethodRegistry.register(name, runner)` accepts a callable with this contract:

```text
runner(ComparisonContext) -> MethodOutcome
```

`ComparisonContext` contains the immutable starting manifest, config, output
directory, shared `Budget`, disabled-cache flag, starting hash, and starting
size. `MethodOutcome` contains status, validity, start/final identity and size,
proposal/evaluation/EDA/tool-command counts, elapsed time, result/final-proof
paths, and a nullable failure reason.

The built-in registry now wires `unreduced`, `edit-only`, `independent`,
`bugpoint`, `coupled`, and `coupled-no-matching`. Runner exceptions still become
retained `HARNESS_ERROR` rows, and an explicitly unregistered runner remains a
retained `UNAVAILABLE` row.

Candidate generators use the public
`ppa_delta.oracle.snapshot_candidate(...) -> Candidate` seam after emitting a
schema-valid pair. It is the stable-copy/hash/size authority shared by the Codex
baselines and Claude's future L09 generator; no reducer duplicates the
evaluator's private snapshot logic.

## Persistence and denominator rule

Each pair/method row is schema-validated and atomically saved under `rows/`
immediately after that method returns or fails. Only after all row files exist
does the harness compose `matrix.jsonl` and `comparison.json`. A runner
exception becomes `HARNESS_ERROR`; an unintegrated method becomes
`UNAVAILABLE`; timeout, failure, interruption, budget exhaustion, and
`NO_GAIN` remain their own rows. Every row has `denominator: true`.

For a reduced result, a smaller size counts only when its separate final
validation is uncached and `INTERESTING`. Otherwise the row retains the original
size. `NO_GAIN` is a valid original witness only when its initial uncached
evaluation is `INTERESTING`. Thus invalid final outputs cannot improve a method.

## Public invocation

```text
ppa-delta compare --suite configs/comparison-smoke-v1.json \
  --out runs/AGENT/UNIQUE --agent AGENT
```

The completed comparison is automatically published to the matching vault lane
after `comparison.json` is persisted.

## C08 real smoke

`runs/codex/c08-public-smoke-20260909T213000Z/` ran the public command on f1.
All six rows share starting hash
`18f6633b8f7d03f3689c748857ffae290d1be6e10aea9d40fe4845d5151d94e2`
and size 47. Unreduced remained 47; edit-only returned `NO_GAIN`; independent
reduced to 39 with an uncached EQY `PASS`/`INTERESTING` final validation. The
three not-yet-integrated methods are explicit denominator rows. Automatic
publication passed.

This smoke validates harness mechanics and real baseline routing. It is not the
Week 3 comparison and makes no coupled-method claim.
