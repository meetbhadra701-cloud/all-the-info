# Yosys PR #6231 — Contribution Ownership and Policy Review

PR: <https://github.com/YosysHQ/yosys/pull/6231>  
Title: `Fix signed FMA correction in wide compressor trees`  
Head: `meetbhadra701-cloud/yosys:exp6-fma-fix`  
Commit: `30b851e63ff071578cda4e1e49eccd367f7881d9`

## Executive conclusion

The technical defect is real and the patch has substantial bounded evidence:
the clean current-main build fails the packaged functional SAT regression, the
patched build passes it, and the patch is limited to the signed partial-product
correction plus one functional regression test.

The authorship/policy position is separate. The saved development history shows
that Codex generated the C++ correction, its C++ comments, the regression test,
the commit message, the reports, and the pull-request draft. Codex also ran the
builds, synthesis, formal checks, packaging, push, and PR creation. The user
selected the research direction, supplied the experiment specifications and
stop rules, directed the investigation, made the project decisions, approved
submission, and supplied the public GitHub identity. The available record does
not establish that the user personally authored the C++ implementation or its
comments.

That distinction matters under the current YosysHQ policy. This review should
not be used to claim that the existing PR is policy-compliant, that the code was
human-authored, or that the user independently discovered every implementation
detail. The technically honest next step is for the user to disclose the AI
assistance personally and ask maintainers whether they prefer the PR to remain
open, be revised through a genuinely human-authored change, or be closed in
favor of a bug report containing the minimal reproducer.

## 1. YosysHQ policy provisions

