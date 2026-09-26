# Prior-art prosecution of the exact residuals

This is not a broad literature review. Each section takes one failure mechanism that the experiments actually established (see `INVESTIGATION_REPORT.md` and `RESULTS.csv`). It asks one question: *does an existing method already explain or solve this exact failure, even if TRACE does not?*

Evidence labels:
- **[OBSERVED]** means measured in this folder.
- **[PAPER]** means stated in the cited paper, read at abstract, HTML or summary level; the full PDF could not be parsed on this host.
- **[NOT VERIFIED]** means a claim I could not check.

The absence of a matching paper title is never used as evidence of novelty.

## R1 — TRACE fails on many post-ABC Yosys netlists, even though the same designs verify before ABC

**Observed mechanism [OBSERVED]**

The default `synth` runs ABC. The post-ABC netlists on which TRACE times out under the six-configuration portfolio are:
- unsigned Bewick Booth at W = 8, 9, 10 and 12 (it passes at 4–7, 11 and 13–64; 260 s at W = 64);
- signed low-power Booth at every W ≥ 7;
- the unsigned default multiplier at W ≥ 20;
- unsigned default and tree MACs at W ≥ 24 and at W = 64 respectively;
- unsigned dot products at W ≥ 12 (default) or W ≥ 16 (tree).

The same designs before ABC (`synth -noabc`) all verify up to W = 64 with the paper's best configuration. The difficulty is not monotone in width, so it is not a scaling law.

**Isolating the ABC pass responsible**

One ABC step was applied at a time to the pre-ABC netlist (`netlists/ABCSTEP/`, `scripts/abc_steps.sh`).
- **Do not break TRACE:** `strash`, `balance`, `rewrite`, `dc2`, `resyn2`; `refactor` passes under at least one configuration.
- **Break TRACE:**
  - `&dch -f` (structural choices) alone, on both Booth multipliers;
  - `fraig` (SAT sweeping) alone, on the low-power Booth;
  - Yosys's full ABC script without mapping (`&fraig -x; scorr; dc2; dretime; &dch -f`), on the dot product too.
- **Technology mapping is irrelevant.** We mapped with four gate libraries through replicas that are byte-identical to the real post-ABC netlists; all behave the same.
- **Growth pattern.** On the post-ABC 8-bit Booth, the polynomial grows from 80 to 34,309 monomials by step 201 of 601. The pre-ABC run peaks at 179. This is the "blurred adder boundary / vanishing monomial" blow-up that the SCA literature attributes to logic-optimised multipliers.

**Not the cause:** Booth recoding, Baugh–Wooley corrections, Brent–Kung/CLA final adders, compressor trees, FMA fusion or signedness. All of them verify before ABC at every width.

**Strongest prior art**

| Work | What it does for this mechanism |
|---|---|
| DyPoSub — Mahzoon, Große, Scholl, Drechsler, *Towards Formal Verification of Optimized and Industrial Multipliers*, DATE 2020 | Dynamic polynomial substitution aimed specifically at optimized multipliers [PAPER]. |
| RevSCA-2.0 — Mahzoon, Große, Drechsler, IEEE TCAD 2022 | Reverse engineering plus local vanishing removal for "non-trivial" multipliers, including Booth [PAPER]. It is a binary-only tool with no license, so it was not run. |
| Konrad & Scholl, *Symbolic Computer Algebra for Multipliers Revisited – It's All About Orders and Phases*, FMCAD 2024 (FMSD 2026 journal version); FastPoly, FMCAD 2025 | Dynamic order and phase optimization, "DynPhaseOrderOpt" [PAPER]. TRACE's `-dyn -p` configurations are this family of techniques. |
| RefSCAT — R. Li, L. Li, H. Yu, M. Fujita, W. Jiang, Y. Ha, *Formal Verification of Logic-Optimized Multipliers via Automated Reference Multiplier Generation and SCA-SAT Synergy*, IEEE TCAD 44(2), 2024/25 | Builds a structurally similar reference multiplier with clear adder boundaries. SCA proves the reference and SAT proves optimized ≡ reference. Verifies logic-optimized multipliers up to 128 bits [PAPER]. |
| ReVEAL — C. Chen, D. Kaufmann, C. Deng, Z. Song, H. Zhang, C. Yu, TACAS 2026 (arXiv 2512.22260) | GNN-guided reverse engineering for Booth and simple partial-product generators, several reduction trees and nine final adders, after ABC `dc2` and `resyn3`. Evaluated at 64/128/256 bits against AMulet2, RevSCA-2.0, DynPhaseOrderOpt and RefSCAT [PAPER]. It explicitly does not address MAC units or complex datapaths [PAPER]. |
| Arisca — Li, Li, Xu, arXiv 2607.10257 (2026) | Table 3 on 310 multipliers (original / `resyn3` / `dc2`): Arisca 310/277/222, DynPOO 299/272/222, AMulet 243/23/7, RevSCA 245/216/170 [PAPER]. The code was not released ("repository_not_ready"). |

