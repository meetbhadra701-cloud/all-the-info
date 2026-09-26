---
agent: codex
type: decision
created: 2026-09-10T03:04:13+00:00
---

# C10 fairness audit: reproducible coordination benefit, sub-threshold, bugpoint caveat

Classification: OBSERVED (real EDA) + DECISION (Week-3 vote REVISE).

C10 independently audited all 18 L10 rows. Starts, suite hash, canonical sizes, and frozen
200-candidate/1800-second budgets match across methods. All 16 valid witnesses are backed by fresh
INTERESTING/formal-PASS records; canonical sizes and hashes were independently recomputed through
the public snapshot/SizeCounter seam.

Two clean uncached Codex reruns reproduced the exact coupled outcomes and hashes: a2 76→62 and
f2s 30→28. Accepted traces show the modest gain comes from coordinated merge/constant edits after
the independent inlining frontier, not from budget or size accounting. Matching is null: coupled
and no-matching produce identical final hashes on all three pairs.

Vote: REVISE. Coupled beats the best valid independent/edit-only baseline on 3/3, but only by
10.26%, 6.06%, and 6.67%; the ≥20% bar is met on 0/3. Approve one method modification only:
coordinated vacuous-construct collapse plus removal of newly unused inputs. Drop the structural
correspondence claim regardless.

C10 also found a baseline-validity caveat: bugpoint is ERROR, not NO_GAIN, on a2 and f2s because
the adapter rejects Yosys logical-not syntax and semantically changes the f2s post-export pair.
Those fail-closed rows remain valid denominator failures, but Codex must repair and rerun the
adapter before any stronger baseline-superiority claim or final bounded comparison.

Evidence:
- docs/codex/week-3-fairness-audit.md
- scripts/c10_fairness_audit.py
- runs/codex/c10-fairness-audit-20260910T025500Z/audit.json
- runs/codex/c10-rerun-a2-20260910T024500Z/reduction.json
- runs/codex/c10-rerun-f2s-20260910T025000Z/reduction.json
