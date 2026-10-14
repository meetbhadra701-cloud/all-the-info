# M0 GATE REPORT — Proof-Carrying Arithmetic Synthesis (PCAS)

**Date:** 13 October 2026  
**Role:** Independent adversarial synthesis / formal-verification research audit  
**Decision:** **NO-GO — kill PCAS as presently claimed as a publishable research contribution.**  
**Scope:** Read-only review of all eight documents in `PCAS_FABLE_OUTPUT_AND_INDEPENDENT_AUDIT(1).zip`, public primary papers, relevant implementation/documentation, patents, and the connected `meetbhadra701-cloud/all-the-info` research archive. No research implementation, benchmark, theorem-prover run, code change, GitHub write, or author contact was performed.

> **Decision is about evidence sufficient to fund an original research project, not a proof that a useful tool cannot exist.** PCAS may be worth implementing as engineering or a teaching/diagnostic tool. This M0 does **not** authorize M1 or a Yosys fork. Reconsider only if a genuinely different, narrowly specified mechanism survives the challenges in §12. A review of selected public sources is not an exhaustive patent or literature search, and an untested B5 reader is a very strong *threat*, not an experimentally established equivalence.

## 1. Executive thesis and decision grounds

PCAS proposes that a compressor-tree *generator* emit a certificate identifying (C1) the initial partial-product and correction-constant identity modulo `2^W`, (C2) local full-adder/half-adder/compressor weighted-sum conservation, (C3) safe truncation, and (C4) final carry-propagate adder equivalence. A separate, allegedly linear-time checker would validate this record, localize arithmetic bugs such as the Yosys wide signed-FMA correction error, and substantially outperform post-hoc SAT or symbolic-computer-algebra verification.

**Why the present paper claim fails M0:**

1. **The principles are heavily occupied.** Proof-producing hardware synthesis predates PCAS (Slind et al., 2007). AMulet 2.2 already generates externally checkable algebraic proofs; later SCA work binds proof operations to the *actual* circuit and exports LPAC. TRACE and Arisca directly tackle MAC/dot-product checking. What is left is *where the information is gathered* and a proposed implementation format, not a demonstrated new proof principle.
2. **The best obvious noninvasive competitor has not been defeated.** Yosys's `arith_tree` implementation already constructs real `$fa` cells, known wires, `$and`/`$xor` partial-product rows, constants, and a final `$add` or prefix adder. An independent reader at the right intermediate RTLIL checkpoint might rederive C1–C3 and perform the same checking without instrumenting the generator. The exact scope of B5 remains untested, but an asserted generator-side advantage is currently **unsupported**.
3. **The offered soundness argument is incomplete.** Local algebraic conservation plus a producer-supplied C1 identity does not prove the function of the *actual* netlist unless an independently obtained specification, cell semantics, every relevant connection, the actual final adder, and primary output mapping are verified. Netlist hashes identify bytes, not correctness. The stated C4 treatment is incorrect for Yosys's default `$add` implementation.
4. **The complexity and proof-export language overstate what is established.** A local linear scan is possible for a strictly restricted, explicitly represented bit-heap circuit; a global, full-netlist, LPAC-checked end-to-end theorem with the same bound has not been specified or proved. General post-mapping circuit analysis may be hard; pre-ABC linear checking does not discharge ABC's correctness.
5. **There is no validated practical effect or discriminator.** The >10× runtime, 20-percentage-point conclusive-rate advantage, ~250 kB certificate, <1-s Python check at 64×64, and B5 inability to reconstruct certain held-out cases are estimates or hopes, not observations. Existing experimental history repeatedly shows weak baselines hiding apparently new contributions.

**Verdict:** **NO-GO**, not GO TO EXPERIMENT. A later **REFRAME** would require a new technical insight about *what cannot be recovered, checked, or preserved by existing methods*, not simply emitting records earlier. No `M1_REQUIREMENTS.md` is issued because PCAS has not survived M0.

## 2. What exactly would have to be novel?

| Proposed claim | Judgment at M0 | Reason / burden of proof |
|---|---|---|
| C1 signed partial products and correction constants via exact arithmetic | **Known mathematics** | Baugh–Wooley/weighted bit heaps and two's-complement modular identities are established. Fixing a missing constant is a useful tool correction, not a new arithmetic theorem. |
| C2 FA/HA/4:2 conservation | **Known mathematics** | Local compressor identities are standard. A 4:2 implementation must be checked by *its actual primitive decomposition*, not by a possibly idealized abstract cell. |
| Generator-emitted arithmetic proof | **Occupied in broad form** | Slind et al. compiled with per-function HOL correctness theorems; IBM describes generator-recorded arithmetic transformations later replayed for equivalence. A portable, narrow Yosys JSON format might differ operationally, but the broad notion is not new. |
| Independent proof checked against actual gates | **Occupied in important form** | AMulet certification and Konrad–Scholl 2026 demonstrate independent LPAC checking; the latter validates substitution steps against actual AIG gates. |
| Fast verification from supplied structural witness | **Obvious in restricted structure / unmeasured** | Exploiting supplied decomposition reduces discovery work, but a no-modification structural reader receives nearly the same information for Yosys `$fa` trees. |
| Linear-time *end-to-end* verification | **Unproved / overbroad** | At best near-linear in the *fully represented, permitted* arithmetic graph plus proof size, with dependence on width and arithmetic representation. Final CPA, gate binding and further synthesis passes remain. |
| Correction-residual bug localization | **Useful but not exclusive** | Weighted-constant residual is straightforward algebra. Algebraic post-hoc tools also yield residual polynomials, though diagnostic quality on this exact error is unmeasured. |
| Demonstrable performance over best baseline | **Unsupported** | No fair executable head-to-head or effect-size evidence exists. |
| Proof of final technology-mapped circuit | **Not provided** | Either separately validate downstream passes with strong equivalence/proof or restrict the advertised claim to the pre-mapping checkpoint. |

**Potential true delta:** A compact **independently replayable, machine-checkable arithmetic transform trace for a precise synthesis-pass boundary**, containing a proof that the *observed* graph equals an independently parsed word-level specification, without search. But its core mathematics and much of its provenance machinery are known, and there is no evidence that such a trace offers capability a post-hoc structural checker lacks. A narrower artifact is not automatically a new algorithm or scientific discovery.