**Does prior art explain or solve the failure?**

- **Explains: yes.** The failing netlists are logic-optimised multipliers, the class these papers define and attack.
  - The published benchmark sets optimise with `resyn3` and `dc2` (Konrad & Scholl; Arisca; ReVEAL's extended sequence adds `mfs`/`resub`/`resyn*`) [PAPER]. None uses `&dch`.
  - `dc2`/`resyn2`-optimised Yosys Booth netlists stay verifiable by TRACE [OBSERVED]. The culprits here, `&dch` and `fraig`, are Yosys's default ABC passes and are outside those benchmark sets.
  - Whether the dedicated engines (AMulet2, RevSCA-2.0, DynPOO, RefSCAT, ReVEAL) handle `&dch`/`fraig`-restructured Booth multipliers *without a reference* is **[NOT VERIFIED]**. AMulet2 would need a new download; the others are not runnable.
- **Solves, for Yosys: yes, with existing tools.** RefSCAT's decomposition is *SCA on an unoptimised reference, then SAT/CEC for optimised ≡ reference*. In a Yosys flow the reference is free: the pre-ABC netlist of the same run, with the same port order. This folder executed that decomposition [OBSERVED]:
  - TRACE (`-dyn -p -c`) proves every pre-ABC netlist up to W = 64:
    - default multipliers: 152 s signed, 264 s unsigned;
    - Booth: 467 s signed, 294 s unsigned after constant folding; low-power Booth to W = 32 after folding;
    - MAC trees: 188 s unsigned, 217 s patched signed;
    - default MAC: 348 s;
    - dot tree: 308 s.

    The last two passed uncontended; they had timed out at 900 s while 10 containers shared 8 CPUs.
  - ABC `&cec` proves pre ≡ post for all 29 tested pairs up to W = 64 (0.2–662 s, `evidence/cec_pre_post.csv`).
  - A SAT sweeper on two netlists of one lineage is not the hard multiplier-equivalence problem. The S1 time-outs were **architecture-to-architecture** comparisons.
- **Residual:** integration, not science. Wiring "TRACE (or AMulet/DynPOO) on `-noabc`, then `&cec` across ABC" into a Yosys verification script needs no new theory. The only reference-free question left is the benchmark-coverage question above. It is an efficacy question in an occupied area, it has the RefSCAT/ReVEAL line as its established approach, and Yosys users do not need it.

## R2 — TRACE phase optimisation is unsound on the Yosys pattern `XOR(AND(p, ¬x), XNOR(x, x))`

**Observed mechanism [OBSERVED]**

The PR #6231-patched `arith_tree` emits `XNOR(c_msb, c_msb)` before ABC for signed MACs at W = 3, 4, 8 and 16, and for `dot2c` at W = 8, 16 and 32. It is built as `NOR(AND(¬x, x), AND(¬x, x))`, a duplicated pair of contradictory AND gates, and XORed with `AND(p, ¬x)`.

Under `-p` (phase optimisation), TRACE's remainder is off by exactly ±2^k·x, where 2^k is the arithmetic weight of the signal. This happens in all four `-p` configurations at W = 8 and in at least one at W = 3, 4 and 16, depending on the traversal; it never happens without `-p`.
- **FALSE_FAIL** on the correct patched netlists. The remainder `-65536 + 65536·i64` is non-zero at points where the netlist matches the reference, under both readings of the undocumented `iK` variable.
- **FALSE_PASS** on mutants whose true error is exactly that term:
  - `y = a*b + zext(c)` (a zero-extended signed addend) is certified "Correct" at W = 3, 4 and 8.
  - The oracle proves it wrong, exhaustively at W = 3 and 4.

Causal controls:
- Removing the pattern by constant folding makes every configuration correct and makes every mutant `Buggy`.
- Grafting the same six-gate context into unrelated correct netlists reproduces spurious remainders of the form 2^k·x. Examples: `2048·n10`, `4·(i38 − 1)`. This happens under `-p` only; `-dyn -c` never produces one (`evidence/trace_ctx_results.csv`).
- Inserting `AND(x, ¬x)` or `XNOR(x, x)` alone, at an output, does **not** trigger it.

**Strongest prior art**

| Work | Relevance |
|---|---|
| Konrad & Scholl, FMCAD 2024 / FMSD 2026 | Phase optimization is defined as replacing a signal by its complemented phase during backward rewriting [PAPER]. As an exact substitution `s = 1 − s̄`, it preserves the ideal, so a correct implementation cannot change the verdict. |
| Kaufmann, Beame, Biere, Nordström, *Adding Dual Variables to Algebraic Reasoning for Gate-Level Multiplier Verification*, DATE 2022 | Introduces dual (negated) variables into the algebraic encoding of AIGs, "together with a novel tail substitution and carry rewriting", yielding "a single, uniform proof certificate" [PAPER]. The dual relation is part of the ideal, so `x·x̄` vanishes soundly. |
| Kaufmann, Fleury, Biere, Kauers, *Practical algebraic calculus and Nullstellensatz with the checkers Pacheck and Pastèque and Nuss-Checker*, FMSD 2022 | Certificate formats (PAC/LPAC) and independent checkers for exactly this kind of algebraic circuit proof. Pastèque is verified in Isabelle/HOL [PAPER]. AMulet 2 (Kaufmann & Biere, TACAS 2021) emits such certificates [PAPER]. |
| Temel, Slobodová, Hunt, *Automated and Scalable Verification of Integer Multipliers*, CAV 2020 | A rewriter whose soundness is proven in ACL2. It handles signed/unsigned and Booth designs, but relies on design hierarchy [PAPER]. |

**Does prior art explain or solve the failure?**

Yes, fully.
- The failure is an implementation defect in TRACE's phase handling of a degenerate but legal AIG construct. The algebra is sound when phases are handled as exact substitutions or dual variables.
- Any certificate-producing engine (PAC) would have exposed it: a certificate for the false-pass mutant cannot be checked, because the mutant is not in the ideal.
- A one-line preprocessing step removes the trigger: structural hashing or constant folding, or ABC `strash`, which every post-ABC netlist has already been through.
- **Residual:** repair (fix TRACE's `-p`, or fold the input) and emit certificates. There is no scientific obligation. It is nevertheless the most consequential practical finding of this investigation. Anyone who uses TRACE's recommended configuration to check pre-ABC Yosys output, which is precisely the stage-wise flow of R1, must fold or strash first or disable `-p`.
- The TRACE repository (commit `d57aa9a7`, 2026-04-13, the latest) has no issues or later commits, so the defect appears unreported [OBSERVED 2026-09-24].

## R3 — Segmentation fault on AND gates with a constant fan-in

**Observed [OBSERVED]**

- Yosys's pre-ABC Booth netlists leave one `AND(x, TRUE)` gate: `synth -booth -noabc` for **unsigned** operands at W = 8, 16, 32 and 64, and `booth -lowpower` for **signed** operands at W = 8, 16 and 32.
- TRACE crashes with signal 11 in about 0.01 s.
- Inserting one such buffer into a passing netlist reproduces the crash. Folding removes it, and the folded netlists verify: unsigned W = 8 in 1 s and W = 64 in 294 s; low-power W = 8..32 in 1–15 s.

**Prior art:** none needed. This is an input-robustness bug; AIGER explicitly allows constant fan-ins. **Residual:** repair.

## R4 — `-igsm` false `Buggy` with an unsubstituted internal variable

**Observed [OBSERVED]**

- On the correct 8-bit signed conventional multiplier (exhaustively verified), `-igsm -p -c` returns the remainder `-4n2n4n18n20 + 4n4n20n34`.
- `n34` is an internal AND node, `a0∧b0`, and the remainder is identically 0 over all 65,536 inputs.
- `-idx` and `-ipc` prove the same netlist Correct.

**Prior art:** backward rewriting is complete only when the final remainder is over primary inputs alone. This is standard in every SCA paper, including TRACE's own description. A remainder that still contains a gate variable indicates an incomplete substitution, i.e. a traversal-order implementation bug. **Residual:** repair.

## R5 — `-dot` ignores `-s`

**Observed [OBSERVED]**

- The DOT remainder is identical with and without `-s`, and equals the unsigned reading of a correct signed netlist.
- Every signed `dot2` therefore gets a false `Buggy`.
- DOT mode is documented only in the README; the paper does not evaluate it.

**Prior art:** signed dot products are a routine SCA specification:
- Bremen *Towards Efficient Formal Verification of Dot Product…*, DATE 2025;
- Arisca's dot-product specifications [PAPER].

**Residual:** a missing or incorrect feature. Repair.

## R6 — Template restrictions: `c − a*b`, accumulators wider than 2W+1, `a*b + c*d + e`

**Observed [OBSERVED]**

- TRACE accepts only fixed templates: add, mul, MAC `F(2n+1) = A(n)·B(n) + S(2n)`, dot, and gen.
- Run in the nearest template:
  - `c − a*b` → `Buggy`, correctly by the template but UNSUPPORTED by intent;
  - `dot2c` → `Buggy`;
  - wide accumulators → TIMEOUT.

**Prior art:**
- In SCA, the specification is just a polynomial over the output and input bits. Any integer-linear-plus-product specification (`c − a·b`, sign-extended accumulators of any width, sums of products plus an addend) is expressed the same way as the built-in templates.
- Arisca exposes this directly (`--spec [4]*[3]+[7]`, MAC with a 128-bit addend, signed truncated multipliers) [PAPER].
- The Bremen MAC line covers MAC architectures across widths from 8 to several hundred bits, and transformation-aided MAC verification:
  - ForMAt, FDL 2025;
  - *Formally Verifying Multiply-and-Accumulate Architectures Using SCA*, SN Computer Science 2026;
  - *Transformation-Aided Verification of MAC Designs using SCA*, DVCon 2025

  [PAPER].
- Arithmetic lowering of these forms by Yosys already verifies once the spec is right. The unpatched netlists fail on the *real* defect, and the patched ones prove Correct in the MAC template wherever the template fits.

**Residual:** a command-line feature (a user-supplied specification polynomial). Engineering.

## R7 — SCA refutation of wrong designs times out

**Observed [OBSERVED]**

- Incorrect 8-bit designs time out (60 s) under every configuration. Longer budgets are in `evidence/trace_long_results.csv`. The designs are:
  - carry-out dropped from the accumulator;
  - signed product zero-extended into the accumulator;
  - product truncated to 2W−1 bits.
- The independent random-simulation oracle finds counterexamples for all of them in under a second.

**Prior art:** it is well known that remainders explode on buggy circuits, and that simulation or SAT is the standard complement for bug finding. SCA debugging work in the Bremen line exists [PAPER, summary level]. **Residual:** none. A verification flow runs simulation first, and a TIMEOUT is never counted as a pass here.

## R8 — Configuration sensitivity (`-dyn` versus `-idx`)

**Observed [OBSERVED]**

- `-dyn` stalls on Yosys conventional multipliers. The polynomial stays flat at 81 monomials while substitution makes almost no progress.
- `-idx` proves the same netlists in 1–24 s.

**Prior art:** the whole point of DynPhaseOrderOpt, and of portfolios, is that order and phase choices dominate SCA cost. **Residual:** use a portfolio, as this investigation did. Engineering.

## Summary table

| # | Mechanism | Real limitation of the **method**? | Prior art that explains or solves it | Residual |
|---|---|---|---|---|
| R1 | Post-ABC (logic-optimized) netlists | Known hard class, not Yosys-specific | DyPoSub, RevSCA-2.0, DynPOO, RefSCAT, ReVEAL, Arisca; stage-wise SCA+CEC executed here | Integration |
| R2 | `-p` unsound on the `XNOR(x,x)` pattern | No (implementation) | Exact phase substitution; dual variables; PAC certificates | Repair (+ certificates) |
| R3 | Crash on constant fan-in | No (implementation) | – | Repair |
| R4 | `-igsm` incomplete substitution | No (implementation) | Standard completeness condition | Repair |
| R5 | DOT ignores `-s` | No (feature bug) | Bremen DATE'25, Arisca | Repair |
| R6 | Fixed templates | No (missing feature) | Arisca user spec; Bremen MAC line | Feature |
| R7 | Slow refutation | No (known property) | Simulation/SAT complement | None |
| R8 | Order/phase sensitivity | No (known property) | DynPhaseOrderOpt; portfolios | None |

No residual survives as a scientific obligation that the strongest prior art leaves open.

## Sources

- TRACE: https://arxiv.org/abs/2608.16458 and https://github.com/jan-kl/trace (commits and issues checked 2026-09-24)
- Arisca: https://arxiv.org/abs/2607.10257
- Konrad & Scholl FMCAD 2024: https://repositum.tuwien.at/handle/20.500.12708/200799 ; FMSD 2026: https://link.springer.com/article/10.1007/s10703-026-00494-9 ; FastPoly FMCAD 2025: https://repositum.tuwien.at/handle/20.500.12708/219550
- RefSCAT: https://ieeexplore.ieee.org/document/10634894/ (authors per https://unnc.globalimpact.cn/en/publications/refscat-formal-verification-of-logic-optimized-multipliers-via-au)
- ReVEAL: https://arxiv.org/abs/2512.22260 (HTML full text read)
- Dual variables (DATE 2022): https://par.nsf.gov/biblio/10342985-adding-dual-variables-algebraic-reasoning-gate-level-multiplier-verification
- PAC checkers (FMSD 2022): https://link.springer.com/article/10.1007/s10703-022-00391-x ; https://github.com/d-kfmnn/pacheck
- AMulet2 improvements (STTT): https://link.springer.com/article/10.1007/s10009-022-00688-6
- Temel, Slobodová, Hunt CAV 2020: https://pmc.ncbi.nlm.nih.gov/articles/PMC7363191/
- RevSCA-2.0: https://www.researchgate.net/publication/351856099
- Bremen MAC/dot-product line: https://agra.informatik.uni-bremen.de/doc/konf/DVCon2025_LW.pdf ; https://agra.informatik.uni-bremen.de/doc/konf/DATE2025_LW.pdf ; https://agra.informatik.uni-bremen.de/doc/konf/FDL2025_LW.pdf ; https://link.springer.com/article/10.1007/s42979-026-04859-z
