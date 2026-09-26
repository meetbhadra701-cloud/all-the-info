---
agent: claude
type: experiment
created: 2026-09-10T22:47:34+00:00
---

# L13 maintainer relevance + Week-4 REVISE recommendation

Classification: OBSERVED (release replay + frozen L12 rows) + DECISION (Week-4 vote). L13 done.

## Deliverable

`analysis/l13-maintainer-relevance.md` — reproduce-as-a-stranger check, scored maintainer
checklist, drafted (UNSENT) upstream issue, final novelty statement, complete limits, paper
outline, and the Week-4 recommendation. Backed by C12's clean-room audit
(`runs/codex/c12-release-audit-20260910T193300Z/audit.json`, PASS) and `analysis/month-one-report.md`.

## Maintainer relevance

- Stranger-reproducibility from README only: **PASS** — C12 clean-room did exactly this route,
  source-free, 10/10 uncached formal-PASS exact, 57.3 s.
- Maintainer checklist: **7/8 present** (small example, single replay command, tool/version/library
  provenance, expected-vs-observed, reduction trace, license clarity, specific diagnostic reason).
  **Item 8 (external review): NONE** — no maintainer contacted, no issue filed. Recorded as a gap.
- Would it help a maintainer? **Yes in FORM, unproven in SUBSTANCE** — the f1 witness is an ideal
  3-line minimal reproducer, but all ten pairs are synthetic and hand-authored; no real need shown.
- Upstream issue drafted **locally, not sent**; I recommend NOT filing it (synthetic, demonstrates
  intended behavior — it proves the format works, not that a bug exists).

## Week-4 vote: REVISE

- **Technical PASS NOT MET**: the gate requires ≥70% original-AST reduction on ≥7 cases; actual
  **0/10** (max 51.5%). The other technical bars pass (10/10 valid, 23.08% median ≥20%, held-out
  3/3), but one required bar fails literally, so the technical gate does not pass. Not redefined.
- **Practical PASS NOT MET**: report is maintainer-ready (7/8) but no external review and a fully
  synthetic corpus leave user need unresolved. Internal assessment ≠ external validation.
- Maps to the gate's **REVISE** verbatim. Not CONTINUE (needs both PASS + credible need). Not STOP
  (novelty intact per L01, simple reducer insufficient — coupled 10/10, results reproducible — C12).

## Recommended next experiment (fixed budget, for the user's decision)

Sourced-provenance mini-study: 5 real combinational pairs from public cores (ibex/OpenTitan prim_*,
picorv32, SERV), frozen oracle + frozen six-method matrix, ≤1 week, **no method change**. Success =
coupled beats the better baseline on ≥3/5 real pairs. Attacks the provenance/relevance gap directly;
does not chase the 70% bar (structurally unreachable on already-minimal witnesses; arguably
mis-calibrated for a relational reducer — flagged for the user, NOT used to upgrade the vote).

## For Codex (C13)

L13 is DONE and my Week-4 vote is REVISE (recorded via control.py gate). C13 (final decision packet)
is now unblocked. The month-one verdict is the user's; my evidenced recommendation is REVISE with the
sourced-provenance mini-study. If Codex's independent Week-4 vote also lands, the combined gate
resolves; no month-two work begins without explicit user direction. 43/43 Claude tests, check_pack
PASS. No Codex files touched.
