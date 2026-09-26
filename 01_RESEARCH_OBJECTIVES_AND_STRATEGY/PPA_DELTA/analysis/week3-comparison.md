# L10 — Week-3 frozen comparison and ablation

Source: `runs/claude/l10-compare-20260910T022350Z/comparison.json` · classification: OBSERVED (real EDA).
All methods share one starting snapshot, the frozen 200/1800 budget, cache disabled.

## Final pair-AST by method (lower is better)

| pair | unreduced | edit-only | independent | bugpoint | coupled | coupled-no-matching |
|---|---|---|---|---|---|---|
| f1-mux-share-add | 47 | 47 | 39 | 47 | 35 | 35 |
| a2-share3-add | 76 | 76 | 66 | 76✗ | 62 | 62 |
| f2s-factor-mult4 | 30 | 30 | 30 | 30✗ | 28 | 28 |

✗ = not a valid witness. Valid-export counts: unreduced=3, edit-only=3, independent=3, bugpoint=1, coupled=3, coupled-no-matching=3

## Gate check — coupled vs the better simple baseline

| pair | better baseline (edit-only/independent) | coupled | reduction vs baseline | ≥20%? |
|---|---|---|---|---|
| f1-mux-share-add | 39 | 35 | 10.3% | no |
| a2-share3-add | 66 | 62 | 6.1% | no |
| f2s-factor-mult4 | 30 | 28 | 6.7% | no |

## Ablation — structural matching effect (coupled vs coupled-no-matching)

| pair | coupled | no-matching | matching effect |
|---|---|---|---|
| f1-mux-share-add | 35 | 35 | 0 nodes |
| a2-share3-add | 62 | 62 | 0 nodes |
| f2s-factor-mult4 | 28 | 28 | 0 nodes |

## Verdict (machine-readable)

```json
{
  "pairs": [
    "f1-mux-share-add",
    "a2-share3-add",
    "f2s-factor-mult4"
  ],
  "coupled_beats_baseline_20pct_on": 0,
  "gate_20pct_met": false,
  "coupled_valid_not_lower": true,
  "matching_helps_on_pairs": 0,
  "recommendation": "REVISE_OR_STOP"
}
```
