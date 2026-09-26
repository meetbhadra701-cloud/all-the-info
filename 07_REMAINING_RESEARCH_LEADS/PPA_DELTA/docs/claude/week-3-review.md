# Week 3 review and gate memo — Claude (L10)

Owner: Claude · Task L10 · 2026-09-10 · Classification: OBSERVED (real EDA) + DECISION.
Machine-readable rows: `runs/claude/l10-compare-20260910T022350Z/`; regenerable analysis:
`analysis/week3-comparison.md` (via `python analysis/week3_compare.py <comparison.json>`).
All six methods share one starting snapshot, the frozen 200/1800 budget, and cache disabled.

## Results (final pair-AST, lower is better)

| pair | unreduced | edit-only | independent | bugpoint | coupled | coupled-no-matching |
|---|---|---|---|---|---|---|
| f1 | 47 | 47 | 39 | 47✗ | **35** | 35 |
| a2 | 76 | 76 | 66 | 76✗ | **62** | 62 |
| f2s | 30 | 30 | 30 | 30✗ | **28** | 28 |

✗ = not a valid witness (bugpoint fails closed on a2/f2s; NO_GAIN on f1). Valid-export counts:
coupled 3/3 = every baseline; not lower than any method.

## Gate check — coupled vs the better simple baseline

| pair | better baseline | coupled | reduction | ≥20%? |
|---|---|---|---|---|
| f1 | 39 (independent) | 35 | 10.3% | no |
| a2 | 66 (independent) | 62 | 6.1% | no |
| f2s | 30 (both) | 28 | 6.7% | no |

**Coupled beats the better simple baseline on all three pairs, but the 20% bar is met on 0/3
(needs ≥2).** The advantage is real but modest (6–10%).

## Ablation — structural matching effect

| pair | coupled | coupled-no-matching | matching effect |
|---|---|---|---|
| f1 | 35 | 35 | 0 |
| a2 | 62 | 62 | 0 |
| f2s | 28 | 28 | 0 |

**Structural matching (L08 correspondence) provides zero measurable benefit on all three pairs.**
The correspondence-dependent CSE class fires on a2 but never yields an accepted reduction.

## Strongest negative interpretation (stated first, per the gate)

- The centerpiece 20% signal is **not met on any pair**. Coupled's edge over the baselines is
  6–10% — modest, and well under the predeclared heuristic.
- The **"structural correspondence" element of the L01 novelty claim is unsupported** by this
  evidence: matching is null. What remains is *coordinated* reduction.
- The reductions rely partly on degenerate-but-valid structures (e.g., `sel?c:c`) that the search
  leaves behind — a hint the current primitive set is not extracting the full coordinated gain.

## What genuinely survives (the fair, positive read)

- Coupled **beats every simple baseline on all three pairs**, at equal budget, same oracle, with
  3/3 valid exports and **no size-counting or budget artifact** — the C10 audit can check this.
- The advantage comes from a **distinct mechanism the baselines structurally cannot use**:
  coordinated input elimination (merge/const applied identically to both sides). Independent /
  edit-only edit one side at a time and would break the pair's mutual equivalence; `bugpoint` with
  an external predicate does not reduce these pairs at all (NO_GAIN / invalid). So the coupled
  advantage is not an unfair baseline restriction — it is a capability gap.

## Recommendation: **REVISE** (one bounded iteration), not STOP, not PASS

STOP is not warranted: the simple baselines are **not** as effective (coupled beats them on 3/3),
results reproduce, and the benefit is not from unmatched budgets or weakened constraints. PASS is
not warranted: the 20% bar is missed on every pair and matching is null.

Per the gate, one distinct mechanism shows a credible (if sub-threshold) benefit, so I mark
**REVISE** with a **single testable modification**:

> Add a coordinated *vacuous-construct simplification* primitive — collapse `cond ? X : X → X`
> and drop inputs that become unused after coordinated merge/const edits, applied identically to
> both sides — targeting exactly the degenerate structures the current search leaves (`sel?c:c`).
> Re-run the frozen three-pair comparison and re-test the 20% bar.

If, after that bounded iteration, coupled still fails to reach ≥20% on ≥2 pairs, the honest call is
**STOP/PIVOT** on the centerpiece size-advantage claim — while preserving the genuine, narrower
finding (coordinated relational-predicate reduction beats simple baselines by a modest, fair
margin; structural correspondence adds nothing). The novelty statement must be corrected to drop
"structural correspondence" regardless of the revision outcome.

## Vote: REVISE

Handoff to Codex for the C10 independent fairness audit (verify budgets, hashes, AST accounting,
final validation, and re-run ≥2 claimed results). Week 3 does not advance until both votes and the
bounded iteration resolve.
