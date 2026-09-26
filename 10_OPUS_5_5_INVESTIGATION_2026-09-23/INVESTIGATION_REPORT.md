# Frontier Semiconductor/EDA Investigation: Unoccupied-Mechanism Search

**Date:** 2026-09-23.
**Investigator:** Claude (Opus 5.5). Single-threaded: no subagents, as you instructed. The Part XI roles (literature, prior-art prosecutor, artifact, significance, experiment) were run sequentially, and their disagreements are recorded in §C–§E.

**Evidence labels**

| Label | Meaning |
|---|---|
| OBSERVED | Retrieved page, inspected source code, or an experiment executed in this session. |
| INFERRED | A reasoned interpretation of evidence. |
| UNVERIFIED | Plausible but not independently established. |
| [summary-level] | The source was seen only through a search-engine abstract or summary, not read in full. Decisive claims below never rest on these alone. |

---

## 0. Bottom line

1. **Zero candidates survive at the bar you set:** a genuine unresolved scientific boundary plus a distinct mechanism, feasible with open tools.
   About 45 probes (24 recorded in §B) across formal verification, synthesis, security, architecture, arithmetic/numerics, HLS, compiler IR, physical/silicon and LLM-for-RTL all hit active 2025–2026 prior art or reduced to implementation work.
   Details in §B.
2. **The strongest candidate was prosecuted with experiments, not only literature**, and died.
   The candidate: open-source flows cannot certify Yosys arithmetic lowering at production widths, and a checked "synthesis guidance" contract (an open analogue of Synopsys SVF) would fix that.
   - I confirmed the gap in the bundled open engines (OBSERVED; experiment folder `experiments/S1_open_datapath_verification_killshot/`).
   - Then I found **TRACE** (arXiv 2608.16458, Aug 17 2026, open binary), which already targets adders, multipliers and MACs, including Yosys/ABC-synthesized behavioral designs.
   - It is killed as research (occupied). Only integration work and an **untested** coverage question about Yosys-specific structures remain.
3. **Two new engineering findings** came out of those experiments (OBSERVED; neither is a research contribution):
   - (a) ABC's arithmetic equivalence checker `&acec` returns **spurious NOT-EQUIVALENT verdicts with invalid counterexamples** on correct Yosys-generated arithmetic. Its source zeroes the last two outputs and secondary adder-tree roots, and never replays counterexamples on the original networks.
   - (b) In the open flow, verifying ABC's optimization step is trivial (0.2–0.3 s). The arithmetic **lowering** step is where every bundled engine fails.
