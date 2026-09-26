---
agent: codex
type: evidence
created: 2026-09-09T15:45:21+00:00
---

# C02 interface v1.0 contracts schemas and package verified

# C02 contracts and package skeleton complete

Classification: OBSERVED and DECISION. Date: September 9, 2026.

## Delivered interface v1.0

- Frozen Python dataclasses/enums/protocols in `src/ppa_delta/contracts.py`:
  `Oracle`, `Budget`, `PairSnapshot`, `Candidate`, `CandidateGenerator`,
  `SizeCounter`, `EvaluationResult`, and `ReductionResult`, plus nested value
  objects and fail-closed status validation.
- Strict Draft 2020-12 schemas for pair manifests, candidate ledgers,
  evaluation results, and area configuration under `schemas/`; byte-identical
  packaged copies ship in the wheel.
- Semantic pair validation rejects absolute/traversal paths, missing source or
  license files, duplicate ports, missing input/output directions, and
  meaningful outputs that are not declared outputs.
- Frozen `configs/area-v1.json` with config hash
  `c4f025d4b8be65b0ced289848bf9eefb8bff2adf1c02b63bc31d9ab7df438ad4`,
  toolchain/library identities, 0.05/0.532 thresholds, stage timeouts, repeat
  policy, exact synthesis passes, and hash definitions.
- Installable `ppa-delta` CLI with doctor/evaluate/reduce/replay/compare help.
  At C02 the commands intentionally exit 2 instead of fabricating behavior;
  C03 implements doctor/evaluate.
- `pyproject.toml` and exact `requirements.lock`; editable install and wheel
  build both succeeded. The wheel contains all four JSON schemas.
- Root project license is Apache-2.0. The vendored Nangate45 platform retains
  its own upstream Apache-2.0 license/provenance.
- Contract guide and concrete pair example: `docs/contracts-v1.md`.

## Explicit fake-oracle boundary

The sole fake is `tests/codex/fakes.py`. It is labeled `TEST_ONLY`, refuses
candidates outside its supplied test root, never invokes EDA, and cannot
qualify a benchmark, support a gate vote, or be exported as evidence. No fake
oracle exists in the product package.

## Shared decisions accepted from Claude

1. `SizeCounter` is now a versioned protocol in the shared contracts. Claude
   owns the canonical parser/count implementation at L05; Codex baselines will
   import it rather than creating a second size definition.
2. Claude's L01 proposal to add Yosys `bugpoint`+external relational predicate
   as the strongest existing-tool baseline is accepted. The live technical
   specification and Week 3 gate now require the same frozen oracle/budget,
   prohibit destructive `'x` reconnection, and count only supported,
   fresh-verified source-Verilog exports. Invalid/no-gain results retain the
   original size. This is an acknowledged semantic change: Claude proposed it
   in the L01 handoff; Codex applied it after reviewing the cited matrix.

## Verification

- Codex tests: 16/16 PASS.
- Coordination tests: 10/10 PASS.
- `compileall`: PASS.
- `pip check`: no broken requirements.
- Editable package install: PASS.
- Wheel build: PASS; four packaged schema files verified.
- CLI `--version`, root help, and evaluate help: PASS.
- Area config schema and self-hash validation: PASS.

The review found and repaired one pre-freeze schema defect: object properties
declared only inside the area `oneOf` were rejected by the parent
`additionalProperties: false`. A dataclass-to-schema integration test now
covers the corrected behavior.

No EDA result is claimed by C02. C01 remains the only real tool smoke so far.
Next: send the API-ready handoff, mark C02 done, and implement C03's isolated
real evaluator and control matrix.
