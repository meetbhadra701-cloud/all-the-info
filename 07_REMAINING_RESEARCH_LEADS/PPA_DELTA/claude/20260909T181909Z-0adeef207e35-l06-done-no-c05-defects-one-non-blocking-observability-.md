---
agent: claude
type: handoff
created: 2026-09-09T18:19:09+00:00
---

# L06 done: no C05 defects; one non-blocking observability note (size_counter_error vs COMPILE_ERROR)

Classification: OBSERVED (real EDA via the public v1.0 evaluator).

## L06 adversarial audit — the hardened oracle held

Six adversarial cases driven through `ppa-delta evaluate` (public interface only, no competing
oracle). **None returned INTERESTING.** Full audit: `docs/claude/l06-adversarial-audit.md`;
matrix `benchmarks/adversarial/l06-matrix.json`; raw `runs/claude/l06-adversarial-20260909T181524Z/`.

| case | observed | interesting? |
|---|---|---|
| adv-ineq-biggap (inequivalent + big area gap) | INEQUIVALENT (formal FAIL) | no |
| adv-signed-trap (signed vs unsigned mult) | INEQUIVALENT (formal FAIL) | no |
| adv-iface-width-mismatch | UNSUPPORTED | no |
| adv-path-traversal | setup rejected: "path traversal is prohibited" | no |
| adv-undriven-x | UNSUPPORTED | no |
| adv-source-bloat-equal-area | NOT_INTERESTING (equal mapped area) | no |

Crown jewel (a real area regression that is NOT equivalence-preserving) is correctly rejected.
Traversal blocked before any read. Source bloat confirms mapped-area (not source size) drives
interest. `tests/claude/test_adversarial_expectations.py` locks these as regressions. Full Claude
suite: 24/24 pass.

## Defects found in C05: NONE.

I am reporting no defect because I found none — not manufacturing one. C05 hardening holds
against this adversarial layer.

## One non-blocking observability note for Codex

`adv-signed-trap` first used `$signed()`; the evaluator returned COMPILE_ERROR with
`size_counter_error: "unexpected character '$'"` — the failure came from **Claude's SizeCounter
parser** (which doesn't accept `$`-system functions), not Yosys. Both fail closed, so this is not
a correctness issue. Suggestion (your call, non-blocking): surface a `size_counter_error`
(Claude-lane parse-subset gap) distinctly from a real Yosys COMPILE_ERROR so triage is clearer. I
documented `$signed()/$unsigned()` as outside the v1 parser subset in
`docs/claude/reduction-design.md` §2 (the `signed` keyword itself is supported).

No action required from you to unblock my L07 (which depends on C07). I remain quiescent for a
git checkpoint.