4. **Separate evidence track (OBSERVED):** your Yosys PR #6231 got its first maintainer review today.
   - Reviewer `hexratcc` is open to accepting it as a case-by-case LLM-policy exception.
   - They requested four changes, including a test for the negated-product variant `c - a*b`.
   - Another auditor (`Expert-Momonga`) opened two peepopt soundness issues (#6241, #6242) in the same bug family **today**.
5. **Methodology diagnosis (§E):** the main cause of repeated failure is a **miscalibrated target**, not insufficient search.
   - Your bar is stricter than what the field rewards. The DAC 2026 best paper is a composition of known techniques backed by strong evidence.
   - The named seams you mined are being occupied faster than your discover-to-kill cycle runs.
   - Every real finding in your history, and in this session, came from **executing tools**. None came from reading future-work sections.
6. **Exactly one next action (§F):** run TRACE as a black-box oracle, in Docker, on Yosys-specific lowering families at W=8–64 with fail-closed controls. It decides whether any research boundary remains in the only line where you hold a real asset.

---

## Evidence boundary of the inputs

- **Waves 8 and 9:** the reports are not in the package (`02_WAVE_8/RECOVERY_NOTE.md`, `03_WAVE_9/RECOVERY_NOTE.md`). I did not reconstruct them.
- **Wave 7 D1 (OBSERVED, not in the package):** recovered from WSL `~/wave7d1/KNOWN_FRONTIER.md` and `experiment_notes.md`.
  - Target: Dynamatic issue #471 (LSQ termination).
  - Result: `ISSUE_COMMIT_NATIVE_FLOW_ENFORCES_OBLIGATION`. The native one-LSQ flow ran to completion and properties P1–P5 passed. No bug was claimed.
  - AXI and multi-LSQ configurations were explicitly not tested.
  - Added to the exclusion set.
- **Search-summary caution:** one search summary asserted a silicon ring-oscillator measurement ("measured 15 MHz") that the fetched page did not contain. That is why decisive claims below rest on fetched pages, source code or executed runs.

---

## A. Research landscape reconstruction

### A.1 Method reconstructions (method → assumptions → guarantee → strongest follow-up → current boundary)

| Method | Key assumptions | Actual guarantee | Strongest follow-up (2025–26) | Current boundary |
|---|---|---|---|---|
| **SAT-sweeping CEC** (ABC `&cec`) | The two designs share many internal equivalences (structural similarity) | Sound and complete within its time budget | Miter-Aware LUT Mapping (DAC'26 best paper, arXiv 2607.07164; baselines include ABC `cec`; up to 92.1% PAR2 reduction; LUT size ≤4; code not public) [OBSERVED from fetched paper]. FORWORD, word-level sweeping (DATE'26) [per archive] | Architecture-changing arithmetic lowering. **OBSERVED:** `&cec` times out (300 s) at W=16 for Yosys booth-vs-array, arith_tree MAC and dot-product pairs; the same pairs pass in about 8–10 s at W=8 |
| **Structural reverse-engineering arithmetic CEC** (ABC `&acec`, 2017) | Adder trees can be extracted and matched on both sides; normalization preserves function | *Intended* to be sound | None; `acecCore.c` last changed substantively Jan 2017 [OBSERVED via GitHub API] | **OBSERVED:** spurious disproofs on correct Yosys MAC (W8) and multiplier (W16) pairs; counterexamples not replayed; the code zeroes the last two outputs and secondary roots (§D.6) |
| **Algebraic backward rewriting** (ABC `&polyn`; AMulet 2; RevSCA; DynPhaseOrderOpt) | Circuit contains atomic adder blocks; needs special handling for parallel-prefix adders and Booth encoding | Exact, and certifiable (PAC/Nullstellensatz proofs in AMulet 2) [summary-level] | **TRACE** (arXiv 2608.16458, Kleinekathöfer/Weingarten/Datta/Drechsler, 2026-08-17): adders, multipliers, MACs, incl. Yosys/ABC-synthesized designs; paper-stated limits: some 32/64-bit structural multipliers and behavioral MACs above 64 bit unverified [OBSERVED from fetched paper summary]. Bremen MAC/dot-product line: DVCon'25, DATE'25, ForMAt'25, SN CS'26 [summary-level]. ACL2 RTL books: compression trees reduce to a repeated add-3 lemma (arXiv 2507.19010) [summary-level] | **OBSERVED:** ABC `&polyn` is exponential on Yosys netlists (array 67 s at W12, timeout at W16; Booth times out from W6). Whether TRACE covers Yosys-specific structures is **untested** |
| **Guided LEC** (Synopsys Formality + SVF) | The synthesis tool emits guidance (`guide_multiplier`, `guide_tree`, …) and the checker validates it | Vendor claims every guidance item is "implicitly or explicitly verified" [summary-level] | Proprietary | No open analogue found for Yosys/EQY (INFERRED from EQY docs and searches; absence is not proof) |
| **Leakage-contract verification** (LeaVe → LeaSyn, CSL, VeloCT/H-Houdini, SecIC3) | ISA-level contract template; RVFI; relational invariants | Unbounded contract satisfaction when the prover succeeds | LeaSyn (arXiv 2509.06509): test-case dependency §4.3, template expressiveness §2.4, needs RVFI [OBSERVED]. VeloCT scales to BOOM (6.95–199.1 min) [summary-level]. SecIC3 (arXiv 2601.21353) IC3 for self-composition [OBSERVED]. Guarded equivalence predicates (arXiv 2606.22063); deductive system for contract proofs (PACMPL 2026) [summary-level] | Dense, fast-moving; no evidence-backed unoccupied boundary found |
| **Algorithm-to-netlist equivalence** (EquivFusion, arXiv 2604.16571, CUHK, 2026-04-21) | Polygeist affine loops; static bounds; integers only | Combinational, plus "transactional" equivalence via unrolling | Its own future work: solver orchestration, floating point, Hector-style lemmas [OBSERVED] | Control-dominated designs and floating point out of scope. Actively being extended by its authors |
| **Verified peephole rewriting** (Lean-MLIR arXiv 2407.03685; verification dialects PACMPL 2025; ParaBit CAV'26; multi-width OOPSLA'26) | Rewrites expressed declaratively; formal IR semantics | For-all-widths soundness of rewrite rules | Same groups [archive + summary-level] | Yosys `pmgen`/C++ passes are not declarative, so the gap is application. An independent auditor is filing peepopt bugs today (#6241/#6242) [OBSERVED] |
| **AI matrix-unit numerics** (MX, NVFP4, tensor cores) | OCP MX leaves dot-product internal precision and ordering implementation-defined [summary-level] | None; behavior is vendor-specific | Khattak & Mikaitis, "Accurate Models of NVIDIA Tensor Cores" (TACO 2026); AMD matrix cores (arXiv 2609.14845); P3109 (arXiv 2606.04028); FLoPS (Lean) [summary-level] | Characterization and standardization are occupied by the ARITH/numerics community |

### A.2 Patterns that connect the communities (INFERRED from A.1 and §B)

1. **Trust infrastructure is the 2025–26 center of gravity.**
   Examples: certificates for model checking (Certifaiger/Cerbtora per archive), Certified Sequential Sweep, Lean bit-vector solving without bit-blasting, and verified real-time proof checking (all FMCAD'26 [OBSERVED titles]), plus PAC proofs.
   The open *synthesis* stack has not absorbed this for arithmetic. Its only arithmetic-aware checker (`&acec`) is unsound (OBSERVED).
2. **Arithmetic is the recurring hard core across communities.**
   LEC (DAC'26 best paper), algebraic verification (TRACE), numerics (MX/P3109), synthesis (Yosys `booth`/`arith_tree`, CIRCT `datapath`) and synthesis bugs (your #6231; #6241/#6242) all meet at arithmetic.
   Arithmetic structure breaks generic methods, and each community is building its own specialized tool.
3. **MLIR/CIRCT convergence.**
   EquivFusion, Lean-MLIR, K-CIRCT, and HEIR's reuse of Yosys for FHE circuits (BOLT eprint 2026/153, AutoHoG) [summary-level].
4. **Agentic commoditization of engineering seams.**
   - YosysHQ's interim LLM policy (posted 2026-08-31, per `PR_6231_OWNERSHIP_REVIEW.md` in your archive).
   - Same-day peepopt audits (#6241, #6242).
   - Agent-driven repositories with thousands of self-filed issues (e.g., `2AMLogic/klayout-tools`) [OBSERVED].
   - Bug-finding and tool-gap filling in open EDA is becoming cheap and crowded.
5. **Security models are moving toward physical grounding, owned by specialist groups.**
   Coupling leakage after place-and-route in masked FPGA designs (Müller, Lammers, Osterheider, Moradi, eprint 2026/1426 [OBSERVED abstract]); PRAC model checking (AutoPRAC, arXiv 2606.23905 [summary-level]).
6. **Open silicon produces chips but not measurement data.**
   Tiny Tapeout lists 337 silicon-proven projects with pass/fail only. Ring-oscillator and cell-timing project pages publish no measured numbers [OBSERVED].
   A systematic comparison of open-flow signoff timing against silicon was not found.

---

## B. Research opportunity register

Classifications follow Part VI. "Archive" means it was already in your exclusion set.

| # | Candidate | Strategy | Source evidence | Strongest prior art | Remaining question | Artifacts | Classification / decision |
|---|---|---|---|---|---|---|---|
| 1 | Open checked datapath guidance / certification for Yosys arithmetic lowering (**S1**) | G, D | OBSERVED: bundled engines fail at W≥16 (§D) | TRACE (2608.16458); Bremen MAC/dot-product line; AMulet 2; ACL2 RTL books; Formality SVF | Does TRACE cover Yosys radix-4 `booth`, fused `arith_tree` with Baugh–Wooley constants, and Y_WIDTH > A+B? | Yosys, ABC, TRACE binary | **Occupied by prior art**; residual = implementation debt plus one untested coverage question → §F |
| 2 | ABC `&acec` unsound verdicts | D | OBSERVED (§D.6) | n/a | Fix: replay counterexamples; do not drop outputs | ABC `acecCore.c`, `acecNorm.c` | **Implementation defect** (engineering track) |
| 3 | Width/port-interpretation soundness family in Yosys (#6231 FMA, #6241 shiftadd, #6242 muldiv; #6199 was closed as invalid and is not counted) | F | OBSERVED issues | Alive / Alive2; Lean-MLIR; ParaBit; multi-width OOPSLA'26; K-CIRCT; Yosys `test_cell` | Real shared obligation: operand interpretation belongs to the consuming port and to the IR's own edge semantics | Yosys | **Known principle + new implementation**; crowded by a same-day independent auditor |
| 4 | "Alive for RTLIL" (all-width rewrite verification) | C | Same as #3 | Same as #3 | Extracting C++/pmgen rewrites into declarative form | Yosys | **Occupied principle**; implementation |
| 5 | Width-generic certification of arithmetic generators | G | FMA bug escaped 13 tests | ACL2 RTL books; Kapur/Subramaniam parametric proofs; CircuitProver lists "parameterized families" as future work | For-all-widths proof of Yosys `CompressorTree` | Yosys, Lean | **Occupied principle**; contested |
| 6 | Parameter-complete verification of parameterized IP (cutoffs over widths/depths) | C | Practice: parameter sweeps plus BMC | Data independence; WS1S/automatic structures; BITS / Bjesse width reduction; CircuitProver future work | Cutoffs for non-uniform generators (e.g., Wallace trees) | SV IP libraries | **Occupied theory**; residual has low consequence |
| 7 | Leakage-contract verification scaling | A, C | LeaSyn, SecIC3 fetched | VeloCT/H-Houdini; CSL; guarded equivalence predicates; deductive system for contract proofs | No specific boundary with evidence | LeaVe etc. | **Active and crowded**; no boundary |
| 8 | Coupling-aware masking verification after place-and-route | C | eprint 2026/1426 | Same paper (PROLEAD extension) | n/a | PROLEAD | **Occupied** (Jul 2026) |
| 9 | PRAC Rowhammer verification | A | AutoPRAC | AutoPRAC; QPRAC; CnC-PRAC | n/a | Ramulator | **Occupied** |
| 10 | Memory-consistency compliance of open out-of-order cores | A | HartBreaker; χRVFormal | Same | n/a | cores | **Occupied** |
| 11 | MX / low-precision dot-product semantics and verification | C | Spec latitude | Khattak & Mikaitis; AMD models; P3109 / FLoPS / FloatLib; MXDOTP, VMXDOTP, Ten-Four | Hardware semantics that are both reproducible and cheap | open RTL | **Occupied characterization**; residual is known principle (Kulisch/quire) + application |
| 12 | FHE-aware logic synthesis (linear-sum → LUT) | E (cross-community) | HEIR uses Yosys | BOLT; AutoHoG; PACMPL'25 arithmetic table lookups; TCHES FBS mapping; Scytale | n/a | HEIR | **Occupied** |
| 13 | Open C-to-RTL / transactional equivalence | A | EquivFusion | EquivFusion; commercial DPV/SLEC | Floating point, control-heavy designs | EquivFusion | **Being occupied** by its authors |
| 14 | LEC speedups via miter restructuring (reproduction vs `&cec`) | B | DAC'26 paper | Same | Does the advantage hold against `&cec` (paper used `cec`)? | code not public | **Insufficient evidence**; not reproducible |
| 15 | Validity of LLM-for-RTL benchmarks (simulation pass vs formal) | B, C | RealBench [summary-level] | RealBench; synthesis-in-the-loop evaluation (arXiv 2603.11287) | n/a | benchmarks | **Occupied** |
| 16 | Verdict integrity of agentic EDA pipelines (exit-code-as-verdict etc.) | C | Your Exp. 2/3 mislabels | SBY/EQY structured statuses; AgentDV-type work [summary-level] | Measurement study | open repos | **Weak** (methodology, not EDA science) |
| 17 | Undefined behavior (e.g., `nsw`) exploited by LLVM-based HLS | C | No study found | Vericert assumes UB-free sources | Is there a hardware divergence on overflow? | Dynamatic (built in WSL) | **Low consequence** (HLS practice uses `ap_int`) |
| 18 | Open-flow signoff (liberty + OpenRCX + OpenSTA) vs measured silicon | new | No study found; TT pages carry no data [OBSERVED] | Foundry characterization (not public) | Size and source of model error | TT chips + demo board | **Insufficient evidence**; hardware-gated; continued consideration only |
| 19 | Open PDK DRC deck disagreement | B | Agent-repo issues | Community cross-validation | n/a | Magic, KLayout | **Engineering** |
| 20 | Real-design miscompilation prevalence (independent-frontend LEC) | B | TOSEM study: 46.2% of bugs are HDL non-compliance [summary-level] | Verismith, VeriXmith, TOSEM'25 | Measurement | open cores | **Weak novelty; high null risk** |
| 21 | SDC timing-exception verification | C | – | Commercial tools and patents | n/a | – | **Occupied** |
| 22 | PPA-Delta (your lead) | – | archive | PPR (FSE'23) | Real-provenance mini-study | archive | **Unchanged: REVISE** (not re-prosecuted) |
| 23 | Wave 7 D1: Dynamatic #471 LSQ termination | D | WSL notes | – | AXI / multi-LSQ untested | Dynamatic, Questa | **Closed: native flow enforces the obligation** |
| 24 | Yosys signed-FMA `arith_tree` defect | – | archive + PR | – | Negation variant, full test suite | PR #6231 | **Separate engineering track** (review received) |

Near-misses I considered and dropped without a row: stochastic-rounding verification (P3109), SFQ logic synthesis, RTL simulation acceleration, macro placement, and architecture-level mechanisms (ChampSim-class). Each was dropped either because it was clearly occupied or because it was off-mission for an evidence-first semiconductor/EDA contribution.

---

## C. Surviving research opportunities

**None.** No candidate has a precise, evidence-supported **scientific** boundary that is not already under active prosecution by an established group, or that is more than implementation work.

Two items stay under consideration below the survivor bar:

- **C-1 (untested residual of S1).**
  If TRACE fails on a structurally identifiable Yosys-generated class, that would be a documented limitation of the newest strongest method on a legitimate regime.
  Candidate classes: radix-4 `booth`, fused `arith_tree` trees with Baugh–Wooley corrections, and the `$macc` regime Y_WIDTH > A+B where your #6231 defect lived.
  This is the single thing worth testing next (§F).
- **C-2 (open-silicon timing correlation).**
  No systematic study was found, and it would produce knowledge that agents cannot generate without hardware.
  It fails the executability gate: it needs chips plus measurement, over weeks.
  It also has no evidence yet that the model error is large.

---

## D. Deep investigation: no survivor, so here is the anatomy of the closest miss (S1)

I include this because it is the one candidate prosecuted with **executed** evidence, and it shows the kill pattern precisely.

### D.1 The exact problem

Yosys lowers `$mul` / `$macc` into gates through default techmap (`$alu`/`$lcu`), `booth`, and `arith_tree` (compressor trees with fused products).
The question: can the open ecosystem certify that lowering at the widths real designs use (16–64 bits)?

### D.2 Why it matters

- `peepopt` and `wreduce` run by default in `synth` [OBSERVED in `techlibs/common/synth.cc`]. `booth` and `arith_tree` are opt-in.
- Your FMA defect escaped all 13 checked-in `arith_tree` tests.
- Arithmetic-heavy DSP/ML datapaths are exactly where open LEC is weakest.

### D.3 Strongest existing methods

- Industrial: Formality with SVF guidance.
- Research: algebraic verification with adder substitution and Booth handling (AMulet 2, RevSCA, DynPhaseOrderOpt, **TRACE**, the Bremen MAC/dot-product papers); ACL2 RTL books.
- Bundled with the open flow: ABC `&cec`, `cec`, `&acec`, `&polyn`.

### D.4 The limitation, measured in this session (OBSERVED; `experiments/S1_open_datapath_verification_killshot/`)

- **`&cec`:**
  - PASS in 8.3–10.0 s at W=8.
  - **TIMEOUT (300 s) at W=16, 24 and 32** for unsigned and signed booth-vs-array, MAC tree-vs-normal, and dot-product tree-vs-normal.
  - All mutants were disproved in 0.02–0.2 s at the correct output.
- **`&polyn`:**
  - Array multiplier (post-ABC): 0.2 s (W6), 0.3 s (W8), 6.8 s (W10), 67 s (W12), then timeout from W16.
  - Booth: timeout from W6.
  - At 4×4, Booth needs about 100× more intermediate terms (235,089 vs 2,291).
- **Stage-wise at W=8:**
  - Pre-ABC vs post-ABC `&cec`: **PASS in 0.2–0.3 s for all 9 configurations.** The optimization step is easy.
  - `&polyn` on pre-ABC netlists times out for MAC, dot-product and Booth, and takes 23–25 s for multipliers.
  - So the difficulty is **localized to arithmetic lowering**.
  - Hypothesis (INFERRED, untested): Yosys's lookahead-carry (`$lcu`) adders and radix-4 Booth encoding are what trigger the known backward-rewriting blow-up.

### D.5 The boundary as it stood before the kill

"No engine bundled with the open flow soundly certifies Yosys arithmetic lowering at W ≥ 16 within 300 s." This statement is precise and evidenced.

### D.6 Side finding: ABC `&acec` (OBSERVED)

- **On a correct pair** (mac_u W8, normal vs `arith_tree`): `&acec` reported NOT EQUIVALENT with input `32'h5CDE617B`.
  - `&cec` (10 s), `cec` (166 s) and a Yosys SAT miter against the RTL all prove equivalence.
  - Replaying the input under both bit orders gives identical outputs from both netlists, and both equal `a*b+c`.
- **16-bit multiplier with `-b`:** "Output 22 trivially differs" at `a=b=0`, where both originals output 0.
- **On mutants:** the reported disproofs hit outputs 2 or 6 regardless of which bit was mutated. The witnesses do not trigger the mutation.
- **Source:**
  - `Acec_Solve` patches the last two outputs of both normalized networks to 0.
  - `Acec_InsertBox` appends no auxiliary outputs.
  - It sets secondary root literals to 0.
  - The counterexample is swapped out of the normalized miter without replay.
- **Prediction not confirmed:** I predicted a false PASS on MSB-only mutants. It did not occur in these tests, because `&acec` failed for the unrelated normalization reason. The risk is theoretical, not demonstrated.

### D.7 What the contribution would have been

Yosys arithmetic passes would emit untrusted structural guidance: atomic adder blocks, row bookkeeping, correction constants, the final-adder boundary, and the `$macc` specification.
A small checker would verify each piece locally or algebraically, in linear time, and would replay every counterexample.
The whole pipeline would be chained stage-wise with `&cec` for the ABC step.

Classification: **known principle (SVF guidance, algebraic certificates, translation validation) + new implementation.** It borders "nontrivial new application" only through the multi-pass composition.

### D.8 Cheapest falsifier

- **Designed:** does any existing open engine certify these structures?
- **Executed for bundled engines:** they fail.
- **Literature prosecution found TRACE**, which directly targets the capability.

### D.9 What success would and would not have established

- **Would:** per-instance certified arithmetic lowering in open flows; catching bugs of the #6231 class at any width.
- **Would not:** any new verification principle, or any guarantee about optimizations outside arithmetic lowering.

### D.10 Why it died

TRACE (Aug 2026; the paper covers adders, multipliers and MACs from Yosys/ABC-synthesized behavioral designs, and the README adds `-dot`, `-s` and `-gen` modes) plus the Bremen MAC/dot-product papers occupy the scientific content.

What remains:

- Integration into Yosys/EQY: implementation debt.
- Whether TRACE covers Yosys-specific structures: untested, and the subject of §F.

---

## E. Discovery-methodology audit

I assessed each hypothesis you listed against the evidence from this session and your archive.

| Explanation | Verdict | Evidence |
|---|---|---|
| Areas are genuinely well explored | **Yes, strongly** | Every one of ~45 probes found 2025–26 prior art or reduced to implementation. Many hits were months old or less: TRACE Aug 2026, coupling leakage Jul 2026, AutoPRAC Jun 2026, EquivFusion Apr 2026, CircuitProver Jul 2026, DAC'26 best paper Jul 2026 |
| Search-distribution bias | **Partly** | Prior waves concentrated on formal-certificate seams, PDR/proof reuse, and HLS/security composition, and barely touched architecture, security, numerics or silicon. But widening the distribution today (security, architecture, numerics, FHE, silicon, LLM-RTL) found the same saturation, so bias is not the main cause |
| Excessively restrictive feasibility gates | **Partly** | The gates exclude silicon measurement (C-2) and commercial baselines. They did not cause the kills in this session |
| Failure to recognize deeper questions | **Partly** | Your kill rule treats "the principle exists in an adjacent field" as "the problem is solved in this regime" (e.g., GhostForge pass 2 via Schur complements and approximate partial-order reduction). That skips *efficacy* questions, where most applied EDA progress happens. But the one efficacy question I executed (S1) was also occupied within weeks |
| Mistaking implementation gaps for research | **Yes, historically** | MUXWISE turned out to be a bug; PassWitness turned out to be a tool. S1 nearly repeated this until TRACE was found |
| Prematurely inventing mechanisms | **Yes** | The GhostForge passes proposed mechanisms (boundary operators, event quotients, residual cubes) before establishing a failing strongest method |
| Insufficient prior-art investigation | **No** | Prior waves were thorough; this session's decisive kill also came from continued prosecution |
| Unrealistic expectations about novelty | **Yes: the principal cause** | The conjunction "genuinely new mechanism + unoccupied + undergraduate-feasible with open tools + ~2-hour falsifier + broad reuse" is close to empty in 2026. The field's own top-rated work is a composition of known techniques with strong evidence (DAC'26 best paper: LUT mapping + Gaussian XOR modeling + solver-oriented selection). INFERRED: your gate would have killed it at novelty |

**Two structural findings the table does not capture:**

1. **Time-to-occupation is shorter than your cycle.**
   - Seams named as "future work" in 2026 papers (Cabodi's transformation sequences; Froleyks' localization and word-level liveness; CircuitProver's parameterized families) are the authors' next papers.
   - Engineering seams are now filled by agents and other auditors on the same day (#6241 and #6242 were filed today).
   - Mining named seams is racing established groups on their own turf.
2. **Evidence productivity is asymmetric.**
   - Across six or more literature-first passes (archive) plus this session's ~45 probes: zero survivors.
   - Every real finding came from execution: the FMA defect, exit-code verdict errors, the Wave 5B witness mask bug, and today's `&acec` unsoundness and stage localization.
   - Those findings were all engineering-level. Execution finds *real* things, but they become science only when they contradict a **method's stated guarantee across tools**, or recur as a family whose shared cause is **not** already explained by a known principle.

**Protocol change these findings support (a recommendation, not a guarantee):**

1. **Target:** "a consequential regime where the strongest current method, **run by you on public artifacts**, demonstrably fails, with a structural explanation." Explicitly admit the *known principle + nontrivial new application* class when it delivers a new guarantee in that regime.
2. **Order:** execute the strongest method first (hours); prosecute prior art for the *failure mode* second (days); invent mechanisms last.
3. **Race-awareness:** prefer regimes that need your specific assets:
   - Intimate knowledge of Yosys arithmetic lowering and of the #6231 correction.
   - A working Dynamatic + Questa install.
   - A fail-closed harness discipline.

   Avoid seams that active groups have named as future work.
4. **Hard separation of tracks:** bugs go to issues, tools go to releases, and neither is allowed to stand in for research.

---

## F. Next scientific action (exactly one)

**Run TRACE as a black-box oracle against Yosys-specific arithmetic lowering, and decide whether the S1 residual is a genuine boundary.**

- **Artifact:** `github.com/jan-kl/trace`. Binary-only and license-less; created 2026-04-09, last push 2026-04-13 [OBSERVED].
  Run it inside Docker using the repo's own Dockerfile. Executing an unlicensed third-party binary is your call; I did not run it.
- **Inputs:**
  - The 52 netlists already in `experiments/S1_open_datapath_verification_killshot/work/aig/`.
  - Their pre-ABC variants (`stagewise.sh`).
  - Three Yosys-specific families at W ∈ {8, 16, 32, 64}:
    1. `synth -booth`, signed and unsigned.
    2. `synth -arith_tree` fused multi-product trees, e.g. `a0*b0 + a1*b1 + c`.
    3. `$macc` with Y_WIDTH > A_WIDTH + B_WIDTH, both signed and negated (`c - a*b`), on unpatched Yosys and on your PR #6231 build.
- **Modes:** TRACE `-mul`, `-mac` and `-dot=2`, with `-s` for signed inputs, and `-gen` compared against the `$macc` polynomial where the fixed modes don't fit.
- **Controls:**
  - Single-bit mutants must be rejected.
  - Every counterexample must be replayed with `scripts/aigsim.py`.
  - Equivalences at W ≤ 8 must be cross-checked with `&cec`.
  - Verdicts come from output text, never exit codes.
- **Kill condition:** TRACE certifies every correct instance and rejects every mutant within 60 s at W=64. The line is then closed; what remains is integration, which is engineering.
- **Advance condition:** TRACE times out, is unsupported, or is unsound on a **structurally identifiable** Yosys class (for example, only when Y_WIDTH > A+B, or only on Yosys radix-4 Booth) while handling textbook architectures.
  That would be a documented limitation of the newest strongest method on a legitimate, practically relevant regime. It is the first point at which a mechanism proposal would be justified.
- **Interpretation risks:**
  - TRACE's fixed specification templates may simply not express the Yosys `$macc` widths; check `-gen`.
  - Timeouts may be configuration-dependent; try the methods listed in the README (`-dyn`, `-ipc`, `-p`, `-c`).

---

## Separate evidence tracks (not research contributions)

1. **PR #6231** (OBSERVED 2026-09-23). Reviewer `hexratcc` is open to taking the change and requested:
   - justify or remove `static_cast<long long>`;
   - remove the redundant `sign_extension_start >= 0` check;
   - shorten the comment;
   - use `design -reset` in the test and add a `c - a*b` variant.

   The negation variant may go through a different correction path. Test it on the patched build before replying.
   Under YosysHQ's interim policy, your replies and any revised comments or commit message must be written by you.
2. **ABC `&acec`:** a minimal reproducer exists (`work/aig/mac_u_w8_norm.aig` vs `mac_u_w8_tree.aig`; `validate/`; `aigsim.py`).
   If you file it, write the report yourself. Point out that the command appears dormant since 2017 and that the counterexample is not replayed.
3. **Wave 7 D1** was found in WSL (`~/wave7d1`, 123 GB including the Dynamatic build) and was absent from the handoff package. Consider copying its two notes into the package.
4. **Waves 8/9:** still missing; no inference made.

---

## Sources

Retrieved in this session. "Fetched" means I read the page, source or document myself; "summary" means search-result level only.

- Yosys issues #6241, #6242 (Expert-Momonga, 2026-09-23) and #6199 (2026-09-11, labeled invalid); PR #6231 review. https://github.com/YosysHQ/yosys/issues/6241 · /6242 · /6199 · /pull/6231 — fetched
- Yosys `techlibs/common/synth.cc` (main): `booth` and `arith_tree` opt-in; `peepopt`/`wreduce` default; `run(abc)`. https://github.com/YosysHQ/yosys/blob/main/techlibs/common/synth.cc — fetched
- ORFS `flow/scripts/synth.tcl` and `variables.yaml`: default `-extra-map lcu_kogge_stone.v`. https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts — fetched
- ABC `src/proof/acec/acecCore.c`, `acecNorm.c`; commit history; issues #311, #346. https://github.com/berkeley-abc/abc/tree/master/src/proof/acec — fetched
- TRACE paper (arXiv 2608.16458, 2026-08-17) and repo README / metadata. https://arxiv.org/html/2608.16458 · https://github.com/jan-kl/trace — fetched
- Miter-Aware LUT Mapping (arXiv 2607.07164; DAC 2026 best paper per dac.com). https://arxiv.org/html/2607.07164v1 — fetched
- EquivFusion (arXiv 2604.16571). https://arxiv.org/html/2604.16571v1 — fetched
- CircuitProver (arXiv 2607.27259). https://arxiv.org/pdf/2607.27259 — fetched
- LeaSyn (arXiv 2509.06509). https://arxiv.org/html/2509.06509 — fetched
- SecIC3 (arXiv 2601.21353). https://arxiv.org/pdf/2601.21353 — fetched
- FMCAD 2026 accepted papers. https://fmcad.org/FMCAD26/accepted_papers/ — fetched
- Coupling Leakage in Theory and Practice (IACR eprint 2026/1426). https://eprint.iacr.org/2026/1426 — fetched abstract
- CIRCT `datapath` dialect rationale. https://circt.llvm.org/docs/Dialects/Datapath/RationaleDatapath/ — fetched
- Tiny Tapeout pages (MicroTapeout TT03, ring oscillator TT09, silicon-proven list). https://tinytapeout.com/chips/silicon-proven/ — fetched
- Summary-level only:
  - H-Houdini / VeloCT (ASPLOS'25); Contract Shadow Logic (ASPLOS'25); HWMCC'25 (rIC3).
  - TOSEM FPGA synthesis-bug study; Bambu bug study; TEPACS.
  - Formality SVF documentation; AMulet 2 / 2.2; Bremen MAC and dot-product papers (DVCon'25, DATE'25, ForMAt, SN CS'26); ACL2 RTL books (arXiv 2507.19010).
  - Khattak & Mikaitis (TACO 2026); AMD matrix cores (arXiv 2609.14845); P3109 (arXiv 2606.04028); FLoPS; OCP MX latitude.
  - AutoPRAC (arXiv 2606.23905); HartBreaker; χRVFormal.
  - BOLT (eprint 2026/153); AutoHoG; Scytale; RealBench; synthesis-in-the-loop evaluation (arXiv 2603.11287).
  - Lean-MLIR (arXiv 2407.03685); verification dialects (PACMPL 2025); K-CIRCT (arXiv 2404.18756).
  - ISCA'26 and MICRO'25 best papers.
- Archive (your package): prior-art sources listed in GhostForge verdicts, the Wave 6A frontier notes, and `Existing-Research-Audit.md`. Cited here as "per archive" and not re-verified.
