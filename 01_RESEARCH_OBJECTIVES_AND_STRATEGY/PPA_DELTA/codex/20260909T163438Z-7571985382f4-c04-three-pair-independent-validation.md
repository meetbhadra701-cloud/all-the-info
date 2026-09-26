---
agent: codex
type: evidence
created: 2026-09-09T16:34:38+00:00
---

# C04 three-pair independent validation

# C04 independent validation complete

Classification: OBSERVED. Date: September 9, 2026.

Codex independently validated Claude's three promoted Week-1 pairs using the
frozen v1.0 evaluator, WSL2 OSS CAD Suite runtime, EQY/Yosys/ABC flow, and
Nangate45 Liberty. The authoritative matrix is
`runs/codex/c04-validation/6b773135a67a43019d8ec0ef3d330dec/matrix.json`.

## Results

| Pair | Family | Formal | Area before -> after | Relative delta | Codex repeats |
|---|---|---|---|---:|---|
| `f1-mux-share-add` | operator-sharing-across-mux | PASS | 73.948 -> 101.080 | 36.69% | INTERESTING x3 |
| `a2-share3-add` | operator-sharing-across-mux | PASS | 94.430 -> 157.472 | 66.76% | INTERESTING x3 |
| `f2s-factor-mult4` | factoring-reassociation | PASS | 128.212 -> 186.732 | 45.64% | INTERESTING x3 |

All nine runs were fresh and uncached. Each pair had zero area dispersion,
and Codex's candidate hashes and measured values exactly matched all three of
Claude's L03 repetitions.

## Checks performed

- All pair manifests validate against schema v1.0 and match frozen semantics,
  metric, area unit, relative threshold 0.05, and absolute threshold 0.532.
- Provenance is present and internally consistent: all three pairs are
  explicitly synthetic, identify their authors/families, and carry an
  Apache-2.0 notice pointing to the root full license.
- Live pair source, manifest, license, and provenance hashes were captured
  before evaluation and were unchanged afterward. Each evaluator repetition
  independently snapshotted source bytes and recorded matching content hashes.
- Every run has one nonempty EQY partition with strategy status PASS plus the
  aggregate PASS artifact. Formal success was not inferred from exit status.
- Every mapped design has positive cells. Every `num_cells_by_type` entry has
  a positive area in the exact frozen Liberty, the cell counts sum correctly,
  and recomputed cell-area sums equal the reported areas.
- Every declared meaningful output has a mapped-cell-backed dependency on an
  input. No constant-only or wire-only degeneration passed.
- Interface, combinational two-state syntax, hierarchy, and Yosys check stages
  passed for both sides of every repetition.
- Config, toolchain, library, and threshold identities match the frozen files.

The independent validator is
`tests/codex/c04_validate_pairs.py`. It also audited Claude's nine original
result records before launching Codex runs. No mocked or fake formal/EDA result
was used.

## Boundaries retained

- These are synthetic feasibility witnesses across two structural families,
  not evidence of external relevance or universal synthesis behavior.
- The wider 8-bit multiplier timeout remains a rejection under the frozen
  budget; no timeout, threshold, formal strategy, or synthesis pass was changed.
- Week 4 still requires ten qualifying pairs from at least three families and
  stronger public-design relevance. That future requirement is not silently
  credited by this Week-1 result.

C04 acceptance is satisfied: three qualified pairs have real complete logs,
three fresh repetitions each, and the replayable frozen configuration.
