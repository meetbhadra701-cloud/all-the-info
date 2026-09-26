# Semiconductor and EDA Research Selection

No candidate from this search pass clears the required centerpiece bar. The decisive failure is the absence of an established new computational mechanism after comparison with current and older work. Several important problems remain open, but the mechanisms considered either collide with published methods or leave their essential computational step undefined.

The research state remains SEARCHING. No candidate advances to independent review. This decision rejects the mechanisms examined in this pass; it does not establish that the field contains no suitable opportunity.

The evidence cutoff is September 11, 2026, Pacific time. Accepted work with publicly available descriptions or artifacts is included even when its conference is scheduled later. Conference acceptance, a public technical claim, and independently reproduced performance are treated as different evidence levels. No experimental reproduction was performed.

The scope covered cross-level synthesis, extraction complexity, parametric bitvectors, optimized arithmetic verification, sequential synthesis, proof reuse, memory abstraction, heterogeneous coherence, dynamic dataflow and sparse computation, physical optimization, and clock-domain crossings. The assessment below records the decisive evidence, rather than presenting discarded sketches as project recommendations.

**The most consequential recent prior art**

| Public work | Capability already claimed or demonstrated | Consequence for this selection |
|---|---|---|
| Nextmap / semantic e-graphs, PLDI 2026 | Maintains equivalences across bit-level and word-level representations to support simultaneous optimization and mapping. | Combining arithmetic, Boolean optimization, and technology mapping is already an explicit research contribution. A new proposal needs a different mechanism. |
| ParaBit, CAV 2026 | Proves multi-width parametric bitvector equivalences through modular-arithmetic reasoning and equality saturation; reconstructs proofs in Isabelle. | Multiple widths and certified rewrite validation are already occupied territory. |
| Bhat et al., accepted OOPSLA 2026 | Publicly describes a linear-size reduction from multiple symbolic widths to one, bounded solving through one fixed-width query, and an unbounded decision procedure for a restricted fragment. | Avoiding width-assignment enumeration through masks is a direct prior-art collision. Bounded and unbounded claims must remain separate. |
| TalisMan, CP 2025 | Recovers linear relations using an FGLM-style procedure plus sampling, linear algebra, and SAT checking. | Discovering arithmetic relations and validating them is already a concrete algorithm, not an empty workflow. |
| FORWORD, DATE 2026 | Uses word-level simulation and SMT validation for datapath equivalence sweeping. | A new datapath method cannot claim novelty merely by moving candidate discovery above the bit level. |
| C3PO, ASP-DAC 2026 | Jointly optimizes timing, routability, and wirelength using differentiable kernels and adaptive objective weighting. | A unified differentiable physical optimizer requires a much more specific novelty claim. |

