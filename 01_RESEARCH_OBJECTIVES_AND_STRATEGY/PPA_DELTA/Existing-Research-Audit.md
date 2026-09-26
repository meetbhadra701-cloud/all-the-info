# Historical Research Context

This is the research already completed for the earlier broad RTL optimizer. Its rejection of that broad project is historical context, not a STOP directive for the narrowed PPA-Delta reducer. New agents should reuse its sources, then check only the reducer gap. No new research is claimed by copying this note.

---

# Prior-Art Assessment of Verified RTL Optimization

## Decision

**The broadly described project fails the originality gate.** Automated RTL rewriting, constraint-aware datapath optimization, formal correctness checks, synthesis feedback, and reusable optimization knowledge already appear in closely related research and products. The current description does not identify a sufficiently specific remaining invention. The strongest overlaps are ROVER and its extensions, Dr. RTL, and Intel's published RTL redundancy-removal patent. [1](https://arxiv.org/abs/2406.12421) [2](https://arxiv.org/abs/2303.01839) [3](https://arxiv.org/html/2604.14989v1) [4](https://patents.google.com/patent/US12353862B2/en)

**DO NOT BUILD this broad workflow on the premise that it is an original centerpiece invention.** A useful implementation or a narrower research contribution remains possible, but neither has been established by the current specification. This is a decision about the originality claim, not a claim that the engineering has no value.

Confidence is high that the broad architecture is already explored. Confidence that an unspecified future refinement is original cannot be assessed.

## Scope and evidence limits

This assessment covers public material available through September 8, 2026. Its subject is the concrete RTL example in the supplied project-selection brief: identify redundant arithmetic/datapath structures, propose synthesis-aware transformations, establish sequential equivalence, evaluate PPA using Yosys/OpenROAD, and learn which transformations generalize across benchmark families. The brief does not contain a selected final algorithm or implementation.

The evidence includes original papers, author repositories, official EDA documentation, and published patent records. Recent work from 2023–2026 was supplemented with older antecedents where the mechanisms required it. Publication dates, preprint dates, grant dates, and undated product pages are distinguished below. Search-engine crawl dates were not treated as publication dates.

Papers establish what authors publicly described and reported; this assessment did not reproduce their experiments. Repository inspection establishes public artifacts and documented behavior, not completeness or production readiness. Vendor pages establish advertised capabilities, not independently measured performance. No private EDA implementation or confidential industrial work was inspected.

