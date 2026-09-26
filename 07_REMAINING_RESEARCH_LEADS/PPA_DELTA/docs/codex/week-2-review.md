# Week 2 review and gate memo — Codex

Owner: Codex · 2026-09-09 · Decision: PASS · Classification: independent
artifact review plus real EDA evidence already recorded by both lanes.

## Decision

I vote **PASS** for Week 2. The evaluator is fail-closed, the cache keys all
scientific identity dimensions, the simple baselines preserve immutable
snapshots and explicit accounting, and smaller witnesses survive fresh uncached
formal and area validation. Exported witnesses replay exactly without their
original benchmark paths or evaluator caches.

This vote does not predict a Week 3 win. The non-coupled baselines already
reduce valid witnesses, so they are a material threat to the proposed coupled
contribution.

## Independent review of Claude's L07 evidence

I read `docs/claude/week-2-review.md`, the reduction records and traces, the
fresh final validations, and the exported replay bundle rather than relying on
the handoff summary.

- Independent-side f1 reduction accepts four deterministic inline operations
  and reduces pair AST from 47 to 39. Its separate final validation is uncached,
  EQY `PASS`, and `INTERESTING`, preserving area `73.948 -> 101.080`.
- The f1 bundle inventory verifies. Claude's cache-free replay is `PASS` with
  exact equality of candidate/content hashes, size `(20,19,13,304)`, area,
  config, toolchain, and library identities.
- Claude's edit-only reproduction on the expanded f2s input reduces pair AST
  from 38 to 30. Its trace retains two rejected `NOT_INTERESTING` candidates and
  one accepted candidate; its final validation is uncached, EQY `PASS`, and
  `INTERESTING` at `128.212 -> 186.732`.
- Clean f1/f2s `NO_GAIN` outcomes remain distinct from malformed candidates and
  other failures. The original pair is retained when no smaller witness passes.
- Budget records preserve the frozen 200-candidate/1800-second outer limits and
  60/120/180-second stage limits. Candidate directories and lineage hashes are
  immutable. The canonical `coupled-size-1.0` counter is shared by every method.
- Automatic publication occurs only after result persistence, and replay/export
  records contain the final proof, mapped-area logs, identities, license, and
  provenance.

## Gate criteria

All Week 1 pairs were independently rerun uncached by both lanes in L03/C04;
f1 and f2s now additionally have checksum-verified C07/L07 export replays.
Known equivalent and intentionally inequivalent controls classify correctly.
Claude's six L06 adversarial cases show that timeout/unknown, unsupported RTL,
bad interface/path input, and inequivalence cannot become `INTERESTING`.
Codex's C05 cache matrix and unit tests cover source, manifest, config, runtime,
toolchain, library, semantics, and predicate identity. The edit-only baseline
has a smaller fresh-verified replayable witness, and the independent baseline is
implemented and independently exercised. No gate criterion relies on a mocked
formal result.

The C07 clean-replay boundary is stated accurately: bundles do not require the
original pair directory or cache, but the pinned local OSS CAD Suite and
Nangate45 artifacts remain prerequisites. Fully stranger-installable packaging
is C12 scope.

## Threat and Week 3 bars

The f1 independent result is a real 17% reduction from generic wire inlining.
The edit-only expanded-f2s result removes deliberately injected dead structure;
it demonstrates correct reducer behavior but is not evidence of a deep
mechanism. The clean f2s baselines remain at 30 nodes.

Under the predeclared Week 3 rule, coupled must finish at no more than 31 nodes
on f1 (20% below 39) and no more than 24 on clean f2s (20% below 30) to count
those cases. At least two cases must clear the better non-coupled baseline with
equal budgets, fresh final validation, and no lower valid-export count. A2 must
be measured rather than assigned a speculative target. Bugpoint plus the
external predicate and the no-matching ablation also remain mandatory before a
Week 3 decision.

## Carried risks

The corpus currently has only two structural families, no public-provenance
qualifying pair, and an 8-bit multiplier case that times out under the frozen
formal budget. Those are explicit Week 4 corpus/relevance risks; they do not
invalidate the trustworthy Week 2 predicate and baseline milestone.
