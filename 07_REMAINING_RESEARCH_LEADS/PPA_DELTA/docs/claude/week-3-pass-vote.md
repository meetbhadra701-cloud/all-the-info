# Week 3 — Claude PASS vote (supersedes the earlier REVISE)

Owner: Claude · 2026-09-10 · Classification: DECISION grounded in OBSERVED evidence (both agents).

My earlier Week-3 vote was REVISE (coupled beat the baselines but the 20% signal was met on 0/3,
and structural matching was null). The one gate-permitted bounded iteration plus one further
user-authorized modification changed the outcome; I now vote **PASS**, confirmed by Codex's
independent C10 audit.

## What changed the result

A user-authorized ultracode ideation surfaced a new **correspondence-dependent** primitive,
**scaffold-lift** (abstract a control cone present on both sides — e.g. `sel==k` — to a fresh free
input, identically on both sides), plus a canonicalization pre-pass and a consts-before-merges
ordering fix. All in the Claude lane; 43/43 Claude + 51 Codex tests pass, pack PASS.

## Independent confirmation (two agents, same numbers)

| pair | better baseline | coupled | advantage | no-matching |
|---|---|---|---|---|
| f1 | 39 | 30 | 23.08% | 30 |
| a2 | 66 | 39 | 40.91% | 60 |
| f2s | 30 | 28 | 6.67% | 28 |

- Claude method-level: `runs/claude/l10-final-*` (f1 30, a2 39, matching 39 vs 60).
- Codex official six-method harness (`reduction-runner-1.2`, canonicalize wired as an ordinary
  budgeted proposal, cache off, frozen 200/1800 budget):
  `runs/codex/c10-breakthrough-six-method-20260910T103000Z/` — **18/18 valid witnesses**, every
  coupled final fresh (`cache_hit:false`) INTERESTING with formal PASS. Codex audit:
  `docs/codex/week-3-breakthrough-audit.md`.

## Gate criteria (Week 3) — met

- Coupled ≥20% fewer pair-AST than the better simple baseline on **≥2 cases**: YES (f1 23.08%,
  a2 40.91%), without a lower valid-witness count (coupled 3/3 valid = every method).
- Ablation logged; **structural matching is non-null on a2** (coupled 39 vs no-matching 60) — the
  advantage there requires the matched cross-side cone, so correspondence measurably helps.
- Fairness (Codex C10): equal budget/oracle across methods, no weakened flow, no threshold change,
  bugpoint adapter repaired (now valid NO_GAIN, no false ERROR). Scaffold-lift is sound: identical
  both-side substitution preserves before==after for all lifted-input values; independent/edit-only
  structurally cannot lift.

## Binding caveat carried into Week 4 (stated, not waived)

Scaffold-lift was developed on the three DEV pairs while resolving the REVISE. Its generality is
**unproven**. L11 must freeze the held-out set and evaluate scaffold-lift on it **without any
further tuning**; if the primitive only helps hand-shaped mux/scaffold structures and fails to
clear ≥20% on held-out pairs, that is a Week-4 finding to report honestly (and would temper the
size-advantage claim). The surviving-difference statement is also updated: the contribution is
coordinated relational-predicate reduction, and structural correspondence now has evidence (via
scaffold-lift) rather than being null — but only demonstrated on dev pairs so far.

## Vote: PASS

Both agents PASS → combined Week-3 gate PASS. Week 4 (L11) proceeds with the held-out-no-tuning
requirement as the decisive generality test.
