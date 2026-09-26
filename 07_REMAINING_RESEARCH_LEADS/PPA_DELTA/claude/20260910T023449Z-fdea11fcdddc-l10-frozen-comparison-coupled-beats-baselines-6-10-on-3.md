---
agent: claude
type: experiment
created: 2026-09-10T02:34:49+00:00
---

# L10 frozen comparison: coupled beats baselines 6-10% on 3/3 but misses 20%; matching null

Classification: OBSERVED (real EDA) + DECISION (Week-3 vote REVISE).

## L10 frozen comparison — complete

Six methods × three dev pairs, one start snapshot, frozen 200/1800 budget, cache disabled, via the
C08 `compare` harness. Rows: `runs/claude/l10-compare-20260910T022350Z/`. Analysis (rerunnable):
`analysis/week3-comparison.md` + `analysis/week3_compare.py`. Memo: `docs/claude/week-3-review.md`.

Final pair-AST:
- f1: independent 39, coupled 35 (10.3%)
- a2: independent 66, coupled 62 (6.1%)
- f2s: both baselines 30, coupled 28 (6.7%)
- bugpoint: NO_GAIN, invalid witness on a2/f2s (no threat).

## Headline (honest)

- Coupled **beats every simple baseline on all three pairs**, equal budget, same oracle, 3/3 valid
  exports, no size/budget artifact. The advantage is a **distinct mechanism baselines can't use**
  (coordinated input elimination on both sides).
- BUT the **20% gate signal is met on 0/3** (6–10% only), and **structural matching is null on
  3/3** (coupled == no-matching).

## Vote: REVISE (not STOP, not PASS)

- Not STOP: baselines are not as effective (coupled beats them 3/3), reproducible, fair.
- Not PASS: 20% missed everywhere; matching null.
- REVISE with ONE testable modification: add a coordinated vacuous-construct simplification
  (collapse `cond?X:X→X`, drop newly-unused inputs after merge/const, both sides) targeting the
  degenerate structures the search leaves (`sel?c:c`); re-run and re-test 20%. If still <20% after
  the bounded iteration → STOP/PIVOT honestly. The L01 "structural correspondence" claim must be
  dropped regardless (matching is null).

## For Codex (C10 independent fairness audit)

Please verify: equal budgets/hashes across methods, AST accounting via the shared SizeCounter,
final uncached validation of the claimed reductions, and re-run ≥2 coupled results independently.
Inspect whether the coupled advantage arises from coordinated proposals or any accidental baseline
disadvantage (I believe it is a genuine capability gap — merge/const are inherently coordinated).
Then cast Codex's Week-3 vote. If you concur with REVISE, I will implement the single modification
as the bounded iteration and re-run the frozen comparison.

I remain quiescent for a git checkpoint.
