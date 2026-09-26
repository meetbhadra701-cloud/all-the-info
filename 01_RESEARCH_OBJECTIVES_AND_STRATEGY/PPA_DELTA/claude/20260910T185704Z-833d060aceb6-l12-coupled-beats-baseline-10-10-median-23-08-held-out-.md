---
agent: claude
type: experiment
created: 2026-09-10T18:57:04+00:00
---

# L12: coupled beats baseline 10/10 (median 23.08%), held-out 3/3; but 70% bar 0/10 literal + practical relevance unresolved

Classification: OBSERVED (real EDA, frozen C11 rows). L12 analysis complete.

## Deliverable

`analysis/month_one_analysis.py` (rerunnable, deterministic — same input → same counts) +
`analysis/month-one-report.md`, computed from the frozen C11 comparison rows
(`runs/codex/c11-month-one-six-method-20260910T174500Z/`). 60/60 rows valid.

## Headline numbers (all from machine-readable rows)

- Coupled beats the better simple baseline on **10/10** pairs; all coupled finals fresh uncached
  formal-PASS INTERESTING. Bugpoint reduces none.
- **Median advantage 23.08%** (≥20% ✓); individually ≥20% on 6/10.
- **Held-out advantage 3/3**; scaffold-lift **generalizes** to unseen structures (a4: 48 vs 62;
  m2: 43 vs 53). Matching helps on 4/10 (exactly the `sel==k` scaffold cases).
- Cost (coupled): 247 proposals, 267 evaluations, 267 EDA executions, 1863 tool commands, ~1402 s.

## The honest wrinkle Codex flagged — reported both ways, gate unchanged

Week-4 bar "≥70% ORIGINAL pair-AST reduction on ≥7 cases":
- **Literal (remove ≥70% → final ≤30% of original): 0/10 → NOT met.** Max original reduction is
  a4 at 51.5%. The already-minimal witnesses cannot be cut 70% while keeping the area gap.
- Alternative (final ≤70% of original, i.e. remove ≥30%): 7/10.
I do not resolve this in my favor. Under the pre-registered literal reading the technical gate is
NOT met on this bar.

## Week-4 technical bars summary

| bar | result |
|---|---|
| 10/10 witnesses reproduce equivalence+area | ✅ 10/10 |
| ≥70% original reduction on ≥7 cases (literal) | ❌ 0/10 |
| ≥20% median advantage | ✅ 23.08% |
| ≥2 held-out advantage | ✅ 3/3 |

## Interpretation (feeds L13, not decided here)

Technical results are strong (coupled wins 10/10, held-out generalizes, matching revived on
scaffold cases) BUT (a) the literal ≥70%-reduction bar fails (0/10) and (b) **practical relevance
is UNRESOLVED** — the corpus is entirely synthetic and no external maintainer review occurred. Per
the Week-4 gate this points toward **REVISE** (promising technical, unresolved provenance/
usefulness), not a clean CONTINUE — but that recommendation is L13's, made with the maintainer
checklist and the user's month-one decision rule.

## For Codex (C12)

C12 (clean replay + release candidate) depends on C11 + L12 (both DONE). Please package the release
candidate and run clean-directory replays of the ten final witnesses; if any fails, invalidate it
and I recompute. No method change (frozen). After C12, I do L13 (maintainer relevance + final
recommendation + Week-4 vote). 43/43 Claude tests, check_pack PASS. No Codex files touched.
