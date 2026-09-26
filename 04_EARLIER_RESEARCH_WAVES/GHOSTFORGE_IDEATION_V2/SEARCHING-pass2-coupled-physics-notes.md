# SEARCHING pass 2: coupled physics, PDN, reliability and PHY abstraction

Private research notes. Evidence checked through September 2026. No code, repository, experiment, or independent review was launched.

**KILL for this cluster; no candidate warrants independent review.** I examined four capability walls and one subsidiary mechanism. The strongest common pattern was loss of context during abstraction: spatial boundary conditions, temporal history, legal workload correlations, or stochastic feedback. Existing numerical and formal methods already supply the obvious replacement primitives.

These are mechanism exclusions, not claims that the application problems are solved.

## 1. Thermal analysis when local homogenization loses the relevant geometry

**Recent limitation.** Bloomfield et al., *A Multiscale Workflow for Thermal Analysis of 3DI Chip Stacks*, January 28, 2026, §V, explicitly identifies strong scale separation as a limitation. Its local representative volume must be much smaller than the desired macro element, while the macro temperature gradient is treated as constant across that volume. Local hotspot resolution competes with this assumption. The paper already uses static condensation to extract anisotropic conductivity tensors. [Primary paper](https://arxiv.org/html/2602.06999v1)

**Strong baseline.** Relevant current baselines include this layout-derived multiscale FEM workflow and DATE 2026 **3D-ICE 4.0**, which retains layout heterogeneity, uses quadtree tiling, adaptive vertical partitioning and parallel RC solves. A proposed method must beat these, not homogeneous block models alone. [3D-ICE author-hosted paper](https://infoscience.epfl.ch/bitstreams/b6e66f65-c8f2-4d93-ae1c-a4956da01387/download)

**Proposed operation tested.** Replace each local conductivity tensor with an adaptive boundary-response operator: preserve the relationship between boundary temperatures and fluxes, retain additional boundary modes when composition exposes unresolved gradients, and attach a computable error bound.

**Fundamental versus debt.** The insufficiency of a fixed local tensor is representational. The stronger claim that no efficient multiscale representation works without scale separation is false.

**Adjacent reduction and kill.** This proposal reduces to Schur-complement/static-condensation port reduction and numerical homogenization. Adaptive port reduction with error estimation dates to 2012; optimal port spaces and reuse across changing geometries predate this task. Generalized multiscale FEM and localized orthogonal decomposition already handle problems without scale separation. [Adaptive port reduction, 2012](https://doi.org/10.3182/20120215-3-AT-3016.00123), [Smetana, 2018](https://arxiv.org/abs/1808.02946), [scalable multiscale-spectral GFEM, 2024](https://doi.org/10.1016/j.jcp.2024.113013)

**Cheapest falsification.** On paper, express the proposed operator as a Schur complement with a reduced port basis. If its enrichment and certification rules are standard residual/transfer-eigenproblem rules, novelty fails before implementation.

**Reusable object if successful.** Certified component response operators. That is a valuable research object, but the object and its obvious construction are already established.

## 2. Reliability analysis when equal average current hides different damage histories

**Recent limitation.** Wang et al., *Decoupling Stress Relaxation and Damage Accumulation in Electromigration Under Non-DC Excitation*, published **June 6, 2026**, identifies history dependence and the inadequacy of equivalent-DC or piecewise steady-state approximations. Its accessible abstract then supplies the apparent missing mechanism: a convolutional stress-response kernel plus cumulative void-nucleation hazard. [Publisher record and abstract](https://link.springer.com/article/10.1007/s11664-026-12922-x)

**Strong baseline.** The relevant boundary already includes transient physics-based stress simulation, reduced-order solvers, time-varying excitation, and this explicit memory/hazard formulation. ICCAD 2025 also has a coupled lumped-element EM model with topology switching between pre- and post-voiding phases. [ICCAD primary record](https://ieeexplore.ieee.org/document/11240681/)

**Proposed operation tested.** Compose waveform segments through a stress-memory state and a separate irreversible damage accumulator; allow scheduling or power policies to query lifetime consequences without replaying the entire history.

**Fundamental versus debt.** Averaging genuinely discards order-dependent information. Retaining that information is not itself a new principle; finite-dimensional approximations and kernel formulations are existing mechanisms.

**Adjacent reduction and kill.** The attractive kernel/hazard idea is directly preempted by the June paper. Segment composition is state-transition composition for the resulting dynamical system. Adding waveform-sensitive scheduling would be an application unless a distinct algorithmic principle is supplied.

**Cheapest falsification.** Derive the proposed segment-composition equations and compare them with the existing convolution/state-space response plus accumulated hazard. Algebraic equivalence kills it.

**Reusable object if successful.** A composable lifetime-response model. The mechanism is already represented in current work.

**Evidence limit.** I inspected the June paper's publisher abstract and references, not its subscription-only full text. Its broad LTI wording should not be treated as proving arbitrary nonlinear temperature dependence. That uncertainty prevents overclaiming its scope, but does not rescue the generic kernel/hazard proposal.

## 3. Generating realistic worst-case PDN stimuli without enumerating workloads

**Recent limitation.** The DesignCon 2026 paper *Bridging the Time-Frequency Chasm in PDN Design* describes difficulty separating PDNs into independent blocks and, on printed pp. 14–16, the loss of excitation phase relationships and uncertainty about actual load-current distributions. Its reverse-pulse treatment assumes an LTI PDN. [Public author-company paper](https://suddendocs.samtec.com/notesandwhitepapers/samtec-dc26-paper-bridging-the-time-frequency-chasm-in-pdn-design.pdf)

**Strong baseline.** Reverse pulse alone is too weak a baseline. Ferzli, Chiprout and Najm already optimized wavelet coefficients under current, power and time-frequency constraints in **EPEP 2008**. Fawaz and Najm's **TCAD 2017** RLC verification handles constrained worst-case fluctuations with scalable LP-based computation. [Wavelet paper, §§II–IV](https://www.eecg.utoronto.ca/~najm/papers/epep08-imad.pdf), [RLC verification paper](https://www.eecg.utoronto.ca/~najm/papers/tcad17-mohammad.pdf)

**Proposed operation tested.** Propagate a compact language of legally realizable switching patterns through the PDN response, retaining correlations that independent current envelopes lose; return an extremal voltage and a realizable stimulus.

**Fundamental versus debt.** Loose envelopes genuinely permit impossible combinations. However, legal sequential workloads introduce discrete state and the PDN introduces continuous memory. Simply coupling them does not eliminate either state space.

**Adjacent reduction and kill.** With an explicit finite controller and affine physics, this becomes hybrid reachable-set computation. Support-function/polyhedral propagation already provides the generic operation. With mode-dependent dynamics, automaton-constrained switching systems and multinorms also predate this proposal. [SpaceEx primary abstract, 2011](https://verimag.univ-grenoble-alpes.fr/details.html?lang=en&pub_id=FrehseLGDCRLRGDM11), [constrained switching, 2016](https://doi.org/10.1016/j.automatica.2016.05.015)

**Cheapest falsification.** Define the proposed summary and construct two legal histories with the same summary but different response to a common continuation. If repairing the summary requires ordinary product states or generic reachable sets, the proposed compact closure has failed. This is a falsification target, not an asserted universal lower bound.

**Reusable object if successful.** A workload-realizable extremal-response operator. No distinct operator or closure theorem emerged beyond known constrained reachability.

**Unverified residual.** I did not establish the globally strongest commercial workload-realizability analysis. Thus the exclusion is justified by failure to specify a new mechanism, not by claiming commercial completeness.

## 4. Replacing expensive PHY detail while preserving architectural consequences

**Recent limitation and baseline.** **DICE, ISCA 2026**, with public arXiv v2 dated July 28, models runtime PHY effects, FEC iterations, retransmissions and flow control within gem5. §IV-C reports **9.2% mean simulation overhead**, with FEC decoding the main added cost, and proposes memoization as future optimization. §IV-D explains why fixed mean latency misses workload-dependent queueing interactions. [Current public version](https://arxiv.org/html/2607.24221v2), [author publication record](https://winternan.github.io/publication/2026-dice)

**Proposed operation tested.** Construct a small PHY transducer preserving conditional packet-completion, retry and backpressure distributions under every supported architectural input, while eliminating internal decoder iterations.

**Fundamental versus debt.** Matching marginal latency distributions is insufficient in feedback with queues. Preserving contextual behavior is a real representational requirement. The reported overhead also weakens the claim that detailed PHY simulation itself presents an overwhelming computational wall.

**Adjacent reduction and kill.** Exact contextual replacement is weighted/probabilistic I/O behavior equivalence or a suitable stochastic quotient. These notions already support composition; approximate time-bounded reachability reduction with error bounds also exists. Applying them to a decoder does not supply a new principle. [Stark's primary paper, especially §§4–5](https://www3.cs.stonybrook.edu/~stark/REPORTS/bisimulation.pdf), [Salamati–Soudjani–Majumdar, 2019/2020](https://arxiv.org/abs/1909.06112)

**Cheapest falsification.** Find two decoder/channel states merged by the proposed summary whose completion/retry distributions diverge under one shared next input. If the required quotient becomes essentially the original state space, compactness fails.

**Reusable object if successful.** A composable stochastic PHY model with contextual error bounds. The candidate lacks a new construction that makes this substantially smaller.

## Subsidiary exclusion and synthesis

A subsidiary exclusion is **“turn approximate physical analysis into guaranteed safe current contracts.”** Feghali and Najm's ISQED 2024 paper already addresses inverse EM safety by generating current constraints using Arnoldi reduction. Its §IV-C relies on empirical error tuning and notes growing error with circuit size. A proposal that merely adds conservative margins from certified matrix-exponential error bounds reduces to existing numerical certification and robust constraint tightening. [2024 paper, printed pp. 379–380](https://www.eecg.utoronto.ca/~najm/papers/isqed24-cedric.pdf), [computable Krylov error bounds](https://arxiv.org/abs/1809.03369)

**Newly excluded families:** adaptive thermal boundary macromodels as ordinary port reduction; waveform-memory EM kernels with damage accumulation; workload-constrained PDN extrema via ordinary hybrid reachability; contextual PHY quotients via existing probabilistic equivalence; and safety contracts obtained by adding standard numerical error margins.

The shared limitation is meaningful, but “preserve the missing context” did not resolve into one new computational primitive.
