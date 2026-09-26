# L08 — AST representation, correspondence, and dependency groups

Owner: Claude · Task L08 · 2026-09-09 · Classification: OBSERVED (corpus calibration) + DESIGN.

Built on the owned parser (L05). Delivers the representation the L09 coupled generator proposes
against. Modules (all in `src/ppa_delta/coupled/`):

- `correspond.py` — conservative correspondence between the two sides: `matched_ports`,
  `matched_wires` (by name), `matched_subtrees` (by canonical signature), and `node_identity`
  (path `#` signature — deterministic, never object identity).
- `deps.py` — `analyze` (inputs/outputs/wires, def→dependency map, use sites),
  `undefined_references` (dangling-reference check), `dependency_order` (topological, raises on a
  combinational cycle), and the sound primitive `inline_wire` (removes a wire definition and
  rewrites its uses — never leaves a dangling reference).
- `edits.py` — `inline_all_wires` (deterministic fixed-point canonicalization) and
  `make_candidate_pair` (emits a schema-valid candidate pair; verifies both sides keep an
  identical interface and no dangling refs; never touches originals).

Tests: `tests/claude/test_correspondence.py` (11 cases) + the L05 round-trip suite → **35/35
Claude tests pass**.

## Correctness properties (tested)

- Sound edits: `inline_wire` / `inline_all_wires` leave no dangling reference, strictly shrink the
  AST, and the result reparses within the subset; the original AST and on-disk sources are
  unchanged.
- Deterministic identity: `node_identity` is identical across independent parses of the same
  source (no object-address dependence).
- Cycle safety: a combinational cycle through wires raises rather than looping.
- Valid candidates: `make_candidate_pair` produces a `pair.json` that validates against
  `schemas/pair.schema.json`.

## Calibration finding on the qualified corpus (honest, feeds L09/L10)

Correspondence over f1/a2/f2s: **all ports match**, and there are shared identical subtrees
(f1: 6, a2: 12, f2s: 4), but **no wire names match** across sides (before uses `x,y`; after uses
`s0,s1[,s2]`; f2s has no wires). The before/after are genuinely different structures — which is
exactly why they carry an area gap.

Consequence for the coupled method: a naive "coordinated inline of same-named wires" rarely fires
on this corpus. The coupled advantage over the independent baseline must therefore come from
levers that independent per-side reduction cannot coordinate:

1. **coordinated port/operand width reduction** applied identically to both sides + both manifests
   (keeps the pair equivalent to itself and typically preserves the proportional area gap);
2. **matched-subtree substitution** (replace a corresponding subtree with a smaller equivalent on
   both sides at once);
3. **coordinated output-cone removal** retaining a meaningful output.

These are the L09 primitives. Whether they beat the independent baseline's inlining by the ≥20%
Week-3 bar (f1 ≤ 31 vs 39; f2s ≤ 24 vs 30, from `week-2-review.md`) is an open empirical question
for L10 — not prejudged here.

## Generator seam for L09 / C09

L09 implements `contracts.CandidateGenerator.propose(pair, work_dir) -> Iterable[Candidate]`
using these primitives: parse both sides → correspond → propose a coordinated edit → emit a
candidate pair via `make_candidate_pair` → wrap as a `Candidate`. The one open wiring detail
(raised in the C08 ack) is how `propose` turns a written candidate dir into a `PairSnapshot`
(so `candidate_hash == snapshot.pair_hash`): a shared snapshot/hash helper from Codex is
preferred over duplicating the oracle's `_snapshot`. L09's handoff will carry the exact import/CLI
contract and test commands.
