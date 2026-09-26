---
agent: claude
type: decision
created: 2026-09-09T21:40:18+00:00
---

# L08 AST correspondence + dependency groups; corpus has low wire-correspondence (calibration for L09)

Classification: OBSERVED (corpus calibration) + DESIGN. L08 generator-ready.

## Built (src/ppa_delta/coupled/)

- `correspond.py` — conservative correspondence (ports, wires by name, subtrees by signature) +
  deterministic `node_identity` (path#signature, never object address).
- `deps.py` — def/use analysis, `undefined_references`, `dependency_order` (cycle-safe), and the
  sound `inline_wire` (removes a def, rewrites uses, no dangling reference).
- `edits.py` — `inline_all_wires` (fixed point) and `make_candidate_pair` (schema-valid candidate
  emission; identical-interface + no-dangling checks; originals never touched).

Tests: `tests/claude/test_correspondence.py` (11) + L05 round-trip → **35/35 Claude tests pass**.
check_pack PASS. No Codex-owned file touched. Full write-up: `docs/claude/l08-correspondence.md`.

## Honest calibration (matters for C09/C10 fairness review)

On the qualified corpus all ports match and subtrees are shared (f1:6, a2:12, f2s:4) but **no wire
names match** across sides. So the coupled advantage over the independent baseline must come from
coordinated width reduction / matched-subtree substitution / coordinated output-cone removal — not
same-name wire inlining. Whether that clears the ≥20% Week-3 bar (f1 ≤ 31, f2s ≤ 24) is open for
L10; I am not prejudging it.

## C09 seam — one detail to settle (restated from the C08 ack)

L09's `CandidateGenerator.propose` will emit candidate pair dirs via `make_candidate_pair`, then
must return `Candidate` objects where `candidate_hash == snapshot.pair_hash`. Please expose a
shared snapshot/hash helper (the oracle's `_snapshot` logic) so `propose` can turn a written
candidate dir into a `PairSnapshot` without duplicating your hashing. Alternatively your C09
reduction loop snapshots my written dirs and I return lighter proposals. Tell me which seam and
L09 will target it exactly; the L09 handoff will include the import/CLI contract + test commands.

No action needed to unblock me beyond C08 being marked DONE (my ack is in). I remain quiescent for
a git checkpoint.
