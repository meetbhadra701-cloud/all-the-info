---
agent: claude
type: experiment
created: 2026-09-09T09:43:49+00:00
---

# L02 candidate inventory built and simulation-checked

Classification: OBSERVED (simulation) + HYPOTHESIS (synthesis outcomes).

## What was built

L02 candidate inventory under `benchmarks/candidates/` — 9 candidate directories, each with
`before.v`, `after.v`, and a draft `candidate.json`, plus `ledger.md`, `ledger.draft.json`, and
the reproducible generator `generate_candidates.py`.

- **5 candidate families** (F1 operator-sharing, F2 factoring, F3 sign-extension, F4 mux-shape,
  F5 duplicated cone).
- **4 structural controls** (inequivalent off-by-one, identical, unsupported latch, degenerate
  constant). The 5th control C-METRIC is a library condition, documented for realization in L06
  rather than faked as an RTL file.

## Evidence

Python reference-simulation (stdlib, deterministic, NOT a formal proof) ran on every
intended-equivalent pair. Raw log:
`runs/claude/c1c84f17-306c-4da6-ae32-2a6fb3eb7361/l02-sim-check.txt`.

- F1, F2, F4, F5: 200k random vectors, **0 mismatches**.
- F3: exhaustive 65536, **0 mismatches**.
- ctrl-ineq: exhaustive 65536, **65536 mismatches** (correctly inequivalent).
- ctrl-ident: 0 mismatches. Latch/degenerate controls: structural, no simulation.

All observed behaviours match the intended semantics.

## The load-bearing design decision

The corpus deliberately splits **datapath** structure (F1 adders, F2 multipliers) — expected to
retain an area gap because ABC does not refactor datapath — from **random logic** (F4, F5) —
expected to be canonicalized away. F3 (width/sign-extension) is the boundary case, marked
low-confidence. This split is the hypothesis L03 will test with real synthesis; F4/F5 are kept
as honest expected-negatives, not padding. No candidate is called a regression here.

## Limits and next step

Simulation is not proof and there is no synthesis area yet — both wait on Codex's evaluator
(C03) and `coordination/runtime.json`. Public-provenance pairs (Week 4 needs ≥3) are scouted
but not harvested; honest risk that combinational single-top real pairs are scarce is recorded
in `ledger.md`. L02 → DONE. L03 is blocked on C03; I will yield after this with one open
handoff already sent to Codex.
