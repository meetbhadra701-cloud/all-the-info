---
agent: codex
type: handoff
created: 2026-09-10T18:52:27+00:00
---

# C11 complete; frozen rows ready for L12

# Codex → Claude: C11 complete; take frozen rows into L12

C11 is complete on the unchanged frozen suite. Read the raw rows and machine audit rather than this
summary alone.

## Authoritative run

- `runs/codex/c11-month-one-six-method-20260910T174500Z/comparison.json`
- 60/60 denominator rows; 60/60 valid witnesses.
- Statuses: 10 UNREDUCED, 22 NO_GAIN, 28 REDUCED; no failures or unknowns.
- All ten coupled finals are fresh uncached INTERESTING with formal PASS.
- Suite canonical hash: `49361f01ab4badb4a9711836e4e722daa3e02ef4027323bc454d3659b0496928`.
- Source-file SHA-256: `47fd0d1c96576a32734540bf2d5c1f1be938640973f4291c2b653f74786b632d`.

## Frozen metrics for your independent L12 analysis

| Pair | Split | Initial | Best simple | Coupled | No matching | Coupled advantage |
|---|---|---:|---:|---:|---:|---:|
| f1 | dev | 47 | 39 | 30 | 30 | 23.08% |
| a2 | dev | 76 | 66 | 39 | 60 | 40.91% |
| a3 | dev | 47 | 39 | 35 | 35 | 10.26% |
| a5 | dev | 76 | 66 | 44 | 46 | 33.33% |
| a6 | dev | 47 | 39 | 30 | 30 | 23.08% |
| m1 | dev | 47 | 39 | 32 | 32 | 17.95% |
| f2s | dev | 30 | 30 | 28 | 28 | 6.67% |
| a4 | **held-out** | 99 | 87 | 48 | 62 | 44.83% |
| m2 | **held-out** | 76 | 66 | 43 | 53 | 34.85% |
| f3s | **held-out** | 38 | 38 | 32 | 32 | 15.79% |

Median advantage is 23.08%. Coupled beats the best simple baseline on 10/10 and on 3/3 held-out.
Matching helps both held-out scaffold cases (a4 by 14 nodes, m2 by 10) and is null on the declared
no-scaffold f3s negative. This is within-family synthetic generalization only; public provenance
and actual external review remain unresolved.

Please address one gate-text ambiguity explicitly in L12. The binding wording says “at least 70%
original pair AST reduction.” Literal `reduction_fraction >= 0.70` is 0/10. If the intended metric
was final AST at most 70% of original, that count is exactly 7/10. Codex has not silently selected
the favorable interpretation. Report both and ground your recommendation in the canonical text.

Costs are fully machine-readable: 952 proposals, 1,001 evaluations, 1,011 EDA executions, 5,821
tool commands, 3,883.47 aggregate method-seconds. See
`runs/codex/c11-month-one-audit-20260910T185000Z/audit.json` and
`docs/codex/c11-frozen-ten-pair-comparison.md`.

The first invocation at `runs/codex/c11-month-one-six-method-20260910T174200Z/` is preserved as a
host-permission failure (`Wsl/Service/E_ACCESSDENIED`); it is not the scientific matrix. The second
run used the same hashes after WSL access was permitted. The no-tuning covenant was honored.

L12 is now ready. C12 remains blocked until your L12 analysis is done.
