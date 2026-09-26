# L13 — Maintainer relevance & final month-one recommendation

Owner: Claude · Task L13 · 2026-09-10 · Classification: OBSERVED (release replay + frozen L12
rows) + DECISION (Week-4 vote). Sources: C12 clean-room audit
(`runs/codex/c12-release-audit-20260910T193300Z/audit.json`, status PASS), the release candidate
(`runs/codex/c12-release-candidate-20260910T192551Z-final/`), and the L12 analysis
(`analysis/month-one-report.md`, regenerated from the frozen C11 rows). Nothing here is from
recollection.

---

## 1. Reproduce-as-a-stranger (from the README only)

I read only `README.md` in the release root and followed it as an outside maintainer would.
The path is complete and self-consistent:

- **Prerequisites** name exact tool identities (OSS CAD Suite `20260816`, Yosys/EQY 0.68, ABC,
  Z3, Boolector; Nangate45 Apache-2.0), and state honestly that the CAD suite is too large to
  bundle and must be fetched from the official YosysHQ release, with `ppa-delta doctor` failing
  closed on any byte/hash mismatch.
- **Install** is two `pip` steps from a clean venv (or one wheel install); **replay** is a single
  documented command per bundle plus a ten-bundle driver.
- Codex's C12 executed exactly this route from a **source-free clean room** and got **10/10 PASS,
  all uncached, formal PASS, exact expected==observed** hashes/area/size (audit
  `all_replays_uncached_formal_interesting_exact: true`, `installed_from_clean_venv: true`,
  `source_free_clean_root: true`, wall 57.3 s). I did not re-run the WSL EDA myself (Codex owns the
  oracle/runtime lane and has just done a clean-room pass); I verified the bundle contents and the
  audit that backs the claim.

**Stranger-reproducibility: PASS** — the README alone is sufficient to reinstall and replay, and an
independent clean-room execution confirms it.

## 2. Maintainer checklist (public issue-report conventions)

Scored against what a synthesis-tool maintainer expects in a high-quality bug/witness report. Each
item is materially present in every one of the ten bundles (spot-checked `f1-mux-share-add` in full;
inventory + audit confirm the rest).

| # | Checklist item (Week-4 gate) | Status | Evidence |
|---|---|---|---|
| 1 | Small self-contained example | ✅ | `pair/before.v` + `pair/after.v` — e.g. f1 is two 3-line modules |
| 2 | Single replay command | ✅ | `bundle.json.replay_command`; README "One-command replay" |
| 3 | Tool / version / library provenance | ✅ | `runtime.json`, `config.json`, `THIRD-PARTY-NOTICES.md`, doctor hash-pinning |
| 4 | Expected vs observed outputs | ✅ | `evidence/final-validation/result.json` (formal PASS, area vectors, exact hashes) |
| 5 | Reduction trace | ✅ | `records/trace.jsonl`, `records/reduction.json`, `records/summary.txt`, `budget.json` |
| 6 | License clarity | ✅ | root `LICENSE` (Apache-2.0) + per-pair `pair/LICENSE`; notices file |
| 7 | Specific reason the reduced pair aids diagnosis | ✅ (see §3) | minimal witness isolates the sharing/area divergence |
| 8 | Whether any actual external review occurred | ❌ **NONE** | no maintainer contacted; no issue filed; internal assessment only |

**Checklist score: 7/8 present; item 8 (external review) is explicitly absent.** Per the gate,
"internal assessment is not external validation" — I record this as a real gap, not a pass.

## 3. Would this actually help a synthesis maintainer? (honest answer)

**Yes in form, unproven in substance.** The f1 witness is exactly the shape a maintainer wants: the
smallest pair on which a mapped-area difference appears while the two designs are formally
equivalent —

```verilog
// before:  out = c + (sel ? b : 8'd0);     // adder feeds a mux-to-zero
// after :  out = sel ? c + b : c;          // one adder shared under the select
```

Both compute the same function; `after` maps smaller because the adder is shared across the select
rather than gated to zero. A maintainer debugging why a resource-sharing / operator-sharing pass
does or does not fire has, in this bundle, a 3-line reproducer with a formal proof and an area
report — objectively better than a 500-line RTL attachment.

**But** — and this is the load-bearing caveat — every one of the ten pairs is **synthetic and
hand-authored to exhibit the phenomenon**. I built them to survive Yosys+ABC and show a gap; I did
not find them in a real design or a real bug tracker. So the artifact *format* is maintainer-grade,
while the *demonstrated need* is not: no maintainer has said "I would use this," and no witness came
from a real regression. Practical relevance is therefore **UNRESOLVED**, consistent with L11's
provenance finding.

## 4. Upstream issue — DRAFTED LOCALLY, NOT SENT

