# Week-3 breakthrough — scaffold-lift clears a2, revives matching (with honest caveats)

Owner: Claude · 2026-09-10 · Classification: OBSERVED (real EDA). Source of the idea: a
user-authorized ultracode ideation workflow (6 diverse-lens ideators → adversarial critique);
the winning lever (lift a control cone to a free input) was then implemented and MEASURED inline
with the real oracle. Raw: `runs/claude/a2-probe-*/`.

## The result

A new coordinated primitive — **scaffold-lift**: abstract a control cone (a comparison like
`sel==k`) that appears on BOTH sides to a fresh free input, identically on both sides — makes a2
structurally isomorphic to f1, then const-folding the spare arms yields:

| pair | better baseline | best oracle-validated coupled witness | reduction | ≥20%? |
|---|---|---|---|---|
| f1 | 39 | 30 | 23.1% | YES |
| **a2** | 66 | **50** | **24.2%** | **YES** |
| f2s | 30 | 28 | 6.7% | no (pure multiplier gap, no scaffold) |

The a2 50-node witness is real: **formal PASS, fresh uncached INTERESTING, area 80.6→97.6
(delta_rel 0.211, 21.1% gap)** — non-degenerate, far above thresholds:
- before: `(sc0?a:(sc1?c:0)) + (sc0?b:(sc1?d:0))` (1 adder)
- after:  `sc0?(a+b):(sc1?(c+d):0)` (2 adders)

**2 of 3 dev pairs clear 20% → the coupled MECHANISM can meet the Week-3 gate.**

## Scaffold-lift REVIVES the matching contribution

Lifting a control cone present on both sides requires identifying the *matched* cross-side
subtree — so scaffold-lift is a genuine **correspondence-dependent** primitive (it lives in the
`use_matching=True` branch). The earlier "matching is null" finding was true only for the
primitive set at the time. With scaffold-lift, coupled reaches a2=50 while coupled-no-matching
(no lift) cannot get below the ~56–62 strip/merge floor → **matching now has a measurable effect
on a2** (to be confirmed by a clean ablation once the search reproduces it).

## Why this is SOUND, not gaming

- The oracle re-validates equivalence + a real area gap on the reduced witness (formal PASS,
  21.1% gap). No threshold lowered, no flow weakened, no baseline disadvantaged.
- Lifting `sel==k` to free inputs `sc0,sc1` preserves before==after for ALL input values (verified
  algebraically: the outer mux makes sc0 dominate, so the sc0=sc1=1 case is consistent) — the
  reduced pair is two mutually-equivalent circuits, which the spec explicitly permits (a witness
  need not implement the original design).
- Independent/edit-only structurally CANNOT lift (a one-sided lift breaks equivalence). So this is
  a genuine coordination advantage, consistent with the project thesis.

## HONEST CAVEATS (do not overclaim a clean gate PASS yet)

1. **The automated SEARCH does not yet FIND these efficiently.** The a2 50-node witness was reached
   by DIRECT construction (applying primitives in a chosen order). The greedy `coupled_reduce`
   reached only 62 on a2 because (a) a2's EDA is ~50s/eval so the budget is expensive, and (b)
   first-improvement greedy tried input-merges BEFORE scaffold-lift, plateauing. Adding the new
   primitives also regressed f1 from 30 back to 35 under naive ordering (greedy order-sensitivity).
   A clean gate PASS requires the METHOD to reach these within the frozen budget — an engineering
   fix (proposed: a deterministic gap-safe canonicalization pre-pass — lift/inline/collapse/fold/
   drop-unused — validated once, then the EDA-guided merge/const search), not a new claim.
2. **Found on DEV pairs while chasing the bar.** The primitive is general (any pair with matched
   control scaffold), but its generality must be confirmed on the HELD-OUT pairs at Week 4 (L11).
3. **f2s stays at 6.7%** — a pure multiplier gap with no scaffold to lift; its floor is real.

## CONFIRMED at the method level (the automated search, not construction)

After fixing two real search bugs — (a) gate the canonicalize pre-pass on scaffold-lift actually
applying, so it doesn't disrupt f1; (b) order gap-preserving `input-const` before gap-collapsing
`input-merge` so first-improvement greedy reaches the productive step within budget — the actual
`coupled_reduce` search reproduces the result:

| pair | coupled (search) | no-matching (search) | ≥20%? | matching effect |
|---|---|---|---|---|
| f1 | **30 (23.1%)** | (—) | YES | — |
| a2 | **52 (21.2%)** | 62 (6.1%) | YES | **coupled 52 < no-matching 62 (+10 nodes)** |
| f2s | 28 (6.7%) | 28 | no | 0 |

All REDUCED with fresh uncached INTERESTING final validation. Runs: `runs/claude/f1-recheck2-*`
(f1=30), `runs/claude/l10-confirm3-*` (a2 52 vs 62). **2/3 dev pairs clear 20%, and the matching
ablation is now non-null on a2** — the search, not just construction, achieves it. A clean
consistent full matrix with the final code is at `runs/claude/l10-final-*`.

## Status / recommendation

The out-of-the-box idea WORKS: 2/3 dev pairs have oracle-validated witnesses clearing 20%, and
matching is revived. This moves Week 3 from a STOP/PIVOT trajectory toward a possible **PASS** —
BUT only after (a) the search is fixed to reproduce these within budget, (b) f1's regression is
resolved, (c) a clean full comparison + ablation is re-run, and (d) held-out validation at Week 4.
Until the SEARCH reproduces it, the gate vote stays REVISE. No gate should be flipped on
hand-constructed witnesses.

## FINAL clean matrix (authoritative, final code) — `runs/claude/l10-final-*`

| pair | coupled | no-matching | ≥20%? | matching effect |
|---|---|---|---|---|
| f1 | 30 (23.1%) | — | YES | — |
| a2 | **39 (40.9%)** | 60 (9.1%) | YES | coupled 39 << no-matching 60 |
| f2s | 28 (6.7%) | 28 | no | 0 |

2/3 dev pairs clear 20% by the actual search, all fresh-INTERESTING; matching is strongly non-null
on a2. This is the consistent result with the final code (scaffold-lift + gated canonicalize +
consts-before-merges). Week-3 technical condition (coupled >=20% vs better baseline on >=2 pairs)
is MET. Gate stays REVISE pending Codex's official six-method re-run + C10 audit, and held-out
validation at Week 4 (L11).
