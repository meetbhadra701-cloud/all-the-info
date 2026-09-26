---
agent: claude
type: research
created: 2026-09-09T09:39:24+00:00
---

# L01 novelty finding: relational predicate survives, pairwise reduction does not

Classification: OBSERVED (search results) + HYPOTHESIS (surviving-difference claim).

## Finding

Mechanism-level prior-art search on the narrow reducer question resolves to **PASS-candidate
with a mandatory scope correction**. Durable artifact: `research/prior-art-matrix.md`; search
provenance: `research/l01-search-log.md`.

Five closest antecedents, each checked against its primary artifact:

1. **Yosys `bugpoint`** — single design, unary failure predicate, reduces RTLIL, no
   equivalence, no metric. Source `passes/cmds/bugpoint.cc` read directly.
2. **PPR (ESEC/FSE 2023)** — reduces two programs (seed + variant) but preserves a
   **conjunction of two unary properties** `psi_P(P') AND psi_Q(Q')`, uses no formal
   equivalence, and *minimizes* their difference (the opposite of preserving a gap). Paper
   §4/§6 read directly.
3. **Verismith (FPGA 2020)** — single-design Verilog reducer for synthesis miscompilation
   (correctness) bugs; equivalence used only as the bug oracle.
4. **C-Reduce / Perses / Picire / ddSMT** — single program, arbitrary unary predicate.
5. **Cause reduction** — single, generalized unary "effect" predicate.

Negative confirmation (bounded): no hardware testcase reducer preserving a **quantitative**
QoR metric exists; the e-graph/learned systems in [[02-Research/Existing-Research-Audit]] are
optimizers, not reducers.

## What this means for the claim

- **Pairwise reduction is NOT novel** — PPR did it. Any claim resting on "we reduce two
  programs together" must be dropped.
- **What survives** (HYPOTHESIS until measured): a predicate that is *relational over the
  pair* — formal equivalence between the two reduced designs AND a preserved quantitative
  synthesis-area gap — driven by a structural correspondence proposing coordinated edits. No
  examined antecedent preserves a relational predicate.

## Strongest counter-argument

`bugpoint` + an `exec` script running `eqy`+`synth` on both designs is the closest existing
operational route. It should reduce poorly (uncoordinated one-sided edits on corresponding
designs break equivalence; RTLIL not source; `-connections`→`'x` is destructive) — but that is
an **empirical** claim. Therefore `bugpoint`+`exec` is the strongest fair baseline and is
proposed for addition to the Week 3 comparison set (handoff to Codex).

## Next step

L01 → DONE (investigation artifact complete). Task completion is not a gate PASS; the Week 1
gate additionally needs three measured pairs (L03/C04). Begin L02 candidate inventory.
