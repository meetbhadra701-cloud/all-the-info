---
agent: claude
type: decision
created: 2026-09-09T15:21:08+00:00
---

# Frozen discovery thresholds from Nangate45 (rel 0.05, abs 0.532 = 1x INV_X1)

Classification: OBSERVED (library values) + DECISION (frozen thresholds).

## Receipt

Read and acknowledged Codex's handoff `Runtime v1 ready for Claude`
(`05-Handoffs/codex/20260909T101324Z-ded90c8c25d3-…`) and `coordination/runtime.json`
(status READY, interface 1.0). No semantic objection to the frozen runtime from my lane.

Route confirmed: WSL2 Ubuntu 26.04, OSS CAD Suite 20260816, Yosys 0.68 / EQY 0.68 / ABC 1.01 /
Z3 4.15.5 / Boolector 3.2.4; Nangate45 Liberty (Apache-2.0), library hash
`8d540a4d…db4e9b1`; toolchain hash `759fd5fe…aecbf462`. The 20.482/20.482 smoke is an
equal-area control, not a regression — correct.

## Decision: frozen discovery thresholds (spec §4)

Derived from the authoritative frozen library, not from any candidate's measured result:

- `relative_threshold = 0.05` (spec default 5%).
- `absolute_threshold = 0.532` `Nangate45_library_area_unit` = exactly **one `INV_X1`**, the
  minimum positive-area combinational cell (population 90) per `runtime.json:library`.
- `metric = mapped_cell_area`; `area_unit = Nangate45_library_area_unit` (no physical unit
  inferred — the Liberty file declares none).

These are frozen **now**, before any reducer comparison, and will be written verbatim into each
`benchmarks/pairs/<id>/pair.json` at L03 promotion. They will not be lowered after seeing a weak
result (spec §4). A candidate qualifies only if `delta_rel >= 0.05` AND `delta_abs >= 0.532`,
with an explicit formal PASS and the nonconstant-output guard satisfied.

## What is NOT done here (boundary)

No area or equivalence measurement was run in my lane — that is Codex's oracle (C03). Candidate
syntax validity (F1–F5 + controls) will be confirmed by the evaluator's UNSUPPORTED /
COMPILE_ERROR paths at L03, not by a private Yosys run.

## Blocking status / next step

L03 is still NOT ready: it depends on **C03** (real smoke evaluator) and the exact
`ppa-delta evaluate` argv, which arrive with Codex's C02→C03. When they land:
1. Migrate the L02 draft manifests onto Codex's `schemas/pair.schema.json`.
2. For each F1–F5 candidate, run the evaluator in a UUID dir under `runs/claude/`, keeping every
   rejection with its measured area.
3. Promote exactly the qualifying pairs into `benchmarks/pairs/` with these frozen thresholds,
   three uncached repetitions each, then hand pair IDs to Codex for C04.

No ready Claude task until then; yielding without polling.
