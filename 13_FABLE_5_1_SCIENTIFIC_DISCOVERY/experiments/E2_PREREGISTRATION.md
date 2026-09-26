# E2 — pre-registration (written before any E2 area data was generated)

**Question.** Does the adder-count advantage of universal block patterns (E1) survive real logic synthesis and technology mapping at iso-delay? And does generic synthesis already find the same sharing?

## Designs

- **Matrices:** 128×128 i.i.d. ternary, p0 ∈ {0.33, 0.50}, seed 0 (the same W as E1 seed 0 at n = 128).
- **Designs** (all bit-parallel, combinational, 8-bit signed inputs, exact outputs):
  - `g1`: per-input add/sub/skip, balanced tree per row. This is the via-programmable status quo.
  - `ubp2`, `ubp3`, `ubp4`: universal block patterns. The generator computes all patterns; rows select.
  - `cbp4`: weight-specific block patterns (used patterns only).
  - `da4ml`: the weight-specific CSE DAG (strongest open CMVM).
  - `beh`: y_i = Σ_j w_ij x_j written behaviourally. Yosys `alumacc`/`maccmap` and ABC choose the structure (the generic-synthesis baseline).

## Flow (identical for every design)

1. Our structural Verilog, or the behavioural Verilog.
2. Yosys 0.69 (YoWASP): `synth -flatten -noabc; aigmap; write_aiger -ascii`.
3. **Independent check:** our own Python AIGER simulator, 64 random vectors, against numpy `W@x`.
4. Native ABC (berkeley-abc master `ab2139e`, built here) with the SKY130 HD tt_025C_1v80 liberty:
   - (a) `strash; dch; map; topo; stime -p`. This gives each design's delay-oriented D_i.
   - (b) **iso-delay:** D* = max_i D_i over all designs of the same matrix. Every design is re-mapped with `strash; dch; map -D D*; topo; stime -p`. We report area and achieved delay.
5. ABC `cec` of every mapped network against its own AIG. Only the literal "Networks are equivalent" counts.

## Kill and advance conditions (fixed now)

| ID | Condition at iso-delay (step 4b) | Classification |
|---|---|---|
| K2a | area(g1) / min_g area(ubp_g) < 1.3 for both p0 | Adder advantage does not survive mapping → MECHANISM WEAKENED at gate level |
| K2b | area(beh) ≤ 1.2 × min_g area(ubp_g) | Generic synthesis already captures the sharing → OCCUPIED BY EXISTING TOOL |
| ADV | area(g1) / min_g area(ubp_g) ≥ 1.5 and area(beh) ≥ 1.3 × min_g area(ubp_g) | Advance; the next risk is wiring and PnR |

**Also reported, with no decision attached:** area(da4ml) / min_g area(ubp_g), which is the gate-level price of universality.

## Scope limits declared in advance

- **This measures cell area only.** Via-programmable select wiring is NOT captured, because synthesis turns constant selections into plain wires. The wiring question is handled by a separate, clearly labelled analytic model in `06_…` and is the main risk for the prototype phase.
- One matrix per p0. This is a gate-level confirmation of E1 trends, not a benchmark suite.

## Deviation log

(empty at registration)
