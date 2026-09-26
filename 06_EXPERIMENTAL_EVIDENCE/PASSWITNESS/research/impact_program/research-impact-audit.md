# PassWitness research-impact audit

Date: 2026-09-23  
Stable release audited: `v0.1.0` at `a1bf9ae4df5d718b310d126527e1b82104ada781`  
Research workspace: `research/impact_program/`

This is a feasibility and prior-art report, not a paper, novelty claim, or
release change. No tracked files outside this workspace were modified.

## Executive disposition

**B. IMPORTANT FAILURE FAMILY FOUND, BUT THE RESIDUAL GAP IS UNRESOLVED.**

The most defensible research lead is semantic-contract validation for
hardware compiler representation boundaries: width, signedness, initialization,
unknown values, and synthesis don't-cares. Multiple independently documented
failures show that this is consequential. Existing work already provides
strong pieces—formal equivalence, X-propagation semantics, pass-level
translation validation, and hardware compiler fuzzing—but no evidence gathered
here establishes a general residual method that is both new and experimentally
ready.

Pass-localized equivalence and formal-guided reduction, considered by
themselves, do not survive prior-art prosecution as a strong contribution.
Gauntlet performs pass-by-pass translation validation and reports the pass where
semantic bugs arise; EQY provides hardware equivalence workflows including
X-propagation; CIRCT provides logical equivalence tooling; and recent work
addresses translation validation through a complex accelerator compiler flow.

The next gate is a small, independently curated benchmark experiment—not
feature development in PassWitness.

## 1. Citation-readiness audit

### Observed repository state

| Item | Finding | Consequence |
|---|---|---|
| Release commit | `a1bf9ae4df5d718b310d126527e1b82104ada781` | Matches the audited v0.1.0 tag. |
| Public release | GitHub repository and `v0.1.0` tag are present | The software has a citable version anchor, but not yet an archival DOI. |
| License | `LICENSE` is MIT; copyright line names “PassWitness contributors” | Reuse is documented at project level. |
| `CITATION.cff` | Missing from the release root | GitHub/Zenodo cannot consume project citation metadata automatically. |
| Individual authors | Not identified in tracked metadata | Do not invent names, affiliations, email addresses, or ORCID IDs. |
| DOI | None verified | Do not add a DOI field until Zenodo actually mints one. |
| Reproducibility | `docs/reproducibility.md`, release demo, attribution, and limitations exist | Good basis for archiving; historical Yosys executables are intentionally not bundled. |
| External attribution | `docs/attribution.md` exists | Yosys, EQY, SymbiYosys, Verismith, VlogHammer, VeriXmith, and sv-bugpoint are identified as external projects. |
| Current audit test execution | Blocked on this host: Python 3.14 has no `pytest`, `pip`, or `venv` | Existing release records must not be restated as a fresh passing run. |
| External reducers | `creduce`, `sv-bugpoint`, and `gh` are not on this host | Their availability is environment-specific; prior release evidence records an isolated sv-bugpoint run. |
| Yosys wrappers | Clean and patched wrappers report Yosys 0.69+; the wrappers carry distinct source-revision claims | Binary/source provenance remains a separate field, as documented by the release. |

