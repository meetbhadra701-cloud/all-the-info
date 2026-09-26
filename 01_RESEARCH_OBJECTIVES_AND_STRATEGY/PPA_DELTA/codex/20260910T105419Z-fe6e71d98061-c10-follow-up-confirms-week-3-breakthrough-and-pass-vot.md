---
agent: codex
type: decision
created: 2026-09-10T10:54:19+00:00
---

# C10 follow-up confirms Week-3 breakthrough and PASS vote

# C10 follow-up — Week-3 breakthrough independently confirmed

Codex inspected Claude's actual handoff, implementation, and evidence, then ran the official
six-method comparison fresh through the shared harness and frozen EDA oracle. This Codex session
used no subagents.

## Official result

The comparison contains all 18 expected rows and all 18 final witnesses are valid. The shared
budget remains 200 candidates and 1800 seconds, cache is disabled, and the toolchain, library,
configuration, thresholds, starting hashes, and canonical SizeCounter are unchanged.

| Pair | Independent | Bugpoint | Coupled | No matching | Coupled advantage |
|---|---:|---:|---:|---:|---:|
| `f1-mux-share-add` | 39 | 47 | **30** | 30 | **23.08%** |
| `a2-share3-add` | 66 | 76 | **39** | 60 | **40.91%** |
| `f2s-factor-mult4` | 30 | 30 | **28** | 28 | 6.67% |

The preregistered 20% bar is reached on two of three development pairs. Every claimed coupled
endpoint has fresh uncached `INTERESTING` validation and formal PASS. Matching is materially
non-null on a2: 39 nodes with matching versus 60 without it.

## Integration and baseline findings

Codex wired Claude's gated canonicalization into the official shared runner as an ordinary
budgeted proposal, accepted only after an `INTERESTING` oracle result. Codex also repaired the
bugpoint adapter: simple Yosys logical-not syntax is lowered into the frozen parser subset and
non-port Yosys nets are side-prefixed so generated names cannot create false cross-side EQY
correspondence. Bugpoint now fails cleanly as valid `NO_GAIN` on all three pairs; the independent
baseline's sizes and hashes are unchanged.

The a2 trace starts with a fresh-valid matching-gated canonicalization, then maintains a continuous
accepted parent-hash lineage to the 39-node endpoint. Its lifted `sc0`/`sc1` controls are declared
inputs, so the formal PASS quantifies all their values. The transformation preserves the frozen
relational reduction predicate; it does not weaken equivalence, area thresholds, or nondegeneracy.

## Verification and vote

- 51/51 Codex tests pass.
- 43/43 Claude tests pass.
- `check_pack.py` passes.
- The machine audit independently verifies all 18 rows, identities, hashes, sizes, budgets,
  thresholds, final cache/formal states, and the 2/3 gate result.
- A fresh wheel was built at
  `runs/codex/c10-breakthrough-wheel-20260910T105000Z/ppa_delta-0.1.0-py3-none-any.whl`
  with SHA-256 `45E2FB979469353CED6E8AB6353A93E9261B5F6CF7EBC5EC6E01906E2EFF6F45`.

Codex changes its Week-3 vote from REVISE to **PASS**. This is development-set evidence only:
scaffold-lift was developed while examining the dev pairs and only a2 exercises it. Week 4 must
freeze and evaluate held-out pairs without further dev-set tuning.

Primary evidence:

- `docs/codex/week-3-breakthrough-audit.md`
- `runs/codex/c10-breakthrough-six-method-20260910T103000Z/comparison.json`
- `runs/codex/c10-breakthrough-audit-20260910T104500Z/audit.json`
