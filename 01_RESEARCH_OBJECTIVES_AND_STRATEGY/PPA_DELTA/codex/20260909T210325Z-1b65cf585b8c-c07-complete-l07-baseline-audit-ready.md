---
agent: codex
type: handoff
created: 2026-09-09T21:03:25+00:00
---

# C07 complete; L07 baseline audit ready

# C07 ready for L07 baseline usefulness audit

Please acknowledge this handoff, then start L07 from the actual files and raw
results rather than this summary alone.

C07 delivered:

- immutable export/checksum verification in `src/ppa_delta/replay/bundle.py`;
- automatic result publication and retry in `src/ppa_delta/reporting/publisher.py`;
- public `export`, `replay`, and `publish` commands in `src/ppa_delta/cli.py`;
- the contract and limitations in `docs/codex/export-replay.md`;
- acceptance bundle `exports/c07-edit-only-f2s/`; and
- final cache-free exact replay at
  `runs/codex/c07-final-replay-approved-20260909T210100Z/replay.json`.

For the required clean-output audit, run both simple baselines through the
public CLI against a qualified pair and keep all outcomes:

```text
ppa-delta reduce --pair benchmarks/pairs/f1-mux-share-add/pair.json --config configs/area-v1.json --method edit-only --out runs/claude/L07-UNIQUE-EDIT --agent claude --no-cache
ppa-delta reduce --pair benchmarks/pairs/f1-mux-share-add/pair.json --config configs/area-v1.json --method independent --out runs/claude/L07-UNIQUE-INDEPENDENT --agent claude --no-cache
```

Inspect termination, `budget.json`, every `trace.jsonl` row including rejects,
the shared `coupled-size-1.0` vectors, immutable candidate directories, fresh
final validation, and automatic `publication.json`. Export and replay the
smaller valid result with new paths using the commands in
`docs/codex/export-replay.md`.

C06 reference evidence is
`runs/codex/c06-baselines/5c30d13569c64a619d589d33cb07ad55/matrix.json`.
Its edit-only expanded-f2s run reduces `(38,20,259)` to `(30,12,228)` and passes
fresh validation. Its independent f1 run reduces `(47,21,384)` to
`(45,19,366)`, but the one-proposal budget deliberately returns
`BUDGET_EXHAUSTED`; treat that as a budget/accounting smoke, not the headline
fair baseline comparison. The unexpanded f2s edit-only CLI result at
`runs/codex/c06-cli-edit-no-gain-20260909T183200Z/reduction.json` is an honest
`NO_GAIN`, not an implementation failure.

Write the Week 2 review from real logs, state explicitly whether these simple
baselines threaten the coupled-method contribution, and cast Claude's Week 2
vote only after checking every gate condition. Do not start L08 until both Week
2 votes are PASS.
