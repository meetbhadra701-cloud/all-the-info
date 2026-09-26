---
agent: codex
type: experiment
created: 2026-09-09T18:44:54+00:00
---

# C06 real simple-baseline evidence

C06 is complete with deterministic edit-only/ddmin and independent-side baselines using the sole
shared `coupled-size-1.0` counter and the hardened real oracle.

Real cold evidence is `runs/codex/c06-baselines/5c30d13569c64a619d589d33cb07ad55/matrix.json`:
edit-only reduced an expanded qualifying f2s witness from `(38,20,259)` to `(30,12,228)` and
completed; independent reduced the unmodified f1 pair from `(47,21,384)` to `(45,19,366)` under
an intentionally one-proposal budget and accurately reported `BUDGET_EXHAUSTED`. Both smaller
witnesses passed forced uncached final EQY and area validation. A current-format cached-search /
uncached-final matrix is at
`runs/codex/c06-baselines/7f8b47418d464b75be0cb4efb28d1252/matrix.json`.

The public CLI was exercised. The unexpanded f2s edit-only control returned clean `NO_GAIN`,
showing that no removable edit is distinct from implementation failure. Initial/best snapshots,
candidate lineage, traces, complete results, explicit budgets, timeout consistency, evaluator
calls, uncached EDA evaluations, and tool-command counts are preserved.

Verification: 34/34 Codex tests, 24/24 Claude tests, 21 real evaluation-result schema checks, and
`check_pack.py` all pass. Design and CLI behavior are documented in
`docs/codex/simple-baselines.md`. Final wheel:
`runs/codex/c06-wheel-final/ppa_delta-0.1.0-py3-none-any.whl`, SHA-256
`c19032910204babd7e6f41bc032904d0623465f5a037782b556cc344ac7194ea`.

Next: C07 export, replay, and automatic experiment-note publication.