## 3. Nearest prior art: capability/overlap matrix

Evidence levels in this section refer to source inspection, **not** to our running tools. `VERIFIED BY PRIMARY SOURCE` means that a primary article, repository README/source, or patent text documents the capability. Performance and compatibility with the proposed benchmark remain `SOURCE CLAIM NOT REPRODUCED` until executed.

| Work (source) | Verified representation, supported function and method | Independent proof / executable | Overlap with PCAS | Exact *remaining* distinction and skeptical objection |
|---|---|---|---|---|
| **Slind, Owens, Iyoda, Gordon (2007)**, [paper DOI](https://doi.org/10.1007/s00165-007-0028-5) | HOL4-to-clocked-hardware synthesis by automatic theorem proving for arithmetic/cryptographic functions; theorem for each compilation. | HOL theorem produced; outputs Verilog. Published method, not shown runnable in our environment. | **Generator-time certified synthesis** already exists. | HOL/LCF proof rather than lightweight Yosys-specific cell log. *Format and toolchain are different, not proof-producing synthesis itself.* |
| **AMulet 2.2** [code](https://github.com/anthropics/amulet2), [technical article](https://doi.org/10.1007/s10009-022-00688-6) | Reads AIG multipliers, signed or unsigned, checks via arithmetic algebraic reasoning. `-certify` outputs initial polynomials, LPAC proof, spec; Pacheck2 checks. | **Yes**: public implementation and independently checkable artifact. | **Independent algebraic correctness certificate** and signed multiplication occupied. | README does **not** establish general signed FMA/dot product support. Mark unsupported combinations N/A, not slow/failed. PCAS's possible delta is structured MAC construction and avoiding structural discovery. |
| **Arisca** (Li, Li, Xu, July 2026), [paper](https://arxiv.org/abs/2607.10257), [code](https://github.com/LittleBlackCQ/arisca) | AIG; custom expression grammar, e.g. `[63]*[65]+[128]`; arithmetic including MAC/dot products and truncated outputs modulo output width. Spec variables documented as *unsigned*; `-` exists. | Public Rust implementation; no independently checkable proof file clearly advertised in README. | **General arithmetic MAC / truncation post-hoc checking** already targeted. | Signed two's-complement input semantics require a demonstrated faithful spec encoding; not presume automatic support, but do not exclude fairly encodable cases. |
| **TRACE** (Kleinekathöfer et al., Aug. 2026), [paper](https://arxiv.org/abs/2608.16458), [code](https://github.com/jan-kl/trace) | AIG/AAG; modes `-add`, `-mul`, `-mac`, `-dot=<n>`; `-s` signed; multiple traversal and polynomial-reduction options. Authors report optimized-MAC successes. | Public Linux binary / Docker documented; standalone independently checkable certificate **not documented**. | **Directly competes in signed MAC/dot verification**, not just multipliers. | Needs a pinned, executable trial on the *same emitted gates and exact contract*. Omission from Fable's baselines was a substantive defect. |
| **TalisMan** [code](https://github.com/d-kfmnn/talisman) | AIG, specification modes `-mult-spec`, `-miter-spec`, `-assert-spec`, plus external spec file; reconstructs arithmetic relationships with algebraic/matrix methods. | Public implementation; external independently checked proof not documented in README. | **Reconstructing arithmetic structure** is existing research. | General signed wide MAC support via custom spec is **unverified**, not presumed. Must be in applicability audit. |
| **Konrad & Scholl (2026)**, [FMSD paper](https://doi.org/10.1007/s10703-026-00494-9) | For AIG multipliers, logs algebraic backward-substitution and phase transformations; validates that logged substitutions correspond to gates in the *actual* AIG; converts log to LPAC. | **Yes**: explicitly uses independent **Pacheck2**. | **Netlist-bound, externally checkable proof logging is already demonstrated**, with very substantial proof-generation/checking engineering. | The log is generated during *verification*, not at synthesis-time, and authors emphasize potentially very large proofs. Narrow scope does not rescue the unqualified PCAS claim. |
| **Pacheck2** [code](https://github.com/d-kfmnn/pacheck2) / PAC/LPAC calculus | Independently checks polynomial proof steps against supplied starting polynomials and target specification. | Public independent checker. | The claimed LPAC backend itself is prior art. | An FA conservation trace in custom JSON is **not automatically an LPAC derivation**. One must translate gate constraints, Boolean assumptions, modulus and target relation *correctly*. |
| **Yosys `arith_tree`** [pass](https://github.com/YosysHQ/yosys/blob/main/passes/techmap/arith_tree.cc), [compressors](https://github.com/YosysHQ/yosys/blob/main/kernel/compressor_tree.cc) | Adds `$fa` primitive cells for 3:2 and 4:2 compressor chains, masked partial-product rows, corrections, then default `$add` or prefix CPA. | Public implementation; no claimed PCAS certificate. | **Most of generator's proposed structural witness is already explicit in the intermediate graph.** | Generator instrumentation might be convenient or retain knowledge lost after lowering, but B5 can read a suitable checkpoint before that information disappears. |
| **IBM US12475287B2**, [claims](https://patents.google.com/patent/US12475287B2/en) | Synthesis stores external records of arithmetic expansion/rewrite/optimization; replays transformations to construct a comparison design and performs bit-level equivalence. | Granted US patent, published Nov. 18, 2025; not an open benchmark. | **Construction-time synthesis history as verification evidence** already disclosed, including compressor/arithmetic details. | Records/replay-plus-CEC are not PCAS's precise local algebraic certificate. Patentability and freedom-to-operate require separate professional legal analysis; no infringement conclusion here. |
| **Translation validation / equivalence, ABC, Yosys** | Combinational/word-level checking between source and optimized representation; Yosys `sat`, `equiv_*`, ABC `&cec`. | Public tools; varied proof/log support. | The broad synthesis-validation problem and baseline oracles are known. | Hard arithmetic may favor a structural specialized checker, but needs actual data and honest compare-point conditions. |
| **CIRCT datapath / FloPoCo-style bit heaps**, [CIRCT site](https://circt.llvm.org/docs/Dialects/Datapath/) | Specialized intermediate structures for arithmetic transformations/bit heaps, usable to construct compressors; not asserted to emit the PCAS format. | Public infrastructure. | A structured arithmetic IR is *not* novel. | Emit-and-check an independently bound certificate would be additional implementation, not by itself a theorem or demonstrated speedup. |

**Significant primary-source nuance:** Konrad–Scholl 2026 §4.3 says its log is checked so each substitution matches an *actual AIG gate* before LPAC translation and Pacheck2 verification. This is a stronger challenge than saying AMulet merely recovers full adders. Their 64-bit examples involved **12 GB / 365 GB LPAC proofs** with long generation/check times (§5.5), but these cannot be directly compared to PCAS's speculative **250 kB**: they verify different, heavily optimized gate-level structures and different proof tasks. Using this contrast as a PCAS speed win would be invalid.

**Prior-art status:** No primary source inspected is confirmed to emit *exactly* Fable's C1–C4 records during the Yosys `arith_tree` pass. That narrow negative result is **not** a novelty determination. Broad invention concepts already overlap substantially; further searching could only weaken the claim. Source/CLI applicability details above remain subject to version pinning and execution.

## 4. B5 adversarial source inspection — the central kill risk

The strongest low-complexity alternative is **an independent read-only parser of the existing post-`arith_tree`, pre-`techmap` RTLIL graph**, not another SAT engine.

**Direct source observations (Yosys GitHub, default branch as inspected 2026-10-13):**

- `CompressorTree::emit_compressor_32` constructs **one** `module->addFa(..., cout, sum)` and returns `sum` plus a left-shifted carry vector.
- `emit_compressor_42` constructs **two** `$fa` cells, including the intermediate `cin` wiring. The high-level label `4:2` has no magic primitive meaning: these two actual cell instances must be checked as interconnected.
- `generate_partial_products` creates `$and` rows, optionally `$xor`-inverted rows, `push_one_at` correction constants and, for signed products at enlarged accumulator width, an explicitly generated sign-extension correction vector beginning at `width_a + width_b - 1`.
- `reduce_scheduled` selects FA/4:2 groupings and returns two remaining bit vectors. The code's DADDA comment says the current path follows `PREFER_42` rather than a separately proved column-height algorithm.
- `emit_final_adder`: **DEFAULT/RIPPLE = `module->addAdd(...)`**, whereas **PARALLEL_PREFIX** emits a gate-level Kogge–Stone-style network. `arith_tree` has `-final <auto|ripple|prefix>`, `-strategy`, and `-no-fma`.
- The `arith_tree` worker obtains operands from `$add/$sub/$alu/$macc` and `$macc_v2`, handles negation compensation and then emits the compressor plus final adder. Thus high-level semantic transitions must be checked from the appropriate *original* input boundary, not simply from the newly emitted graph.

**What B5 likely can reconstruct without producer cooperation:** actual `$fa` cells and their columns, a connectivity-derived conservation graph, the observed constants and partial-product logic, and final two vectors. Given independently supplied word-level semantics and supported gate types, the C1 polynomial identity can be recomputed from the observed graph. A generator-only certificate may largely duplicate those facts.

**Crucial caveat:** `$fa` retention has been established by *source construction*, not by running the pinned pipeline or proving that all published `synth -arith_tree; write_json` invocations preserve them. Subsequent `techmap`/optimization can lower or rewrite `$fa`. The original Fable pseudocode `synth -arith_tree; write_json pre_abc.json` is **not validated as a genuine immediately post-pass checkpoint**. It must not be considered an executable preregistration. Take the snapshot immediately after the named pass (and before any rewrite that destroys its cells), with checked pass options and exact tool SHA. This test was **not run in M0**.

**Why the proposed conditional kill criterion is backwards:** Fable says B5 should fail on “≥1 held-out class” for PCAS to advance. B5's failure may be due to an impoverished parser, absence of semantic metadata because of checkpoint selection, an unsupported cell type, or an artificial Booth benchmark. These are not scientifically meaningful wins for construction-time emission unless the information is *provably unavailable* in the actual trace and its absence matters on representative synthesis flows. Both candidates must be held to identical trusted semantics, proof targets and workflow boundaries.

**B5 gate judgment:** High-probability reduction of “generator emission” to **engineering convenience**. Do **not** claim experimental dominance/equivalence of B5 until both are implemented and independently validated; do **not** fund M1 on an unsupported supposition that B5 will fail.

## 5. Soundness audit: the present proof is not an end-to-end proof

### 5.1 A minimal falsifying counterexample to the suggested C1–C4 argument

Let a certificate describe a correct FA network computing `F(x)` and supply genuine local FA equations and an accurate C1 identity. Let the *actual emitted netlist* drive its primary output from `F(x) XOR 1`, or swap its output with a different signal. If the checker only verifies the certificate's equations and an opaque hash recorded in C0, every local equation can pass despite a wrong implementation. The producer can hash the *wrong* netlist; hashing does not prove the certificate's selected cells, output maps or semantic claims agree with that netlist.

A less conspicuous attack replaces one `$fa` actual input with a different wire but retains the same C2 record; another changes the correction constant in the netlist but leaves the C1 record unchanged. A third preserves C1–C3 exactly and changes an internal gate of the prefix final adder. All can defeat a checker that accepts producer assertions, or ignores unmatched reachable gates, and all can evade “mutant kills” when mutations do not target the real trusted boundary.

**Necessary independent components of a *sound* checker:**

1. **Original specification:** obtain and interpret an externally supplied word-level arithmetic expression or trusted independent elaboration, with operand widths, signedness, truncation, Boolean/two-state semantics, high-level negative MAC terms and interface bit order. Do not extract the golden expression from the same potentially buggy producer implementation.
2. **Actual netlist parser:** read *every live cell and connection needed for the certified cone* from the observed checkpoint. Validate cell type, every input/output pin, bit ordering, aliases/constant drivers, port interface, absence of unsupported multiple drivers, dangling/extraneous live drivers and combinational cycles. Enumerate allowed untrusted/pass-through gates or reject.
3. **Binding:** independently recompute cryptographic digests of original artifacts and bind *record IDs and edges* to the exact graph. The digest prevents swapping artifacts **only after** semantic binding is established.
4. **Local semantics:** interpret `$fa` by a trusted, separately documented Boolean definition, or check its instantiated primitive decomposition; verify HAs/4:2 cells from their actual circuit; check `$and/$xor/$not` row logic, sign extensions and every constant's source.
5. **Conservation over *occurrences*, not wire names:** establish an incidence/flow or DAG-certificate invariant. A signal may fan out to two arithmetic contributions legitimately; bookkeeping must distinguish multiplicity from illegal implicit creation/discard. Each output/carry needs a unique, correctly weighted producer and all necessary terminal uses. Verify weights and every truncated output/bit.
6. **Final outputs:** check the last two rows and the **actual** final adder network or a separately verified `$add` semantic contract. The current blanket statement “ripple CPA reuses C2 FA records” is **false for the Yosys default**.
7. **Closed proof boundary:** precisely identify which artifact is certified and which transformations are excluded. Certification of a pre-ABC RTLIL checkpoint cannot be relabeled certification of the optimized AIG, mapped cell netlist or fabricated silicon.

### 5.2 Algebraic invariant and its limitations

For a full adder at column `k`, with Boolean inputs `a,b,c`, sum `s` and carry `t`:

`2^k(a + b + c) = 2^k s + 2^(k+1) t` in integers, since `a+b+c=s+2t`.

Summing *correctly wired* local identities gives a conservation theorem for a **fully accounted-for** bit heap. Truncating terms of weight `>= W` is legitimate only for the stated ring `Z/(2^W)`. This shows an attractive *restricted-IR* proof scheme, but not correctness of an arbitrary Boolean netlist.

For signed `m`-bit two's-complement word `A`, use `A_unsigned - 2^m * a_(m-1)`; analogous for `B`. For an FMA/multiply-add, signedness, individual product widths, negated products and addend sign extensions must be combined at the actual expression widths before reducing modulo `2^W`. In a Baugh–Wooley-style inversion at weight `k`, replacing a negative term can use `-2^k b = 2^k(1-b) - 2^k` for Boolean `b`, and `-2^k mod 2^W` has ones from `k` through `W-1` when `0 <= k < W`. **But** this derivation does *not* license one universally identical correction mask for every operand order, mixed signedness case, number of products, Booth recoding, or intermediate-width truncation. The Yosys implementation itself uses *several* correction components.

Negative terms `c-a*b`, mixed-width `macc`, overflow carry, output sign extension, narrow intermediate truncation and final `$add` must be included explicitly in the theorem. The original Yosys issue is therefore a *good regression case*, not proof that the general certificate mechanism is complete.

### 5.3 LPAC and Pacheck2 are **not** available by assertion

A certificate of “FA identities” is not by itself an accepted LPAC proof. A proof checker needs a valid **starting ideal** encoding each relevant *actual* gate, Boolean constraints (`x^2-x=0` for bit variables as appropriate), a precisely formulated target, and a stepwise derivation under the chosen coefficient ring. To prove an output relation only **modulo `2^W`**, a proof calculus over integers or rationals needs explicit justified congruence/quotient handling or a sound modular encoding; ordinary integer equality is stronger than modular equality and may be false at overflow. A proof accepted against a fictitious polynomial set proves nothing about the real circuit.

No handoff document presents valid Pacheck2 input instances for C1–C4, complete gate polynomials, a derivation of the target, or an actual checker run. “LPAC-style” is an analogy and **must be downgraded from validation to proposed future work**. Importantly, Konrad–Scholl's independently bound LPAC method already occupies the general contribution of “netlist-bound proof steps checked by Pacheck2.”

### 5.4 End-to-end claim boundary

- **Verified pre-mapping structured arithmetic:** plausible with a *new, sound, strictly specified* checker.
- **Verified bit-blasted/post-ABC logic:** not implied. An actual translation-validation proof or separately independently checked proof log for *every later transformation* is needed, unless those transformations are in the checker’s trusted computing base (which weakens its claim).
- **Verified top-level RTL correctness:** not implied from the arithmetic subset; surrounding logic, sequential behavior, initialization, unknown values and environmental assumptions remain.

A conditional theorem could be stated as: given a trusted interpretation of external specification `S`, an independently parsed supported two-state acyclic intermediate graph `G`, a certificate `C` whose records are exhaustively bijective with the relevant observed graph transitions, a proved local interpreter for each allowed cell type including the final adder, and no unsupported live cone, acceptance entails `eval(G, inputs) = eval(S, inputs) (mod 2^W)` for all two-state inputs. **This is a plausible theorem schema, not a theorem established by the package.**

## 6. Complexity audit — state the input size, not just “linear-time”

**Restricted best case:** For a graph whose whole relevant circuit consists of permitted, constant-arity Boolean gates and FA/HA elements, each local truth table/edge can be checked in O(1) machine operations, and each observed wire/record can be visited a constant number of times. For `P` serialized pins and cell records, `R` certificate records, `T` monomial/constant terms in an independently reconstructed source identity, total work can be *near-linear* `O(P + R + T)` **if** weights are machine-sized, normalizations use linear-time data structures, and every proof dependency is already explicitly represented. Storage is O(P+R+T) or smaller with streaming in bounded ordering.

**Qualified bound:** More precisely the complexity must account for bit-width `W`, bit-complexity of coefficients and shifts, sorting/hashing worst cases, alias resolution, polynomial normalization, and any implicit generator expansion. A straightforward symbolic multiplication of two m- and n-bit variables has `mn` terms, so `T = Theta(mn)`; there are analogous terms across MAC products. Operations on W-bit coefficients cannot honestly be called O(1) bit-time as W grows unboundedly. A prefix adder may have O(W log W) internal gates and should be counted in the *full parsed graph*, not described as linear merely in compressor-cell count.

**Not proved:** `O(#FA)` for arbitrary multiplier/MAC outputs; near-linear independent equivalence of arbitrary post-ABC gates; `O(#FA)` LPAC proof sizes; bounded memory for all supported input formats; `<1s` Python for 64x64 signed FMA W=160; `~250kB` artifact. These are implementation-dependent hypotheses with no recorded timings or sizes.

**Scientific value issue:** When the cost of a proof is proportional to a proof deliberately embedded in a specially structured circuit, it does not establish a generally easier verification algorithm. The relevant question is whether the proposed certificate offers a new **quality-of-proof versus input-access** frontier relative to direct graph analysis, existing proof systems and history replay. That frontier has not been specified, much less measured.

## 7. Corrected baseline and applicability plan (not executable in M0)

Fable's original B1–B5 omitted two especially relevant public engines and two important independent certification comparisons. Corrected lineup:

| ID | Required baseline / oracle | Fair common target | Applicability and limitations |
|---|---|---|---|
| **B0** | Native no-modification Yosys `arith_tree` graph and independent arithmetic source oracle | The pre-techmap arithmetic checkpoint | Mandatory reference artifact; distinguish source-to-checkpoint from checkpoint-to-output. |
| **B1** | Arisca with **faithful custom `--spec`** | Identical AIG, equivalent arithmetic semantics | MAC and truncation documented; signed notation needs verified encoding. Do not auto-count unsupported mode as failure. |
| **B2** | AMulet 2.2 `-verify` and `-certify` + Pacheck2 | Signed/unsigned standalone multipliers it documents | Narrow *applicability* cohort; a signed FMA is not presumed supported. |
| **B3** | ABC `&cec` / `cec` against an independently generated structural reference | Same genuine source function, same outputs | Reference construction and restructuring can radically change difficulty; disclose whether independent. |
| **B4** | Yosys `sat`, `equiv_*`, suitable solver configurations | Same compare-point and two-state semantics | SAT timeout = UNKNOWN, not proof. Yosys-produced ‘golden’ needs independent validation. |
| **B5** | **Post-hoc reader** of actual intermediate RTLIL `$fa`, rows, constants, `$add` | Same *proof target* and trusted semantics as PCAS | **Decisive novelty/utility baseline.** Reader must have a fair ability to handle exactly the permitted cells. |
| **B6** | **TRACE** with `-mac`/`-dot`, `-s` for signed cases | Same AIG with verified input order, output width | Public signed MAC/dot modes; tune only published options under a preregistered, symmetric budget. |
| **B7** | **TalisMan** and appropriate external arithmetic specification | Supported AIG cohort | Custom signed MAC capability unverified; record N/A when honestly unsupported. |
| **B8** | Konrad–Scholl 2026 certifying SCA, where runnable | Full post-hoc AIG certification cohort | If exact implementation not independently reproducible, include primary-source claims as **non-executable** comparison; do not report local measurements. |
| **B9** | Pacheck2 on independently derivable LPAC artifacts | Checks proof verification overhead and soundness | **Checker**, not stand-alone synthesis equivalence competitor. |
| **B10** | Native proof/certificate-less structured arithmetic lint and direct source-vs-RTLIL checker | Same pre-techmap graph | Trivial simpler alternatives, parser/checker cost and time separate. |

**Crucial fairness controls:** Predefine truth conditions, two-state/signed/width contract and input/output ordering for every test. Record `SUPPORTED`, `UNSUPPORTED`, `INVALID INPUT`, `PASS`, `FAIL WITH WITNESS`, `UNKNOWN`, `TIMEOUT`, `CRASH`; never fold last four into the same denominator as a proven inequivalence. Verify exporters/format converters preserve functionality with an independent oracle before timing. A tool cannot win by declining a problem; an inapplicable specialized baseline also cannot be credited with a loss.

Present at least three distinct cohorts, with no pooled headline number across incomparable tasks: (i) ordinary signed/unsigned multipliers supported by all applicable tools; (ii) MAC/dot and truncation supported by Arisca/TRACE/custom-spec engines; (iii) specifically structured pretechmap graph where PCAS and B5 compete. Compare proof-producing modes **separately** from verify-only modes, and report end-to-end elapsed time including conversion, proof generation and checking as well as individual phases. Limit runtime/memory/threads identically, pin revisions, store raw logs and first independently checked witnesses. Draw performance profiles over widths and multiple structures rather than cherry-picking one PR bug. No claim about broad scalability is supported by a single 64x64 FMA.

## 8. Fable's infeasible tests and corrected bounded minimal plan

### 8.1 Original exhaustive-test arithmetic is impossible as scheduled

Exhausting all two-state assignments of two multiplicand inputs widths `m,n` and an independently variable `c` width `q` requires exactly `2^(m+n+q)` assignments **for each circuit**. Examples:

| Operand bits | Addend bits | Full assignments per case | Assessment |
|---|---:|---:|---|
| m=n=3 | q=4 | `2^10 = 1,024` | Practical |
| m=n=4 | q=4 | `2^12 = 4,096` | Practical |
| m=n=6 | q=16 | `2^28 = 268,435,456` | Impractical for the promised fast, multi-variant gate |
| m=n=8 | q=16 | `2^32 = 4,294,967,296` | Infeasible for that gate |
| m=n=8 | q=20 | `2^36 = 68,719,476,736` | Infeasible |

An addend's **declared output width W is not necessarily its independent input bit-width**; document `q` separately. Setting `q=W` in the above examples is an explicit *scenario*, not something every MAC does. Constraining `c` to a few constants can reduce assignments but must be labeled as a restricted oracle, not exhaustive general FMA testing. Exhaustiveness on small bit sizes cannot stand in for a proof over unbounded widths.

**Repaired oracle design:** Exhaustive enumeration only for `m,n<=4` and `q<=4` (plus separately defined tractable corner cases); symbolic SMT/bit-vector equivalence with independent oracle and checked counterexamples for medium widths; randomized testing (with fixed seeds and directed edge cases) as **bug-finding, not proof** for larger widths; independent proof check for any actual LPAC instance if and when fully available. Negative/control mutants must cover all classes in §5 and exhibit real source-to-actual-netlist divergences.

### 8.2 Corrected experiment order — **hypothetical only, not approved M1**

The *only* rational preregistration if a genuinely revised invention is later proposed is **falsification-first**, with minimal time sunk into code:

**Desk gates, before coding:** (D0) pin supported circuit semantics/checkpoint and verify from paper/source what external tools genuinely claim; (D1) produce an independently reviewable theorem statement and list *every trusted component*; (D2) articulate what information cannot be reconstructed from existing netlist plus original spec and why it matters; (D3) specify a new mechanism, not a repackaging of a recorded bit heap.

**First local gate if D0–D3 pass:** B5 is built first, not last; verify source/checkpoint retention of `$fa`, `$and/$xor`, corrections, `$add` and output edges; apply the simplest complete independent graph checker and mutation controls. If it achieves the same correctness/diagnostic scope without instrumenting synthesis, **kill generator-side PCAS immediately**. Do not rescue with a synthetic unsupported benchmark.

**Only thereafter:** Run supported B1, B3, B4, B6, B7 on representative pinned workloads and held-out designs; B2 only on supported multiplier subset. Separate signedness/width/topology cohorts, counterexamples and conversion correctness. Restrict speed claims to same proof target, equal time/memory/thread budgets, reproducible evidence, and prior-art-compatible success semantics. Add genuine certificate export and independent Pacheck2 checking *before* making any final proof-certification claim. Any “M1 first, baseline later” plan reverses the scientific gate.

**Threshold repair:** Do not count “100% mutant kill” as soundness or **10× median speed / 20 percentage points** as universal materiality bars. Those are arbitrary preregistration choices and depend on problem cohort. A credible advance requires (a) an independently sound checker, (b) *documented unavailability* of the same information to B5 or a new theorem that changes the trust/scalability frontier, (c) at least one reproducible practically relevant setting with a material, statistically stable improvement over **best applicable** current tools, and (d) no comparable simplification by a trivial reference design, pass-aware proof hint or plain CEC. An unsupported baseline mode is not a speedup.

## 9. Five strongest hostile-review attacks

1. **“You are certifying a story, not the netlist.”** C1/C2 and a recorded digest can be internally consistent while the actual output is wrong. The final adder and post-mapping transformations are not proved. **Fatal until fixed with independent graph/source binding and a full theorem.**
2. **“Yosys already gives you the witness.”** The code emits `$fa` cells, constants and rows. A post-hoc reader of the intermediate graph can plausibly derive the same arithmetic proof with no synthesis hook. **Fatal to asserted construction-time novelty unless an exact new mechanism explains irrecoverable information.**
3. **“Your proof architecture is old.”** HOL4 proof-producing hardware synthesis, AMulet/Pacheck2 certification, Konrad–Scholl AIG-bound LPAC logs, IBM synthesis histories and arithmetic SCA are already established. **No specific uncovered theorem is identified.**
4. **“The benchmark is designed to beat missing or inappropriate tools.”** Fable omitted TRACE, had no TalisMan or modern certified AIG comparator, incorrectly treated AMulet wide FMA as naturally supported, and proposed a tool/format workflow never tested. The time/success advantage is imaginary until fair applicability-aware trials. **An eventual speed advantage over poorly configured SAT would not establish scientific novelty.**
5. **“You are proving the easy half.”** FA conservation is linear *because* the generator exposes arithmetic structure. The hard end-to-end task is proving arbitrary optimized gate connectivity and pass correctness; PCAS pushes it to unchecked `$add`, post-ABC CEC or trusted transformations. **The scientific problem is narrowed until it may have no independently important unsolved core.**

**Strongest conceivable defense (also unproven):** Yosys-native, externally checked structured certificates might outperform gate-level algebraic proof generation by orders of magnitude for wide signed MAC, and keep a small trusted checker while preserving useful debugging information. But this defense needs a *verified end-to-end contract and a proof that this capability is not recoverable cheaply from intermediate RTLIL*, then a fair TRACE/Arisca/B5 evaluation. The package establishes neither condition.

## 10. Research-history cross-check: do not repeat the same mistake

Connected GitHub repository: [`meetbhadra701-cloud/all-the-info`](https://github.com/meetbhadra701-cloud/all-the-info), especially:

- [`05_KILLED_CANDIDATES/RESEARCH_KILL_DATABASE.md`](https://github.com/meetbhadra701-cloud/all-the-info/blob/main/05_KILLED_CANDIDATES/RESEARCH_KILL_DATABASE.md): explicitly records definitive kills for MOSAIC's novelty, HBRoute's shortest-path reduction, MUXWISE generic sharing and arithmetic-tree PPA rationale; provisional kills of GhostForge, ArchWitness, generic certificate transport and others. The **actual wide signed-FMA defect** was a real engineering finding, **not** a warrant to claim a new proof framework. Fable had incorrectly marked this database inaccessible; it was read via connected GitHub.
- [`12_WAVE_10_EXPERIMENTAL_DISCOVERY/00_EXECUTIVE_SUMMARY.md`](https://github.com/meetbhadra701-cloud/all-the-info/blob/main/12_WAVE_10_EXPERIMENTAL_DISCOVERY/00_EXECUTIVE_SUMMARY.md), [`06_FINAL_DECISION.md`](https://github.com/meetbhadra701-cloud/all-the-info/blob/main/12_WAVE_10_EXPERIMENTAL_DISCOVERY/06_FINAL_DECISION.md): reported 1,855 independently evaluated map variants. Apparent mapping benefits failed when compared with stronger `emap` or iso-delay controls; OpenROAD search-based resynthesis lost to standard timing repair; **no candidate advanced**. Crucially, the report classed its prior TRACE/Yosys investigation **ENGINEERING ONLY**. These are repo-reported runs; this M0 did **not** independently rerun them.
- [`13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION/03_ADVERSARIAL_REVIEW.md`](https://github.com/meetbhadra701-cloud/all-the-info/blob/main/13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION/03_ADVERSARIAL_REVIEW.md), [`04_HYPOTHESIS_EVOLUTION.md`](https://github.com/meetbhadra701-cloud/all-the-info/blob/main/13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION/04_HYPOTHESIS_EVOLUTION.md): mapping mechanisms repeatedly failed upon inspection of established exact-recovery, near-tie optimization and current-tool competitors; H1.6 explicitly sought independent evaluation and early assumption falsification. Lessons: an apparently different *place to compute something* is weak unless it changes the underlying hard mechanism; best existing baseline comes **before** months of invention development.
- [`06_EXPERIMENTAL_EVIDENCE/PASSWITNESS/README.md`](https://github.com/meetbhadra701-cloud/all-the-info/blob/main/06_EXPERIMENTAL_EVIDENCE/PASSWITNESS/README.md): PassWitness honestly described as a workflow around existing Yosys SAT, not a new formal algorithm. That transparency is the right model for a PCAS engineering utility.

**History-derived decision:** PCAS has the same failure signature as earlier proposals: real tool bug → attractive witness idea → familiar known proof method → no strong noninvasive baseline → premature novelty claim. The positive contribution already established by PR #6231 is a corrected arithmetic transformation and regression evidence. It should not be inflated into a patent/paper whose distinct method has not survived an obvious competing implementation.

## 11. Evidence and correction ledger

| Claim or finding | Evidence class | Corrected conclusion |
|---|---|---|
| Slind et al. generates theorem-backed arithmetic hardware | **VERIFIED BY PRIMARY SOURCE** | Broad proof-producing arithmetic synthesis is prior art. |
| AMulet 2.2 certifies signed/unsigned multipliers in LPAC | **VERIFIED BY PRIMARY SOURCE** | Independent algebraic multiplier certificates already exist; not a documented general signed-FMA verifier. |
| Arisca supports MAC/dot and truncated width | **VERIFIED BY PRIMARY SOURCE** | Broad MAC algebraic verification is occupied; signed semantic encoding needs testing. |
| TRACE `-mac`, `-dot`, `-s` | **VERIFIED BY PRIMARY SOURCE** | Missing indispensable baseline. |
| TalisMan supports alternative algebraic AIG specifications | **VERIFIED BY PRIMARY SOURCE** | Missing reconstruction baseline; custom signed wide-MAC support unverified. |
| Konrad–Scholl checks proof logs against actual AIG and exports LPAC | **VERIFIED BY PRIMARY SOURCE** | Netlist binding and independent LPAC validation are not PCAS-exclusive. |
| Yosys current `arith_tree` emits `$fa`, masked rows, constants, final `$add`/prefix | **VERIFIED BY PRIMARY SOURCE** | Structural B5 feasible enough to be existentially threatening; exact snapshot behavior **not executed**. |
| B5 equals generator's certificate/checking on all cases | **INFERENCE / NOT TESTED** | Highly plausible for supported pre-techmap cases; neither proved nor measured. |
| PCAS current C1–C4 verifies actual netlist | **CONTRADICTED BY SPECIFICATION GAP** | It does not say how every real connection and CPA is independently bound; a hypothetical certificate can pass over a wrong netlist. |
| Default ripple CPA emits C2 FA records | **CONTRADICTED BY YOSYS SOURCE** | Default is `$add`, not necessarily FA records. |
| Linear-time bound, 250 kB, <1s at 64x64 | **UNSUPPORTED ESTIMATES** | Recast as conditional bound; benchmark needed. |
| 10× / 20pp improvement, zero false accepts | **UNSUPPORTED HYPOTHESES** | No M0 evidence; finite mutants never prove soundness. |
| C1 missing correction mask formula | **MATHEMATICAL INFERENCE + SOURCE-MATCHED SPECIAL CASE** | Algebraic explanation applies to properly specified negative-weight occurrence; not a universal BW mask. |
| Exhaustive `m,n<=8`, addend W<=20, fast M1 | **CONTRADICTED BY COUNTING** | Up to tens of billions of combinations/case; restrict exhaustive domain. |
| LPAC/Pacheck2 can directly check C1–C4 as written | **UNSUPPORTED** | Formal starting polynomials, target, modular semantics, derivation and actual acceptance missing. |
| IBM patent contains arithmetic synthesis-history + replay claims | **VERIFIED BY PRIMARY DOCUMENT** | Relevant risk/overlap, not an infringement or patentability conclusion. |
| Wave 10/11 and kill database support prior research kills | **VERIFIED REPOSITORY REPORTS; NOT RERUN** | Specific records accessed and reviewed; experiments themselves not recreated. |
| PCAS offers significant new scientific value over strong baselines | **UNSUPPORTED / M0 NEGATIVE ASSESSMENT** | No distinct demonstrated mechanism or advantage. |

## 12. Decision, kill rules, and what would justify a genuinely different proposal

### Final M0 verdict: **NO-GO**

Kill the current PCAS thesis as the centerpiece for a research paper or patent: *construction-time compressor-tree records + C1/C2 weighted conservation + linear independent checker + LPAC + speedup*. The parts are known or unproved, the netlist-soundness boundary is unresolved, and the strongest no-generator-change competitor has been neither refuted nor clearly distinguished. **Do not begin M1; do not spend effort on a Yosys fork, a certificate schema, benchmarking wrappers, or a patent filing based on this claim.** No `M1_REQUIREMENTS.md` is produced.

This is **not** the unsupported statement “no one can ever do original work in certifying arithmetic synthesis.” The appropriate possible future research problems are different and must earn their own M0:

1. **Proof preservation across actually destructive transforms:** exhibit a specific Yosys→ABC/technology-mapping transformation family where both the checkpoint-based reader and modern certifying SCA/CEC consistently fail under fair bounds, and introduce a *new compositional proof mechanism* that certifies the real mapped gates rather than trusting an additional pass. Prove or demonstrate why it is not standard translation validation, post-hoc SCA or synthesis-history replay.
2. **A new, independently proved compact certificate calculus for optimized arithmetic:** establish a nontrivial bound versus existing LPAC representations and a formal checker theorem over actual gates. An assertion of “linear because full adders are linear” is insufficient.
3. **A verified negative result / robust bug reproducer:** publish the known Yosys correction fault and disciplined cross-tool comparisons as reproducibility/engineering, if a meaningful audience exists. Do **not** market this as PCAS novelty or build paper claims around a single vendor bug.

**Evidence necessary to reopen research funding:** first, a written precise problem and source/graph semantic contract; second, an explicit counterexample showing why *best possible* B5 with the same spec cannot reconstruct needed information (not a contrived parser limitation); third, a concrete new mechanism with its own theorem or falsifiable property; fourth, prior-art differentiation against Slind, AMulet, Arisca, TRACE, TalisMan, Konrad–Scholl, Pacheck2 and the IBM patent; fifth, a fair baseline-support matrix and pre-registered effect size. If these cannot be written down without coding, stay **NO-GO**.

### Residual uncertainty, explicitly preserved

- We did **not** execute or build a B5 RTLIL reader; verified existence of `$fa` emission in source is not a proof that all post-`arith_tree` snapshots retain every useful relationship.
- We did **not** reproduce TRACE/Arisca/TalisMan on the same signed wide-MAC circuit, or establish their failure cases. Their GitHub-documented supported modes and paper claims are primary-source observations, not our timing data.
- We did **not** inspect every proprietary synthesis certification feature, all backward/forward paper citations, unpublished theses, or full patent families. Therefore absence of the *exact* PCAS implementation in inspected sources is not proof of novelty.
- We did **not** formally prove impossibility of an improved bit-heap certificate, and did **not** disprove a conditional linear checker for a restricted structured IR. Those are narrower and plausible than the claimed end-to-end contribution.
- The user's GitHub research archive records experimental outcomes, but its assertions were **read**, not rerun, by this audit.

## 13. Primary-source references and audit trail

Public sources directly inspected or corroborated (links identify the actual source, not merely a search snippet):

1. Slind, Owens, Iyoda, Gordon, *Proof producing synthesis of arithmetic and cryptographic hardware*, *Formal Aspects of Computing* 19(3), 343–362 (2007), DOI [10.1007/s00165-007-0028-5](https://doi.org/10.1007/s00165-007-0028-5); [full paper text](https://www.researchgate.net/publication/225163217_Proof_producing_synthesis_of_arithmetic_and_cryptographic_hardware).
2. Kaufmann and Biere, *AMulet 2.0 for Verifying Multiplier Circuits*, TACAS (2021), [primary PDF](https://fmv.jku.at/papers/KaufmannBiere-TACAS21.pdf); [AMulet 2.2 source/README](https://github.com/anthropics/amulet2); *Improving AMulet2 ...*, *STTT* (2023), [DOI](https://doi.org/10.1007/s10009-022-00688-6).
3. Li, Li, Xu, *Arisca: A Parameterized Symbolic Algebra Framework for Arithmetic Circuit Verification*, July 2026, [arXiv:2607.10257](https://arxiv.org/abs/2607.10257), [primary source](https://github.com/LittleBlackCQ/arisca).
4. Kleinekathöfer, Weingarten, Datta, Drechsler, *TRACE: Traversal and Reasoning Algebraic Computing Engine for Formal Hardware Verification*, Aug. 17, 2026, [arXiv:2608.16458](https://arxiv.org/abs/2608.16458), [source/README](https://github.com/jan-kl/trace).
5. [TalisMan source and CLI documentation](https://github.com/d-kfmnn/talisman); [Pacheck2 source/README](https://github.com/d-kfmnn/pacheck2).
6. Konrad and Scholl, *Symbolic computer algebra for multipliers revisited — demonstrating the significance of order and phase optimization*, *Formal Methods in System Design* 68(2) (2026), DOI [10.1007/s10703-026-00494-9](https://doi.org/10.1007/s10703-026-00494-9), especially §§4.3, 5.5.
7. [Yosys `arith_tree` source](https://github.com/YosysHQ/yosys/blob/main/passes/techmap/arith_tree.cc); [Yosys compressor implementation](https://github.com/YosysHQ/yosys/blob/main/kernel/compressor_tree.cc); [Yosys `arith_tree` docs](https://yosyshq.readthedocs.io/projects/yosys/en/stable/cmd/index_passes_techmap.html). Source was read via the connected GitHub interface; default-branch SHA was not globally frozen.
8. [IBM US12475287B2 complete granted patent/claims](https://patents.google.com/patent/US12475287B2/en), especially independent claims 1, 5 and 8, and descriptive arithmetic compressor examples. This is a *technical novelty* comparator, not legal advice.
9. [CIRCT datapath dialect](https://circt.llvm.org/docs/Dialects/Datapath/); [project Yosys PR #6231](https://github.com/YosysHQ/yosys/pull/6231), as referenced by the supplied package.
10. User's connected research archive: [kill database](https://github.com/meetbhadra701-cloud/all-the-info/blob/main/05_KILLED_CANDIDATES/RESEARCH_KILL_DATABASE.md), [Wave 10 summary](https://github.com/meetbhadra701-cloud/all-the-info/blob/main/12_WAVE_10_EXPERIMENTAL_DISCOVERY/00_EXECUTIVE_SUMMARY.md), [Wave 10 final decision](https://github.com/meetbhadra701-cloud/all-the-info/blob/main/12_WAVE_10_EXPERIMENTAL_DISCOVERY/06_FINAL_DECISION.md), [Wave 11 adversarial review](https://github.com/meetbhadra701-cloud/all-the-info/blob/main/13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION/03_ADVERSARIAL_REVIEW.md), and [Wave 11 evolution](https://github.com/meetbhadra701-cloud/all-the-info/blob/main/13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION/04_HYPOTHESIS_EVOLUTION.md).

**Package inspection:** `FINAL_IDEATION_REPORT.md`, `PROJECT_HANDOFF_FOR_CHATGPT.md`, `FIRST_EXPERIMENT_SPEC.md`, `CLAIM_TO_PRIOR_ART_AND_KILL_REGISTER.md`, `SOURCE_LEDGER.md`, `FRESH_CHAT_STARTER_PROMPT.md`, `NEXT_M0_RESEARCH_PROMPT.md`, and `INDEPENDENT_REVIEW_AND_CORRECTIONS.md` — eight files, read-only. Source links are supplied for external verification. No test command, checker implementation, synthesis run, patent prosecution search or benchmarking result is implied by this report.
