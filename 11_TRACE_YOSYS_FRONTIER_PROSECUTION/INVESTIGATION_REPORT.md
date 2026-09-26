# TRACE vs. Yosys arithmetic lowering: investigation report

**Date:** 2026-09-24.

**Folder:** `11_TRACE_YOSYS_FRONTIER_PROSECUTION/`.

**Prior material reused, not modified:**
- `10_OPUS_5_5_INVESTIGATION_2026-09-23/`, including S1;
- the Experiment 4 Yosys images: MAIN `e8db64c6` (clean) and PATCH (PR #6231 at `30b851e6`).

**Evidence labels:**
- **[OBSERVED]**: measured here. Every number comes from `RESULTS.csv`, `evidence/*.csv` or `logs/`; the tables in Appendix A are generated from those files.
- **[PAPER]**: stated in a cited paper.

## Decision: **ENGINEERING ONLY**; no research residual survives

**What TRACE handles.** TRACE, the strongest algebraic engine for this problem, verifies the arithmetic structures that Yosys's lowering produces **before ABC**:
- radix-4 Booth (Bewick and low-power);
- default `alumacc/maccmap` multipliers and MACs;
- `arith_tree` compressor trees with FMA fusion and Baugh–Wooley corrections;
- dot products.

These are verified signed and unsigned, up to 64 bits, in at most about 8 minutes each.
- TRACE finds the real Yosys `arith_tree` sign-extension defect wherever a template fits.
- It proves the PR #6231-patched output correct.

**Where it falls short.** Its failures are of two kinds, and both are covered by prior art:

1. **Implementation defects in TRACE.**
   - Its recommended phase-optimisation setting is **unsound** on a six-gate redundancy that the patched `arith_tree` emits before ABC. It certified the sign-extension bug `y = a*b + zext(c)` as a correct signed MAC.
   - It crashes on the constant-fan-in gates of Yosys's pre-ABC Booth netlists.
   - It ignores `-s` in DOT mode.
   - One traversal order leaves gate variables in its remainders.
   - It has no templates for `c − a*b`, wide accumulators or `a*b + c*d + e`.
2. **The known "logic-optimised multiplier" problem.** Some post-ABC netlists time out. We pinned this to two ABC passes, choice-based restructuring (`&dch`) and SAT sweeping (`fraig`), not to any Yosys lowering structure.

**The executed remedy.** We ran the published remedy with existing tools: SCA on the unoptimised reference, plus SAT equivalence across the optimisation step (RefSCAT's architecture). In a Yosys flow the reference is free, because it is the `-noabc` netlist of the same run.
- TRACE proves the pre-ABC netlist of every design and architecture tested up to 64 bits. The one exception is the patched 8-bit signed MAC tree, which needs `-p` off or a folded input because of the defect above.
- ABC `&cec` proves pre-ABC ≡ post-ABC for all 29 pairs tried, up to 64 bits.

**Conclusion.** No scientific obligation remains that the strongest prior art leaves open. What remains is repair (TRACE), integration (a stage-wise script) and a missing feature (a specification input). §9 gives the gate criteria.

---

## 1. What TRACE actually guarantees (Q1): capability reconstruction

Sources: arXiv 2608.16458 (HTML); `github.com/jan-kl/trace` at `d57aa9a7` (the latest commit; README, Dockerfile, examples; no issues); this folder's runs.

1. **Method.** Symbolic computer algebra with backward rewriting on an AIG. The specification polynomial `SP = Σ weighted outputs − spec(inputs)` is rewritten gate by gate with five AND-node rules, in reverse topological order under a chosen traversal (`idx`, `dyn`, `igs`, `ipc`, …). A final remainder of 0 means correct; non-zero means a fault [PAPER].
   - Signed modes use two's-complement weights. This was confirmed by sign-mismatch controls (`BL18`, `D07`) and by the MAIN/PATCH signed MAC results [OBSERVED].
   - Optional phase optimisation (`-p`) and ATPG-style conflict removal (`-c`) [PAPER].
2. **Operations.**
   - Paper templates: `-add`, `-mul`, and `-mac` (`F(2n+1) = A(n)·B(n) + S(2n)`).
   - The README adds `-dot=<n>` and `-gen`.
   - Operand order is implied by the template.
3. **Representations.** Combinational AIGER only. There is no word-level input and no user specification.
4. **Widths demonstrated** [PAPER]:
   - adders to 128 bits;
   - array, Dadda, counter-based Wallace and Wallace multipliers with seven final adders, to 64 bits (24/28 at 64 bits);
   - 28 MAC configurations (22/28 at 64 bits);
   - "behavioural" Yosys/ABC-synthesised MUL and MAC to 64 bits.

   Reproduced exactly here: 64-bit WT_KS max polynomial 27,310 (288 s); 64-bit behavioural MAC 15,135 (273 s) [OBSERVED].
5. **What `Correct` guarantees.** The AIG implements the selected template for all inputs, *if the implementation is correct*. That condition fails under `-p` for one input pattern (§6.1).
   - `Buggy` prints a remainder but never a counterexample.
   - Of 266 `Buggy` verdicts replayed here, 79 had remainders that describe no mismatch at all (§6.1, §6.4, §6.5).
6. **User-supplied specifications:** none.
7. **Specification derivation:** `-gen` (README). In this build it printed no polynomial and no verdict (`BL28`). It was never used as a reference.
8. **Certificates:** none; only metrics in a log. The process exit code is 0 for both `Correct` and `Buggy`. Verdicts here were read only from the `Result:` line.
9. **Limitations the authors acknowledge** [PAPER]:
   - some structural multipliers fail: CWT∘CS at 16 bit, DT∘CS at 32 bit, four architectures at 64 bit;
   - static ordering handles behavioural MACs only to about 8 bits.
10. **Booth and fused arithmetic.** Booth is not evaluated in the paper. MAC is supported via its template, with the addend merged into the partial-product array. No Booth- or `arith_tree`-specific handling is described [PAPER].

**Licence and provenance**
- The repository has **no licence file**. The binary is a static x86-64 ELF, 2,932,376 bytes, sha256 `a5c24904…4f92d`. Its git blob was verified against the repository tree.
- The upstream Dockerfile only copies the binary.
- With the user's authorisation, the binary was downloaded, kept under `third_party/` with a do-not-redistribute notice, and executed only in a hardened container:
  - `--network none`, read-only root;
  - `--cap-drop ALL`, `no-new-privileges`;
  - an unprivileged UID; pids, memory and CPU limits;
  - a read-only data mount.
- It was never run on the host.

## 2. Baseline trust (prompt §4) [OBSERVED, `trace_baseline_results.csv`]

- **It runs; the format and options behave as documented.** All 14 correct examples from the paper and README → `Correct`:
  - README multiplier and GenMul array;
  - behavioural MUL 8–64 and 64-bit WT_KS;
  - behavioural MAC 8–64 and NMAC;
  - 8-bit adder.
- **Identity-rewritten copies** (three `IDENT_*`) → `Correct`.
- **Incorrect designs are rejected.**
  - Gate-level mutants whose behaviour change is proven by the oracle: four `Buggy`, each replayed as a real mismatch; two TIMEOUT at 900 s; none `Correct`.
  - Wrong-mode and wrong-sign invocations → `Buggy` (witness confirmed) or TIMEOUT. Never `Correct`.
- **Configuration matters.** Without `-dyn -p -c`, `ADD_128_CL` and behavioural MUL-16 exhaust 14 GiB. Capability was therefore always tested with a six-configuration portfolio.

## 3. Yosys structures tested (Q2)

`EXPERIMENTAL_MATRIX.md` has the full matrix. `RESULTS.csv` holds 1,214 classified TRACE runs: PASS 477, TIMEOUT 447, FAIL 185, FALSE_FAIL 79, ERROR 10, FALSE_PASS 10, UNSUPPORTED 6.

**Designs**
- **A, `y = a*b`.** Unsigned and signed.
  - Default lowering: `alumacc`/`maccmap`, Brent–Kung `$lcu`, then ABC.
  - `-booth`: Bewick for unsigned, pre-encoded low-power for signed, plus a `-lowpower` variant.
  - W = 8, 12, 16, 20, 24, 32, 64, plus an onset sweep W = 4..16.
- **B.** `a*b + c`, `a*b + c*d`, `a*b + c*d + e`, unsigned and signed.
  - Default lowering versus `arith_tree` (4:2 compressors, FMA, final adder) and its `-no-fma`, `-strategy fa` and `-final ripple` variants.
  - W = 8..64, plus an onset set at W = 40/48/56.
- **C, Y_WIDTH > A+B.** `a*b + c` and `c − a*b` with Y = 2W+8 and 2W+16, plus natural-width `c − a*b`.
  - W = 4..32, unsigned and signed.
  - Default lowering, unpatched `arith_tree`, and PR #6231 `arith_tree`.
- **Mini signed MACs,** W = 2..6, MAIN and PATCH.

**Synthesis stages.** Every architecture was synthesised post-ABC (the default `synth`) and pre-ABC (`-noabc`). Cause isolation added:
- nine single ABC steps applied to pre-ABC netlists;
- four ABC target gate libraries, via replicas that are byte-identical to the real post-ABC netlists.

**Mutants**
- RTL: sign extension, truncated product, dropped accumulator carry, off-by-one accumulator.
- Gate level: polarity flips; MSB ⊕ c_msb (= `a*b + zext(c)`); unconditional MSB flips.
- The real defect: the Baugh–Wooley correction is not sign-extended in unpatched `arith_tree`.

**Ground truth, independent of TRACE**
- 497 main netlists (406 correct, 91 incorrect), with every port order audited.
- Every derived and extra netlist is oracle-checked (`evidence/ground_truth_*.csv`).
- The oracle is exhaustive ≤ 20 input bits, otherwise 4,096 corner plus 16,384 random vectors.

## 4. Results

### 4.1 What passed (Q3) [OBSERVED]

- **Every pre-ABC Yosys netlist tested, up to W = 64, with the paper's configuration `-dyn -p -c`:**

  | Design | 64-bit TRACE time |
  |---|---|
  | Unsigned default multiplier | 264 s |
  | Signed default multiplier | 152 s |
  | Unsigned Booth (constant-folded) | 294 s |
  | Signed Booth | 467 s |
  | Unsigned MAC, default lowering | 348 s, uncontended |
  | Unsigned MAC, `arith_tree` | 188 s |
  | Unsigned dot-product tree | 308 s, uncontended |
  | Patched signed MAC tree | 217 s |

  At W ≤ 32 every pre-ABC netlist takes ≤ 34 s. The signed low-power Booth passes pre-ABC at 8/16/32 bits after folding.

  Exception: the patched **8-bit** signed tree needs `-p` off, or folding (§6.1).
- **Post-ABC netlists that pass directly** (portfolio; Appendix A):

  | Netlist class | Widths passed |
  |---|---|
  | Signed default multiplier | 8–64 (64-bit: 162 s) |
  | Signed Booth | 8–64 (270 s) |
  | Unsigned Booth | 16–64 (260 s); also 4–7, 11, 13–15 in the sweep |
  | Unsigned default multiplier | 8–16 |
  | Unsigned MAC, default lowering | 8–16 |
  | Unsigned MAC, `arith_tree` | 8–32 |
  | Signed default MAC | 12–32; also 8 given 1,092 s |
  | Patched signed MAC trees | 8–32 |
  | Unsigned dot2 | 8 (and the tree at 12) |
- **The real Yosys defect is detected.** Every template-fitting unpatched signed `arith_tree` MAC was reported `Buggy`, and every remainder replays as the real constant offset:
  - post-ABC at W = 8, 12, 16, 24, 32;
  - pre-ABC at W = 8, 16, 32, 64;
  - the `-strategy fa` and `-final ripple` variants;
  - minis at W = 2..6.

  This is the successful verification outcome the prompt asks about (class FAIL).
- **The patched implementations are proved correct** wherever a template fits: post-ABC W = 8..32, and pre-ABC W = 16..64 plus 8 with `-p` off or folded.

### 4.2 What failed (Q4) [OBSERVED]

| Class | Where | Evidence |
|---|---|---|
| **FALSE_PASS** | `a*b + zext(c)` mutants of the patched pre-ABC signed MAC (W = 3, 4, 8), under `-p` configurations | 10 runs. The oracle mismatch is replayed (`counterexamples/FALSE_PASS__*.json`), exhaustively at W = 3/4 |
| **FALSE_FAIL** | Correct patched pre-ABC signed MACs (W = 3/4/8/16) under `-p`; the context grafts; `-igsm` on the 8-bit signed multiplier; every signed `-dot=2 -s` | 79 runs. Every remainder is invalid on replay |
| **ERROR** | Raw pre-ABC unsigned Booth (W = 8..64) and signed low-power Booth (W = 8..32): segfault on the constant-fan-in AND | Controlled by `buffer`/`fold` |
| **TIMEOUT, genuine** | Post-ABC unsigned Booth W = 8, 9, 10, 12 (1,800 s at W = 8); post-ABC signed low-power Booth W ≥ 7 (1,800 s at W = 8) | Rewriting blow-up: 80 → 34,309 monomials in 201 of 601 steps. The pre-ABC versions take ~1 s |
| **TIMEOUT, other post-ABC** | Post-ABC unsigned default multiplier W = 20..32; unsigned default MAC W = 24/32; unsigned dot2 W ≥ 12 (default) / 16 (tree); the 64-bit post-ABC MAC trees (900 s, one configuration) | Uncontended 1,800 s calibration: unsigned default multiplier W = 32 and dot2 W = 16 still time out (6.3 GB and 2.0 GB peaks). The blow-ups are genuine |
| **TIMEOUT (refutation)** | 22 of 24 post-ABC RTL mutant netlists, under every configuration, up to 900 s | Only `plus1_dot2` at W = 8 (default and tree) was refuted. There was no false pass on any of them |
| **UNSUPPORTED** | All of Family C, `a*b + c*d + e`, and `-gen` | No template |

### 4.3 What remains uncertain (Q5)

- **Budget versus blow-up.** Contention caused some timeouts: both 64-bit *pre*-ABC timeouts passed uncontended in 308–348 s. The *post*-ABC timeouts that were recalibrated (unsigned default multiplier W = 32; dot2 W = 16; 8-bit Booth and low-power Booth) persisted at 1,800 s. The remaining post-ABC timeouts were not recalibrated one by one. None of them affects the decision, because the stage-wise route covers them.
- **Other SCA engines on post-ABC netlists.** Whether AMulet2, DynPhaseOrderOpt, RevSCA-2.0, RefSCAT or ReVEAL verify the `&dch`/`fraig`-restructured Yosys netlists *directly* was not run:
  - AMulet2 needs a new download;
  - the others are unreleased or unlicensed binaries.

  The published benchmark sets use `resyn3`/`dc2` optimisation, not `&dch`/`fraig` [PAPER: Konrad & Scholl; Arisca; ReVEAL]. See §8 for why this does not change the decision.
- **Other triggers of the `-p` defect.** The one trigger found was surveyed across all 650 Yosys-generated netlists here: it occurs only in PATCH signed `arith_tree` pre-ABC output (MAC W = 3, 4, 8, 16; `dot2c` W = 8, 16, 32). The constant-fan-in crash trigger occurs only in pre-ABC Booth output. Other structures might trigger the same `-p` bug; TRACE's source is not available.
- **Family C correctness at large widths** rests on the sampling oracle (exhaustive only at W = 4). It does not affect any TRACE classification, because TRACE cannot express these specifications.
- **Synthesis timeout.** `B_dot2_u_w64` default lowering did not finish in Yosys itself (3,600 s).

## 5. What the controls established (Q6) [OBSERVED]

| Control | Result | Establishes |
|---|---|---|
| TRACE examples plus identity rewrites | All `Correct`; the paper's polynomial sizes reproduced | The tool, format and options work |
| Replay of all 266 `Buggy` verdicts (`counterexamples/`) | 183 real mismatches on incorrect netlists; 3 deliberate template-mismatch controls; 79 invalid remainders on correct netlists; 1 `-igsm` remainder that is wrong on an incorrect netlist | A `Buggy` verdict must be replayed before it is believed: 79 of 266 were false alarms, all caused by the `-p`, `-igsm` and DOT `-s` defects. Every replayed one is a real bug |
| Wrong-mode / wrong-sign invocations | Never `Correct` | Template semantics understood |
| `buffer` / `fold` | One inserted `AND(x, TRUE)` → segfault; the crashing netlists folded → `Correct` | The constant-fan-in gate alone causes the crash |
| `-p` / `-c` ablation | Only configurations with `-p` produce the false verdicts | Phase optimisation is necessary |
| `fold` of the trigger | The folded 8-bit netlist is `Correct` under the two `-p` configurations that had failed. Its three MSB mutants are `Buggy` under all 8 configurations | The `AND(x,¬x)` pattern is necessary |
| Isolated `AND(x,¬x)` or `XNOR(x,x)` at an output | Never a false verdict | The pattern alone is not sufficient |
| **Graft of the six-gate Yosys context** at 55 positions in 4 unrelated correct netlists | False `Buggy` under ≥ 1 `-p` configuration in **49/55**; `-dyn -c` correct in **55/55**; spurious remainders exactly ±2^k·x | **Causal.** Context plus `-p` is sufficient, independent of design and signedness |
| **Single ABC steps** on pre-ABC Booth and dot netlists | `strash`, `balance`, `rewrite`, `dc2`, `resyn2`: verifiable; `refactor` verifiable under at least one configuration. `&dch` breaks both Booth multipliers; `fraig` breaks the low-power Booth; the full Yosys ABC script (without mapping) breaks all three | The post-ABC difficulty is caused by choice-based restructuring and SAT sweeping |
| **ABC gate library** (`-g aig`/`gates`/`simple`/default; replicas byte-identical to the real post-ABC netlists) | Identical outcome for every library | Technology mapping and `aigmap` re-expansion are not the cause |
| Pre ≡ post `&cec` | 29/29 PASS, W = 8..64, 0.2–662 s | The ABC step is independently checkable |
| Onset sweeps (W = 4..16 multipliers; W = 40..56 MAC/dot) | Non-monotone post-ABC failures; smooth pre-ABC growth | Not a scaling law of Booth or trees |
| Uncontended reruns | 64-bit pre-ABC MAC/dot: TIMEOUT ×6 contended → PASS in 308–348 s. Post-ABC W = 32 default multiplier and W = 16 dot2: still TIMEOUT at 1,800 s | Pre-ABC contended timeouts were budget artefacts; the post-ABC blow-ups are real |
| Byte-identical re-synthesis | Sweep W = 8/16 and ABC replicas identical to the main set | Deterministic, reproducible synthesis |

## 6. Exact causes (Q7)

### 6.1 Phase-optimisation unsoundness (TRACE implementation defect; consequential) [OBSERVED]

**Trigger**

Before ABC, the PR #6231-patched `arith_tree` sign-extends the addend with a half-adder whose two inputs are the same sign bit `x`. In the AIG this becomes:
- two identical `AND(¬x, x)` gates;
- their NOR, `XNOR(x,x) = 1`;
- an XOR with `u = AND(p, ¬x)`.

**Effect**

Under phase optimisation, TRACE's remainder differs from the true remainder by exactly ±2^k·x (mod 2^(2W+1)), where 2^k is the arithmetic weight of the affected signal. This happens in all four `-p` configurations at W = 8, and in at least one `-p` configuration at W = 3, 4 and 16; it depends on the traversal. It never happens without `-p`.
- On the correct 3-bit netlist (144 ANDs), `-dyn -p -c` returns `SP: {2} -64 + 64i24`.
- On `y = a*b + zext(c)`, whose true error is ∓2^6·c5, it returns **`Correct`**. `-dyn -c` correctly returns `Buggy`, with a remainder `-64n24` that replays.

Minimal package: `evidence/trace_phaseopt_minimal_repro/`.

**Guarantee violated and scope**
- The violated guarantee is "remainder 0 ⇒ correct". Exact phase substitution `s = 1 − s̄` cannot change the remainder, so this is an implementation defect, not a limit of the method.
- The pattern exists only in unsimplified netlists: ABC `strash` or constant folding removes it.

### 6.2 Post-ABC timeouts (known problem class; the exact passes identified) [OBSERVED]

**Not the cause**

The failures are **not** caused by any Yosys lowering structure. Booth recoding, Baugh–Wooley corrections, Brent–Kung/CLA final adders, compressor trees, FMA fusion and signedness all verify before ABC at every width tested.

**The cause**

The single-step experiment identifies it:
- ABC's `&dch` (structural choices) alone makes both Booth multipliers unverifiable.
- `fraig` (SAT sweeping) alone does so for the low-power Booth.
- Yosys's full ABC script without mapping does so for all three test designs.
- Local rewriting (`strash`, `balance`, `rewrite`, `dc2`, `resyn2`) leaves them verifiable; `refactor` does too under at least one configuration.
- Technology mapping is irrelevant: every gate library gives the same result.

**Mechanism**

The polynomial explodes early in rewriting: 80 → 34,309 monomials on 8-bit Booth. The failures are non-monotone in width: unsigned Booth fails at W = 8, 9, 10, 12 and passes at 11 and 13–64. Both facts fit the literature's account: optimisation merges and restructures nodes across adder boundaries, so the intermediate polynomials lose the cancellations they would otherwise have [PAPER: DyPoSub, RevSCA-2.0, Konrad & Scholl, RefSCAT, ReVEAL].

**Remedy (executed)**

RefSCAT's decomposition with Yosys's own reference:
1. TRACE proves the `-noabc` netlist.
2. `&cec` proves that netlist equivalent to the post-ABC netlist.

The stage-wise table (Appendix A) shows this closing every post-ABC timeout that has a CEC pair, up to 64 bits.

### 6.3 Crash on constant-fan-in AND (TRACE implementation defect) [OBSERVED]

- Yosys's pre-ABC unsigned Bewick Booth and signed low-power Booth each contain one `AND(x, TRUE)`.
- TRACE segfaults (signal 11) in about 0.01 s.
- Controlled both ways. The folded netlists verify: unsigned to W = 64 in 294 s, low-power to W = 32.

### 6.4 `-igsm` invalid remainders (TRACE implementation defect) [OBSERVED]

- **On a correct netlist.** On the exhaustively correct 8-bit signed default multiplier, `-igsm -p -c` returns `Buggy`, remainder `-4n2n4n18n20 + 4n4n20n34`. `n34` is the internal gate `a0∧b0`, and the remainder is identically 0 over all 65,536 inputs. `-idx` and `-ipc` prove the same netlist.
- **On an incorrect netlist.** On the off-by-one dot-product mutant, `-igsm` returns a 904-term remainder with internal gate `n74`. It evaluates to 0 on 20,202 inputs, although the true error is the constant 1: the verdict is right, but the remainder is wrong.
- **Diagnosis:** incomplete substitution.

### 6.5 DOT mode ignores `-s` (TRACE feature defect) [OBSERVED]

- Remainders are identical with and without `-s`. They equal the unsigned reading of a correct signed dot product.
- Every signed `dot2`, patched or not, → false `Buggy`.
- DOT is README-only.

### 6.6 Template restrictions (missing feature) [OBSERVED]

- `c − a*b` run as `-mac` → `Buggy`. The witness confirms the template mismatch, so the outcome is UNSUPPORTED.
- `dot2c` run as `-dot=2` → `Buggy`.
- Wide accumulators → TIMEOUT.

An SCA specification is just a polynomial, so this is a missing input format.

### 6.7 Refutation timeouts (known property of SCA) [OBSERVED]

- Data-dependent RTL bugs (sign extension, truncation, dropped carry) make remainders explode: 22/24 post-ABC mutant netlists time out under every configuration.
- The random-simulation oracle finds each of them in under 1 s.
- Constant-offset bugs are refuted quickly; the real `arith_tree` defect is one of these.

### 6.8 Configuration sensitivity (known property) [OBSERVED]

- `-dyn` stalls on some Yosys default multipliers where `-idx` proves them in 1–24 s.
- A portfolio is required, which is DynPhaseOrderOpt's central observation.

## 7. Prior art on each failure (Q8)

`PRIOR_ART_PROSECUTION.md` has the full analysis.

| Mechanism | Prior art that explains or solves it | Residual |
|---|---|---|
| Post-ABC (`&dch`/`fraig`-restructured) netlists | Optimised-multiplier SCA: DyPoSub (DATE'20), RevSCA-2.0 (TCAD'22), Konrad & Scholl (FMCAD'24/FMSD'26), ReVEAL (TACAS'26), Arisca (arXiv'26). Reference-plus-SAT decomposition: RefSCAT (TCAD'24/25), **executed here** with Yosys's own reference | Integration |
| `-p` unsound on the Yosys `XNOR(x,x)` context | Exact phase substitution (Konrad & Scholl); dual variables (Kaufmann, Beame, Biere, Nordström, DATE'22); PAC certificates with Pacheck/Pastèque, the latter Isabelle-verified (FMSD'22); ACL2-verified rewriting (Temel et al., CAV'20) | Repair; certificates |
| Crash; `-igsm`; DOT `-s` | Standard completeness conditions; signed dot-product SCA (Bremen DATE'25; Arisca) | Repair |
| Templates | SCA accepts any polynomial spec: Arisca user specs; Bremen MAC line (DVCon'25, FDL'25, SN CS'26) | Feature |
| Refutation; order sensitivity | Simulation/SAT as complement; order/phase optimisation and portfolios | None |

## 8. Does a genuine scientific question remain? (Q9)

No.

**Candidate residual 1**

> "SCA fails on Yosys's ABC-optimised Booth, MAC and dot-product netlists."

This is the published optimised-multiplier problem. For Yosys it is sidestepped with existing tools: the unoptimised reference is a free by-product of the same synthesis run, and SAT sweeping verifies ABC's step up to 64 bits.

The closest thing to an open question is that the published SCA benchmark sets optimise with `resyn3`/`dc2` [PAPER], while our failures come from `&dch` and `fraig` (§6.2). Whether dedicated engines handle *choice-restructured and SAT-swept* multipliers **without** a reference is an efficacy question in a crowded area.
- RefSCAT's reverse-engineered-reference approach is the established answer to reference-free verification.
- Yosys users do not need it.

It fails gate criteria 4 and 5. To revisit it, the evidence needed is: AMulet2, RevSCA-2.0, DynPhaseOrderOpt, ReVEAL or RefSCAT run on the `netlists/ABCSTEP/*__dch.aig` and `*__fraig.aig` netlists (and the post-ABC W = 8/12 Booth). Only a failure of *all* of them would make it a candidate.

**Candidate residual 2**

> "Phase optimisation is unsafe on degenerate reconvergent structures."

The theory is sound (exact substitution, dual variables), and a certificate-producing engine would reject the false pass mechanically. This is a bug fix.

**Candidate residual 3**

> "Specifications for negated, wide and multi-product accumulations."

These are polynomials that SCA accepts. This is a missing input format.

## 9. Decision gate (Q10)

| ADVANCE criterion | Status |
|---|---|
| 1. A reproducible failure of the strongest applicable existing method | **Partly.** TRACE fails reproducibly. The strongest applicable *method* for the post-ABC class (reference + SAT) succeeds on every design tested |
| 2. A legitimate, consequential circuit family | Yes: Yosys Booth, MAC and dot-product lowering |
| 3. A precise structural explanation | Yes. The `-p` defect is isolated to a causally verified six-gate context. The post-ABC failures are isolated to `&dch`/`fraig` |
| 4. A scientific obligation not addressed by prior art | **No** (§7, §8) |
| 5. A plausible path to a substantial technical contribution | **No.** What is available: bug reports, a TRACE fix, certificates, a flow script, a spec input |
| 6. An independently reproducible foundation | Yes (`REPRODUCTION.md`; deterministic synthesis; sandboxed runs; replayed witnesses) |

Criteria 4 and 5 fail, so the candidate does not advance. It is not KILLED in the strict sense, because real limitations exist in the strongest dedicated tool. The classification is **ENGINEERING ONLY**.

## 10. Practical consequences (engineering, not research)

1. **TRACE's recommended `-dyn -p -c` can return a false `Correct` on unsimplified netlists.** This includes pre-ABC Yosys output. Until TRACE is fixed:
   - fold constants or `strash` first, or omit `-p`;
   - replay remainders instead of trusting them.
2. **A certifying Yosys arithmetic check is achievable today:**
   - `synth … -noabc` → fold/`strash` → TRACE portfolio against the template, *and* `&cec` pre ≡ post.
   - Designs outside TRACE's templates (Family C, `dot2c`, signed dot) need a spec-polynomial input or another engine.
3. The unpatched `arith_tree` defect is caught wherever a template fits. The PR #6231 output is proved correct wherever a template fits, including 64-bit pre-ABC.

## 11. Exactly one next action

Close this line as research. If the user wishes, they can send the minimal reproduction (`evidence/trace_phaseopt_minimal_repro/`) to the TRACE authors; the report must come from the user, and nothing has been sent. The remaining engineering (a stage-wise script, a spec-polynomial input) does not meet the research objective.

---

## Appendix A: generated tables

Regenerate with `python scripts/finalize.py`, which runs replay → classification → tables. The content of `evidence/report_tables.md` follows.

<!-- TABLES -->

### Family A — `y = a*b` (portfolio over six configurations, plus the longer/uncontended reruns; best outcome, solving configuration, TRACE time)

Unsigned `booth_pre` (raw) crashes TRACE at every width (constant-fan-in AND); the folded copy is the same function.

| netlist | W=8 | W=12 | W=16 | W=20 | W=24 | W=32 | W=64 |
|---|---|---|---|---|---|---|---|
| unsigned · default synth (post-ABC) | PASS (idx, <1 s) | PASS (idx, <1 s) | PASS (idx, 23 s) | TIMEOUT ×6 (≤180 s) | TIMEOUT ×6 (≤240 s) | TIMEOUT ×6 (≤300 s) | – |
| unsigned · synth -booth (post-ABC) | TIMEOUT ×7 (≤1800 s) | TIMEOUT ×6 (≤90 s) | PASS (dyn, 1 s) | PASS (dyn, 3 s) | PASS (dyn, 6 s) | PASS (dyn, 21 s) | PASS (dyn, 260 s) |
| unsigned · default, pre-ABC | PASS (dyn, <1 s) | – | PASS (dyn, <1 s) | – | – | PASS (dyn, 11 s) | PASS (dyn, 264 s) |
| unsigned · booth, pre-ABC, const-folded | PASS (dyn, <1 s) | – | PASS (dyn, <1 s) | – | – | PASS (dyn, 23 s) | PASS (dyn, 294 s) |
| signed · default synth (post-ABC) | PASS (idx, <1 s) | PASS (dyn, <1 s) | PASS (dyn, 1 s) | PASS (dyn, 2 s) | PASS (dyn, 16 s) | PASS (dyn, 15 s) | PASS (dyn, 162 s) |
| signed · synth -booth (post-ABC) | PASS (dyn, <1 s) | PASS (dyn, <1 s) | PASS (dyn, <1 s) | PASS (dyn, 3 s) | PASS (dyn, 5 s) | PASS (dyn, 25 s) | PASS (dyn, 270 s) |
| signed · booth -lowpower (post-ABC) | TIMEOUT ×7 (≤1800 s) | – | TIMEOUT ×6 (≤120 s) | – | – | TIMEOUT ×2 (≤300 s) | – |
| signed · default, pre-ABC | PASS (dyn, <1 s) | – | PASS (dyn, <1 s) | – | – | PASS (dyn, 15 s) | PASS (dyn, 152 s) |
| signed · booth, pre-ABC | PASS (dyn, <1 s) | – | PASS (dyn, <1 s) | – | – | PASS (dyn, 23 s) | PASS (dyn, 467 s) |

### Family B — fused arithmetic (MAIN = unpatched; PATCH = PR #6231; portfolio plus longer/uncontended reruns)

MAIN signed `a*b+c` trees (except `-no-fma`) are INCORRECT by the oracle (the real Yosys defect): FAIL is the correct outcome there. Signed `dot2` is excluded: `-dot=2 -s` ignores `-s` (every run a FALSE_FAIL; `dotspec` stage).

| netlist | W=8 | W=12 | W=16 | W=24 | W=32 | W=64 |
|---|---|---|---|---|---|---|
| MAIN a*b+c u · default (post-ABC) | PASS (idx, <1 s) | PASS (idx, 1 s) | PASS (ipc, 16 s) | TIMEOUT ×6 (≤240 s) | TIMEOUT ×6 (≤300 s) | – |
| MAIN a*b+c u · default, pre-ABC | PASS (dyn, <1 s) | – | PASS (dyn, <1 s) | – | PASS (dyn, 8 s) | PASS (dyn, 348 s) |
| MAIN a*b+c u · arith_tree (post-ABC) | PASS (idx, <1 s) | PASS (ipc, <1 s) | PASS (idx, t=n/a) | PASS (ipc, 16 s) | PASS (ipc, 269 s) | TIMEOUT ×1 (≤900 s) |
| MAIN a*b+c u · arith_tree, pre-ABC | PASS (dyn, <1 s) | – | PASS (dyn, 1 s) | – | PASS (dyn, 9 s) | PASS (dyn, 188 s) |
| MAIN a*b+c u · arith_tree -no-fma | PASS (idx, <1 s) | – | PASS (ipc, 17 s) | – | – | – |
| MAIN a*b+c u · arith_tree -strategy fa | PASS (idx, <1 s) | – | PASS (idx, 6 s) | – | – | – |
| MAIN a*b+c u · arith_tree -final ripple | PASS (idx, <1 s) | – | PASS (idx, 7 s) | – | – | – |
| MAIN a*b+c s · default (post-ABC) | PASS (idx, 1092 s) | PASS (dyn, <1 s) | PASS (dyn, 2 s) | PASS (dyn, 15 s) | PASS (dyn, 20 s) | – |
| MAIN a*b+c s · default, pre-ABC | PASS (dyn, <1 s) | – | PASS (dyn, <1 s) | – | PASS (dyn, 13 s) | – |
| MAIN a*b+c s · arith_tree (post-ABC) | FAIL (igsm, <1 s) | FAIL (igsm, <1 s) | FAIL (ipc, <1 s) | FAIL (igsm, 2 s) | FAIL (idx, 10 s) | TIMEOUT ×1 (≤900 s) |
| MAIN a*b+c s · arith_tree, pre-ABC | FAIL (igs, <1 s) | – | FAIL (dyn, <1 s) | – | FAIL (dyn, 9 s) | FAIL (dyn, 209 s) |
| MAIN a*b+c s · arith_tree -no-fma | TIMEOUT ×6 (≤60 s) | – | PASS (dyn, 2 s) | – | – | – |
| MAIN a*b+c s · arith_tree -strategy fa | FAIL (idx, <1 s) | – | FAIL (idx, <1 s) | – | – | – |
| MAIN a*b+c s · arith_tree -final ripple | FAIL (igsm, <1 s) | – | FAIL (igsm, <1 s) | – | – | – |
| PATCH a*b+c s · arith_tree (post-ABC) | PASS (dyn, <1 s) | PASS (ipc, <1 s) | PASS (dyn, <1 s) | PASS (ipc, 2 s) | PASS (dyn, 63 s) | TIMEOUT ×1 (≤900 s) |
| PATCH a*b+c s · arith_tree, pre-ABC | **FALSE_FAIL** ×2, TIMEOUT ×4 | – | PASS (dyn, <1 s) | – | PASS (dyn, 8 s) | PASS (dyn, 217 s) |
| PATCH a*b+c s · arith_tree -strategy fa | PASS (dyn, 21 s) | – | PASS (dyn, 5 s) | – | – | – |
| PATCH a*b+c s · arith_tree -final ripple | PASS (dyn, <1 s) | – | PASS (dyn, <1 s) | – | – | – |
| MAIN a*b+c*d u · default (post-ABC) | PASS (idx, 9 s) | TIMEOUT ×6 (≤90 s) | TIMEOUT ×6 (≤120 s) | TIMEOUT ×6 (≤240 s) | TIMEOUT ×2 (≤300 s) | – |
| MAIN a*b+c*d u · default, pre-ABC | PASS (dyn, <1 s) | – | PASS (dyn, 2 s) | – | PASS (dyn, 32 s) | – |
| MAIN a*b+c*d u · arith_tree (post-ABC) | PASS (idx, <1 s) | PASS (ipc, 32 s) | TIMEOUT ×6 (≤120 s) | TIMEOUT ×6 (≤240 s) | TIMEOUT ×2 (≤300 s) | – |
| MAIN a*b+c*d u · arith_tree, pre-ABC | PASS (dyn, <1 s) | – | PASS (dyn, 2 s) | – | PASS (dyn, 29 s) | PASS (dyn, 308 s) |
| MAIN a*b+c*d u · arith_tree -no-fma | PASS (idx, 13 s) | – | TIMEOUT ×6 (≤120 s) | – | – | – |
| MAIN a*b+c*d u · arith_tree -strategy fa | PASS (idx, 2 s) | – | TIMEOUT ×6 (≤120 s) | – | – | – |
| MAIN a*b+c*d u · arith_tree -final ripple | PASS (idx, <1 s) | – | TIMEOUT ×6 (≤120 s) | – | – | – |

### Onset sweep (`y = a*b`, W = 4..16, 60 s per configuration)

| netlist | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A_mul_u norm | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| A_mul_u booth | ✓ | ✓ | ✓ | ✓ | ⏱ | ⏱ | ⏱ | ✓ | ⏱ | ✓ | ✓ | ✓ | ✓ |
| A_mul_s norm | ✓ | ✓ | ✓ | ✓ | ✓ | ⏱ | ✓ | ✓ | ✓ | ⏱ | ✓ | ✓ | ✓ |
| A_mul_s booth | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| A_mul_s booth_lp | ✓ | ✓ | ✓ | ⏱ | ⏱ | ⏱ | ⏱ | ⏱ | ⏱ | ⏱ | ⏱ | ⏱ | ⏱ |

✓ = proved by at least one of the configurations run; ⏱ = every configuration timed out.

### Stage-wise certification: TRACE on the pre-ABC netlist + ABC `&cec` pre ≡ post

| design (build) | W | TRACE on pre-ABC netlist | `&cec` pre≡post | TRACE directly on post-ABC |
|---|---|---|---|---|
| A_mul_s_w8 booth_lp (MAIN) | 8 | PASS (dyn, <1 s) | PASS (1.0 s) | TIMEOUT ×7 (≤1800 s) |
| A_mul_s_w16 booth (MAIN) | 16 | PASS (dyn, <1 s) | PASS (0.5 s) | PASS (dyn, <1 s) |
| A_mul_s_w16 booth_lp (MAIN) | 16 | PASS (idx, <1 s) | PASS (1.3 s) | TIMEOUT ×6 (≤120 s) |
| A_mul_s_w16 norm (MAIN) | 16 | PASS (dyn, <1 s) | PASS (0.5 s) | PASS (dyn, 1 s) |
| A_mul_u_w16 booth (MAIN) | 16 | PASS (dyn, <1 s) | PASS (1.2 s) | PASS (dyn, 1 s) |
| A_mul_u_w16 norm (MAIN) | 16 | PASS (dyn, <1 s) | PASS (0.6 s) | PASS (idx, 23 s) |
| B_dot2_u_w16 norm (MAIN) | 16 | PASS (dyn, 2 s) | PASS (0.7 s) | TIMEOUT ×6 (≤120 s) |
| B_dot2_u_w16 tree (MAIN) | 16 | PASS (dyn, 2 s) | PASS (0.3 s) | TIMEOUT ×6 (≤120 s) |
| B_mac_s_w16 tree (PATCH) | 16 | PASS (dyn, <1 s) | PASS (0.3 s) | PASS (dyn, <1 s) |
| B_mac_u_w16 norm (MAIN) | 16 | PASS (dyn, <1 s) | PASS (0.3 s) | PASS (ipc, 16 s) |
| B_mac_u_w16 tree (MAIN) | 16 | PASS (dyn, 1 s) | PASS (0.2 s) | PASS (idx, t=n/a) |
| A_mul_s_w32 booth (MAIN) | 32 | PASS (dyn, 23 s) | PASS (1.6 s) | PASS (dyn, 25 s) |
| A_mul_s_w32 booth_lp (MAIN) | 32 | PASS (dyn, 10 s) | PASS (49.3 s) | TIMEOUT ×2 (≤300 s) |
| A_mul_s_w32 norm (MAIN) | 32 | PASS (dyn, 15 s) | PASS (1.2 s) | PASS (dyn, 15 s) |
| A_mul_u_w32 booth (MAIN) | 32 | PASS (dyn, 23 s) | PASS (0.8 s) | PASS (dyn, 21 s) |
| A_mul_u_w32 norm (MAIN) | 32 | PASS (dyn, 11 s) | PASS (1.5 s) | TIMEOUT ×6 (≤300 s) |
| B_dot2_u_w32 norm (MAIN) | 32 | PASS (dyn, 32 s) | PASS (44.2 s) | TIMEOUT ×2 (≤300 s) |
| B_dot2_u_w32 tree (MAIN) | 32 | PASS (dyn, 29 s) | PASS (4.4 s) | TIMEOUT ×2 (≤300 s) |
| B_mac_s_w32 tree (PATCH) | 32 | PASS (dyn, 8 s) | PASS (0.5 s) | PASS (dyn, 63 s) |
| B_mac_u_w32 norm (MAIN) | 32 | PASS (dyn, 8 s) | PASS (0.5 s) | TIMEOUT ×6 (≤300 s) |
| B_mac_u_w32 tree (MAIN) | 32 | PASS (dyn, 9 s) | PASS (0.4 s) | PASS (ipc, 269 s) |
| A_mul_s_w64 booth (MAIN) | 64 | PASS (dyn, 467 s) | PASS (28.5 s) | PASS (dyn, 270 s) |
| A_mul_s_w64 norm (MAIN) | 64 | PASS (dyn, 152 s) | PASS (126.5 s) | PASS (dyn, 162 s) |
| A_mul_u_w64 booth (MAIN) | 64 | PASS (dyn, 294 s) | PASS (48.0 s) | PASS (dyn, 260 s) |
| A_mul_u_w64 norm (MAIN) | 64 | PASS (dyn, 264 s) | PASS (46.3 s) | – |
| B_dot2_u_w64 norm (MAIN) | 64 | – | no netlist (synthesis timeout) | – |
| B_dot2_u_w64 tree (MAIN) | 64 | PASS (dyn, 308 s) | PASS (662.4 s) | – |
| B_mac_s_w64 tree (PATCH) | 64 | PASS (dyn, 217 s) | PASS (3.7 s) | TIMEOUT ×1 (≤900 s) |
| B_mac_u_w64 norm (MAIN) | 64 | PASS (dyn, 348 s) | PASS (4.5 s) | – |
| B_mac_u_w64 tree (MAIN) | 64 | PASS (dyn, 188 s) | PASS (5.4 s) | TIMEOUT ×1 (≤900 s) |

### Phase-optimisation defect: natural netlists and mutants (P PASS, F FAIL, FF FALSE_FAIL, FP FALSE_PASS, t TIMEOUT)

Mutants `…y{MSB}xor{lit}`: lit = sign bit of c (even literal) gives exactly `a*b + zext(c)`; odd literal = its complement; `xor1` = unconditional MSB flip. `_folded` = constant-folded (pattern removed).

| netlist (oracle) | `-dyn -p -c` | `-dyn -p` | `-igs -p -c` | `-igs -p` | `-idx -p -c` | `-dyn -c` | `-dyn` | `-igs -c` | `-igs` | `-idx -c` | `-idx` | `-idx -p` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CONTROL/MUTX_PATCH_B_mac_s_w3__tree_pre__y6xor24 (INCO) | **FP** | **FP** | **FP** |  | F | F | F | F |  | F |  |  |
| CONTROL/MUTX_PATCH_B_mac_s_w3__tree_pre__y6xor25 (INCO) | F | F | F |  | F | F | F | F |  | F |  |  |
| CONTROL/MUTX_PATCH_B_mac_s_w4__tree_pre__y8xor32 (INCO) | F | **FP** | **FP** |  | F | F | F | F |  | F |  |  |
| CONTROL/MUTX_PATCH_B_mac_s_w4__tree_pre__y8xor33 (INCO) | F | F | F |  | F | F | F | F |  | F |  |  |
| CONTROL/MUTX_PATCH_B_mac_s_w8__tree_pre__y16xor1 (INCO) | F | F | F | F |  | F | F | F | F |  |  |  |
| CONTROL/MUTX_PATCH_B_mac_s_w8__tree_pre__y16xor64 (INCO) | **FP** | **FP** | **FP** | **FP** |  | F | F | F | F |  |  |  |
| CONTROL/MUTX_PATCH_B_mac_s_w8__tree_pre__y16xor65 (INCO) | F | F | F | F |  | F | F | F | F |  |  |  |
| CONTROL/MUTX_PATCH_B_mac_s_w8__tree_pre_folded__y16xor1 (INCO) | F | F | F | F |  | F | F | F | F |  |  |  |
| CONTROL/MUTX_PATCH_B_mac_s_w8__tree_pre_folded__y16xor64 (INCO) | F | F | F | F |  | F | F | F | F |  |  |  |
| CONTROL/MUTX_PATCH_B_mac_s_w8__tree_pre_folded__y16xor65 (INCO) | F | F | F | F |  | F | F | F | F |  |  |  |
| CONTROL/PATCH_B_mac_s_w8__tree_pre_folded (CORR) | P |  | P |  |  |  |  |  |  |  |  |  |
| MAIN/B_mac_u_w8__tree_pre (CORR) |  | P |  |  |  | P | P |  |  |  |  |  |
| MINI_MAIN/B_mac_s_w2__tree_pre (INCO) | F | F | F |  | F | F | F | F |  | F |  |  |
| MINI_MAIN/B_mac_s_w3__tree_pre (INCO) | F | F | F |  | F | F | F | F |  | F |  |  |
| MINI_MAIN/B_mac_s_w4__tree_pre (INCO) | F | F | F |  | F | F | F | F |  | F |  |  |
| MINI_MAIN/B_mac_s_w5__tree_pre (INCO) | F | F | F |  | F | F | F | F |  | F |  |  |
| MINI_MAIN/B_mac_s_w6__tree_pre (INCO) | F | F | F |  | F | F | F | F |  | F |  |  |
| MINI_PATCH/B_mac_s_w2__tree_pre (CORR) | P | P | P |  | P | P | P | P |  | P |  |  |
| MINI_PATCH/B_mac_s_w3__tree_pre (CORR) | **FF** | P | **FF** |  | P | P | P | P |  | P |  |  |
| MINI_PATCH/B_mac_s_w4__tree_pre (CORR) | P | **FF** | **FF** |  | P | P | P | P |  | P |  |  |
| MINI_PATCH/B_mac_s_w5__tree_pre (CORR) | P | P | P |  | P | P | P | P |  | P |  |  |
| MINI_PATCH/B_mac_s_w6__tree_pre (CORR) | P | P | P |  | P | P | P | P |  | P |  |  |
| PATCH/B_mac_s_w16__tree_pre (CORR) | P |  | **FF** |  |  |  |  |  |  |  |  |  |
| PATCH/B_mac_s_w8__tree_pre (CORR) |  | **FF** |  | **FF** |  | P | P | P | P | t | t | t |
| REPRO/mac_s_w3_patched_noabc_CORRECT (CORR) | **FF** |  |  |  |  | P |  |  |  |  |  |  |
| REPRO/mac_s_w3_zext_addend_mutant_INCORRECT (INCO) | **FP** |  |  |  |  | F |  |  |  |  |  |  |

### Causal graft of the six-gate Yosys context into unrelated correct netlists (`ctx`, 55 graft positions)

| source netlist | grafts | `-dyn -p -c` FF / P / t | `-igs -p -c` FF / P / t | `-dyn -p` FF / P / t | `-dyn -c` FF / P / t |
|---|---|---|---|---|---|
| A_mul_s_w8__norm_pre | 9 | 1 / 8 / 0 | 7 / 2 / 0 | 0 / 9 / 0 | 0 / 9 / 0 |
| B_mac_u_w8__tree_pre | 16 | 6 / 10 / 0 | 15 / 1 / 0 | 0 / 16 / 0 | 0 / 16 / 0 |
| PATCH_B_mac_s_w5__tree_pre | 11 | 4 / 7 / 0 | 9 / 2 / 0 | 1 / 10 / 0 | 0 / 11 / 0 |
| PATCH_B_mac_s_w8__tree_pre_folded | 19 | 7 / 11 / 1 | 15 / 3 / 1 | 2 / 15 / 2 | 0 / 19 / 0 |

### Which ABC step destroys verifiability? One ABC step applied to the pre-ABC netlist (`-dyn -p -c` and `-idx -p -c`; ✓ = proved by either)

`yosysnomap` = Yosys's default ABC script without the final technology mapping: `&fraig -x; scorr; dc2; dretime; strash; &dch -f`.

| pre-ABC source | strash | balance | rewrite | refactor | dc2 | resyn2 | fraig | dch | yosysnomap | full `synth` (post-ABC) |
|---|---|---|---|---|---|---|---|---|---|---|
| A_mul_s_w8 booth_lp_pre | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ⏱ | ⏱ | ⏱ | ⏱ |
| A_mul_u_w8 booth_pre_folded | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ⏱ | ⏱ | ⏱ |
| B_dot2_u_w16 norm_pre | ✓ 1 s | ✓ 1 s | ✓ 1 s | ✓ 1 s | ✓ 1 s | ✓ 3 s | ✓ 2 s | ✓ 2 s | ⏱ | ⏱ |

### Does the ABC target gate library matter? (`synth … -noabc; abc -g <lib>; aigmap`; `default` is byte-identical to the real post-ABC netlist)

| design | g_aig | g_gates | g_simple | default |
|---|---|---|---|---|
| A_mul_s_w8 booth_lp | ⏱ | ⏱ | ⏱ | ⏱ |
| A_mul_u_w12 booth | ⏱ | ⏱ | ⏱ | ⏱ |
| A_mul_u_w20 norm | ⏱ | ⏱ | ⏱ | ⏱ |
| A_mul_u_w8 booth | ⏱ | ⏱ | ⏱ | ⏱ |
| B_dot2_u_w16 norm | ⏱ | ⏱ | ⏱ | ⏱ |

### Onset of 64-bit pre-ABC cost (`-dyn -p -c`; W = 64 from `stage2_pre` under contention and `long64` uncontended)

| netlist | W=32 | W=40 | W=48 | W=56 | W=64 (900 s, contended) | W=64 (3600 s, uncontended) |
|---|---|---|---|---|---|---|
| B_mac_u norm_pre | ✓ 8 s | ✓ 31 s | ⏱ | ✓ 346 s | ⏱ | ✓ 348 s |
| B_mac_u tree_pre | ✓ 9 s | ✓ 12 s | ✓ 37 s | ✓ 60 s | ✓ 188 s | – |
| B_dot2_u tree_pre | ✓ 29 s | ✓ 47 s | ✓ 119 s | ✓ 252 s | ⏱ | ✓ 308 s |

### Signed low-power Booth before ABC (`booth -lowpower`, no ABC)

| W | raw pre-ABC netlist | constant-folded copy | post-ABC (portfolio) | `&cec` pre ≡ post |
|---|---|---|---|---|
| 8 | ERROR (segfault) | ✓ | ⏱ | PASS (1.0 s) |
| 16 | ERROR (segfault) | ✓ | ⏱ | PASS (1.3 s) |
| 32 | ERROR (segfault) | ✓ 10 s | ⏱ | PASS (49.3 s) |

### Longer or uncontended reruns of TIMEOUT results

| stage | netlist | configuration | budget | outcome | TRACE time | cgroup peak MiB |
|---|---|---|---|---|---|---|
| calib | A_mul_u_w32 norm | `-idx -p -c` | 1800 s | TIMEOUT | – | 6282.2 |
| calib | B_dot2_u_w16 norm | `-dyn -p -c` | 1800 s | TIMEOUT | – | 1966.6 |
| long64 | B_mac_u_w64 norm_pre | `-dyn -p -c` | 3600 s | PASS | 348 s | 176.5 |
| long64 | B_dot2_u_w64 tree_pre | `-dyn -p -c` | 3600 s | PASS | 308 s | 288.2 |
| long | A_mul_u_w8 booth | `-dyn -p -c` | 1800 s | TIMEOUT | – | 628.9 |
| long | A_mul_s_w8 booth_lp | `-dyn -p -c` | 1800 s | TIMEOUT | – | 1608.1 |
| long | B_mac_s_w8 norm | `-idx -p -c` | 1800 s | PASS | 1092 s | 783.9 |
| long | MUT_accum_mac_u_w8 tree | `-dyn -p -c` | 900 s | TIMEOUT | – | 626.4 |
| long | MUT_signext_mac_s_w8 norm | `-dyn -p -c` | 900 s | TIMEOUT | – | 225.8 |
| long | MUT_trunc_mul_u_w8 norm | `-idx -p -c` | 900 s | TIMEOUT | – | 926.7 |

### Class totals per stage (`RESULTS.csv`)

| stage | PASS | FAIL | FALSE_FAIL | FALSE_FAIL? | FALSE_PASS | TIMEOUT | UNSUPPORTED | ERROR | UNKNOWN | runs |
|---|---|---|---|---|---|---|---|---|---|---|
| abcmap | 0 | 0 | 0 | 0 | 0 | 40 | 0 | 0 | 0 | 40 |
| baseline | 17 | 6 | 0 | 0 | 0 | 5 | 1 | 0 | 0 | 29 |
| calib | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 2 |
| contra | 27 | 0 | 3 | 0 | 0 | 12 | 0 | 0 | 0 | 42 |
| ctrlcrash | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 5 |
| ctx | 149 | 0 | 67 | 0 | 0 | 4 | 0 | 0 | 0 | 220 |
| diag1 | 4 | 0 | 1 | 0 | 0 | 4 | 0 | 1 | 0 | 10 |
| dotspec | 3 | 1 | 1 | 0 | 0 | 2 | 0 | 0 | 0 | 7 |
| isolation | 46 | 0 | 0 | 0 | 0 | 23 | 0 | 6 | 0 | 75 |
| long | 1 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 6 |
| long64 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| mini | 43 | 74 | 4 | 0 | 5 | 6 | 0 | 0 | 0 | 132 |
| phaseopt_probe | 19 | 44 | 0 | 0 | 4 | 5 | 0 | 0 | 0 | 72 |
| portfolio_w32 | 70 | 56 | 2 | 0 | 0 | 280 | 0 | 0 | 0 | 408 |
| repro | 1 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 4 |
| stage1 | 1 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 3 |
| stage2_pre | 18 | 3 | 0 | 0 | 0 | 21 | 0 | 0 | 0 | 42 |
| sweep | 71 | 0 | 0 | 0 | 0 | 33 | 0 | 0 | 0 | 104 |
| unsupported_probe | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 5 |
| w64post | 3 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 6 |
| **all** | 477 | 185 | 79 | 0 | 10 | 447 | 6 | 10 | 0 | 1214 |

