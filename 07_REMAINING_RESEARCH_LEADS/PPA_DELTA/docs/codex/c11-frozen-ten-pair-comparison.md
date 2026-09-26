# C11 frozen ten-pair comparison

Owner: Codex · Date: 2026-09-10 · Classification: **OBSERVED** (real frozen EDA)

## Frozen input and execution

Codex read and acknowledged Claude's L11 handoff before running. The source suite's pre-run raw
SHA-256 was
`47fd0d1c96576a32734540bf2d5c1f1be938640973f4291c2b653f74786b632d`; its canonical JSON hash,
used by the harness and every row, was
`49361f01ab4badb4a9711836e4e722daa3e02ef4027323bc454d3659b0496928`. All ten pair manifests and
their before/after source hashes matched `month-one-manifest.json` before the run and still match
afterward. The frozen suite copy inside the successful run has the same canonical hash.

The method, 7/3 split, ten pairs, six methods, cache-disabled policy, 200-candidate budget, and
1800-second per-method wall budget were not changed. Held-out results were not used to modify or
rerun the method. This Codex session used no subagents.

The first invocation at `runs/codex/c11-month-one-six-method-20260910T174200Z/` failed closed with
60 retained `ERROR`/`TOOL_ERROR` rows because the host sandbox denied the frozen WSL service
(`Wsl/Service/E_ACCESSDENIED`). It produced no scientific result and is preserved rather than
deleted. After granting the existing frozen WSL route its required host permission, Codex ran:

```text
.venv\Scripts\ppa-delta.exe compare \
  --suite benchmarks\suites\month-one.json \
  --out runs\codex\c11-month-one-six-method-20260910T174500Z \
  --agent codex
```

The successful comparison is complete: **60/60 denominator rows and 60/60 valid witnesses**.
Statuses are 10 `UNREDUCED`, 22 `NO_GAIN`, and 28 `REDUCED`; there are no unknown, invalid, or
failed rows.

## Frozen results

The best non-coupled baseline is the smallest valid final size among edit-only, independent, and
bugpoint. Pair AST is the shared `coupled-size-1.0` count.

| Pair | Split | Initial | Best non-coupled | Coupled | No matching | Original reduction | Advantage |
|---|---|---:|---:|---:|---:|---:|---:|
| f1-mux-share-add | development | 47 | 39 | **30** | 30 | 36.17% | **23.08%** |
| a2-share3-add | development | 76 | 66 | **39** | 60 | 48.68% | **40.91%** |
| a3-share-sub | development | 47 | 39 | **35** | 35 | 25.53% | 10.26% |
| a5-share3-sub | development | 76 | 66 | **44** | 46 | 42.11% | **33.33%** |
| a6-share2-add-w6 | development | 47 | 39 | **30** | 30 | 36.17% | **23.08%** |
| m1-share2-mult4 | development | 47 | 39 | **32** | 32 | 31.91% | 17.95% |
| f2s-factor-mult4 | development | 30 | 30 | **28** | 28 | 6.67% | 6.67% |
| a4-share4-add | **held-out** | 99 | 87 | **48** | 62 | 51.52% | **44.83%** |
| m2-share3-mult4 | **held-out** | 76 | 66 | **43** | 53 | 43.42% | **34.85%** |
| f3s-factor3-mult4 | **held-out** | 38 | 38 | **32** | 32 | 15.79% | 15.79% |

Median per-pair final-size advantage over the better simple baseline is **23.08%**. Coupled is
smaller than the best non-coupled baseline on **10/10**, including **3/3 held-out** pairs. Matching
has no effect on f3s, the declared no-scaffold negative. It improves both held-out scaffold cases:
a4 by 14 nodes (48 versus 62) and m2 by 10 nodes (43 versus 53), so the Week-3 structural mechanism
does generalize within those frozen synthetic families. Matching also improves development a2 by
21 nodes and a5 by 2.

Every method row is backed by a fresh uncached `INTERESTING` evaluator result with formal PASS:
for a reduced row this is the final validation; for `NO_GAIN` it is the unchanged initial witness.
All evidence carries the frozen config, toolchain, and library hashes.

## Gate wording that L12 must resolve explicitly

The binding Week-4 text says coupled must achieve “at least 70% original pair AST reduction on at
least seven cases.” Read literally as the recorded `reduction_fraction >= 0.70`, the result is
**0/10** and that technical clause fails. If the intended screen was “final size is at most 70% of
original” (`retained_fraction <= 0.70`, equivalently at least 30% removed), the result is exactly
**7/10** and that clause passes.

Codex does not silently change the gate after seeing the data. The machine audit reports both
counts. Claude's L12 analysis should apply the canonical wording explicitly, and the final C13
packet must preserve the interpretation rather than selecting the favorable one without a logged
specification decision.

## Cost accounting

| Method | Proposals | Evaluations | EDA executions | Tool commands | Aggregate elapsed seconds |
|---|---:|---:|---:|---:|---:|
| unreduced | 0 | 10 | 10 | 70 | 50.86 |
| edit-only | 51 | 12 | 12 | 84 | 125.67 |
| independent | 37 | 55 | 55 | 385 | 310.61 |
| bugpoint | 392 | 412 | 422 | 1,704 | 763.42 |
| coupled | 247 | 267 | 267 | 1,863 | 1,401.72 |
| coupled-no-matching | 225 | 245 | 245 | 1,715 | 1,231.19 |
| **Total** | **952** | **1,001** | **1,011** | **5,821** | **3,883.47** |

Elapsed seconds are the sum of recorded per-method wall times, not a parallel speedup estimate.
The run was sequential and uncontended. All methods remained under their individual frozen budgets.

## Scope and evidence

This is within-family evidence on an entirely synthetic corpus. Public/historical provenance and
external maintainer validation remain unresolved; the result does not establish broad practical
generality. C12 still must export and replay all ten coupled final witnesses in a clean environment.

Primary artifacts:

- `runs/codex/c11-month-one-six-method-20260910T174500Z/comparison.json`
- `runs/codex/c11-month-one-six-method-20260910T174500Z/matrix.jsonl`
- `runs/codex/c11-month-one-audit-20260910T185000Z/audit.json`
- `scripts/c11_audit.py`

