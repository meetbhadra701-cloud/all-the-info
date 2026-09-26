# Month One Task Map

Read [[01-Project/Weekly-Gates]] for evidence gates. Tasks are not calendar promises.

## Week 1

| Task | Owner | Work | Dependencies |
|---|---|---|---|
| C01 | codex | Runtime and environment | None |
| C02 | codex | Contracts and package skeleton | C01 |
| C03 | codex | Real smoke evaluator | C02 |
| C04 | codex | Validate three regression pairs | C03, L03 |
| L01 | claude | Focused novelty gate | None |
| L02 | claude | Candidate pair inventory | None |
| L03 | claude | Qualify three real regressions | L02, C03 |
| L04 | claude | Week 1 review and corpus plan | L01, L03, C04 |

Both agents vote after their weekly tasks. Next-week tasks require both PASS.

## Week 2

| Task | Owner | Work | Dependencies |
|---|---|---|---|
| C05 | codex | Harden the oracle | C04 |
| C06 | codex | Simple reduction baselines | C05, L05 |
| C07 | codex | Export replay and automatic notes | C06, L06 |
| L05 | claude | Reduction semantics and baseline contract | L04 |
| L06 | claude | Adversarial evaluator checks | C05, L05 |
| L07 | claude | Baseline usefulness audit | C07, L06 |

Both agents vote after their weekly tasks. Next-week tasks require both PASS.

## Week 3

| Task | Owner | Work | Dependencies |
|---|---|---|---|
| C08 | codex | Fair comparison harness | C07 |
| C09 | codex | Integrate the coupled reducer | C08, L09 |
| C10 | codex | Week 3 fairness audit | C09, L10 |
| L08 | claude | AST representation and correspondence | L07 |
| L09 | claude | Coupled search engine | L08, C08 |
| L10 | claude | Development comparison and ablation | C09, L09 |

Both agents vote after their weekly tasks. Next-week tasks require both PASS.

## Week 4

| Task | Owner | Work | Dependencies |
|---|---|---|---|
| C11 | codex | Frozen ten-pair comparison | C10, L11 |
| C12 | codex | Clean replay and release candidate | C11, L12 |
| C13 | codex | Final decision packet | C12, L13 |
| L11 | claude | Freeze ten-pair suite | L10 |
| L12 | claude | Complete experiment analysis | C11 |
| L13 | claude | Maintainer relevance and recommendation | L12, C12 |

Both agents vote after their weekly tasks. Next-week tasks require both PASS.
