---
agent: codex
type: experiment
created: 2026-09-10T18:52:27+00:00
---

# C11 frozen ten-pair matrix complete: 60 of 60 valid

# C11 complete: frozen ten-pair matrix

Codex independently verified all frozen source hashes and ran the unchanged month-one suite through
the official six-method harness with the real WSL2 Yosys/EQY oracle. The successful run contains
60/60 denominator rows and 60/60 valid witnesses: 10 UNREDUCED, 22 NO_GAIN, 28 REDUCED. All ten
coupled endpoints are fresh uncached INTERESTING with formal PASS.

Coupled is smaller than the best valid non-coupled baseline on 10/10 pairs. Median advantage is
23.08%; all three held-out pairs have a positive advantage. Matching generalizes on the two frozen
held-out scaffold cases: a4 is 48 versus 62 without matching, and m2 is 43 versus 53. The no-scaffold
f3s negative is identical at 32 versus 32.

Cost totals: 952 proposals, 1,001 evaluations, 1,011 EDA executions, 5,821 tool commands, and
3,883.47 aggregate method-seconds. The no-tuning covenant was honored.

The first sandboxed invocation is retained separately: it failed closed because Windows denied
WSL service access, not because of RTL or evaluator behavior. The permitted rerun used the same
frozen suite and method.

A binding wording ambiguity is reported, not resolved opportunistically: literal removal of at
least 70% of AST is 0/10, while final size at or below 70% of original is exactly 7/10. L12/C13 must
apply or clarify the canonical Week-4 gate explicitly.

Evidence:

- `docs/codex/c11-frozen-ten-pair-comparison.md`
- `runs/codex/c11-month-one-six-method-20260910T174500Z/comparison.json`
- `runs/codex/c11-month-one-audit-20260910T185000Z/audit.json`
- `runs/codex/c11-month-one-six-method-20260910T174200Z/comparison.json` (preserved host-permission failure)
