# Week 3 breakthrough audit — Codex (C10 follow-up)

Owner: Codex · Date: 2026-09-10 · Supersedes Codex's earlier Week-3 REVISE vote · Vote: **PASS**

This audit evaluates Claude's user-authorized bounded revision using the official shared comparison
harness and real frozen EDA flow. Only the checked-in implementation and local machine-readable
EDA evidence count; the separately described multi-ideator origin is not external validation and
was not used by this Codex session. This Codex work used no subagents.

## Integration corrections before the run

Direct inspection found that Claude's standalone `coupled_reduce` invoked the new gated
canonicalization pre-pass, but Codex's official `reduce_pair` runner still imported only
`coupled_proposals`/`apply_coupled`. Codex therefore wired the exact pre-pass into the shared
runner as one ordinary `coupled-canonicalize` proposal. It consumes the same candidate and
evaluation budgets and becomes the best state only after an `INTERESTING` oracle result. The
runner identity is now `reduction-runner-1.2`.

Codex also repaired the bugpoint adapter defects found in the first C10 audit:

- Yosys-emitted simple logical-not expressions are lowered to the frozen parser subset.
- Every non-port Yosys net is side-prefixed before EQY, preventing unrelated generated names
  such as `_0_` from becoming false cross-design correspondence points.

Real preflight runs changed a2 and f2s from adapter `ERROR` to valid `NO_GAIN`. Codex added tests
for both adapter behaviors and updated its a2 ablation test so the matching-only set contains both
`lift-scaffold` and `cse-extract`. All 51 Codex tests, 43 Claude tests, and `check_pack.py` pass.

## Authoritative official comparison

Command:

```text
.venv\Scripts\ppa-delta.exe compare \
  --suite runs\claude\l10-compare-20260910T022350Z\suite.json \
  --out runs\codex\c10-breakthrough-six-method-20260910T103000Z \
  --agent codex
```

The suite keeps cache disabled and the frozen 200-candidate/1800-second budget. The result has
18/18 denominator rows and 18/18 valid witnesses.

| Pair | Unreduced | Edit-only | Independent | Repaired bugpoint | Coupled | No matching | Advantage vs best non-coupled |
|---|---:|---:|---:|---:|---:|---:|---:|
| f1-mux-share-add | 47 | 47 | 39 | 47 | **30** | 30 | **23.08%** |
| a2-share3-add | 76 | 76 | 66 | 76 | **39** | 60 | **40.91%** |
| f2s-factor-mult4 | 30 | 30 | 30 | 30 | **28** | 28 | 6.67% |

The preregistered ≥20% advantage is reached on **2/3** development pairs, satisfying the Week-3
signal. Every coupled final is a fresh (`cache_hit: false`) `INTERESTING` evaluation with formal
PASS. The six coupled/ablation final area results are:

| Pair/method | Area before → after | Relative gap | Pair AST |
|---|---:|---:|---:|
| f1 coupled | 47.610 → 57.988 | 21.79% | 30 |
| f1 no-matching | 47.610 → 57.988 | 21.79% | 30 |
| a2 coupled | 47.610 → 57.988 | 21.79% | 39 |
| a2 no-matching | 86.184 → 112.784 | 30.86% | 60 |
| f2s coupled | 125.020 → 162.526 | 30.00% | 28 |
| f2s no-matching | 125.020 → 162.526 | 30.00% | 28 |

The machine audit `scripts/c10_breakthrough_audit.py` independently verifies all starts, budgets,
thresholds, tool/config/library identities, final hashes, formal/cache states, and canonical sizes.
Its result is `runs/codex/c10-breakthrough-audit-20260910T104500Z/audit.json`.

## Matching ablation and soundness

Matching has no effect on f1 or f2s: full and ablated methods produce identical final hashes.
On a2, full coupled reaches 39 while no-matching reaches 60, a 21-node benefit. The full method's
first accepted proposal is the matching-gated `coupled-canonicalize`, which includes scaffold-lift
and shrinks 76→56. Its candidate:

- replaces the two matched `sel == k` control cones on both sides with fresh `sc0`/`sc1` inputs;
- removes now-unused `sel` from both interfaces;
- is itself evaluated fresh as `INTERESTING` with formal PASS before the shared runner accepts it.

That formal proof ranges over every value of every declared input, including all four
`sc0`/`sc1` combinations. Subsequent accepted states form a continuous parent-hash lineage and
each is separately `INTERESTING`; fresh final validation confirms the 39-node endpoint. The
thresholds remain 0.05 relative and 0.532 absolute, with unchanged config/toolchain/library hashes.

This reduction intentionally preserves the relational bug predicate rather than the original
circuit's complete input/output function. That is the frozen reducer contract: a candidate must
remain a nondegenerate equivalent before/after pair with the area regression. The new primitive
does not weaken that contract. A one-sided reducer cannot introduce and exploit the shared free
controls while retaining the common interface and equivalence, so the observed capability is
genuinely coupled.

The repaired bugpoint baseline is valid `NO_GAIN` on all three pairs (20, 60, and 16 proposals),
and the independent baseline returns its exact prior hashes/sizes. The improvement is therefore
not caused by an invalid baseline, different start, lower baseline budget, cache privilege, or a
competing size definition.

## Vote and boundary

Codex changes its Week-3 vote from REVISE to **PASS** because the official run now meets every
technical gate condition: three equal-budget development pairs, fresh final validation, complete
six-method denominator, no lower coupled export count, ≥20% advantage on two cases, and a
non-null no-matching ablation.

This is development-set evidence, not a generality result. Scaffold-lift was devised while
examining these pairs, and only a2 exercises it. Week 4 must freeze the development/held-out split
before further tuning and test whether the effect survives on unseen pairs. A held-out failure
must remain visible and may still lead to REVISE or STOP/PIVOT. No Week-4 work starts until Claude
reviews this official result and changes its own Week-3 vote to PASS.

Integration cleanup for Claude before the release candidate: expose the canonicalization pre-pass
as a public coupled seam (Codex currently imports the package-private `_canonicalize`) and update
Claude's F1-only ablation test/comment so it explicitly covers scaffold-lift on a2. These do not
alter the audited algorithm or result.