The CFF draft in this workspace is syntactically shaped as a CFF 1.2.0
software citation, but its project entity is a placeholder for unresolved
individual authorship. CFF requires authors and supports repository, version,
commit, license, and identifier metadata; it does not authorize us to infer
human authors from a GitHub account or a commit identity. See the [CFF schema
guide](https://github.com/citation-file-format/citation-file-format/blob/main/schema-guide.md)
and [GitHub's citation-file documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-repository/about-citation-files).

### Exact Zenodo checklist

This is a future maintainer action list. It was not executed by this audit.

1. Resolve the individual author list, ordering, affiliations, contact address,
   and ORCID identifiers. Obtain explicit approval for the citation metadata.
2. Move the approved CFF metadata into the repository root in a new, reviewed
   commit. Do not alter the `v0.1.0` tag in place.
3. Verify that the release tree contains no private paths, credentials,
   generated outputs, compiled Yosys binaries, or temporary research data.
4. Connect the GitHub account to Zenodo, synchronize repositories, and enable
   `meetbhadra701-cloud/passwitness`. Zenodo documents that enabled repositories
   are ingested when new GitHub releases are created; see [Enable a
   repository](https://help.zenodo.org/docs/github/enable-repository/).
5. Decide whether to reserve a concept DOI before creating a new archival
   release. Do not fabricate a DOI in CFF or documentation.
6. Create a new archival release only after deciding whether the archive is
   `v0.1.0` exactly or a later metadata-only release. Inspect the generated
   archive before publication.
7. Record the exact Git commit, tag, archive checksum, repository URL, and
   Zenodo version DOI. Zenodo assigns a DOI when the record is published; see
   [Archive a release from GitHub](https://help.zenodo.org/docs/github/archive-software/github-upload/).
8. Verify the downloaded archive from an unrelated directory: install the
   package, run the documented control, and confirm that references use valid
   relative paths. Check that the archive does not contain the developer's
   Windows/WSL path.
9. Add the version DOI and, if desired, the concept DOI to a subsequent
   reviewed metadata commit. Do not rewrite the historical release tag.
10. Preserve both the version DOI and concept DOI. Zenodo documents the
    distinction between a DOI for one version and the DOI representing the
    software collection; see [DOI versioning](https://zenodo.org/help/versioning).

## 2. Factual technical-publicity roadmap

No public post is authorized by this report. If publicity is later approved,
the evidence should be presented in this order:

1. **Problem.** Final RTL-to-netlist equivalence failure tells an engineer that
   behavior changed, but not which synthesis transition introduced it.
2. **Demonstration.** Show the signed-FMA result with exact clean and patched
   executable provenance, the `alumacc` last passing checkpoint, the
   `arith_tree` first failing transition, the SAT witness, and the independent
   replay result.
3. **Evidence discipline.** State that the defect was investigated by this
   project and that the associated [Yosys PR #6231](https://github.com/YosysHQ/yosys/pull/6231)
   is still shown as open and under review as of this audit; it must not be
   described as merged.
4. **Historical reproductions.** Identify Yosys #1047, #6085, and #997 as
   previously reported defects reproduced or examined by the project, not as
   new discoveries. Yosys #1047 links to merged PR #1049; #6085 documents a
   signed-negative-constant `cmp2lut` failure; #997 documents a lost register
   initialization in an affected historical build.
5. **Reduction.** Separate the real signed-FMA source reduction from the
   intentionally injected arithmetic-fault reduction. Do not use the injected
   70.63% size reduction as evidence about the real compiler defect.
6. **Limitations.** State the small combinational-Verilog scope, the
   version-sensitive historical builds, the unavailable larger FIR4 workspace,
   and the unresolved semantics of sequential initialization and X values.

The public pages support these distinctions: the signed-FMA PR is open and
contains a clean-versus-patched SAT claim; [#1047](https://github.com/YosysHQ/yosys/issues/1047)
records a wrong synthesized result and its [fix PR #1049](https://github.com/YosysHQ/yosys/pull/1049);
[#997](https://github.com/YosysHQ/yosys/issues/997) explicitly contrasts an
affected build with official Yosys 0.8; and [#6085](https://github.com/YosysHQ/yosys/issues/6085)
describes a signed comparison lowering error and its propagation into storage
deletion.

## 3. Failure-family register

### F1 — Value and definedness preservation across representation boundaries

**Semantic obligation.** A compiler transformation must preserve the source
meaning of bit-vector operations, including operand width, signedness,
extension/truncation, and the distinction between a defined value, an unknown,
and a synthesis don't-care. The obligation is not merely “the emitted file
parses.”

**Concrete evidence.**

| Failure | Independent fact | Consequence | Status here |
|---|---|---|---|
| Yosys #1047 / PR #1049 | A shift-and-multiply peephole produced a wrong Boolean result for a legal input in Yosys 0.8 development code; PR #1049 was merged to avoid the pattern when the multiplication result was truncated. | Observable combinational miscompilation. | Reproduced historically; pass attribution independently supported by the fixing PR. |
| Yosys #6085 | `cmp2lut` treated a signed negative constant as raw unsigned data; the issue reports wrong LUT masks and downstream deletion of key storage. | Silent wrong logic and state removal in several target flows. | Publicly documented; this project independently reproduced the relevant failure in its prior pilot. |
| Verilator/VlogHammer signed-extension failure | VlogHammer records a Verilator bug in signed/unsigned expression evaluation, fixed in commit `adb39ce`; the report contrasts the faulty result with multiple other tools. | Simulation/compiler mismatch in a separately developed HDL compiler. | Public independent corroboration of the same semantic obligation. |
| Yosys #997 | An affected development build emitted an X initialization where official 0.8 emitted zero. | Potential initial-state mismatch; top-level consequence depends on observability and sequential semantics. | Historical internal discrepancy verified in the research workspace; full-seed output consequence remains unresolved. |

The Yosys cases are not independent compiler families, so they should not be
counted as three independent discoveries. The Verilator/VlogHammer case is
useful as a separate implementation family, but its simulator semantics and
Yosys synthesis semantics are not interchangeable.

**Strongest prior art.** EQY explicitly documents safe-replacement equivalence
and an X-propagation strategy that treats the gold side with three-valued
semantics and the gate side with unconstrained two-valued choices; see the
[EQY X-propagation documentation](https://yosyshq.readthedocs.io/projects/eqy/en/latest/xprop.html).
The 2025 paper [The Simulation Semantics of Synthesisable
Verilog](https://doi.org/10.1145/3720484) argues that the standard itself has
inconsistencies and supplies an executable repaired semantics. Vericert supplies
a separately mechanized C-to-Verilog semantics and correctness proof for a
restricted HLS compiler; see its [source repository](https://github.com/ymherklotz/vericert).

**Residual gap.** The evidence does not establish a common, scalable, and
validated contract that can classify boundary mismatches across historical
RTLIL, synthesized Verilog, four-state simulation, and two-state SAT while
retaining observable-versus-internal distinctions. This may be a real research
problem, but it may also reduce to careful integration of existing semantic
models. The gap is therefore unresolved, not claimed as novel.

**PassWitness compatibility.** Current PassWitness supplies useful artifact
provenance, checkpoint capture, witnesses, and combinational SAT. It is not
enough for the sequential initialization portion: the recovered Verismith seed
has a verified internal `reg93` discrepancy but unresolved top-level output
consequence. Additional infrastructure would include explicit semantic modes,
four-state/definedness modeling, historical-IR import validation, and a
licensed multi-tool corpus.

**Cheapest kill experiment.** Curate 12–20 public defects spanning at least
two independently developed HDL tools and at least three mechanisms (for
example, signed constant lowering, shift width/truncation, and initialization
or X propagation). For every case, record affected/fixed revisions, the
observable contract, and the representation boundary. Run the same artifacts
under: (i) two-state SAT, (ii) EQY safe-replacement/X-propagation where
applicable, and (iii) an independent simulator or bit-accurate reference.
Reject this research direction if the cases either cannot be reproduced from
public artifacts, collapse to one Yosys-specific implementation defect, or are
already classified without ambiguity by existing EQY/semantic tooling.

### F2 — Pass-by-pass translation validation and fault localization

**Obligation.** Each accessible compiler transformation should preserve the
semantics of the IR it receives and emits, and a failed proof should identify
the earliest transition for which the obligation is violated.

**Prior-art prosecution.** This is not an unoccupied idea. [Gauntlet](https://arxiv.org/abs/2006.01074)
performs translation validation on P4 IR after compiler passes and uses solver
counterexamples to pinpoint the pass; it reports 96 confirmed distinct bugs
across three P4 compiler platforms. [EQY](https://yosyshq.readthedocs.io/projects/eqy/en/latest/quickstart.html)
is explicitly designed to check that synthesis or refactoring preserves
functionality. [CIRCT-LEC](https://circt.llvm.org/docs/Tools/circt-lec/) checks
equivalence of CIRCT HW/Comb/Seq modules, and the 2025 accelerator work
[Automated Translation Validation of a Compiler for Statically Scheduled
Accelerators](https://repositum.tuwien.at/handle/20.500.12708/219556) reports
translation validation throughout a complex end-to-end hardware-accelerator
compiler flow.

**Disposition.** The basic scientific mechanism is already established. A
Yosys-specific implementation with better provenance is useful software, but
the evidence does not support presenting it as a new algorithm. A paper would
need a different question, such as a demonstrated semantic blind spot or a
scaling result not covered by this prior art.

### F3 — Generated and metamorphic testing of synthesis tools

**Obligation.** Test generation must produce valid, semantically controlled HDL
that exercises transformations without converting undefined or unsupported
behavior into a false bug report.

**Prior-art prosecution.** [VlogHammer](https://yosyshq.net/yosys/vloghammer.html)
already combines generated Verilog, multiple synthesis/simulation tools, and
Yosys SAT. [Verismith](https://github.com/ymherklotz/verismith) generates
deterministic valid Verilog and reports vendor-confirmed bugs. [VeriXmith](https://github.com/icsnju/VeriXmith)
cross-checks Verilog compilers and documents frontend/port/escaped-name
limitations. [LegoHDL](https://arxiv.org/abs/2407.12037) targets more diverse
HDL generation. [VERMEI](https://arxiv.org/abs/2508.15536) uses equivalent
mutation around zombie logic, while [Lin-Hunter](https://arxiv.org/abs/2509.01149)
uses metamorphic transformations and adaptive strategy selection.

**Disposition.** Better generation heuristics, more bugs, or an adapter around
these systems would be implementation research unless the contribution
isolates a new semantic coverage principle with controlled evidence. The
research program must not select this family merely because PassWitness can
serve as another oracle.

### F4 — Correctness of sequential/HLS transformations under scheduling and state

**Obligation.** A compiler must preserve cycle-level behavior while changing
state representation, scheduling, memory, and resource binding.

**Evidence and prior art.** Vericert provides a mechanically verified
restricted HLS compiler. Earlier behavioral-synthesis work developed sequential
equivalence checking for operation gating and global variables and reported a
commercial-tool bug. The 2025 accelerator translation-validation work extends
validation to a statically scheduled accelerator compiler.

**Disposition.** Important, but current PassWitness is not the right immediate
instrument. The missing infrastructure—sequential semantics, memory models,
cycle alignment, and larger proofs—is substantial. Treat this as a separate
long-term direction, not a reason to expand v0.1.

## 4. Strongest surviving direction

### Candidate: cross-representation semantic contracts for synthesis correctness

**Falsifiable question.** Can a small, explicit contract vocabulary for
width/sign interpretation, definedness, X/don’t-care semantics, and observable
connectivity distinguish genuine synthesis miscompilations from checker/model
artifacts across multiple HDL compiler families more reliably than a default
two-state final-equivalence check?

**Existing solution.** EQY already provides an important answer for one class of
sequential/X cases; Yosys SAT provides two-state counterexamples; Verilog
semantics work provides a repaired executable model; Vericert provides a
mechanized semantics for a restricted HLS compiler. These are strong baselines,
not straw men.

**Exact residual.** We have not found evidence of a single, reusable contract
and artifact protocol that spans historical Yosys RTLIL, synthesized Verilog,
four-state simulation, and independently developed HDL tools while reporting
whether a discrepancy is top-level observable, internal only, or merely a
legal refinement/don’t-care choice. That assertion needs to be tested against a
curated corpus before it can be called a gap.

**Potential contribution type.** If the kill experiment succeeds, the likely
contribution is an empirical semantic taxonomy plus a validated contract
checker and benchmark corpus—not a new SAT solver or universal Verilog
semantics. The contribution must show improved classification on independent
defects, not merely more report fields.

**Generalization.** Signed/unsigned arithmetic, shifts, truncation, constant
folding, X/initialization, and representation import across Yosys, Verilator,
and at least one additional synthesis or frontend family. Commercial-tool
claims require legally redistributable artifacts or public vendor-confirmed
reproduction; otherwise they cannot be part of the reusable corpus.

**Required implementation.** Keep this outside the stable release until the
experiment justifies it. Likely components are a semantic-mode adapter,
definedness/observability checker, historical-IR provenance manifest, and
independent simulation/reference harness. PassWitness can provide execution,
checkpoint, witness, and package infrastructure, but substantial sequential
support should not be smuggled into this project.

**Evaluation.** Measure, per defect: reproducibility, independently supported
bug identity, top-level versus internal observability, classification under
each semantic mode, false-positive and false-negative cases, proof runtime,
representation-import failures, and artifact portability. Separate tool-family
replication from independent root causes. Include negative cases where two
representations are legally related but not bitwise equal.

**Reviewer objections.**

- “This is EQY plus wrappers.” Answer only with cases EQY cannot classify and
  a measured improvement over EQY's documented X-propagation modes.
- “The semantic contract is hand-written after seeing the bugs.” Use a
  preregistered taxonomy and a held-out defect set.
- “X is not silicon behavior.” Report simulation semantics, synthesis
  don't-cares, and hardware initialization as separate contracts; do not merge
  them into one PASS/FAIL label.
- “Historical tool reproduction is not reproducible.” Publish source hashes,
  executable hashes, exact scripts, and raw representations; mark unavailable
  cases blocked.
- “The corpus is just Yosys bugs.” Require at least two independent tool
  families and deduplicate by fixing change/root cause.
- “More precise labels do not improve engineering outcomes.” Include a user-
  relevant outcome such as correct fix/pass attribution or reduced invalid bug
  reports, not just label agreement.

**Why others might reuse it.** A validated corpus and explicit semantic
contracts would be useful to Yosys/EQY/CIRCT/Verilator developers and to
researchers testing new HDL transformations. Reuse would come from the corpus,
machine-readable contracts, and negative examples—not from PassWitness's name.

## 5. Cheap kill experiments and gates

### Gate 1 — corpus feasibility

Acquire public source, exact affected revision, fix, flow, and license status
for at least eight candidate defects. Stop if fewer than three independent
mechanisms across two tool families can be verified without private binaries or
unrecoverable attachments.

### Gate 2 — semantic classification

For each viable case, compare two-state SAT, EQY safe replacement/X-propagation,
and an independent simulator/reference. Stop if the proposed contract adds no
classification power over the existing baseline or if disagreements are mostly
unobservable internal artifacts.

### Gate 3 — held-out validation

Freeze the taxonomy and contract rules before analyzing a held-out set. A
positive result requires fewer consequential misclassifications without an
unacceptable proof/runtime or setup-failure burden. Do not set a success
threshold after seeing the results.

### Gate 4 — reuse test

Give the manifest and contract vocabulary to an independent researcher or a
second tool adapter. Stop if it requires project-specific assumptions that do
not transfer.

## 6. What is not a research result

- The signed-FMA defect is a genuine case study, not evidence that PassWitness
  is a new verification algorithm.
- Yosys #1047, #6085, and #997 are previously reported defects; reproduction is
  not discovery.
- Pass-by-pass localization, formal witnesses, and reduction oracles are useful
  engineering capabilities with substantial prior art.
- A portable report package, provenance fields, or a CFF file is software
  sustainability work, not by itself a scientific contribution.
- The historical Verismith initialization seed currently supports an internal
  discrepancy, not a verified full-design top-level miscompilation.

## 7. Final recommendation

Do not write a manuscript or add research features yet. Preserve v0.1.0 as a
stable engineering artifact. Run the corpus-feasibility and semantic-mode kill
experiments on a separate research branch/workspace. If those gates succeed,
the research question becomes defensible. If existing EQY semantics classify
the corpus or no independent artifacts can be recovered, close this direction
and record that the strongest residual was implementation integration rather
than a scientific gap.

### Primary sources consulted

- [Yosys #1047](https://github.com/YosysHQ/yosys/issues/1047), [fix PR #1049](https://github.com/YosysHQ/yosys/pull/1049)
- [Yosys #997](https://github.com/YosysHQ/yosys/issues/997)
- [Yosys #6085](https://github.com/YosysHQ/yosys/issues/6085)
- [Yosys PR #6231](https://github.com/YosysHQ/yosys/pull/6231)
- [VlogHammer](https://yosyshq.net/yosys/vloghammer.html), [VlogHammer source](https://github.com/YosysHQ/VlogHammer)
- [Verismith source](https://github.com/ymherklotz/verismith), [FPGA 2020 paper](https://doi.org/10.1145/3373087.3375310)
- [VeriXmith source](https://github.com/icsnju/VeriXmith)
- [LegoHDL paper](https://arxiv.org/abs/2407.12037)
- [VERMEI paper](https://arxiv.org/abs/2508.15536)
- [Lin-Hunter paper](https://arxiv.org/abs/2509.01149)
- [Gauntlet paper](https://arxiv.org/abs/2006.01074)
- [EQY quickstart](https://yosyshq.readthedocs.io/projects/eqy/en/latest/quickstart.html), [EQY X-propagation](https://yosyshq.readthedocs.io/projects/eqy/en/latest/xprop.html)
- [CIRCT logical equivalence checking](https://circt.llvm.org/docs/Tools/circt-lec/), [CIRCT Verif dialect](https://circt.llvm.org/docs/Dialects/Verif/)
- [Formal Verification of High-Level Synthesis / Vericert](https://doi.org/10.1145/3485494), [source](https://github.com/ymherklotz/vericert)
- [Automated Translation Validation of a Compiler for Statically Scheduled Accelerators](https://doi.org/10.34727/2025/isbn.978-3-85448-084-6_26)
- [The Simulation Semantics of Synthesisable Verilog](https://doi.org/10.1145/3720484)
- [CFF schema guide](https://github.com/citation-file-format/citation-file-format/blob/main/schema-guide.md)
- [Zenodo GitHub integration](https://help.zenodo.org/docs/github/enable-repository/)
