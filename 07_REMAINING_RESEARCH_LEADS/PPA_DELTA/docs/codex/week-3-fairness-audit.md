# Week 3 fairness audit — Codex (C10)

Owner: Codex · Task: C10 · Date: 2026-09-09/10 · Vote: **REVISE**

This memo independently audits Claude's frozen L10 comparison rather than accepting its derived
summary. The authoritative input is
`runs/claude/l10-compare-20260910T022350Z/comparison.json`. The executable audit is
`scripts/c10_fairness_audit.py`; its result is
`runs/codex/c10-fairness-audit-20260910T025500Z/audit.json`.

## Fairness and accounting

- The denominator is complete: 18/18 rows (three pairs × six methods), all retained.
- Every row has the same suite hash and the frozen 200-candidate/1800-second limits.
- Within each pair, all six methods have the same initial pair hash and complete canonical size.
- I independently recomputed every non-unreduced valid row's best size and pair hash by calling the
  evaluator's public `snapshot_candidate` seam, which invokes the sole shared
  `coupled-size-1.0` counter. All values match the row and evaluation records.
- All 16 valid rows point to fresh (`cache_hit: false`) `INTERESTING` evaluations with formal PASS
  and matching candidate hashes. Reduced methods have a distinct final validation; unchanged
  methods retain their fresh initial validation. The two invalid rows remain in the denominator.
- The test suites remain green: 48/48 Codex tests, 43/43 Claude tests, and `check_pack.py` PASS.

The fixed starting identities are:

| Pair | Initial hash | Pair AST |
|---|---|---:|
| f1-mux-share-add | `18f6633b8f7d03f3689c748857ffae290d1be6e10aea9d40fe4845d5151d94e2` | 47 |
| a2-share3-add | `0fab2227e70992c1491bab0c5a92418150ca3774884fc96d07dbd77c8917179d` | 76 |
| f2s-factor-mult4 | `8b13cb0f3e78293cb6d314f01ddcded2e646dbb9e313007d4f6ff90bcb120893` | 30 |

## Recomputed result

| Pair | Better valid non-coupled baseline | Coupled | Advantage | ≥20%? | No-matching |
|---|---:|---:|---:|---:|---:|
| f1-mux-share-add | 39 (independent) | 35 | 10.26% | no | 35 |
| a2-share3-add | 66 (independent) | 62 | 6.06% | no | 62 |
| f2s-factor-mult4 | 30 (edit-only/independent) | 28 | 6.67% | no | 28 |

Coupled is smaller than the best valid baseline on 3/3 cases, but the preregistered 20% signal is
met on 0/3 rather than the required two. Coupled and no-matching have the same final size **and
the same final hash on all three pairs**. Structural matching therefore has no measured effect.

## Independent reproduction

I reran two claimed coupled benefits through the public CLI with cache disabled and the same full
budget:

| Pair | L10 result | Codex rerun | Final predicate |
|---|---:|---:|---|
| a2-share3-add | 76 → 62 | 76 → 62 | fresh INTERESTING, formal PASS |
| f2s-factor-mult4 | 30 → 28 | 30 → 28 | fresh INTERESTING, formal PASS |

The final hashes also reproduce exactly: a2
`43946d83877e982cd7739d87d55e1f21beb8ef7fd72bdcd0770876f5dcddc1da`; f2s
`fcb697d7b531b58337f739e7ffba833b06acca144966b19b50ffde888cd4fb31`.
Evidence is under `runs/codex/c10-rerun-a2-20260910T024500Z/` and
`runs/codex/c10-rerun-f2s-20260910T025000Z/`.

## Mechanism audit

The gain over independent reduction is not a size-counter artifact. On f1 and a2, coupled first
accepts `coupled-inline-all`, reaching exactly the independent baseline's final hash. It then
accepts coordinated transformations unavailable to a one-side-at-a-time reducer:

- f1: `coupled-const0-d`, `coupled-merge-a-into-c`;
- a2: `coupled-merge-a-into-b`, `coupled-merge-b-into-c`;
- f2s: `coupled-merge-a-into-b` (independent has no accepted proposal).

Each transformation changes the common interface and both implementations together, then passes
the unchanged relational oracle. Applying it to only one side would violate the shared interface
or equivalence. This is a real coordination capability gap. It is **not** evidence for structural
correspondence: the corrected ablation reaches byte-identical finals without matching.

## Bugpoint caveat found by C10

Claude's prose calls bugpoint "NO_GAIN/invalid," but the raw rows are more specific:

- f1 is a valid `NO_GAIN` bugpoint result (47);
- a2 is `ERROR` before any proposal because the adapter cannot parse Yosys-emitted `! sel`;
- f2s is `ERROR` because the post-export initial pair is classified `INEQUIVALENT`.

These are fail-closed outcomes, so they do not create a false successful witness and are correctly
retained as failures. They do, however, expose an accidental baseline disadvantage in the Codex
adapter. Consequently, the present evidence supports the 6–10% advantage over the best **valid**
independent/edit-only baseline; it does not establish superiority to a fully functioning bugpoint
baseline on a2 or f2s. Codex must repair and rerun that adapter as experiment hygiene before any
stronger comparison claim or bounded-iteration decision.

## Vote: REVISE

PASS is unavailable: coupled reaches the 20% threshold on 0/3 cases, and matching is null. STOP is
premature: the modest coordination-only benefit reproduces on all three cases and cannot be
explained by starting hashes, budgets, final validation, or canonical-size accounting.

I concur with exactly one testable method modification for the permitted bounded iteration:

> Add coordinated vacuous-construct simplification: collapse `cond ? X : X` to `X`, then drop
> inputs made unused by the already-accepted coordinated merge/constant transformations.

The revised frozen comparison must also use a repaired bugpoint adapter; that is correction of a
baseline validity defect, not an additional coupled-method modification. The L01 contribution must
be narrowed now from structural-correspondence-guided reduction to **coordinated reduction under a
relational predicate**. If the one method modification still fails to achieve ≥20% on at least two
cases—or a corrected bugpoint baseline removes the advantage—the prescribed outcome is STOP/PIVOT
for the centerpiece size-advantage claim.
