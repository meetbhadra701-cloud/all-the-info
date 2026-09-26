# Week 2 review and gate memo — Claude (L07 baseline usefulness audit)

Owner: Claude · Task L07 · 2026-09-09 · Classification: OBSERVED (real EDA via the public v1.0
CLI) + DECISION. Raw runs under `runs/claude/l07-*`. All runs `--no-cache`, clean output dirs.

## 1. Baselines are trustworthy — first-hand audit

Ran both simple baselines through `ppa-delta reduce` on qualified pairs from clean dirs:

| pair | method | status | initial → best (pair_ast) | evals | final validation |
|---|---|---|---|---|---|
| f1-mux-share-add | edit-only | NO_GAIN | (47,21,384) → (47,21,384) | 3 | original kept |
| f1-mux-share-add | independent | **REDUCED** | (47,21,384) → **(39,13,304)** | 6 | fresh INTERESTING, 73.948→101.08 |
| f2s-factor-mult4 | edit-only | NO_GAIN | (30,12,228) → same | 2 | original kept |
| f2s-factor-mult4 | independent | NO_GAIN | (30,12,228) → same | 1 | original kept |
| l07-expanded-f2s (dead-wire injected) | edit-only | **REDUCED** | (38,20,259) → **(30,12,228)** | 5 | fresh INTERESTING, 128.212→186.732 |

Audited on the real logs:
- **Termination & budget:** each run terminated; `budget.json` matches the frozen `area-v1`
  (200 candidates / 1800 s / 60-120-180 stage caps). The one-proposal smoke correctly reports
  `BUDGET_EXHAUSTED` (Codex C06), not a false stop.
- **Retained failures / accounting:** `trace.jsonl` records every rejected proposal with reason —
  f1 edit-only shows `LOCAL_NON_SHRINKING` ×3 and `COMPILE_ERROR` ×2, all `accepted:false`. Rejects
  are kept, not discarded.
- **NO_GAIN ≠ failure:** f1/f2s edit-only return `NO_GAIN` because there is *no removable edit
  group* in those already-minimal witnesses — explicitly distinct from an implementation failure.
  Injecting one removable group (the expanded-f2s dead wire) makes edit-only reduce it, confirming
  the mechanism works.
- **Shared size authority:** every trace/size vector is `coupled-size-1.0` (my SizeCounter). No
  competing count.
- **Immutable candidates:** one directory per proposal (`candidates/NNNN-...`), never overwriting
  a parent; `candidate_hash == snapshot.pair_hash` per contract.
- **Fresh final validation:** the reduced witnesses re-validate uncached (`cache_hit:false`,
  formal PASS, area gap preserved) — not a cached echo.
- **Automatic publication:** `publication.json` shows the vault note was created (returncode 0)
  after the result was persisted.
- **Export + replay:** I exported the reduced f1-independent witness to
  `exports/l07-f1-independent-reduced/` and replayed it in a fresh dir with cache off →
  **status PASS, expected==observed** on candidate hash, area (73.948→101.08), formal PASS, size
  (39,13,304), and all identity hashes. The bundle is self-contained.

## 2. Threat to the coupled contribution — stated plainly (this is the point of L07)

**The simple baselines already produce smaller valid witnesses.** Independent-side reduction
shrank f1 from 47→39 pair-AST (~17%) by inlining intermediate wires, preserving the +36.7%
regression; edit-only removes injected dead code. This is a real threat the coupled method must
overcome. The Week-3 gate requires coupled to beat the **better** simple baseline by ≥20% pair-AST
on ≥2 development cases. Concrete bars this audit fixes:

- **f1:** better baseline = independent at **39** → coupled must reach **≤ 31** pair-AST.
- **f2s (clean):** both baselines NO_GAIN at **30** → coupled must reach **≤ 24** pair-AST.
- **a2:** not yet baselined (deferred to the L10 full comparison); do not assume a bar for it.

**Honest nuance both ways:** the independent win on f1 is *generic wire-inlining*, not the
structural-correspondence mechanism the coupled method claims; and edit-only only reduced an
*artificially expanded* pair, getting NO_GAIN on both clean corpus witnesses. So the baselines'
demonstrated usefulness on the real minimal witnesses is shallow. Whether coupled reduction beats
generic inlining by 20% on corresponding structure is genuinely open and is the Week-3 test — not
prejudged here.

## 3. Week-2 gate criteria — all met with first-hand evidence

| criterion | status | evidence |
|---|---|---|
| All Week-1 pairs replay | ✅ | f1 reduced witness replayed exactly (§1); Codex C07 `exports/c07-edit-only-f2s` bundle replays; originals validated L03/C04 |
| Known equivalent example passes | ✅ | all qualified pairs formal PASS; `ctrl-ident` NOT_INTERESTING |
| Intentional inequivalent control rejected | ✅ | L06 `adv-ineq-biggap` → INEQUIVALENT (formal FAIL); `ctrl-ineq` |
| Timeouts / malformed / unsupported cannot be accepted | ✅ | L06 adversarial audit: all 6 fail closed, none INTERESTING |
| Cache identity tests pass | ✅ | Codex C05 cache matrix (cold miss / validated hit / changed-config miss) |
| Edit-only emits ≥1 smaller, fresh-verified, replayable witness | ✅ | reproduced expanded-f2s 38→30 fresh (§1); Codex C07 edit-only bundle replays |
| Independent-side baseline ready before coupled comparison | ✅ | independent reduced f1 47→39, fresh + replayed |

No REVISE trigger (trustworthy equivalence/measurement established; oracle replays). No STOP
trigger (no fabricated/mocked EDA — L06 confirmed fail-closed; results reproduce).

## 4. Vote: PASS

Week-2 acceptance is satisfied on first-hand evidence: the predicate + baselines are trustworthy,
reproducible, and honestly accounted. PASS is **not** a claim that the coupled method wins — the
baselines already reduce, and the ≥20% bars above are the real Week-3 test. Carried-forward open
items: two families only (≥3 needed at L11), no public-provenance pairs yet, 8-bit multiplier
formal intractability. Week 3 does not open until both agents record Week-2 PASS.
