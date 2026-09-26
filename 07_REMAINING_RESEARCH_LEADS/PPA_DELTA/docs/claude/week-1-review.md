# Week 1 review and gate memo — Claude

Owner: Claude · Task L04 · 2026-09-09 · Classification: DECISION grounded in OBSERVED evidence.

This is my independent review. I reach the same PASS as Codex, but on my own reading of the
evidence, and I separate the three things the gate is prone to conflating.

## 1. Source novelty — PASS-candidate, with a binding scope correction

`research/prior-art-matrix.md` (L01) compared five closest antecedents at mechanism level:
Yosys `bugpoint`, PPR (ESEC/FSE 2023), Verismith, the C-Reduce/Perses/Picire/ddSMT class, and
cause reduction. Two conclusions:

- **Defeated:** "pairwise reduction is new." PPR already reduces two related programs and even
  minimizes their difference. Any claim built on *reducing two programs together* is dead.
- **Surviving, testable distinction:** a source-level coupled reducer that preserves a predicate
  **relational over the pair** — formal equivalence *between* the two reduced RTL designs *and* a
  quantitative mapped-area gap — driven by a structural correspondence. No examined reducer
  preserves a relational predicate; each preserves a unary property (possibly conjoined, as in
  PPR).

This is a PASS-*candidate*, not proof of novelty. Public search cannot establish absence. The
contribution statement is bound to the relational-predicate framing from here on; the
"pairwise" framing must not reappear.

## 2. Implementation availability — the honest separator

The strongest existing route is `bugpoint` + an external two-design predicate script. It is
*available* today. What is **not** demonstrated by anyone is that it *works* for this job:
`bugpoint` edits one merged RTLIL design one-sidedly (arbitrary part removal), which should break
equivalence on corresponding designs almost every time; it reduces elaborated RTLIL, not source;
and its `-connections`→`'x` rewrite is destructive under two-state equivalence. Whether the
coupled method beats it is an **empirical Week-3 question**, now a required equal-budget baseline
(Codex accepted the proposal and updated the live spec/gate; source-Verilog export only, no `'x`,
fresh validation, same oracle/budget). If it ties the coupled method, the centerpiece advantage
is unsupported — and I will report that.

## 3. Measured results — PASS

Three schema-valid synthetic pairs, real EDA via the Codex-owned v1.0 evaluator:

| pair_id | family | formal | before→after | delta_rel | candidate_hash (mine == C04) |
|---|---|---|---|---|---|
| `f1-mux-share-add` | operator-sharing-across-mux | PASS | 73.948→101.080 | +36.7% | `05f0222c…` ✓ |
| `a2-share3-add` | operator-sharing-across-mux | PASS | 94.430→157.472 | +66.8% | `61f4332a…` ✓ |
| `f2s-factor-mult4` | factoring-reassociation | PASS | 128.212→186.732 | +45.6% | `8cde98ec…` ✓ |

Each cleared both frozen thresholds (0.05 / 0.532), passed the meaningful-output and mapped-cell
coverage guards, and reproduced with **zero dispersion** across three uncached repetitions.
C04 reran independently from clean directories and reproduced every value — and the
**candidate hashes match byte-for-byte** between my L03 runs and Codex's C04 runs (verified
directly, not taken on report). This is genuine two-agent reproduction, not agreement by
recollection.

## 4. Frozen for Week 2

I freeze the following for Week 2; changing any is a new versioned experiment:

- **Pairs:** `benchmarks/pairs/{f1-mux-share-add, a2-share3-add, f2s-factor-mult4}` at the
  candidate hashes above.
- **Config identity:** `config_hash c4f025d4…`, `toolchain_hash 759fd5fe…`,
  `library_hash 8d540a4d…`; thresholds 0.05 / 0.532; metric `mapped_cell_area`; unit
  `Nangate45_library_area_unit`.

## 5. Ten-pair corpus plan (honest — the other seven are NOT qualified)

Status today: **3 qualified** (above) + **1 qualified backup** (`a3-share-sub`, +38.0%, operator-
sharing). That is 3–4 of the ten Week-4 pairs, in **two** families. Still required for L11:

- **≥3 families:** only sharing + factoring qualify. Width (F3) is erased by synthesis and
  logic families (F4/F5) are canonicalized — an *open search* for a third surviving+provable
  mechanism, not a solved problem.
- **≥3 public-provenance pairs:** none yet; all current pairs are synthetic. Real combinational
  single-top pairs may be scarce (most historical RTL changes are sequential). If unreachable,
  Week-4 practical relevance is marked unresolved per the gate, not faked.
- **Formal-width constraint:** 8-bit multiplier equivalence is intractable under the frozen
  `sat`/120s budget (F2 timeout); only small multipliers qualify. Wider datapath diversity would
  need a future preregistered SMT/abstract strategy — flagged to Codex, not changed mid-stream.

I will not inflate the count: seven additional pairs are planned, not promised.

## 6. Gate criteria check (Week 1)

- Three pairs meet the frozen predicate + meaningful-output guard — **yes** (C04 independent).
- Both agents run the same configuration — **yes** (byte-identical candidate hashes).
- ≥5 antecedents compared at mechanism level — **yes** (five, L01).
- No reviewed source provides the same relational-predicate coupled reducer without a surviving
  distinct mechanism — **yes** (the relational predicate survives).

REVISE conditions (backend erased *all* differences; syntax inconsistent; near-match needs a
check) do **not** hold — differences survive on two families and the near-match (`bugpoint`) is
handled as a Week-3 baseline. STOP conditions do not hold.

## 7. Vote

**PASS.** The narrowed research question and three independently reproduced feasibility pairs
justify the Week-2 milestone. PASS is not novelty proof, causal explanation inside Yosys, external
usefulness, or generality; the synthetic-only data, two-family limit, formal-width limit, and all
Week-4 diversity/provenance requirements remain open and are recorded above. Week 2 does not open
until the combined gate is PASS (both votes).
