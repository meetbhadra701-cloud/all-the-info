# L12 — Month-one complete experiment analysis

Source rows: `runs/codex/c11-month-one-six-method-20260910T174500Z/comparison.json` · classification: OBSERVED (real EDA).
Regenerate: `python analysis/month_one_analysis.py <comparison.json>`. All numbers below are computed from the frozen per-row artifacts; nothing is from recollection.

## Method comparison (final pair-AST; lower is better)

| pair | split | family | unred | edit | indep | bugpoint | **coupled** | no-match | adv vs best baseline | orig AST reduction |
|---|---|---|---|---|---|---|---|---|---|---|
| f1-mux-share-add | deve | op-share | 47 | 47 | 39 | 47 | **30** | 30 | 23.1% | 36.2% |
| a2-share3-add | deve | op-share | 76 | 76 | 66 | 76 | **39** | 60 | 40.9% | 48.7% |
| a3-share-sub | deve | op-share | 47 | 47 | 39 | 47 | **35** | 35 | 10.3% | 25.5% |
| a5-share3-sub | deve | op-share | 76 | 76 | 66 | 76 | **44** | 46 | 33.3% | 42.1% |
| a6-share2-add-w6 | deve | op-share | 47 | 47 | 39 | 47 | **30** | 30 | 23.1% | 36.2% |
| m1-share2-mult4 | deve | mul-share | 47 | 47 | 39 | 47 | **32** | 32 | 17.9% | 31.9% |
| f2s-factor-mult4 | deve | factor | 30 | 30 | 30 | 30 | **28** | 28 | 6.7% | 6.7% |
| a4-share4-add | held | op-share | 99 | 99 | 87 | 99 | **48** | 62 | 44.8% | 51.5% |
| m2-share3-mult4 | held | mul-share | 76 | 76 | 66 | 76 | **43** | 53 | 34.8% | 43.4% |
| f3s-factor3-mult4 | held | factor | 38 | 38 | 38 | 38 | **32** | 32 | 15.8% | 15.8% |

## Ablation — structural matching effect (coupled vs coupled-no-matching)

| pair | split | scaffold? | coupled | no-match | matching effect |
|---|---|---|---|---|---|
| f1-mux-share-add | deve | no | 30 | 30 | 0 |
| a2-share3-add | deve | yes | 39 | 60 | +21 |
| a3-share-sub | deve | no | 35 | 35 | 0 |
| a5-share3-sub | deve | yes | 44 | 46 | +2 |
| a6-share2-add-w6 | deve | no | 30 | 30 | 0 |
| m1-share2-mult4 | deve | no | 32 | 32 | 0 |
| f2s-factor-mult4 | deve | no | 28 | 28 | 0 |
| a4-share4-add | held | yes | 48 | 62 | +14 |
| m2-share3-mult4 | held | yes | 43 | 53 | +10 |
| f3s-factor3-mult4 | held | no | 32 | 32 | 0 |

## Per-family advantage (coupled vs better baseline)

| family | pairs | median adv | matching helps |
|---|---|---|---|
| operator-sharing-across-mux | 6 | 28.2% | 3/6 |
| multiplier-sharing-across-mux | 2 | 26.4% | 1/2 |
| factoring-reassociation | 2 | 11.2% | 0/2 |

## Week-4 technical bars (computed; the ≥70% bar reported BOTH ways, gate unchanged)

- Exported witnesses reproduce equivalence+area: **10/10** valid (60/60 rows valid). ✅
- **≥70% ORIGINAL pair-AST reduction on ≥7 cases** — literal reading (remove ≥70%): **0/10** → NOT met.
  - Alternative reading (final size ≤70% of original, i.e. remove ≥30%): **7/10**. Reported without changing the pre-registered gate.
- ≥20% MEDIAN advantage vs better baseline: **23.08%** (6/10 pairs individually ≥20%). ✅
- ≥2 held-out cases show a coupled advantage: **3/3** held-out. ✅
- Cost (coupled method): 247 proposals, 267 evaluations, 267 EDA executions, 1863 tool commands, 1402 method-seconds.

## Interpretation (strongest-negative first, per the gate)

- **No pair reaches 70% ORIGINAL-AST reduction** (max is a4 at 51.5%). Under the literal reading of the pre-registered ≥70%-reduction bar, that technical condition is NOT met (0/10). This is a real shortfall, not a wording quibble I get to define away.
- **The advantage is modest on several pairs**: f2s +6.7%, a3 +10.3%, f3s +15.8%, m1 +17.9% — four pairs fall below the 20% mark individually; the 23.08% figure is a MEDIAN, not a floor. Small multiplier/factoring pairs are near their gap-preservation floor.
- **Matching helps ONLY where scaffold exists** (a2, a5, a4, m2 = the multi-select cases); on 6/10 pairs coupled==no-matching. So the revived correspondence effect is real but narrow — concentrated in `sel==k` mux structures, absent elsewhere.
- **Practical relevance is UNRESOLVED**: the corpus is entirely synthetic and no external maintainer review occurred. Ten synthetic examples support feasibility, not generality or real-world usefulness. No statistical-significance claim is made from n=10.

## What genuinely holds

- Coupled beats the better simple baseline on **10/10** pairs, all fresh uncached formal-PASS INTERESTING, at equal budget/oracle — via coordinated edits (input elimination, scaffold-lift) that per-side baselines structurally cannot do. Bugpoint reduces none.
- **Held-out advantage 3/3**, and scaffold-lift **generalizes** to unseen structures (a4 4-way: 48 vs 62; m2 3-way mult: 43 vs 53) — matching was not tuned on these.
- Median advantage 23.08% clears the ≥20% median bar; ≥2-held-out bar clears (3/3).

## Verdict inputs (machine-readable; L13 decides the recommendation)

```json
{
  "pairs": 10,
  "rows_valid": true,
  "coupled_valid": 10,
  "coupled_beats_baseline_on": 10,
  "median_advantage_pct": 23.08,
  "advantage_ge20_on": 6,
  "orig_reduction_ge70_on": 0,
  "orig_reduction_ge30_on": 7,
  "heldout_advantage_on": 3,
  "matching_helps_on": 4,
  "bar_70pct_literal_met": false,
  "bar_median20_met": true,
  "bar_heldout2_met": true,
  "bar_tenof ten_valid": true,
  "practical_relevance": "UNRESOLVED (synthetic corpus, no external review)"
}
```
