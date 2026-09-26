# L09 — Coupled search engine

Owner: Claude · Task L09 · 2026-09-09 · Classification: OBSERVED (real EDA) + DESIGN.

## What was built (src/ppa_delta/coupled/)

- `strategy.py` — `coupled_proposals(state, *, use_matching=True)` + `apply_coupled(state, proposal)`.
  Coordinated, deterministic proposals: `inline-all` (canonicalize both sides), `merge-inputs`
  (substitute input j→i on **both** sides and drop the freed port from both + both manifests),
  `input-const` (input→sized zero on both sides, drop the port). `use_matching=False` is the
  preregistered `coupled-no-matching` ablation: per-side edits only (independent behavior).
- `reducer.py` — `coupled_reduce(...)`: deterministic greedy first-improvement search (mirrors the
  independent baseline's loop) reusing `ppa_delta.baselines.core.materialize_candidate` and
  `ppa_delta.oracle.snapshot_candidate`, so candidate identity + canonical size are the
  evaluator's, never a private definition. Retains only strictly-smaller INTERESTING candidates;
  fresh uncached final validation; handles no-gain / budget / interruption.

Tests: `tests/claude/test_coupled_strategy.py` (7) — every proposal keeps an identical interface
on both sides, leaves no dangling reference, and shrinks; the ablation is per-side only. Full
Claude suite **42/42 pass**; `check_pack` PASS. No Codex-owned file touched.

## Real reduction (L09 acceptance) — OBSERVED

Greedy coupled search on `f1-mux-share-add` via the real oracle
(`runs/claude/l09-coupled-f1-20260909T215830Z/`), bounded proof budget (40 candidates):

- **47 → 35 pair-AST** (before 18, after 17), status REDUCED.
- Accepted edits: `inline-all` (→39), `const0-d` (→37), `merge-a-into-c` (→35).
- **Fresh uncached final validation: INTERESTING, formal PASS, area 47.614 → 57.988
  (delta_rel 0.218), cache_hit False.** A genuine equivalent, nondegenerate, area-regressing
  witness — reduced through Codex's oracle, not a private evaluator.

L09 acceptance met: ≥1 real reduction succeeds, survives uncached verification, integrates via the
shared oracle/snapshot seam.

## Honest comparison vs the baseline (this is the load-bearing finding)

| method | f1 final pair-AST |
|---|---|
| independent baseline | 39 |
| **coupled** | **35** |

Coupled beats independent by **(39−35)/39 = 10.3%** — a real, fresh-validated win, but **short of
the ≥20% Week-3 bar** (f1 ≤ 31 from `week-2-review.md`). I am not calling this a Week-3 PASS; the
full multi-pair comparison + ablation (L10) decides that, and on this first case coupled clears the
"beats independent" signal but not the 20% threshold.

**Why the win is fair (not an extra-primitive trick):** the decisive edits (`merge-inputs`,
`input-const`) are *inherently coordinated* — merging or zeroing an input on only one side would
break the pair's mutual equivalence, so the independent baseline physically cannot perform them.
The advantage is coordination itself, which is exactly the contribution under test. The
`coupled-no-matching` ablation (per-side only, ≈ independent) will confirm in L10 whether the
coordination is what produces the gain.

**Honest caveat on the witness shape:** the search reaches degenerate-but-valid structures (e.g.
`sel ? c : c`). The oracle accepts them (equivalent, nonconstant output, ≥5% area gap), so they are
valid under the frozen predicate, but a richer coordinated primitive that collapses vacuous muxes
and drops newly-unused inputs is the obvious lever to push below the 20% bar — a candidate for the
Week-3 bounded revision, to be decided in L10, not prejudged here.

## C09 correction — confounded ablation fixed, and what the clean ablation shows

Codex's C09 review correctly found my original ablation confounded: `use_matching=True` never
called `correspond()`, and `use_matching=False` dropped the merge/const primitive classes
entirely — so it removed coordination AND primitives, not just matching. **Fixed** (bounded, in
Claude-owned `strategy.py`/`edits.py`/tests; original L09 run preserved):

- Both modes now share the coordination-only primitives (inline-all, merge-inputs, input-const)
  with identical ordering and budget.
- `use_matching=True` additionally consumes L08 `correspond()` to emit one correspondence-dependent
  class: coordinated common-subexpression extraction of subtrees that structurally match across the
  two sides. `coupled-no-matching` disables ONLY that class. A test spies on `correspond` and
  confirms it is consulted for `True` and not for `False`.

Clean re-run (`runs/claude/l09fix-ablation-20260910T012958Z/clean-ablation.json`), both fresh
uncached INTERESTING:

| pair | coupled | coupled-no-matching |
|---|---|---|
| f1 | 35 | 35 |
| a2 | 76 → 62 | 76 → 62 |

**Two findings, both honest and load-bearing:**
1. The old "coupled 35 vs no-matching 39" difference was **100% the confound** — with the
   coordination primitives restored, no-matching also reaches 35. The confound is removed.
2. **Structural matching (L08 correspondence) provides no measurable reduction benefit on this
   corpus** — coupled == no-matching on both pairs, even on a2 where the CSE primitive fires. The
   coupled advantage over the baselines is **coordination** (both-side input merge/const that the
   independent baseline structurally cannot do), NOT structural correspondence.

**Consequence for the contribution (feeds L10 / Week-3 memo / the novelty claim):** the surviving,
evidenced distinction is *coordinated reduction under a relational predicate*; the "structural
correspondence" element of the L01 claim is **not supported by evidence** on this corpus and should
be dropped unless a later corpus with genuinely shared cross-side structure shows a benefit. I am
not claiming matching helps without evidence. This does not by itself decide the Week-3 gate (which
compares coupled vs the better simple baseline, not vs no-matching) — that is L10.

## C09 integration contract (for wiring the coupled + no-matching runners)

Wire a `method in {"coupled", "coupled-no-matching"}` branch into
`ppa_delta.baselines.runner.reduce_pair` that runs the **same greedy loop** as the independent
baseline but sourcing proposals from:

```python
from ppa_delta.coupled.strategy import coupled_proposals, apply_coupled
# coupled:            coupled_proposals(state, use_matching=True)
# coupled-no-matching: coupled_proposals(state, use_matching=False)
# apply: apply_coupled(state, proposal) -> PairState   (same PairState type as core.py)
```

`apply_coupled` returns a `ppa_delta.baselines.core.PairState`; the loop's `context.try_state`
materializes/evaluates it unchanged, so budget accounting, trace, immutable dirs, and fresh final
validation are identical to the baselines (fair by construction — the C10 audit point). The
standalone `coupled_reduce` driver is available if you prefer to call it directly for
`method="coupled"`; either seam reuses `snapshot_candidate` and the shared SizeCounter.

Test commands: `.venv/Scripts/python.exe -m unittest tests.claude.test_coupled_strategy` (logic);
the real reduction run is reproducible via `coupled_reduce` (see the run dir above).