Sources for the rows: [Nextmap, §§2–5](https://zsisco.net/papers/nextmap-pldi26.pdf), [ParaBit, §§4–6](https://link.springer.com/chapter/10.1007/978-3-032-32519-8_20), [OOPSLA accepted-paper abstract](https://2026.splashcon.org/details/oopsla-2026/137/Sound-and-Complete-Solving-for-Multi-Width-Parametric-Bitvectors-via-Principled-Reduc), [TalisMan, §§3–5](https://drops.dagstuhl.de/storage/00lipics/lipics-vol340-cp2025/LIPIcs.CP.2025.14/LIPIcs.CP.2025.14.pdf), [FORWORD paper](https://past.date-conference.com/proceedings-archive/2026/DATA/55.pdf), and [C3PO paper](https://hhsiao30.github.io/papers/yichen_apsdac26__Camera_Ready_eXpress.pdf).

**Cross-level optimization: the gap has moved**

Nextmap addresses a precise representational failure: syntactically enumerating equivalent concatenations and slices becomes unwieldy. Its semantic identifiers and custom decomposition operations propagate equality across levels. Its extraction already represents registers and distinguishes permitted sequential feedback from combinational cycles. Consequently, simply adding a shared hardware representation, semantic equality, or register-aware extraction would not establish novelty. This does not mean Nextmap solves arbitrary sequential transformation or routed PPA optimization. Those stronger claims are not established by its paper. [Nextmap, §§2–5](https://zsisco.net/papers/nextmap-pldi26.pdf)

The adjacent-field attack also closes an obvious response to expensive extraction. Treewidth-parameterized optimal extraction exists in both *Fast and Optimal Extraction for Sparse Equality Graphs* and *E-Graphs as Circuits, and Optimal Extraction via Treewidth*. “Use separators and dynamic programming instead of an ILP” therefore starts with substantial existing machinery. [Goharshady, Lam, and Parreaux, OOPSLA 2024](https://doi.org/10.1145/3689801), [Sun et al., 2024 preprint](https://arxiv.org/abs/2408.17042)

The 2026 effectful-program work adds another relevant threat: statewalk DP exploits a structural parameter to enforce effect ordering during extraction. Its public description establishes an adjacent technique, not a ready-made solution to hardware retiming. Nevertheless, hardware-specific timing annotations alone would not be enough to distinguish a descendant. [Flatt et al., accepted OOPSLA 2026](https://ztatlock.net/pubs/2026-oopsla-eggcc/)

Selection judgment: no surviving decomposition was identified that both changes the computational bottleneck and plausibly supports field-level reuse. A new cost function, integration of these engines, or a faster implementation could be useful, but does not by itself meet this search's bar.

**Parametric arithmetic: important residual limitations, no surviving primitive**

ParaBit is incomplete and has representational limitations. Its paper excludes some operators and data constraints, reports memory failures, and identifies symbolic interval reasoning as future work. These are real boundaries; they do not make “add data constraints” a new centerpiece mechanism. [ParaBit, §§6–8](https://link.springer.com/chapter/10.1007/978-3-032-32519-8_20)

The newer OOPSLA work is particularly consequential because it attacks the enumeration bottleneck directly. Its unbounded result is for a stated fragment, not arbitrary multiplication and arbitrary bitvector formulas. The accepted-paper description and an artifact created August 2 establish a current prior-art threat. The full theorem and implementation were not independently audited in this pass. [Accepted-paper description](https://2026.splashcon.org/details/oopsla-2026/137/Sound-and-Complete-Solving-for-Multi-Width-Parametric-Bitvectors-via-Principled-Reduc), [dated artifact](https://zenodo.org/records/21764865)

Automata-based reasoning over widths also has an established certified lineage in the 2025 work. Recasting a width as a sequence of bit positions, with carry information carried through states, would require a precise distinction from that lineage. [Certified width-independent decision procedures and artifact](https://zenodo.org/records/16269885)

Selection judgment: extending a supported fragment could become serious research. No tractable extension, structural theorem, or new inference procedure was established here that warrants elevating such an extension to the requested centerpiece.

**Optimized arithmetic verification: the strongest near-miss**

This area received the closest mechanism-level scrutiny. The attraction is clear: recover useful arithmetic relations after Boolean optimization has obscured recognizable operators, then use those relations to avoid large intermediate reasoning objects.

The proposed sampling-and-repair core collides directly with TalisMan. Its Algorithm 3 grows subcircuits, obtains linear relations using two complementary methods, and reduces a linearized specification. Its evaluation also cautions against selecting it as the sole strongest baseline: some nonlinear lexicographic methods remain faster, and different configurations solve different instances. [Hofstadler and Kaufmann, Algorithm 3 and §5](https://drops.dagstuhl.de/storage/00lipics/lipics-vol340-cp2025/LIPIcs.CP.2025.14/LIPIcs.CP.2025.14.pdf)

The older and neighboring lineage includes incremental column-wise algebraic verification, combined SAT and computer algebra, and dynamic phase/order optimization. FastPoly further targets the cost of polynomial operations inside these methods. A fair future comparison would need the relevant algebraic and Boolean approaches, not only monolithic SAT or an old SMT configuration. [Konrad and Scholl, FastPoly, FMCAD 2025](https://repositum.tuwien.at/handle/20.500.12708/219550?mode=full)

The domain-stripped problem is relation discovery over a Boolean circuit followed by checking that the relations hold universally. Calling the relations “carry conservation,” “semantic cuts,” or “proof objects” does not change that computation. The unfilled part is a new rule for finding and proving useful decompositions without simply relocating the difficult reasoning into a SAT oracle, a computer-algebra oracle, or a manually chosen boundary.

A basic hostile check illustrates the risk. Agreement on sampled inputs does not exclude a circuit that differs on a rare unsampled input. This is a logical objection to treating sampling as certification; it is not evidence that existing exact algorithms are ineffective. The research contribution would have to improve exact reasoning under explicit structural assumptions.

Selection judgment: the near-miss fails mechanism novelty. No residual claim is advanced under a new project name. Reopening it would require a precise computational step absent from the established methods and an explanation of why that step remains cheap on an independently recognizable circuit family. “Better cuts” is not yet such a step.

**Sequential, memory, and protocol reasoning**

PROMISE already mines invariants from simulation, formally verifies candidates, and uses unreachable states for sequential optimization. Its polynomial-time inference components must not be confused with a polynomial-time solution to all underlying verification obligations. A generic mine–prove–optimize loop is consequently insufficient novelty. [PROMISE, §§II–III](https://dynamo.ethz.ch/wp-content/uploads/2025/10/Xu_Promise_ICCAD25.pdf)

Proof reuse also has substantial precedents. UpProver uses SMT-based summary repair for incremental verification, while 2026 work explicitly studies transporting invariant certificates through model transformations. A dependency graph that invalidates and repairs affected proof fragments is not enough, by itself, to establish a new computational primitive. [UpProver and incremental-verification lineage](https://verify.inf.usi.ch/FVSCU), [Cabodi et al., 2026](https://iris.polito.it/handle/11583/3010750)

For memory abstraction, symmetry and data independence already support automatic reasoning over unbounded address and data domains under restrictions. These restrictions matter: pointer arithmetic, address-dependent behavior, and other operations can destroy the assumed symmetry. A new method would need to identify a broader exploitable structure and establish its soundness, rather than promise a universally compact memory quotient. [Bingham et al., CAV 2004](https://www.microsoft.com/en-us/research/publication/automatic-verification-sequential-consistency-unbounded-addresses-data-values/)

The distinction between a compact input and a cheap decision procedure is particularly important here. The public presentation underlying the 2026 array-complexity work reports different complexity classes depending on width encoding and allowed array sorts. It gives no basis for rejecting restricted practical methods; it does block casual claims that keeping memory symbolic makes general reachability tractable. [Masaryk University technical presentation](https://formela.fi.muni.cz/events/chess-students-day-2025), [FMCAD 2026 publication record](https://repositum.tuwien.at/handle/20.500.12708/230509)

vCXLGen already supplies automatic bridge synthesis from coherence specifications and compositional liveness verification for heterogeneous architectures. Separately, the Stanford FAVA materials expose current tools for deriving formally checked microarchitectural and coherence-related specifications. These sources do not establish automatic verification of arbitrary raw processor RTL. They do require a new proposal to distinguish itself from existing composition, synthesis, and specification-extraction methods. [vCXLGen, ASPLOS 2026](https://anatolelefort.net/papers/vcxlgen-asplos26-preprint.pdf), [FAVA, ISCA 2026](https://fava.stanford.edu/)

Selection judgment: no new composition or abstraction rule was established that defeats the earlier refinement, template-leakage, and auxiliary-state concerns. The previously killed projects remain closed.

**Physical design and adjacent systems**

C3PO's relevant result is concurrent optimization with downstream evaluation, not a universal exact router. Its differentiable routability objective is based on RUDY. A research gap remains between such objectives and detailed discrete feasibility, but a gap is not an algorithm. [C3PO, §§I–IV](https://hhsiao30.github.io/papers/yichen_apsdac26__Camera_Ready_eXpress.pdf)

Decomposing placement and routing and returning conflicts or cuts has an obvious adjacent-field ancestry in Benders methods. One published networking formulation already separates placement at the master level from routing subproblems. That is not identical to VLSI routing. It does mean the novelty must reside in hardware-specific cuts, decomposition, or a demonstrated structural advantage, rather than the master/subproblem architecture. [Benders decomposition for VNF placement and routing, 2021](https://www.sciencedirect.com/science/article/pii/S0305054821000198)

For sparse computation, Scorch already provides algorithms for ordering, tiling, and format inference, and D2T2 uses sparse data distributions to choose nonuniform tiling. The remaining dynamic scheduling problem cannot be claimed as new merely by exposing it through an accelerator compiler. [Scorch, CGO 2026](https://ajroot.pl/cgo2026scorch.html), [D2T2, MICRO 2025](https://doi.org/10.1145/3725843.3756095)

Clock-domain crossing was screened against both existing metastability-containing circuit theory and commercial metastability-effect modeling. A ternary or uncertainty-propagating representation alone is not a new capability, and physical metastability cannot be treated as a Boolean event that an algorithm can always eliminate. [Friedrichs, Függer, and Lenzen](https://arxiv.org/abs/1606.06570), [Siemens CDC-FX](https://resources.sw.siemens.com/es-MX/white-paper-questa-cdc-fx-metastability-effects-delay-modeling/)

Selection judgment: these areas remain technically important. The examined routes did not yield a sufficiently distinct computational method with a credible cheap falsification path. No inference is made that their future research ceiling is low.

**Commercial and patent evidence**

Public commercial material establishes relevant existing functionality. Synopsys DPV advertises transaction-level equivalence between C/C++ references and RTL, including arithmetic datapaths. Siemens describes SLEC verification of HLS results. Cadence documents sequential equivalence and hierarchical formal capabilities. These claims invalidate blanket statements that commercial tools lack such functions; they do not reveal the complete proprietary algorithms or prove universal scalability. [Synopsys DPV](https://www.synopsys.com/verification/static-and-formal-verification/vc-formal/vc-formal-datapath-validation.html), [Siemens SLEC](https://blogs.sw.siemens.com/verificationhorizons/2019/07/11/the-many-flavors-of-equivalence-checking-part-1-synthesis-validation-with-lec-and-slec-a-k-a-the-most-popular-formal-apps-ever/), [Cadence Jasper](https://www.cadence.com/en_US/home/tools/system-design-and-verification/formal-and-static-verification/jasper-core-formal-apps.html)

Patent US8122401B1, published in 2012, describes mixed finite/infinite-precision reasoning and recovery of word-level functionality from bit-level portions. It is a concrete historical disclosure relevant to generic lifting claims. This is a technical prior-art observation, not a conclusion about patent validity, enforceability, infringement, or freedom to operate. The patent search was preliminary, not comprehensive. [US8122401B1, description and claims](https://patents.google.com/patent/US8122401B1/en)

**Why the result stops here**

The rejection is not based on demanding that all components be unprecedented. A combination can be a major contribution when a new interaction, theorem, representation, or algorithm produces the capability. Here, the necessary interaction could not be specified beyond known mechanisms or an unresolved oracle.

No candidate could answer all of the following with adequate precision: which competitive method fails; the structural reason it fails; the new operation that changes that failure; why that operation avoids simply transferring the same difficulty elsewhere; and the restricted, representative case that could cheaply falsify the claim.

The citation test fails for the same reason. A reusable implementation or common output format could attract adoption, but no new object was identified on which later algorithms would have a compelling technical reason to depend. Adding such an object to the proposal would not repair missing mechanism novelty.

Confidence is approximately 85% in the decision to withhold advancement of the examined mechanisms. This is a subjective assessment of the selection decision, not a probability that no suitable project exists. Confidence in a field-wide absence claim is not estimated because the search cannot support that claim.

A standard candidate brief is not supplied because no candidate survives the preliminary screen. Filling its novelty, feasibility, and upside fields for a rejected sketch would create an impression of maturity unsupported by the evidence. Independent Claude/Codex prompts and model selections are likewise deferred until a candidate passes the gate.

**Next action**

The next gate remains SEARCHING. A further pass should use a specific new mechanism and the failure cases of competitive methods as its admission criteria. A more elaborate tool architecture, a larger benchmark, or an unsupported claim that an LLM will find the right decomposition does not qualify.

The researcher need not install tools or start a repository. To continue, send: “Continue SEARCHING under the same bar. Treat this evidence as exclusions; surface only a mechanism that defeats its strongest prior-art threat.” This authorizes another search pass only.

**Sources and evidence status**

All linked material was checked during this pass. The following inventory identifies the principal source types and publication dates; individual claims are linked above at their point of use.

1. Kong et al. [Improving Equality Saturation for EDA via Semantic E-Graphs](https://zsisco.net/papers/nextmap-pldi26.pdf). PLDI, June 2026. Author-hosted full paper, especially §§2–5.
2. Rinaldi, Wickerson, and Coward. [A Multi-width Parametric Bitvector Equivalence Solver](https://link.springer.com/chapter/10.1007/978-3-032-32519-8_20). CAV; first online July 24, 2026. Publisher full text, including limitations and evaluation.
3. Bhat et al. [Sound and Complete Solving for Multi-Width Parametric Bitvectors via Principled Reductions](https://2026.splashcon.org/details/oopsla-2026/137/Sound-and-Complete-Solving-for-Multi-Width-Parametric-Bitvectors-via-Principled-Reduc). Accepted OOPSLA 2026; conference scheduled October. Official abstract and [dated public artifact](https://zenodo.org/records/21764865); full correctness proof not audited.
4. Hofstadler and Kaufmann. [Guess and Prove: A Hybrid Approach to Linear Polynomial Recovery in Circuit Verification](https://drops.dagstuhl.de/storage/00lipics/lipics-vol340-cp2025/LIPIcs.CP.2025.14/LIPIcs.CP.2025.14.pdf). CP 2025. Publisher full paper, algorithms and evaluation.
5. Yang et al. [FORWORD: Accelerating Formal Datapath Verification via Word-Level Sweeping](https://past.date-conference.com/proceedings-archive/2026/DATA/55.pdf). DATE 2026; preprint first submitted July 2025. Conference paper and [authors' repository](https://github.com/yangziyiiii/FORWORD).
6. Lu et al. [C3PO: Commercial-Quality Global Placement via Coherent, Concurrent Timing, Routability, and Wirelength Optimization](https://hhsiao30.github.io/papers/yichen_apsdac26__Camera_Ready_eXpress.pdf). ASP-DAC 2026. Author-hosted full paper; reported results, not reproduced results.
7. Goharshady, Lam, and Parreaux. [Fast and Optimal Extraction for Sparse Equality Graphs](https://doi.org/10.1145/3689801). OOPSLA 2024. Publisher record and abstract.
8. Sun, Zhang, and Ni. [E-Graphs as Circuits, and Optimal Extraction via Treewidth](https://arxiv.org/abs/2408.17042). First submitted August 30, 2024. Author-submitted abstract.
9. Flatt et al. [Efficient Extraction for Effectful E-graphs](https://ztatlock.net/pubs/2026-oopsla-eggcc/). Accepted OOPSLA 2026, October publication designation. Public author page and paper.
10. Bhat et al. [Certified Decision Procedures for Width-Independent Bitvector Predicates](https://zenodo.org/records/16269885). OOPSLA 2025. Authors' public artifact and publication information.
11. Konrad and Scholl. [FastPoly: An Efficient Polynomial Package for the Verification of Integer Arithmetic Circuits](https://repositum.tuwien.at/handle/20.500.12708/219550?mode=full). FMCAD 2025. Institutional publication record and indexed paper text.
12. Xu, Cortadella, and Josipović. [PROMISE: Property Mining for Sequential Synthesis](https://dynamo.ethz.ch/wp-content/uploads/2025/10/Xu_Promise_ICCAD25.pdf). ICCAD 2025. Author-hosted full paper.
13. Asadi et al. [UpProver: Incremental Verification by SMT-based Summary Repair](https://verify.inf.usi.ch/FVSCU). FMCAD 2020. Research-lab publication and artifact page.
14. Cabodi et al. [Manipulating Proof Certificate Invariants in the Presence of Model Transformations](https://iris.polito.it/handle/11583/3010750). IEEE Access 2026. Institutional record and abstract.
15. Bingham et al. [Automatic Verification of Sequential Consistency for Unbounded Addresses and Data Values](https://www.microsoft.com/en-us/research/publication/automatic-verification-sequential-consistency-unbounded-addresses-data-values/). CAV 2004. Microsoft Research publication page.
16. Jonáš, Petřivalská, and Šárník. [On the Complexity of Word-Level Model Checking with Arrays](https://repositum.tuwien.at/handle/20.500.12708/230509). FMCAD 2026. Institutional publication record and [earlier university technical abstract](https://formela.fi.muni.cz/events/chess-students-day-2025); no independent proof audit.
17. [vCXLGen: Automated Synthesis and Verification of CXL Bridges for Heterogeneous Architectures](https://anatolelefort.net/papers/vcxlgen-asplos26-preprint.pdf). ASPLOS 2026. Author-hosted full paper.
18. Stanford [FAVA](https://fava.stanford.edu/). ISCA 2026 tutorial. Authors' capability descriptions and publication links.
19. [Benders decomposition for a node-capacitated Virtual Network Function placement and routing problem](https://www.sciencedirect.com/science/article/pii/S0305054821000198). Computers & Operations Research, June 2021. Publisher text.
20. Yan et al. [Fast Autoscheduling for Sparse ML Frameworks](https://ajroot.pl/cgo2026scorch.html). CGO, February 2026. Author publication page.
21. Sharma et al. [A Probabilistic Perspective on Tiling Sparse Tensor Algebra](https://doi.org/10.1145/3725843.3756095). MICRO; published October 17, 2025. Publisher text describing D2T2 and [authors' publication record](https://compilers.stanford.edu/publications/micro25/).
22. Friedrichs, Függer, and Lenzen. [Metastability-Containing Circuits](https://arxiv.org/abs/1606.06570). 2016 preprint. Author-submitted abstract.
23. [Synopsys DPV](https://www.synopsys.com/verification/static-and-formal-verification/vc-formal/vc-formal-datapath-validation.html), [Cadence Jasper](https://www.cadence.com/en_US/home/tools/system-design-and-verification/formal-and-static-verification/jasper-core-formal-apps.html), and [Siemens CDC-FX](https://resources.sw.siemens.com/es-MX/white-paper-questa-cdc-fx-metastability-effects-delay-modeling/). Public vendor capability pages, undated. Product claims, not independently benchmarked algorithms.
24. Siemens. [The Many Flavors of Equivalence Checking: Part 1](https://blogs.sw.siemens.com/verificationhorizons/2019/07/11/the-many-flavors-of-equivalence-checking-part-1-synthesis-validation-with-lec-and-slec-a-k-a-the-most-popular-formal-apps-ever/). July 11, 2019. Vendor technical article.
25. [US8122401B1: System, method, and computer program product for determining equivalence of netlists utilizing at least one transformation](https://patents.google.com/patent/US8122401B1/en). Published February 21, 2012. Patent disclosure; no legal status conclusion.

KILL
