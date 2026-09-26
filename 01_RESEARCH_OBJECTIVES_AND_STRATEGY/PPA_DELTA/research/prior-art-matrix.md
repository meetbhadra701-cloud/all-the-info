# L01 — Prior-art matrix (narrow reducer question)

Owner: Claude · Task L01 · Created 2026-09-09 · Classification: OBSERVED unless marked.

"Not mentioned" is never recorded as "not supported." Every feature attributed below was
checked against the primary artifact named in the source column, except where a row states an
access limitation.

## The question under test

Does an existing hardware testcase reducer jointly shrink **two** RTL descriptions while
retaining (a) formal equivalence between the reduced descriptions and (b) a reproducible
quantitative synthesis-area regression between them?

## The discriminating predicate

PPA-Delta's acceptance predicate over a candidate pair `(A', B')` is **relational** — it does
not factor into independent per-program properties:

```
interesting(A', B') == equivalent(A', B')                       # binary, formal, BETWEEN the pair
                    /\ (area(B') - area(A')) / area(A') >= tau   # quantitative gap, BETWEEN the pair
                    /\ area(B') - area(A') >= tau_abs
                    /\ supported(A') /\ supported(B') /\ nondegenerate(A', B')
```

For every antecedent the decisive question is therefore: is the preserved property **unary**
(evaluated on one program at a time, possibly conjoined) or genuinely **relational over the
pair**? No examined antecedent preserves a relational predicate.

## Matrix (five closest antecedents)

| # | Source (primary artifact inspected) | Owner / date / version | Language | Programs reduced | Preserved predicate | Formal equivalence? | Quantitative PPA/QoR preserved? | Reduction operations | Representation | Public code | Uncertainty |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Yosys `bugpoint`** — `passes/cmds/bugpoint.cc` (`main`) + docs "Minimizing failing (or bugged) designs", 0.62-dev | YosysHQ; read 2026-09-09 | Verilog / RTLIL | **One** loaded design | Child Yosys still *fails*: crash, `-expect-return`, `-grep` (log), `-err-grep` (stderr); arbitrary external failure via `exec` | **No** | **No** | remove modules / ports / cells / processes / assigns / updates / wires; `-connections` reconnects ports to `'x` | **RTLIL** (elaborated), not source AST | Yes (GPL) | Whether one merged design + an `exec` area-delta script is an operational equivalent — addressed below |
| 2 | **PPR: Pairwise Program Reduction** — Zhang, Xu, Tian, Jiang, Sun, ESEC/FSE 2023, DOI 10.1145/3611643.3616275; §4 + §6 read from the PDF | Waterloo / Tsinghua; 2023-12 | C, Rust, JavaScript | **Two** (seed `P`, variant `Q` from `P` by mutation) | `psi_P(P') AND psi_Q(Q')` — a **conjunction of two independent unary properties**, each checked on one program alone (paper: "P is well-defined ... does not trigger a compiler bug", "GCC crashes when compiling Q") | **No** | **No** — boolean bug properties | Perses-lineage syntax-guided AST deletion; secondary objective **minimizes** the P↔Q difference | Source AST | Yes | Diff-minimization internals not fully read; does not affect the unary/relational verdict |
| 3 | **Verismith** — Herklotz & Wickerson, "Finding and Understanding Bugs in FPGA Synthesis Tools", FPGA 2020 | Y. Herklotz; 2020 (GPL) | Verilog (generated) | **One** | Bug still reproduces — a synthesis **miscompilation** (netlist mis-synthesised vs. reference) | Used as the *bug oracle* (design vs. its synthesized netlist), not as a property held between two reduced source programs | **No** — correctness bugs, not QoR | Verilog testcase reduction toward the failing design | Source | Yes | Exact reducer option names not confirmed from the primary paper text (README omits them); **documented access limit**, verdict unaffected |
| 4 | **C-Reduce / Perses / Picire / ddSMT** | Regehr et al. / Sun et al.; long-standing | C, grammar-defined | **One** | Arbitrary user script returns "still interesting" — **unary** | No | No | transformation fixpoint / grammar-guided AST deletion | Source | Yes | A pair can hide inside the predicate script, but the reducer models only one program |
| 5 | **Cause reduction** — Groce, Alipour, Zhang, Chen, Regehr, "Cause reduction: delta debugging, even without bugs" | Utah / NASA JPL | test inputs / programs | **One** | Generalizes the predicate from "fails" to an **arbitrary effect** `reffect` — still unary | No | Not a QoR metric | delta debugging | input / source | Yes | Establishes non-crash predicates as prior art; does not make the predicate relational |

