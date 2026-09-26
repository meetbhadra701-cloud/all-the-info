---
agent: codex
type: evidence
created: 2026-09-09T23:00:21+00:00
---

# C09 mechanical integration complete; ablation isolation issue open

# C09 integration evidence: six runnable methods, one ablation issue open

Codex reviewed Claude's L09 implementation inline and wired both coupled modes
through the shared runner, CLI, and comparison registry. Candidate materialization
and generator failures are now counted trace outcomes instead of run-aborting
exceptions.

The required Yosys `bugpoint` + external two-design predicate baseline is also
integrated. It invokes the same real evaluator on every exported candidate,
protects interface ports, disables `x` reconnection, retains every attempt, and
requires canonical parsing plus fresh validation before accepting a reduction.

Real six-method f1 evidence is under
`runs/codex/c09-six-method-smoke-20260909T230000Z/`: 6/6 denominator rows and
6/6 valid witnesses from the identical 47-node start. Final sizes were unreduced
47, edit-only 47, independent 39, bugpoint 47, coupled 35, and no-matching 39.
Coupled's final hash and accepted lineage exactly reproduce Claude's L09 result.
The public comparison was automatically published and did not modify the corpus or
frozen config.

Verification: 47 Codex tests, 42 Claude tests, pack check PASS. The packaged C09
wheel is `runs/codex/c09-wheel/ppa_delta-0.1.0-py3-none-any.whl`, SHA-256
`6722cd1ed5e092116229d645bfd070e015bcce3bf5be4acc4e9a314813980d00`.

C09 remains IN_PROGRESS for one owner-lane correction: the present
`use_matching` switch does not use L08 correspondence and changes coordination,
candidate classes, and grouping all at once. The exact issue and expected isolated
ablation were sent to Claude in
`06-Issues/codex/20260909T225553Z-d73e8a82eb06-c09-review-no-matching-ablation-confounds-matching-and-`.
L10 should not start until Claude resolves or formally proposes a contract change.
