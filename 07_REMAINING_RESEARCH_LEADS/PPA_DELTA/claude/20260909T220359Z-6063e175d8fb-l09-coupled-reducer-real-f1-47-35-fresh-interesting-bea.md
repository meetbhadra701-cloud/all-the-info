---
agent: claude
type: experiment
created: 2026-09-09T22:03:59+00:00
---

# L09 coupled reducer: real f1 47->35 (fresh INTERESTING); beats independent 39 by 10.3%, short of 20% bar

Classification: OBSERVED (real EDA) + DESIGN. L09 coupled reducer complete + integration contract.

## Real reduction (acceptance met)

Coupled greedy search on f1 via the real oracle reduced **47 → 35 pair-AST**, fresh uncached
final validation **INTERESTING** (formal PASS, area 47.614→57.988, delta_rel 0.218, cache_hit
False). Run: `runs/claude/l09-coupled-f1-20260909T215830Z/`. Uses `snapshot_candidate` +
`materialize_candidate` + the shared SizeCounter — no private evaluator. Full writeup:
`docs/claude/l09-coupled-reducer.md`. 42/42 Claude tests, check_pack PASS.

## Honest headline result

Coupled 35 vs independent 39 → coupled wins by **10.3%**, SHORT of the ≥20% Week-3 bar (f1 ≤ 31).
Real, fresh-validated win, but not a Week-3 PASS on this case. The full multi-pair + ablation
comparison (L10) decides the gate; I am not prejudging it. The win is fair: the decisive edits
(`merge-inputs`, `input-const`) are inherently coordinated — independent cannot do them without
breaking equivalence. Caveat: the search reaches degenerate-but-valid shapes (`sel?c:c`); a richer
coordinated primitive (collapse vacuous muxes, drop newly-unused inputs) is the obvious lever
toward ≤31 and a candidate for the Week-3 bounded revision — for L10 to decide.

## C09 integration contract (coupled + no-matching runners)

Wire `method in {"coupled","coupled-no-matching"}` into `reduce_pair` running the SAME greedy loop
as independent, sourcing proposals from:

```python
from ppa_delta.coupled.strategy import coupled_proposals, apply_coupled
# coupled:             coupled_proposals(state, use_matching=True)
# coupled-no-matching: coupled_proposals(state, use_matching=False)
# apply_coupled(state, proposal) -> ppa_delta.baselines.core.PairState
```

`apply_coupled` returns the same `PairState` type; your `context.try_state` consumes it unchanged,
so budget/trace/immutable-dirs/fresh-validation match the baselines exactly (the fairness point for
C10). The standalone `ppa_delta.coupled.reducer.coupled_reduce(pair_manifest, oracle, budget,
run_dir, *, use_matching, use_cache)` is available if you prefer to call it directly. Both reuse
`snapshot_candidate`. Please review inline, wire the CLI + registry, and run the equal-budget
comparison; send any interface fix by handoff (I fix in my lane).

Next for me: L10 (development comparison + ablation) depends on your C09. I remain quiescent for a
git checkpoint.
