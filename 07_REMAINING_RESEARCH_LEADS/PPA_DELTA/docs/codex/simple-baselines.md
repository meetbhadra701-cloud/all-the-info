# Simple reduction baselines (C06)

Owner: Codex · 2026-09-09 · Baseline version `simple-baselines-1.0` · Shared size authority
`coupled-size-1.0`.

## Implemented methods

`edit-only` parses the submitted before/after sources and defines deterministic ordered AST body
edit groups against the original before side. Positional replacements and trailing
insertions/deletions reconstruct the after side; unsupported alignments conservatively fall back
to a whole-file replacement. Ordinary ddmin tests complements at increasing granularity and keeps
only candidates for which the unchanged real oracle returns `INTERESTING`. Exhaustion is only
1-minimal relative to this deliberately simple body-edit transformation set.

`independent` enumerates the same frozen source-AST simplification class one side at a time, in
`before`/`after`, file, item, operation order. C06 implements removal of unused initialized wires
and inlining of single-use initialized wires. It restarts deterministic enumeration after every
accepted candidate. The other side remains byte-identical for each proposal; formal equivalence
and the area predicate are always decided by the real oracle.

Both methods use `ppa_delta.coupled.size.DEFAULT`; no baseline-specific node count exists. They
reject nonshrinking proposals locally but still charge them as proposals. Every evaluated
candidate has a fresh immutable candidate directory, parent hash, transformation ID, source
snapshot, and trace row.

## Budgets and outcomes

The default search budget is 200 proposals or 1,800 wall seconds. Compile/formal/synthesis caps
are serialized in `budget.json` and must exactly match the frozen effective evaluator config;
changing them requires a new versioned config. Evaluator calls, uncached EDA-reaching evaluations,
and actual tool commands are accounted separately. Cache hits consume proposal/evaluator budget.

The original pair is preserved and evaluated as the zero-work reference. The best accepted pair
is preserved separately under `snapshots/best/` and receives a forced uncached final evaluation.
A final failure invalidates the reduction and returns `ERROR`. No accepted simplification returns
`NO_GAIN` with the original hash/size. Candidate or wall exhaustion returns `BUDGET_EXHAUSTED`
with an explicit reason; a caught keyboard interrupt atomically records `INTERRUPTED`. Traces and
all already-created immutable candidates survive every outcome.

Public command:

```text
ppa-delta reduce --pair PAIR/pair.json --config configs/area-v1.json \
  --method edit-only|independent --out runs/AGENT/UNIQUE --agent AGENT \
  [--max-candidates 200] [--max-wall-seconds 1800] [--no-cache]
```

Exit 0 means `REDUCED` or a clean `NO_GAIN`; exit 1 means `BUDGET_EXHAUSTED`; exit 130 means
`INTERRUPTED`; setup/final-validation errors return 2. `coupled` remains explicitly unimplemented
until L08/C09.

## Controlled and real evidence

`tests/codex/test_baselines.py` uses clearly labeled fake-oracle fixtures only for search-logic
properties: exact edit reconstruction, deterministic ordering, ddmin minimality, identity/size
agreement, zero-success, frozen timeout enforcement, budget exhaustion, fresh-validation routing,
and interrupt persistence. It is not EDA evidence. The complete Codex suite is 34/34 passing;
Claude's suite is 24/24 passing.

The first cold real matrix is
`runs/codex/c06-baselines/5c30d13569c64a619d589d33cb07ad55/matrix.json`. Every one of its
eight evaluator calls was uncached. The edit-only case starts from an expanded copy of the
qualified `f2s-factor-mult4` pair, adding one mapped-away after-side declaration without changing
the owner-controlled benchmark. Ddmin removes that irrelevant edit and reduces the shared
objective from `(38,20,259)` to `(30,12,228)`. Its fresh final result is EQY PASS,
`128.212 → 186.732`, and `INTERESTING`.

The independent smoke uses the unmodified `f1-mux-share-add` pair with an explicitly tiny
one-proposal budget. It inlines one before-side single-use wire and reduces `(47,21,384)` to
`(45,19,366)`. It honestly returns `BUDGET_EXHAUSTED(max_candidates)`, then its smaller best pair
still receives a fresh uncached EQY PASS, `73.948 → 101.080`, `INTERESTING` validation.

The current-format cache-reuse matrix is
`runs/codex/c06-baselines/7f8b47418d464b75be0cb4efb28d1252/matrix.json`. Search calls reuse
the complete cold records, while both final validations remain uncached and each records seven
actual EDA commands. A public-CLI independent reproduction is at
`runs/codex/c06-cli-independent-20260909T183100Z/reduction.json`.

Finally, `runs/codex/c06-cli-edit-no-gain-20260909T183200Z/reduction.json` runs edit-only on the
unexpanded original `f2s-factor-mult4`: removing its sole semantic edit produces equal area, so
the baseline correctly returns `NO_GAIN`, preserves the original `(30,12,228)` witness, and does
not confuse “no removable edit” with an implementation failure.