Source: [Interim YosysHQ LLM Policy](https://yosyshq.discourse.group/t/interim-llm-policy/163),
posted August 31, 2026. The policy is interim and expressly subject to later
revision.

### General rule

The policy states: “Please do not file pull requests to our GitHub projects
containing LLM generated code.” This is the governing default, not a statement
that a technically correct result automatically overrides the rule.

### LLM-generated bug fixes

The policy specifically discusses LLM-generated bug fixes. It asks users to
refrain from sending such fixes and instead use the LLM to produce a minimal
failing test case and submit a regular issue. It also says that maintainers may
independently fix the bug, including applying an equivalent change themselves
when there is effectively no creative choice. That is maintainer discretion; it
is not permission for the submitter to represent generated code as human-authored.

PR #6231 is directly within this provision: it is a correctness repair to core
Yosys code, and the available history records Codex generating the repair.

### Human attribution and technical responsibility

The policy says that every code change should be attributed to a human who
authored it and can explain and defend it during review and later. It generally
allows “AI assisted” code, but defines that assistance as a commitment to defend
the choices in the code as the human’s choices, even when an AI suggested them.

This creates a real distinction:

- Directing an AI experiment is not automatically the same as authoring the
  generated C++.
- Approving a patch is not automatically the same as understanding every line.
- Technical ownership can become credible if the user independently learns,
  checks, and accepts responsibility for the exact implementation, but that
  personal state cannot be inferred from the tool transcript alone.

### Case-by-case exceptions

The policy permits exceptions only case by case, especially where a prompt is
specific enough that different models would produce essentially the same simple
code and a student would reasonably be expected to produce it. For such an
exception, the policy says the commit message should include relevant
information, including the full prompt that produced the code.

This patch is not obviously covered by that exception. It modifies a compiler
kernel arithmetic transformation, required source-level reasoning about
Baugh–Wooley correction terms, and was produced through a multi-step
investigation. Only YosysHQ maintainers can decide whether an exception applies.

### Comments and commit messages

The policy separately states a complete ban on LLM-generated code comments and
commit messages. The current patch contains a generated explanatory comment in
`kernel/compressor_tree.cc`, and the commit message was generated during the
Codex workflow. This is a specific policy concern, not something to conceal by
rewriting history or claiming independent authorship.

### What the policy does and does not establish

Expressly established by the policy:

- LLM-generated code should generally not be submitted in a PR.
- LLM-generated bug fixes should generally be reduced to a failing test and an
  issue instead.
- AI-assisted code can be acceptable when a human authors and can defend the
  choices, subject to maintainer judgment.
- Exceptions are case by case, not automatic.
- LLM-generated code comments and commit messages are not acceptable.

Not established by the policy:

- That a real bug creates an automatic exception.
- That a user directing the work is automatically the author of generated code.
- That passing formal tests proves policy compliance.
- That absence of maintainer comments means approval.

## 2. Verified development history

The following reconstruction is based on the saved reports, logs, scripts, RTL,
source checkout, and Git history in the experiment outputs. Paths below are
relative to the saved experiment workspaces.

### Experiment 1 — MUXWISE feasibility

The initial question was whether selective sharing of mutually exclusive RTL
operators represented an optimization opportunity beyond Yosys. The baseline
compared shared and unshared add descriptions across W=8, 16, 32, and 64.

Verified outcome:

- The correct and deliberately incorrect designs were handled correctly by the
  formal setup.
- `opt_share` recognized the basic common-operand sharing transformation.
- Normal synthesis and mapping converged the tested forms.
- The multi-operator design showed intermediate sharing choices, but no useful
  final area/timing opportunity was established.
- Physical design was not executed.
- Final disposition: **A — BASIC IDEA ALREADY COVERED**.

Evidence: `muxwise-experiment-01/EXPERIMENT_REPORT.md` and its `logs/`,
`rtl/`, and `results/` directories.

### Experiment 2 — optimization failure discovery

The investigation broadened to resource sharing, arithmetic structure,
bit-width reduction, and ABC mapping sensitivity. It completed 136 valid
synthesis runs using Yosys 0.69+77 and ABC 1.01, plus seven formal checks.

Verified outcome:

- Resource-sharing and width-trim differences disappeared in normal downstream
  synthesis.
- The documented `-arith_tree` configuration produced different final generic
  mapped structures across related arithmetic families.
- The observation was retained as F-AT-01, not promoted to a new algorithmic
  opportunity, because it was an existing documented configuration and lacked
  physical validation.
- No viable new optimization gap was found.

Evidence: `muxwise-experiment-02/EXPERIMENT_02_REPORT.md` and
`results/surviving_findings.csv`.

### Experiment 3 — physical prosecution of F-AT-01

The arithmetic-tree/default comparison was taken through Nangate45 mapping,
STA, placement, and global routing for selected designs.

Verified outcome:

- Arithmetic-tree area and delay varied by circuit family.
- FIR4 W16 and mixed arithmetic showed larger and slower arithmetic-tree
  implementations in the pilot.
- Add-chain W64 showed a small area decrease coupled with worse delay.
- The experiment discovered that a zero process exit code is not sufficient to
  classify a Yosys SAT proof as PASS; the log verdict must be checked.
- A formal counterexample invalidated inherited PASS labeling.
- Final disposition: **E — INCONCLUSIVE**.

Evidence: `muxwise-experiment-03/EXPERIMENT_03_REPORT.md`.

### Experiment 4 — correctness prosecution

The formal harness was repaired to use an explicit output mismatch, to inspect
the SAT verdict text, to retain witnesses, and to distinguish PASS, FAIL,
timeout, and setup failure. Independent Icarus replay and a fixed-width
reference model were added.

Verified outcome:

- Normal synthesis matched the RTL.
- Default `arith_tree` diverged immediately after the arithmetic-tree pass.
- Techmap and ABC preserved the mismatch rather than creating it.
- FIR4 W4 witness: signed inputs `x0=7`, `x1=12`, `x2=9`, `x3=6`; expected
  `0x00000`, candidate `0x00180`.
- FIR4 W8 witness: `234, 22, 100, 0`; expected `0x000186`, candidate
  `0x001986`.
- `-no-fma` avoided the observed failure.
- The binary provenance was dirty, so clean-upstream confirmation was still
  required.

Evidence: `muxwise-experiment-04/EXPERIMENT_04_REPORT.md`, `witnesses/`,
`replay/`, and `results/`.

### Experiment 5 — clean reproduction and local repair

The exact upstream commit
`9ff27d29c672cc5274ce69106145a8aed7c9ba3d` was built cleanly. The defect
reproduced in the original FIR4 at W4/W8 and in a minimized two-product signed
FMA at W4/W8/W16.

The root-cause investigation inspected `kernel/compressor_tree.cc`,
`CompressorTree::generate_partial_products()`, the generated RTLIL, and
`kernel/macc.h`. It identified the one-bit signed Baugh–Wooley correction at
`width_a + width_b - 1` as insufficient for a wider accumulation.

The local patch changed that correction into a mask extending from the product
sign position through the target width. It also evaluated the width sum in a
wider integer type before the range check.

Verified outcome:

- Clean unpatched W4/W8/W16 minimized cases failed.
- Patched cases passed.
- The full FIR4 W16 proof timed out and was not treated as PASS.
- Existing arithmetic-tree tests passed, but they did not catch this functional
  defect.

Evidence: `yosys-fma-correctness-investigation/FINAL_REPORT.md`,
`source_analysis/ROOT_CAUSE.md`, `patch/arith_tree_fix.patch`, and
`results/`.

### Experiment 6 — hostile validation

Current upstream main at
`e8db64c609c7ae4574e66bbd475f5f10f36d7a31` was built cleanly. The mathematical
review independently checked the correction identity and a bounded bit-level
model.

Verified outcome:

- Current clean main failed original FIR4 W4/W8 and minimized W4/W8/W16.
- The patched build passed those cases.
- The patched bounded matrix had 42 completed PASS proofs, two timeouts, and no
  completed patched counterexample.
- All 13 pre-existing arithmetic-tree tests passed on both builds; the added
  packaged regression passed on the patched build and failed with a real SAT
  counterexample on clean current main.
- The full FIR4 W16 proof remained inconclusive.
- The final saved engineering disposition before submission was **C — PATCH
  CORRECT FOR TESTED CASES, BUT IMPORTANT VALIDATION GAPS REMAIN**.

Evidence: `yosys-fma-final-validation/FINAL_VALIDATION_REPORT.md`,
`mathematical_review/CORRECTION_PROOF.md`, `review/PATCH_REVIEW.md`,
`review/REMAINING_RISKS.md`, and `submission/final.patch`.

### Submission preparation and PR creation

After the user approved submission, Codex:

- verified the checkout, branch, commit, and two changed files;
- amended the commit to `meetbhadra701-cloud <meetbhadra701@gmail.com>`;
- added the user’s fork as `fork` while preserving `origin`;
- created the fork when it did not exist;
- pushed only `exp6-fma-fix` without force-push;
- created PR #6231; and
- verified the remote commit and PR metadata.

These are verified actions, but they do not by themselves establish that the
user authored the code.

## 3. AI-assistance inventory and ownership boundary

### Actions visibly performed by Codex

The available transcript and artifacts show Codex performing the following:

- generated the experiment RTL, Yosys scripts, formal miters, analysis scripts,
  and reports;
- generated the `kernel/compressor_tree.cc` correction;
- generated the explanatory C++ comments in that correction;
- generated the official `tests/arith_tree/arith_tree_signed_fma_wide.ys`
  regression;
- ran Docker builds, Yosys, ABC, SAT, Icarus, mapping, and analysis commands;
- interpreted logs and summarized the mathematical mechanism;
- generated the commit message and pull-request draft;
- amended the local commit after receiving the user’s public identity;
- pushed the branch and opened PR #6231 after explicit authorization.

### Actions attributable to the user from the available record

The user:

- selected and framed the MUXWISE research question;
- supplied the detailed experimental requirements, adversarial stop rules, and
  correctness constraints for Experiments 1–6;
- directed the transition from optimization research to compiler-bug repair;
- approved the specific contribution for submission;
- supplied the public GitHub identity and authorized fork/push/PR actions;
- is now seeking to understand and take responsibility for the arithmetic,
  source change, and validation.

### Facts requiring the user’s personal confirmation

The artifacts do not establish whether the user has personally:

1. read and understood every changed C++ line;
2. independently derived the correction rather than accepting Codex’s derivation;
3. reproduced the formal failure without Codex’s assistance;
4. checked the C++ implementation against Yosys conventions;
5. written or substantially rewritten any code, comments, or commit message;
6. can answer the maintainer questions in this document without assistance; or
7. accepts responsibility for defending the patch after this conversation.

Those are questions for the user, not facts to be filled in optimistically.

## 4. Technical ownership study guide

The goal is understanding sufficient to answer maintainers honestly, not to
produce a scripted authorship claim.

### 4.1 What is an FMA?

An FMA datapath computes one or more products and adds them into a result,
typically without independently rounding or truncating each product. In this
case, the two-product form is conceptually:

```text
y = sign_extend(a) * 3 + sign_extend(b) * (-2)
```

Yosys represents this class of operation through `$macc_v2` terms before the
arithmetic-tree expansion. The term “FMA” here describes the fused multiply-
accumulate structure, not a floating-point operation.

### 4.2 What is a compressor tree?

Multiplication creates many bit rows. A compressor tree reduces those rows to
two rows using full adders and, where selected, 4:2 compressors. A final
carry-propagate adder then produces the result. In this source,
`generate_partial_products()` creates the rows and correction constants;
`reduce_scheduled()` compresses them. The patch changes row construction, not
the compressor strategy or final adder.

### 4.3 What is Baugh–Wooley multiplication?

Baugh–Wooley is a regular partial-product construction for two’s-complement
multiplication. Instead of carrying negative sign-bit weights through an
irregular array, it inverts selected sign-related partial products and adds
correction constants. The source implements the inversions with per-row masks
around lines 65–95 of `kernel/compressor_tree.cc`, then emits correction
constants around lines 100–128.

### 4.4 Why are correction terms needed?

The most significant bit of a two’s-complement operand has negative weight.
The regular AND partial-product array assumes positive bit weights, so the
sign-bit inversions and correction constants compensate for that difference.
The correction is arithmetic, not metadata: omitting or misplacing it changes
the output bits.

### 4.5 What is native product width?

For operand widths `m` and `n`, the conventional full product width is
`P = m + n`. “Native product width” means retaining that product-width result
before embedding it in a wider accumulation. In the source, the compressor
tree’s target width is `W`; the defect appears when `W > P`.

### 4.6 What happens in a wider accumulation?

The product rows are extended to the compressor width. In this implementation
the rows are zero-extended with `extend_u0(width, false)`. A signed product’s
correction must therefore be represented through the entire target width. A
single one at `P-1` leaves the higher sign-extension bits absent.

### 4.7 Why did the old implementation fail?

The old code was:

```cpp
if (a_signed || b_signed)
    push_one_at(width_a + width_b - 1);
```

That emits only `2^(P-1)`. For a wider target, the required correction is the
mask with ones from `P-1` through `W-1`. The missing high bits produce a
modular error of one native product modulus per affected signed product.

For the original W4 FIR4 witness, the relevant product widths were 4×3 and
4×4, so the observed error is:

```text
2^7 + 2^8 = 0x080 + 0x100 = 0x180.
```

The W8 witness produced the corresponding `0x1800` difference. These are
observed matches to the source-level model, not merely cell-count differences.

### 4.8 Why does the new mask work?

The new code emits:

```text
C_old = 2^(P-1)
C_new = sum(i=P-1..W-1) 2^i
```

For `W > P`, the new term supplies the missing high correction bits. Modulo
`2^W`, the difference between the old and new constants is the native product
modulus `2^P`. At `W=P`, the range has one bit and behavior is unchanged. For
`W<P`, the guard emits no final correction term, matching the old guard
behavior for this term; this does not prove every other truncation detail.

The independent identity check covered 360 selected width pairs, and the
bit-level model found no supported-domain failures in its 576 configuration
rows. This remains bounded evidence, not a complete proof of all Yosys
arithmetic.

### 4.9 What exactly changed in C++?

In `CompressorTree::generate_partial_products()`:

1. The old single-bit final correction was replaced by a conditional mask.
2. `sign_extension_start` is computed using `long long` before the range check.
3. A width-`W` constant vector is initialized to zero.
4. Bits from `sign_extension_start` through `W-1` are set to one.
5. That vector is added as one product-row operand at offset zero.

No compressor strategy, final-adder option, FMA enablement, FIR coefficient,
or witness-specific condition was added.

### 4.10 Why are unsigned products unaffected?

The added block is guarded by `if (a_signed || b_signed)`. For an unsigned ×
unsigned product, the block is inactive, and the existing unsigned partial
product construction is unchanged. The bounded model also found no unsigned
failures before or after the patch.

Mixed signedness is a boundary. `Macc::from_cell()` asserts equal A/B
signedness for each `$macc_v2` product, so mixed RTL expressions that remain
mixed may not exercise this exact Baugh–Wooley path. They must not be described
as universal validation of the changed code.

### 4.11 What does the packaged regression prove?

`tests/arith_tree/arith_tree_signed_fma_wide.ys`:

1. Defines a small signed two-product FMA implementation.
2. Runs `synth -top fma_impl -arith_tree`.
3. Renames the synthesized implementation to `fma_candidate`.
4. Defines a separately elaborated `fma_gold` reference.
5. Builds `fma_miter` with `mismatch = |(candidate_y ^ gold_y)`.
6. Runs `sat -prove mismatch 0 -verify -set-def-inputs -show-ports`.

The clean current-main build produces a real SAT counterexample, including
`a=6`, `b=7`, and exits nonzero. The patched build reports SAT success and
exits successfully. This is a functional regression, not a cell-count or
internal-name test.

It proves the fixed W4 packaged instance for all unconstrained defined input
values. It does not prove every width, every `$macc_v2` parameter vector, or
the full FIR4 W16 design.

### 4.12 Remaining limitations

The honest limitations are:

- full FIR4 W16 proof timed out;
- two larger bounded matrix cases timed out;
- all legal `$macc_v2` combinations were not exhaustively proved;
- mixed signedness often does not enter the affected path;
- no direct unit-level proof of `generate_partial_products()` exists;
- the full Yosys test suite was not run;
- no physical-design validation is relevant to this correctness PR;
- current public PR #6231 has no review or CI result yet.

## 5. Hostile maintainer interview

The questions below are intentionally difficult. The answer key follows them.

### Questions

1. What exactly is fused in this FMA path, and why is this not floating-point
   FMA?
2. Given operand widths `m` and `n`, what are `P` and `W`, and which one
   controls whether the correction must be extended?
3. Where in `compressor_tree.cc` are sign-related partial products inverted?
4. What is the old correction constant, and what is the new correction mask?
5. Why is one correction bit correct at `W=P` but incorrect at `W>P`?
6. Derive the W4 FIR error `0x180` from the relevant product widths.
7. What exact source-level behavior makes the missing bits matter: sign
   extension, zero extension, or truncation?
8. Why does the patch not change unsigned × unsigned products?
9. Why is mixed RTL signedness not equivalent to proving the affected
   `$macc_v2` Baugh–Wooley path?
10. What does the packaged SAT miter prove, and what does it not prove?
11. Why did the earlier harness incorrectly label a failing SAT result as
    PASS?
12. What evidence shows that techmap or ABC did not create the original bug?
13. Why should a maintainer care about the `long long` intermediate?
14. What do the 42 PASS results and two timeouts justify saying?
15. If a maintainer asks whether you personally authored the patch, what is
    the accurate answer based on the saved history?

### Worked answer key

1. The path fuses products and additions in a `$macc_v2` representation and
   expands them into a shared compressor tree. It operates on integer bit
   vectors, not floating-point values.
2. `P=m+n` is the native full product width. `W` is the compressor/accumulator
   width. The correction needs extension when `W>P`.
3. The row loop computes `row_is_bottom`, `any_inversion`, and a per-row mask;
   the inversion decision is around lines 65–93. The correction constants are
   emitted after the row loop.
4. Old: one at `P-1`. New: ones at every position `P-1` through `W-1`, when
   that range is valid.
5. At `W=P`, the range contains exactly one bit. At `W>P`, the higher bits are
   part of the two’s-complement sign correction and cannot be omitted.
6. The source analysis identifies 4×3 and 4×4 signed products. Their missing
   correction contributions are `2^7` and `2^8`, totaling `0x180`.
7. The source extends partial-product rows to the target width with unsigned
   zero extension. The correction must restore the signed interpretation
   across the wider width.
8. The new block is conditional on signedness; unsigned construction does not
   receive the correction. The bounded unsigned cases remained correct.
9. `Macc::from_cell()` requires equal A/B signedness for each product. A mixed
   RTL expression can be normalized into a different representation and may
   never reach the changed Baugh–Wooley path.
10. It proves the W4 candidate’s output equals the independently elaborated
    reference for all defined inputs. It does not prove all widths, all
    compressor arrangements, or the full FIR4 W16 instance.
11. The old harness trusted process exit status. Yosys can return zero while
    printing `SAT proof finished - model found: FAIL!`; the repaired harness
    parses the proof verdict.
12. The earliest divergence was immediately after `arith_tree`; later techmap
    and ABC preserved it. Independent simulation and a reference model agreed.
13. `width_a + width_b - 1` could theoretically overflow signed `int` before
    the range check. The wider intermediate removes that arithmetic risk.
14. They support the patch over the tested bounded domain. They do not convert
    the timeouts into PASS and do not establish universal compiler correctness.
15. The accurate answer is that Codex generated the current C++ correction and
    comments, while the user directed and approved the work. The user should
    claim personal authorship only for work they actually performed and can
    honestly defend.

## 6. Public PR inspection

Verified through the authenticated GitHub CLI on the public repository:

- PR: [#6231](https://github.com/YosysHQ/yosys/pull/6231)
- State: **OPEN**
- Draft: no; it is a normal open PR.
- Base: `YosysHQ/yosys:main`
- Head: `meetbhadra701-cloud/yosys:exp6-fma-fix`
- Head commit: `30b851e63ff071578cda4e1e49eccd367f7881d9`
- Author: `meetbhadra701-cloud`
- Changed files: exactly two, the intended C++ source and regression test.
- Reviews: none.
- Maintainer comments: none.
- Review decision: none.
- Check runs: none reported.
- GitHub merge state: `BLOCKED`; GitHub also reports the branch as mergeable.

The `BLOCKED` merge state is not a technical rejection. With no reviews,
comments, or check runs, there is currently no public maintainer conclusion
about either the code or the AI-policy issue.

## 7. Factual disclosure outline for the user

This is an outline, not a generated comment to paste. The user should write
and submit any public response personally.

Facts the user can state if accurate:

1. The work began as a directed investigation into whether Yosys already
   eliminated a proposed resource-sharing optimization.
2. The investigation found a reproducible arithmetic-tree correctness defect,
   not the originally hypothesized optimization opportunity.
3. The clean-current-main defect was reproduced with functional SAT miters and
   independent replay.
4. Codex assisted with experiment execution, source analysis, implementation,
   regression preparation, report generation, and submission packaging.
5. The current C++ patch, its comments, the regression test, and the commit
   message were generated during that Codex-assisted workflow.
6. The user selected the research scope, directed the experiments, reviewed
   findings, made the decision to submit, and is studying the implementation
   and evidence to take responsibility for the contribution.
7. The user recognizes the YosysHQ interim LLM policy and is asking
   maintainers which contribution path they prefer.
8. The available validation is bounded: 42 completed patched PASS proofs, two
   timeouts, and an inconclusive full FIR4 W16 proof.

Claims the user should not make unless independently true:

- “I wrote the patch.”
- “The patch is entirely human-authored.”
- “The patch is universally proven correct.”
- “The policy permits this because I directed the AI.”
- “The absence of comments means maintainers accepted the AI use.”

## 8. Possible maintainer outcomes

### A. Maintainers permit the existing PR to proceed

The user should acknowledge the permission, answer technical questions in
their own words, and make only changes they personally author and understand.
No claim of human authorship should be made retroactively for the existing
generated code.

### B. Maintainers request explicit AI disclosure or more explanation

The user should provide a factual account like the inventory above, identify
which artifacts were generated with Codex, separate personal decisions from
generated implementation, and answer the technical questions directly. The
user should not minimize the assistance or imply that formal results resolve
the policy question.

### C. Maintainers request a genuinely human-authored revision

The user should personally re-derive and write any requested source, comments,
tests, and commit message, following the maintainer’s instructions. The goal
must be genuine understanding and authorship, not stylistic rewriting to evade
AI detection. The user should preserve the original history and disclose the
earlier assistance if asked.

### D. Maintainers prefer closing the PR and filing an issue

This is consistent with the policy’s specific recommendation for
LLM-generated bug fixes: retain the minimal failing regression, provide the
clean counterexample and exact reproduction command, and let YosysHQ own the
upstream implementation. The user should accept that outcome without opening
a duplicate PR.

## 9. Recommended next public action

The most defensible action is a personally written, factual disclosure to the
maintainers asking which path they prefer. It should not be an AI-generated
claim of authorship, and it should not include a replacement commit message or
generated code comments.

Given the policy’s specific treatment of LLM-generated bug fixes, the user
should be prepared for maintainers to request closure of PR #6231 and a
minimal issue/reproducer instead. The user should not modify, push, close, or
open anything further without making that personal response and receiving the
maintainer’s direction.

## Source index

- Policy: <https://yosyshq.discourse.group/t/interim-llm-policy/163>
- Public PR: <https://github.com/YosysHQ/yosys/pull/6231>
- Experiment 1: `muxwise-experiment-01/EXPERIMENT_REPORT.md`
- Experiment 2: `muxwise-experiment-02/EXPERIMENT_02_REPORT.md`
- Experiment 3: `muxwise-experiment-03/EXPERIMENT_03_REPORT.md`
- Experiment 4: `muxwise-experiment-04/EXPERIMENT_04_REPORT.md`
- Experiment 5: `yosys-fma-correctness-investigation/FINAL_REPORT.md`
- Experiment 6: `yosys-fma-final-validation/FINAL_VALIDATION_REPORT.md`
- Current patch: `yosys-fma-final-validation/submission/final.patch`
- Packaged regression: `yosys-fma-final-validation/current_upstream/patched-source/tests/arith_tree/arith_tree_signed_fma_wide.ys`
