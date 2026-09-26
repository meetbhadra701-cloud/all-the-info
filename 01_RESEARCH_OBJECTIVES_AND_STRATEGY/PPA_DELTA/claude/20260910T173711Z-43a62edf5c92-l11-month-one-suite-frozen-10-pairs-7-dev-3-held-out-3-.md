---
agent: claude
type: decision
created: 2026-09-10T17:37:11+00:00
---

# L11: month-one suite frozen (10 pairs, 7 dev/3 held-out, 3 families); held-out tests scaffold-lift generality

Classification: OBSERVED (oracle-qualified) + DECISION (frozen splits). L11 suite frozen.

## Frozen month-one suite

`benchmarks/suites/month-one.json` (compare-runnable, comparison-suite schema) + 
`month-one-manifest.json` (families/splits/hashes/eligibility) + `discovery-ledger.md` (rejects).
All 10 pairs promoted to `benchmarks/pairs/`, schema-valid, oracle-qualified INTERESTING.

**10 pairs · 7 development / 3 held-out · 3 families:**
- operator-sharing-across-mux (6): f1, a2, a3, a5, a6 (dev) + a4 (held-out)
- multiplier-sharing-across-mux (2): m1 (dev) + m2 (held-out)
- factoring-reassociation (2): f2s (dev) + f3s (held-out)

Qualifying delta_rel per pair (all INTERESTING, formal PASS): f1 +36.7, a2 +66.8, a3 +38.0,
a5 +102.6, a6 +39.2, m1 +75.8, f2s +45.6, a4 +60.4, m2 +125.2, f3s +89.3 (%).

## Held-out design (tests scaffold-lift generality WITHOUT tuning)

Held-out {a4, m2, f3s} spans all 3 families. a4 (4-way adder) and m2 (3-way mult) carry the
`sel==k` scaffold that scaffold-lift keys on (tuned on dev a2) → they test WITHIN-FAMILY structural
generalization of the frozen method. f3s (factoring, no scaffold) is the honest negative.
Splits were declared BEFORE any held-out reduction was run; method is frozen as of Week-3 PASS.

## Honest limitations (stated, in the manifest)

1. **Held-out shares origins with dev** — they are same-family variants (4-way vs 3-way, etc.).
   This tests structural-variant generalization, NOT origin-independent novelty.
2. **Public provenance UNRESOLVED** — all 10 synthetic; no real public-design/historical pairs
   sourced (combinational single-top real pairs are scarce). Marked unresolved per the gate.
3. **Erased/intractable families kept in the discovery ledger** — width/sign, mux-shape,
   duplicated-cone are erased by ABC; 8-bit multipliers are formally intractable. Not hidden.

## For Codex (C11)

The suite is independently runnable: `ppa-delta compare --suite benchmarks/suites/month-one.json
--out runs/codex/C11 --agent codex`. All 10 manifests resolve; config/toolchain/library hashes in
the manifest match the frozen runtime.

**NO-TUNING COVENANT (binding):** the reduction method is frozen. Held-out reduction results from
C11 must NOT be used to modify the method; doing so compromises the evaluation and requires a
genuinely new holdout. The decisive Week-4 question is whether coupled clears >=20% on the HELD-OUT
pairs it was not built for, and whether it hits the Week-4 technical bars (>=70% original-AST
reduction on >=7 cases; >=20% median advantage; coupled advantage on >=2 held-out).

C11 depends on L11 (done). Please run the frozen ten-pair six-method comparison; I take the
machine-readable rows into L12 analysis. 43/43 Claude tests, check_pack PASS. No Codex files touched.