Public search cannot establish that nobody anywhere has done an idea. Unpublished research, internal tools, poorly indexed material, and unpublished patent applications remain outside its reach. U.S. utility applications generally publish after an 18-month period, subject to exceptions, so even a careful patent search has visibility limits. [5](https://www.uspto.gov/web/offices/pac/mpep/s1120.html)

## Closest research and implementation overlaps

| Existing work | Public date and status | Specific overlap | Boundary that matters |
|---|---|---|---|
| **ROVER** [1](https://arxiv.org/abs/2406.12421) | TCAD online June 5, 2024; arXiv June 18, 2024 | Mixed-width and signedness rewrites; arithmetic restructuring; equivalent alternatives in e-graphs; synthesis-aware extraction; verification certificates | The core paper treats combinational RTL. It should not be represented as an unrestricted sequential optimizer. |
| **Constraint-aware datapath optimization** [2](https://arxiv.org/abs/2303.01839) | March 3, 2023 preprint; DAC 2023 | Branch-local assumptions and abstract interpretation expose bitwidth and arithmetic simplifications. The frontend already uses Yosys and sv2v. | Semantic branch/input constraints differ from timing budgets. The original implementation has restricted combinational bitvector semantics. |
| **Combining Power and Arithmetic Optimization via Datapath Rewriting** [6](https://arxiv.org/html/2404.12336v1) | April 18, 2024 preprint; ARITH 2024 | ROVER extension with gating, arithmetic transformations, limited retiming, power-aware exploration, and cycle-accurate formal checking | Single clock and zero-initialized registers; commercial evaluation. This is substantial sequential overlap, with explicit limits. |
| **SymRTLO** [7](https://arxiv.org/html/2504.10369v2) | April 2025 preprint; September 22, 2025 revision reviewed | Reusable rules/templates, AST edits, resource sharing, FSM transformations, verification feedback, Yosys/ABC and reported Formality sequential checking | Commercial PPA flow. Stored templates alone do not establish held-out-family generalization. |
| **ASPEN** [8](https://www.csl.cornell.edu/~zhiruz/pdfs/aspen-mlcad2025.pdf) | MLCAD, September 2025 | LLM-guided e-graph rewrites, theorem-prover validation, synthesis feedback, cost-model updates and candidate extraction | Primarily datapath area/delay exploration; the reviewed evidence does not establish unrestricted sequential support. |
| **Dr. RTL** [3](https://arxiv.org/html/2604.14989v1) | April 16, 2026 preprint | Critical-path feedback, parallel RTL rewriting, sequential equivalence checking, and learned cross-design pattern–strategy skills | Uses commercial synthesis and Jasper SEC. This is a close collision with the learning-plus-verification clause, not merely a similar title. |
| **RTLScout** [9](https://arxiv.org/html/2606.06530v1) | June 3, 2026 preprint | Agentic RTL and synthesis exploration with Yosys/OpenROAD, candidate pools, and reusable lessons | The paper describes simulation validation and post-mapping metrics. The current [pipeline](https://github.com/huawei-csl/rtlscout/blob/main/run_pipeline.py) additionally supports golden-reference combinational equivalence for applicable designs. Neither establishes general sequential proof or routed PPA. |
| **Siemens PowerPro** [10](https://www.siemens.com/en-gb/products/ic/powerpro/automatic-power-optimization/) | Current official documentation; original page date not established | Automatic low-power RTL generation through multi-cycle clock/memory gating, with automatically configured SLEC-Pro formal comparison | Specialized commercial power optimization. Public product evidence, not an independently reproduced result. |

**Interpretation:** no single row needs to match every implementation detail to defeat the broad claim that this is an unexplored research direction. That judgment is separate from a legal determination about whether a particular patent claim is anticipated or obvious.

Dr. RTL reports 47 reusable strategy entries, held-out cross-design evaluation, and comparisons involving Yosys, Design Compiler and post-route Innovus. This directly challenges the proposed learning/generalization distinction. These are author-reported experiments, not independently reproduced measurements. [3](https://arxiv.org/html/2604.14989v1)

## Feature-by-feature originality test

| Proposed feature | Prior-art result | What remains to specify |
|---|---|---|
| Detect and remove redundant arithmetic/datapath logic | Already described in ROVER and RTL redundancy-removal work. [1](https://arxiv.org/abs/2406.12421) [4](https://patents.google.com/patent/US12353862B2/en) | A new transformation, analysis, or class of redundancy with an explicit correctness argument |
| Use constraints to enable stronger optimization | Already addressed by branch-local constraint analysis. [2](https://arxiv.org/abs/2303.01839) | Exactly which constraints, how they are derived, and what existing analyses cannot infer |
| Formally verify rewritten RTL | Established across the reviewed systems | A measurable improvement in proof coverage, cost, automation, or supported semantics |
| Support sequential changes | Existing restricted research support and commercial implementations. [6](https://arxiv.org/html/2404.12336v1) [10](https://www.siemens.com/en-gb/products/ic/powerpro/automatic-power-optimization/) | Reset behavior, clocks, state correspondence, latency, memories, and any genuinely new supported transformation |
| Use Yosys and OpenROAD | Already a public optimization workflow. [9](https://arxiv.org/html/2606.06530v1) | Replacing a backend may improve accessibility; identify any additional technical invention separately |
| Learn reusable optimization strategies | Already described in recent work. [3](https://arxiv.org/html/2604.14989v1) [7](https://arxiv.org/html/2504.10369v2) | A distinct learning signal, representation, generalization result, or sample-efficiency mechanism |
| Release code, benchmarks, CLI and reproducibility scripts | Valuable deliverables, but not a standalone algorithmic distinction | A demonstrated unmet user need and an adoption advantage |

The architecture as a whole is best classified as **already well explored**. An open implementation could be an **engineering/accessibility contribution**. A refined mechanism is **uncertain until a focused prior-art search and experiment**. None should be labeled “likely genuinely novel” yet.

## Patent overlaps requiring attention

These are technical disclosures to compare against. The table does not establish infringement, patentability, enforceability, or freedom to operate. The stated priority dates are bibliographic metadata; they are not interchangeable with dates of public disclosure.

| Patent record | Dates | Relevant disclosure and claim distinction |
|---|---|---|
| **Intel US12353862B2 — Automatic code generation of optimized RTL via redundant code removal** [4](https://patents.google.com/patent/US12353862B2/en) | Priority June 23, 2023; A1 published March 14, 2024; grant July 8, 2025 | Claim 1 covers automated edits, equivalent intermediate versions, redundancy identification and removal. Claims 2–8 include operational equivalence, area/latency, mux branches and datapath width. Claims 9–15 address valid-edit sets, subset retries, formal proof and operational/input constraints. Distinguish these claim limitations from broader descriptive examples. |
| **LSI US6438730B1 — RTL code optimization for resource sharing structures** [11](https://patents.google.com/patent/US6438730B1/en) | Filed May 30, 2001; granted August 20, 2002 | Claims describe finding decision constructs and substituting equivalent optimized constructs, including arithmetic resource-sharing patterns. This shows why the search must extend beyond recent AI literature. |
| **Intel US20240111925A1 — Hardware power optimization via e-graph based automatic RTL exploration** [12](https://patents.google.com/patent/US20240111925A1/en) | Filed December 13, 2023; published April 4, 2024 | Published claims describe an RTL e-graph, equivalence-preserving transformations, simulation, operator-power modeling and low-power extraction. This is a published application claim set; granted scope was not established here. |
| **Synopsys US20240320406A1 — Identifying RTL code that can be a source of verification complexity** [13](https://patents.google.com/patent/US20240320406A1/en) | Filed March 24, 2023; published September 26, 2024 | Identifies RTL triggers and circuit elements associated with verification difficulty; dependent claims include recommending RTL or synthesis-constraint changes. Relevant if the proposed novelty becomes proof-tractability-aware optimization. |
| **Michigan US8365110B2 — Automatic error diagnosis and correction for RTL designs** [14](https://patents.google.com/patent/US8365110B2/en) | Priority May 25, 2007; A1 published November 27, 2008; grant January 29, 2013 | Solver-guided diagnosis and repair through selectable RTL modifications. The objective is correcting faulty logic, which differs from improving PPA in correct RTL; nonetheless, generic failure-driven repair is longstanding. |

For a serious filing decision, the next professional search would need a concrete mechanism, relevant patent families and continuations, claim histories, non-patent literature, and the intended jurisdictions. A keyword search is insufficient for that decision. The immediate engineering decision is easier: the broad redundancy-removal/formal-verification premise already has direct antecedents.

## Why obvious pivots do not automatically solve the problem

**“Make it open source.”** This can materially improve access and enable outside adoption. It is not evidence that the underlying mechanism is new. Evaluate practical usefulness and research originality separately.

**“Reuse proofs after each edit.”** IBM's FMCAD 2011 work already reuses IC3 information across related designs and properties, for both proofs and counterexamples. A new reuse criterion or soundness-preserving dependency mechanism would require a precise comparison. [15](https://research.ibm.com/publications/incremental-formal-verification-of-hardware)

**“Make equivalence reset- and X-aware.”** EQY documents safe-replacement equivalence, asymmetric refinement, formal X propagation and initial-state handling. A proposed tool must state its semantic contract; existing behavior must not be relabeled as a new equivalence theory. [16](https://yosyshq.readthedocs.io/projects/eqy/en/latest/xprop.html)

**“Build PPA regression CI.”** OpenROAD Flow already collects metrics and compares them with reference rules, including synthesis-only gates. A dashboard or threshold checker alone would overlap existing infrastructure. [17](https://openroad-flow-scripts.readthedocs.io/en/latest/contrib/Metrics.html)

**“Produce reproducible implementation bundles.”** Antmicro's 2024 bazel-orfs work already describes hermetic builds, stage-level iteration and caching. Reproducibility is necessary infrastructure; a new attribution or validation mechanism must be identified separately. [18](https://antmicro.com/blog/2024/08/bazel-orfs-for-rapid-asic-design-iteration-with-caching/)

**“Audit assumptions and vacuous proofs.”** Yosys AppNote-120 already discusses witness/precondition coverage and regression checks. A 2026 Tessolve presentation describes assumption ablation and reachability checks for generated formal harnesses. Merely surrounding a proof result with an evidence report does not establish originality. [19](https://yosyshq.readthedocs.io/projects/ap120/en/latest/) [20](https://www.tessolve.com/verification-futures/vf2026-uk/evaluating-ai-generated-formal-verification-harnesses-for-rtl-using-an-open-source-non-vacuity-aware-flow/)

**“Perturb equivalent RTL and study PPA sensitivity.”** The DAC 2011 paper *Are logic synthesis tools robust?* already describes equivalence-preserving transformations of Verilog syntax trees and a study of synthesis sensitivity. A contemporary replication could be useful, but the broad experimental idea is old. [21](https://www.researchgate.net/publication/221062563_Are_logic_synthesis_tools_robust)

## Narrower hypotheses worth screening

These are **unverified search targets**, not recommended inventions certified as novel. Their purpose is to make the next originality question concrete.

| Hypothesis | Specific proposed output | Essential comparison | Early rejection condition |
|---|---|---|---|
| **Minimal PPA regression witness** | Given two revisions, reduce interacting RTL edits to a small replayable subset that reproduces a PPA regression under pinned tools and constraints | Git bisect, ordinary delta debugging, stage-metric comparison, existing EDA testcase reducers | Existing reduction methods provide the same explanatory result and cost; or nondeterminism prevents reproducible attribution |
| **Assumption-change witness** | Produce an input sequence admitted by an old formal harness but excluded by a new one, showing how that exclusion changes a property result | Vacuity checks, assumption ablation, specification differencing and regression verification | The implementation is only assumption ablation with a new report; or witness generation cannot scale beyond trivial examples |
| **Semantic-contract disagreement reducer** | Reduce an optimization that passes under one reset/X/output-validity contract but fails under another to a small circuit and trace | EQY, differential verification, counterexample minimization and hardware testcase reducers | Existing tools already produce the same reduction; or the supposed failure is merely a misconfigured harness |

Among these, the minimal PPA regression witness is a reasonable **next investigation** because its output is concrete and independent users could verify it. It has not earned a build recommendation: causality, edit interactions, reduction cost, and existing testcase-reduction work all remain unresolved. No absence claim is made for any of the three.

## Experimental gate before a long project commitment

Write the contribution in this form:

> Given a defined class of RTL and explicit correctness assumptions, the method computes a specified new artifact using a particular mechanism. Relative to named existing approaches, it improves a measured outcome under a fixed evaluation budget. It fails on stated classes of inputs.

Every term should be operational. “AI-powered,” “automatic,” “formally verified” and “synthesis-aware” do not identify the missing mechanism by themselves.

Use the following order:

1. **State the claim.** Limit the first version to one transformation or diagnostic mechanism and an explicit supported RTL subset.
2. **Find the closest five antecedents.** Read method sections, supplementary artifacts and code where available. Follow earlier references and later citations. Include patents if the mechanism is intended for an invention review.
3. **Create a difference table.** Mark each mechanism as disclosed, partial, unverified, or genuinely different in implementation. “Not mentioned” is not “not supported.”
4. **Reproduce the smallest relevant baseline.** Record tool commits, settings, libraries, inputs, timeouts and failures. If commercial tools are unavailable, label that comparison unavailable; do not silently substitute a weaker baseline.
5. **Test one mechanism.** Compare against both a simple baseline and the closest serious method with matched evaluation budgets.
6. **Keep or kill.** Continue only if there is a precise surviving difference, measurable benefit, and a user who would value the result.

The evaluation must not mistake weak synthesis for a novel optimization. RTL-OPT's authors report that only 13 of 43 examined human-optimized designs were better under their Design Compiler `compile_ultra`, 1 ns setup, versus 24 with their Yosys comparison. The paper's categories and metrics depend on the flow; these counts are not universal failure rates for RTL optimization. They show why backend settings can change the conclusion. [22](https://arxiv.org/html/2601.01765v1)

For an optimization prototype, freeze clocks, I/O assumptions, latency, reset, libraries and tool settings. Report area and timing separately, and power only with a stated activity model. Preserve failed proofs and timeouts as outcomes. Use held-out design families for any generalization claim and an ablation removing the proposed new mechanism. A run with less constrained behavior or a different latency contract is not a fair like-for-like win.

## First 30 days for a replacement candidate

| Period | Work | Concrete decision artifact |
|---|---|---|
| Week 1 | Define one claim; build a source ledger; examine nearest papers, repositories and patent families | A short mechanism description and a feature-level prior-art table. Stop if no distinct mechanism survives. |
| Week 2 | Reproduce one relevant baseline on a small, versioned corpus; identify real user pain from public issues or existing workflow examples | Baseline logs, supported-input contract and a reproducibility manifest. Stop if the required data or verification route is unavailable. |
| Week 3 | Implement only the mechanism under test; run a controlled comparison and its ablation | A working experiment with all failures and compute cost retained. Stop if the benefit comes only from weakened constraints or unmatched budgets. |
| Week 4 | Repeat on held-out examples and assess whether a third party could rerun it | A go/no-go memo: novelty delta, measured effect, uncertainty, limitations and next milestone. |

A successful month does not require a patent, paper, public launch or recognition. It requires enough evidence to justify continued engineering. If patent protection matters, resolve disclosure timing with qualified counsel before publicly releasing a potentially patentable mechanism.

## Reusable originality gate for project selection

The following can be added to a project-selection prompt before scoring or long-term roadmaps:

> **Mandatory prior-art rejection gate**
>
> Treat every candidate as potentially already done. Before recommending it, define the exact mechanism, supported input semantics, outputs, closest baselines and claimed advantage.
>
> Search original papers, author repositories, official commercial documentation, and relevant patent publications. Cover the last four years and trace foundational work further back. Search synonyms and underlying mechanisms rather than project names alone. Follow references and citing work. Record search date, source dates, versions and unavailable evidence.
>
> For every serious candidate, identify up to five closest antecedents, selecting for proximity rather than citation count. Provide a feature-level comparison. Separate public disclosure, available implementation, reported results and independently reproduced results. Do not infer missing functionality solely from a README's silence.
>
> State the proposed technical difference in two sentences. Explain what existing work cannot do, why the new mechanism addresses that limitation, and what experiment would falsify the claim. Adding AI, formal checking, a new programming language, an open-source backend, a GUI or a benchmark is not sufficient by itself.
>
> Classify the candidate as already well explored, engineering/accessibility improvement, incremental research, potentially distinct mechanism requiring validation, or insufficiently specified. Do not translate a failed search into a claim of uniqueness. Separate research novelty from patentability and freedom to operate.
>
> Reject or narrow a candidate whose central mechanism is already disclosed. Do not let a high weighted score override a failed novelty gate. If fewer than ten candidates survive, report that honestly. If none survive, return NO VERIFIED WINNER and the smallest next research step instead of forcing a winner.
>
> Only after a candidate passes this gate should you prepare its full implementation roadmap and portfolio strategy. An initial pass is permission to investigate, not proof of originality or future significance.

## Final verdict

**Current broad example: DO NOT BUILD as a claimed original invention.**

**Narrowed alternative: originality remains unverified.**

The next deliverable should be a defensible technical difference supported by a small experiment. A new project name, a longer feature list, or a portfolio plan cannot supply that difference.

## Sources

1. Samuel Coward, Theo Drane and George A. Constantinides. [ROVER: RTL Optimization via Verified E-Graph Rewriting](https://arxiv.org/abs/2406.12421). TCAD 2024; [publisher record with June 5 online date](https://ieeexplore.ieee.org/document/10549954/).
2. Samuel Coward, George A. Constantinides and Theo Drane. [Automating Constraint-Aware Datapath Optimization using E-Graphs](https://arxiv.org/abs/2303.01839). March 3, 2023 preprint; DAC 2023.
3. Wenji Fang and colleagues. [Dr. RTL: Autonomous Agentic RTL Optimization through Tool-Grounded Self-Improvement](https://arxiv.org/html/2604.14989v1). April 16, 2026 preprint, version 1 reviewed. [Author repository](https://github.com/hkust-zhiyao/Dr_RTL).
4. Intel. [US12353862B2, Automatic code generation of optimized RTL via redundant code removal](https://patents.google.com/patent/US12353862B2/en). July 8, 2025 grant; predecessor US20240086161A1 published March 14, 2024.
5. USPTO. [MPEP §1120: Eighteen-Month Publication of Patent Applications](https://www.uspto.gov/web/offices/pac/mpep/s1120.html). Current official guidance consulted September 2026.
6. Samuel Coward, Theo Drane, Emiliano Morini and George A. Constantinides. [Combining Power and Arithmetic Optimization via Datapath Rewriting](https://arxiv.org/html/2404.12336v1). April 18, 2024 preprint; ARITH 2024.
7. SymRTLO authors. [SymRTLO paper, version 2](https://arxiv.org/html/2504.10369v2). September 22, 2025 revision. [Repository](https://github.com/NellyW8/SymRTLO).
8. ASPEN authors. [ASPEN: LLM-Guided E-Graph Rewriting for RTL Datapath Optimization](https://www.csl.cornell.edu/~zhiruz/pdfs/aspen-mlcad2025.pdf). MLCAD, September 2025. Author-hosted paper.
9. RTLScout authors. [RTLScout: Joint Agentic Code and Synthesis Optimization for Efficient Digital Circuits](https://arxiv.org/html/2606.06530v1). June 3, 2026 preprint. [Repository](https://github.com/huawei-csl/rtlscout).
10. Siemens. [PowerPro Automatic Power Optimization](https://www.siemens.com/en-gb/products/ic/powerpro/automatic-power-optimization/). Undated official product page, consulted September 2026.
11. LSI Logic. [US6438730B1, RTL code optimization for resource sharing structures](https://patents.google.com/patent/US6438730B1/en). August 20, 2002 grant.
12. Intel. [US20240111925A1, Hardware power optimization via e-graph based automatic RTL exploration](https://patents.google.com/patent/US20240111925A1/en). April 4, 2024 application publication.
13. Synopsys. [US20240320406A1, Identifying RTL code that can be a source of verification complexity](https://patents.google.com/patent/US20240320406A1/en). September 26, 2024 application publication.
14. University of Michigan. [US8365110B2, Automatic error diagnosis and correction for RTL designs](https://patents.google.com/patent/US8365110B2/en). January 29, 2013 grant.
15. Hana Chockler and colleagues. [Incremental formal verification of hardware](https://research.ibm.com/publications/incremental-formal-verification-of-hardware). FMCAD 2011; IBM Research publication record.
16. YosysHQ. [EQY: Equivalence and X-Propagation](https://yosyshq.readthedocs.io/projects/eqy/en/latest/xprop.html). Current project documentation, consulted September 2026.
17. The OpenROAD Project. [OpenROAD Flow Metrics](https://openroad-flow-scripts.readthedocs.io/en/latest/contrib/Metrics.html). Current project documentation, consulted September 2026.
18. Antmicro. [Bazel-ORFS for rapid ASIC design iteration with caching](https://antmicro.com/blog/2024/08/bazel-orfs-for-rapid-asic-design-iteration-with-caching/). August 2024 implementation account.
19. YosysHQ. [Application Note 120](https://yosyshq.readthedocs.io/projects/ap120/en/latest/). Current project documentation, consulted September 2026.
20. Tessolve, Verification Futures 2026. [Evaluating AI-generated formal verification harnesses for RTL using an open-source non-vacuity-aware flow](https://www.tessolve.com/verification-futures/vf2026-uk/evaluating-ai-generated-formal-verification-harnesses-for-rtl-using-an-open-source-non-vacuity-aware-flow/). Presentation abstract.
21. Alberto Puggelli, Tobias Welp, Andreas Kuehlmann and Alberto L. Sangiovanni-Vincentelli. [Are logic synthesis tools robust?](https://www.researchgate.net/publication/221062563_Are_logic_synthesis_tools_robust). DAC 2011, pp. 633–638; DOI 10.1145/2024724.2024869. Author-posted paper; [official DAC program](https://www.dac.com/portals/0/documents/archive/2011/48DAC_Final_Program_front.pdf) corroborates the presentation.
22. Yao Lu and colleagues. [A New Benchmark for the Appropriate Evaluation of RTL Code Optimization](https://arxiv.org/html/2601.01765v1). January 5, 2026 preprint, version 1 reviewed.