Per the gate ("draft one technically specific upstream issue locally; do not send it. No unsolicited
outreach"). This is a **draft for the user's judgment only**; I have sent nothing.

> **Title:** Minimal equivalent-pair witness where mapped area depends on operator-sharing across a
> mutually-exclusive select
>
> **Body:** Two formally equivalent combinational modules differ in Nangate45 mapped cell area after
> `synth; abc -liberty`. `before` = `out = c + (sel ? b : 8'd0)`; `after` = `out = sel ? c + b : c`.
> EQY reports equivalence; mapped area differs by ≥ one INV_X1 (0.532 units), reproducibly. The pair,
> the exact tool/library hashes, and a one-command cache-free replay are attached. This isolates a
> case where sharing an adder across the select changes area while function is preserved — a minimal
> reproducer for anyone characterizing the sharing/area interaction. *(Not filed. Synthetic example;
> offered as a diagnostic-format demonstration, not a defect claim against any tool.)*

I recommend the user **not** file this as-is: it demonstrates a known, intended synthesis behavior on
a synthetic input, so filing it would be noise to a real tracker. It shows the *reporting format*
works; it is not itself a real bug.

## 5. Final novelty statement

The defensible contribution (from L01, unchanged): existing reducers minimize **one** program
against a **self-contained** predicate (bugpoint, C-Reduce/Perses, Verismith's reduction, PPR).
PPA-Delta minimizes **two** programs **jointly** under a **relational** predicate that requires both
(a) formal equivalence between the reduced pair and (b) a preserved quantitative mapped-area gap,
using a structural correspondence to propose **coordinated** edits (input-elimination, and the
scaffold-lift that abstracts a shared control cone on both sides at once) that per-side reducers
cannot express. L01 found this survives the focused prior-art check; PPR (FSE 2023) defeats a
naive "pairwise reduction" framing, which is why the contribution is scoped to the *relational
equivalence-plus-area-gap* predicate, not "reducing pairs" in general. **The novelty is defensible
but narrow, and empirically demonstrated only on synthetic inputs.**

## 6. Limits (complete, not hedged)

1. **≥70% original-AST reduction is 0/10 literally** (max 51.5%, a4). The pre-registered technical
   bar is not met. The "final ≤70% of original" reading is 7/10, reported but not substituted.
2. **Corpus is 100% synthetic** — no public-design/historical provenance; practical relevance
   unresolved.
3. **No external review** occurred (checklist item 8).
4. **Advantage is modest on several pairs** (f2s +6.7%, a3 +10.3%, f3s +15.8%, m1 +17.9% — below 20%
   individually; 23.08% is a median, not a floor). Small factoring/multiplier pairs sit near their
   gap-preservation floor.
5. **Matching helps only where scaffold exists** (4/10; null on the other six). The revived
   correspondence effect is real but concentrated in `sel==k` mux structures.
6. **n=10 → no statistical-significance claim.** Feasibility screen only.
7. **Scope**: combinational, two-state, single-top Verilog subset; metric is mapped standard-cell
   area, not timing/power/place/route/silicon.

## 7. Paper / write-up outline (if the work continues)

1. **Problem** — minimal *relational* witnesses for synthesis area regressions between equivalent
   designs; why single-program reducers do not address it.
2. **Related work & the surviving gap** — bugpoint, C-Reduce/Perses/Picire, Verismith, PPR;
   the relational-predicate distinction.
3. **Method** — coupled objective (lexicographic pair-AST / changed-nodes / bytes), coordinated edit
   primitives, structural correspondence, scaffold-lift; the oracle (compile→EQY→Nangate45 area).
4. **Evaluation** — 10 pairs / 3 families / 7 dev + 3 held-out; six-method matrix; ablation
   (matching vs no-matching); costs.
5. **Results** — 10/10 vs best baseline, 23.08% median, held-out 3/3, matching-helps 4/10.
6. **Threats to validity** — §6 in full, foregrounded (synthetic corpus, 0/10 on the 70% bar,
   no external review, n=10).
7. **Conclusion** — feasibility established; real-world provenance and usefulness are the open
   questions a next study must answer.

---

## 8. Week-4 vote: **REVISE**

**Technical PASS: NOT MET.** The gate requires *all* of: 10/10 witnesses reproduce ✅; ≥70% original
AST reduction on ≥7 cases ❌ **(0/10)**; ≥20% median advantage ✅ (23.08%); ≥2 held-out advantage ✅
(3/3); costs reported ✅. One required bar fails literally, so the technical gate does not pass. I do
not get to redefine the bar in my favor.

**Practical PASS: NOT MET.** The maintainer-ready report exists and scores 7/8, but item 8 (external
review) is absent and the corpus is entirely synthetic, so a *credible demonstrated user need* is
unresolved. Internal assessment ≠ external validation.

**This maps to the gate's REVISE outcome**, verbatim: *"technical results are promising but
originality, real-world provenance or user usefulness remains unresolved. Recommend one short next
experiment with a fixed budget; do not claim the month passed."*

- **Not CONTINUE** — that needs both votes PASS *and* a credible user need; the 70% bar fails and
  provenance is unresolved.
- **Not STOP/PIVOT** — novelty is **not** defeated (L01), the simple reducer is **not** sufficient
  (coupled wins 10/10), and results are **reproducible** (C12 clean-room 10/10). None of the STOP
  triggers fire.

### Recommended one short next experiment (fixed budget)

**Sourced-provenance mini-study — 5 real combinational pairs, ≤1 week, no method change.** Pull
equivalent-but-area-divergent combinational slices from permissively licensed public cores
(`ibex`/OpenTitan `prim_*`, `picorv32`, `SERV` ALU/decoder/priority-encoder logic), qualify them
through the *frozen* oracle, and run the frozen six-method matrix. Success = coupled beats the better
baseline on ≥3 of 5 **real** pairs, resolving the single biggest open question (provenance/relevance)
without touching the method. This directly attacks the REVISE cause; it does not chase the 70% bar,
which the gap-preservation floor makes structurally unreachable on already-minimal witnesses (that
bar itself is arguably mis-calibrated for a relational reducer — a point for the user to weigh, but I
am **not** using it to upgrade the vote).

**The month-one decision is the user's.** My evidenced recommendation is REVISE with the mini-study
above.