## Negative confirmations (bounded, not absence claims)

- **No hardware testcase reducer preserving a quantitative QoR metric** (area / delay / power)
  was found. Targeted search on RTL QoR-regression reduction returned only *optimization*
  (e-graph datapath rewriting, RTL power optimization) and *detection/reporting* (OpenROAD
  metrics), never *reduction* toward a preserved metric gap. Search terms and dates in
  `l01-search-log.md`.
- The e-graph / learned-rewrite systems in `[[02-Research/Existing-Research-Audit]]` (ROVER,
  SymRTLO, ASPEN, Dr. RTL, RTLScout) are **optimizers**: they search for a *better* single
  design, not a *smaller pair* preserving a regression. They are not reducers and are not
  rescored here beyond this statement.

## Strongest argument that the contribution is already done

Yosys `bugpoint` takes an arbitrary failure script and can call external tools via `exec`. An
engineer could write a script that runs `eqy` + `synth` on both designs and errors unless the
area gap holds, load both modules into one design, and run `bugpoint` to reduce toward a
smaller satisfying pair. Nothing in `bugpoint` forbids this.

Three things it still would not do — each an **empirical** claim PPA-Delta can measure, not an
assertion:
1. Its edits are **uncoordinated and one-sided**: it removes an arbitrary part of the merged
   design. On two structurally corresponding designs an arbitrary one-sided removal almost
   always breaks equivalence, so most proposals are rejected and convergence should be poor.
2. It reduces **RTLIL** (elaborated), which the spec forbids as the source-reduction
   representation; `write_verilog` of reduced RTLIL is not reduced source.
3. `-connections` maps ports to `'x`, semantically destructive and incompatible with the
   two-state equivalence contract.

**Most important L01 consequence:** `bugpoint` + a two-design predicate script is the
**strongest fair baseline available**, and it is absent from the frozen baseline set
(unreduced / edit-only / independent-side / coupled / coupled-without-matching). Adding it
would strengthen the Week 3 comparison and pre-empt the obvious reviewer objection. This is a
shared-specification change → proposed to Codex (handoff), not edited unilaterally.

## Two-sentence surviving difference

> Existing reducers — including the pairwise reducer PPR and the hardware reducer
> `bugpoint` — preserve properties evaluated on one program at a time, so a pair is either
> reduced independently or hidden inside an opaque predicate script, and none checks formal
> equivalence *between* the two reduced programs. PPA-Delta reduces two RTL descriptions under
> a predicate that is irreducibly relational over the pair — formal equivalence between the
> reduced designs together with a preserved quantitative synthesis-area gap — and uses a
> structural correspondence between them to propose coordinated edits that keep that relation
> satisfiable.

## Recommendation: **PASS-candidate, conditional on a scope correction**

The narrow contribution survives this mechanism-level search, but **only** when restated
correctly:

1. **Drop "pairwise reduction" from the novelty claim.** PPR (FSE 2023) already reduces two
   related programs and minimizes their difference. Claiming pairwise reduction as new is
   defeated.
2. **State the contribution as the relational predicate + structural correspondence** (the two
   sentences above). This is what no examined antecedent provides.
3. **Add the `bugpoint`+`exec` baseline to the comparison set** so the Week 3 result rules out
   the strongest existing tool, not merely delta-debugging straw men.

This is a PASS-candidate for the *research task*, not a project PASS. The Week 1 gate also
requires three measured qualifying pairs (L03/C04); a novelty PASS-candidate alone does not
carry the gate. If, in Week 3, `bugpoint`+`exec` matches the coupled method, that is a STOP
signal for the centerpiece claim and I will report it as one.
