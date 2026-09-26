# L10 bounded-iteration outcome (Week-3 REVISE → verdict)

Owner: Claude · 2026-09-10 · Classification: OBSERVED (real EDA). Raw:
`runs/claude/l10-revised-20260910T030949Z/revised-ablation.json`. The single authorized
modification (coordinated vacuous-construct collapse + newly-unused-input removal) was
implemented and the frozen three-pair search re-run at the frozen 200/1800 budget.

## Result after the one permitted bounded iteration

| pair | better simple baseline | coupled before iter | coupled after iter | reduction vs baseline | ≥20%? |
|---|---|---|---|---|---|
| f1 | 39 | 35 | **32** | 17.9% | no (target ≤31; one node short) |
| a2 | 66 | 62 | 62 | 6.1% | no |
| f2s | 30 | 28 | 28 | 6.7% | no |

- All coupled results remain valid (fresh uncached INTERESTING; the area gap is preserved — the
  search stopped short of collapsing the two sides into identical structures, which would have
  been rejected as NOT_INTERESTING).
- Ablation still null after the new primitives: coupled == coupled-no-matching on all three
  (32/32, 62/62, 28/28). Structural matching contributes nothing.
- The new primitive helped only f1 (35→32); a2/f2s were unchanged (no vacuous construct on their
  best path stayed a valid regression once collapsed).

## Second iteration (user-authorized, beyond the gate's one) — algebraic identity folding

Added coordinated `x+0/0+x/x-0/x*1/1*x/x|0/0|x → x` folding (both sides), targeting the residue the
const/merge edits leave. Re-run `runs/claude/l10-rev2-20260910T033223Z/`:

| pair | baseline | iter1 | iter2 | reduction vs baseline | ≥20%? |
|---|---|---|---|---|---|
| f1 | 39 | 32 | **30** | 23.1% | **YES** |
| a2 | 66 | 62 | 62 | 6.1% | no |
| f2s | 30 | 28 | 28 | 6.7% | no |

f1 now clears (folded `c + 8'd0 → c`, fresh INTERESTING, area gap preserved). **a2 and f2s are
unchanged → 1/3 at 20% (gate needs ≥2).** Ablation still null throughout.

### Why a2/f2s are structurally stuck (the real finding)

The coupled advantage is bounded by the requirement to **preserve the area gap**: reductions can
only shrink the pair until the two sides converge, at which point the gap vanishes and the oracle
rejects (NOT_INTERESTING). For a2 (`shared 3-way adder` vs `3 adders`) and f2s (`b*(b+c)` vs
`b*b+b*c`), that convergence floor sits at ~6% advantage — every further coordinated edit tried
(more merges/consts) collapses the 2-vs-1-operator gap. So the ~6% is not a search weakness; it is
a structural ceiling for these pairs. Only f1's mux-share structure had removable non-gap residue.

## Verdict: after TWO iterations the 20% claim is met on 1/3 (need ≥2) — STOP/PIVOT stands

Per the Week-3 gate, one bounded iteration was permitted and is now spent. The honest call is
**STOP / PIVOT on the centerpiece "≥20% coupled size advantage" claim.**

What is defeated:
- The ≥20% size-advantage claim (best is f1 at 17.9%, one node short; a2/f2s ~6%).
- The "structural correspondence" element of the L01 novelty claim (matching is null throughout).
- Week-4 technical targets are further out of reach (they require ≥70% original AST reduction on
  ≥7 cases and ≥20% median advantage — current original reductions are 32%/18%/7%).

What honestly survives (the pivot candidate, not the original claim):
- Coupled reduction **beats every simple baseline on all three pairs** (f1 17.9%, a2 6.1%, f2s
  6.7%), at equal budget, same oracle, 3/3 valid exports, with **no size/budget artifact** — via a
  distinct mechanism the baselines structurally cannot use (coordinated input elimination on both
  sides). `bugpoint` does not reduce these pairs at all.
- This is a real but modest, fair, reproducible advantage — a *diagnostic-reduction* contribution,
  not a 20% size-advantage result.

## Recommendation (user decision — month-one verdict is theirs)

1. **STOP/PIVOT** the centerpiece 20% claim; either pivot to the narrower honest finding
   (coordinated relational-predicate reduction beats simple baselines by a modest fair margin;
   correspondence adds nothing) or stop the research claim. This is the gate-indicated call.
2. The user has signalled a last-resort external lever ("astra 6"). That is the user's to deploy
   if they wish to pursue the 20% claim further; it is outside my inline scope and I have not used
   it. If deployed, it would constitute a further (unbudgeted) iteration beyond the one the gate
   permits, and any result must be re-audited for fairness before any PASS.

I am not latching a STOP vote unilaterally: the month-one continue/stop verdict is explicitly the
user's, and they have signalled a fallback. I am reporting the honest technical outcome and the
gate-indicated recommendation, and awaiting the user's direction.
