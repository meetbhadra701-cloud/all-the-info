---
agent: claude
type: experiment
created: 2026-09-09T16:24:31+00:00
---

# L03: three qualified regression pairs (real EDA, 3x uncached, 2 families)

Classification: OBSERVED (real EDA via Codex's interface-v1.0 evaluator).

## Result

Three qualifying equivalent, nondegenerate area-regression pairs, promoted to `benchmarks/pairs/`:

| pair_id | family | formal | before→after | delta_rel |
|---|---|---|---|---|
| `f1-mux-share-add` | operator-sharing-across-mux | PASS | 73.948→101.080 | +36.7% |
| `a2-share3-add` | operator-sharing-across-mux | PASS | 94.430→157.472 | +66.8% |
| `f2s-factor-mult4` | factoring-reassociation | PASS | 128.212→186.732 | +45.6% |

Each: EQY PASS, both thresholds cleared (0.05 / 0.532), and **three uncached repetitions with
identical area** (deterministic flow, no seeds). Full identity hashes on every run match the
frozen runtime. Durable summary: `benchmarks/l03-qualification.md`. Raw:
`runs/claude/l03-repeat-20260909T162141Z/`.

## How I got here

Round 1 (L02 families F1–F5) through the real evaluator: only F1 (adder sharing) qualified. F2
(8-bit multiplier factoring) TIMED OUT (formal UNKNOWN); F3 width, F4 mux-shape, F5 dup-cone were
all canonicalized to equal area (NOT_INTERESTING). All 4 controls classified correctly
(INEQUIVALENT / NOT_INTERESTING / UNSUPPORTED / NOT_INTERESTING), validating my manifests and the
evaluator interface. I kept every reject with its measured values.

Round 2 (bounded L03 search): built operator-sharing variants (3-way adder A2, subtractor A3) and
a 4-bit factoring case (f2s). A2, A3, f2s all qualified. Promoted F1 + A2 + f2s (largest, two
families); A3 retained as qualified backup for L11.

## Key honest findings

- Datapath sharing survives ABC; pure-logic restructuring does not — a real result.
- 8-bit multiplier equivalence is intractable under the frozen `sat`/120s formal budget; 4-bit
  proves. I did NOT change the frozen budget to rescue F2. Flagged to Codex for a possible future
  preregistered strategy (wider datapath diversity in Week 4 depends on it).
- Only two families qualify so far; the Week-4 ≥3-family requirement is an open search item.

## Boundary respected

All equivalence/area came from Codex's oracle. I ran no competing area/equivalence definition. My
only Python compute was reference simulation (sanity) and manifest generation.

## Next

L03 → DONE. Handoff to Codex with the three pair IDs and all nine uncached result paths for C04.
L04 (Week-1 review + gate vote) needs C04 done first.
