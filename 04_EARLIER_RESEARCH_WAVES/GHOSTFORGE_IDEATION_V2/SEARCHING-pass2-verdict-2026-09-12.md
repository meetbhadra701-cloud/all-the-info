# Semiconductor / EDA centerpiece search — second-pass verdict

**KILL the examined formulations. Research state: SEARCHING. No candidate advances to independent hostile review.**

This completes the search pass interrupted by the rate limit. Findings already produced by all three research agents were retained. The physical-analysis and silicon-test agents resumed their unfinished checks; the compiler/security agent's session was unavailable, and its specific source leads were verified and completed locally. The first pass remains an exclusion set throughout.

The new work concentrated on underexplored walls in physical-model reduction, transient reliability, workload-realizable power analysis, chiplet PHY behavior, diagnosis, testability, event-sensitive timing, temporal masking, and compiler resource composition. It also screened clocking, FPGA/NoC mapping, ECO, and approximate-circuit analysis. This was not an exhaustive search of every category in the user's list.

The evidence window covers work available through September 12, 2026, with older primary sources used to test algorithmic ancestry. Publication, preprint disclosure, prototype evaluation, and independently reproduced results are distinct evidence levels. No implementation, experiments, repository, 30-day manual, or full specification was produced.

**What the recent limitation search actually revealed**

Several strong limitations clustered around a common problem: an abstraction discards information that becomes relevant again when components interact. The missing information differs by domain—boundary flux patterns, current history, legal workload sequences, decoder/channel state, joint leakage, or observation histories. This cluster is more useful than treating each paper's future-work paragraph as a project proposal.

| Recent limitation, with source location | Deeper issue | Consequence for this pass |
|---|---|---|
| Bloomfield et al.'s multiscale thermal workflow requires strong scale separation, §V. | A local conductivity tensor cannot encode arbitrary boundary-dependent behavior. | Tested adaptive boundary-response operators; collided with established port reduction and numerical homogenization. |
| Wang et al., June 2026, discusses non-DC electromigration history. | Average current loses reversible stress dynamics and irreversible damage. | The apparently missing kernel-plus-damage mechanism is already disclosed in that paper. |
| Symbolic timing, 2025 §IV, requires supplied internal event order; its August 2026 successor still faces combinatorial exploration. | Event order can alter physical behavior, while many orders may be redundant. | The older limitation has been partly overtaken; exact and approximate commutation reductions have substantial prior art. |
| Wit-HW, August 2025 §VI, cannot distinguish statements with identical coverage behavior. | The observation interface merges different possible causes. | More ranking or passing witnesses cannot restore erased distinctions; active diagnosis already addresses intervention policies. |
| ETS 2026 KFDD testing, §V, leaves hardware overhead and larger designs open. | A representation enabling tractable test generation can constrain implementation quality. | Generic testability-preserving rewrites already have an older research lineage. |
| LATTE 2026 timeline types, §5, identifies expensive joint binding/scheduling SMT. | Resource choices remain disjunctive after timing is made compositional. | A typed interface does not itself eliminate the scheduling search. |

Primary sources: [thermal workflow](https://arxiv.org/html/2602.06999v1), [non-DC electromigration](https://link.springer.com/article/10.1007/s11664-026-12922-x), [2025 timing paper](https://arxiv.org/html/2510.15907v1), [2026 timing successor](https://arxiv.org/html/2608.04036v1), [Wit-HW](https://arxiv.org/html/2508.14414v1), [KFDD test generation](https://www.ag-rn.tzi.de/doc/konf/ETS2026_MS.pdf), and [timeline-type discussion](https://capra.cs.cornell.edu/latte26/paper/latte26-final17.pdf).

The thermal manuscript's arXiv record also identifies an ITherm 2025 publication. Likewise, the NoC paper uploaded in August 2026 explicitly identifies itself as FPL 2024 work. Upload dates were not treated as invention dates. [Thermal publication record](https://arxiv.org/abs/2602.06999), [NoC manuscript](https://arxiv.org/html/2608.17266v1)

**The strongest shared hypothesis, and why it does not advance**

The hypothesis was: replace weak local summaries with small summaries that preserve the consequences of composition, together with a rule for refining them only when the surrounding system can distinguish the lost information.

The desired capability is consequential. A successful new construction could become an operation that future thermal solvers, PDN analyzers, architecture simulators, security checkers, or compilers repeatedly invoke. It would offer structural reuse rather than merely a new report format or front end.

However, that statement does not yet specify a new construction. Its concrete forms reduced as follows:

| Proposed operation | Existing computational mechanism that threatens novelty |
|---|---|
| Eliminate thermal interiors while preserving boundary response; enrich missing modes with error control. | Schur complements, static condensation, optimal/adaptive port spaces, and multiscale methods. |
| Carry legal workload histories through linear physical dynamics and optimize the extremal response. | Constrained hybrid reachability and support-function/polyhedral propagation. |
| Merge PHY states while preserving conditional retry, completion, and backpressure behavior. | Probabilistic I/O equivalence, stochastic quotients, and approximate reachability reduction. |
| Merge almost-commuting timing events while bounding downstream error. | Approximate partial-order reduction over metric transition systems. |
| Partition faults by distinguishability and choose interventions to separate them. | Active diagnosis/controller synthesis for partially observed systems. |
| Export temporal share/randomness dependencies and compose masked components. | Existing probing-security composition strategies and symbolic dependency tracking. |

Relevant primary roots include [adaptive port reduction](https://doi.org/10.3182/20120215-3-AT-3016.00123), [optimal port spaces](https://arxiv.org/abs/1808.02946), [SpaceEx](https://verimag.univ-grenoble-alpes.fr/details.html?lang=en&pub_id=FrehseLGDCRLRGDM11), [probabilistic I/O bisimulation](https://www3.cs.stonybrook.edu/~stark/REPORTS/bisimulation.pdf), [approximate partial-order reduction](https://arxiv.org/pdf/1610.06317), [active diagnosis](https://www.sciencedirect.com/science/article/pii/S0022000016300198), and [MATCHI's composition machinery](https://github.com/cassiersg/matchi).

These are not interchangeable algorithms. Their assumptions and semantics differ. Their relevance is that each supplies the obvious operation in the corresponding formulation; merely putting all six under one name would conceal that fact.

The unresolved step was a particular new closure, elimination, inference, or refinement rule that is both useful under explicit hardware assumptions and meaningfully different from these mechanisms. No such rule survived this pass. Claiming that a compact summary exists is especially insufficient when constructing it may require the original state-space computation.

A cheap falsification pattern emerged: find two histories or component states assigned the same summary, and one allowed continuation that makes them behave differently. If the repair is simply to retain the complete product state or invoke the original exact solver, the proposed compression has not yet created the claimed capability. This is a test for a proposed representation, not a theorem forbidding useful restricted abstractions.

**New mechanism families added to the exclusion set**

1. **Adaptive thermal boundary macromodels using ordinary port reduction.** The open thermal problem survives. The generic boundary-operator/enrichment/certification proposal does not establish novelty over mature numerical methods. Current comparisons must also include layout-aware tools such as 3D-ICE 4.0. [DATE 2026 paper](https://infoscience.epfl.ch/bitstreams/b6e66f65-c8f2-4d93-ae1c-a4956da01387/download)

2. **Waveform-memory electromigration models and standard numerical safety margins.** A stress kernel plus accumulated damage is already current work. Certified margins around reduced models require a new principle beyond ordinary numerical error bounds. Full-text access to the June EM paper was limited; the exclusion concerns its clearly disclosed generic mechanism, not every nonlinear extension.

3. **Workload-constrained PDN extrema through generic hybrid reachability.** Independent envelopes admit impossible combinations, but retaining a legal workload automaton and physical state does not remove the combined search. Strong baselines already optimize constrained current waveforms; reverse-pulse analysis alone is too weak a comparison. [Wavelet optimization, 2008](https://www.eecg.utoronto.ca/~najm/papers/epep08-imad.pdf), [RLC-grid verification, 2017](https://www.eecg.utoronto.ca/~najm/papers/tcad17-mohammad.pdf)

4. **Contextual chiplet-PHY compression through generic stochastic equivalence.** Preserving marginal latency is insufficient with queue feedback. DICE already includes dynamic PHY/FEC/retry effects and reports modest mean simulation overhead, weakening an assumed overwhelming simulation wall. A smaller context-preserving model needs a distinct construction. [DICE, public July 2026 version, §IV](https://arxiv.org/html/2607.24221v2)

5. **Exact or approximate event-order reduction presented as a new timing primitive.** The 2026 symbolic timing work and older exact/approximate reduction methods occupy the generic mechanism. Preserving hazards near digital thresholds remains an important technical obligation; it was not solved merely by carrying a numerical error bound.

6. **Generic active diagnosis or causal intervention for hardware.** Observational indistinguishability is fundamental relative to the allowed interface. Intervention helps only when available actions can separate hypotheses. Active-diagnosis synthesis and adaptive interventional debugging already formalize that strategy. [Causality-guided debugging](https://arxiv.org/abs/2003.09539)

7. **Partial-assignment ATPG and generic testability-preserving synthesis.** PastATPG already targets unnecessary input assignments. Implicant extraction, fault compaction, and local testability-preserving transformations are substantive baselines. The KFDD overhead problem does not itself supply a new transformation calculus. [PastATPG, DAC 2025](https://ieeexplore.ieee.org/document/11132425/), [older testability-transformation literature](https://ira.informatik.uni-freiburg.de/en/src/publications_short_tfi.php.html)

8. **Temporal masking summaries without a new composition rule.** State-sensitive HLS splitting and tracking randomness/share validity are already represented by MaskedHLSVerif and MATCHI. This does not establish arbitrary temporal or higher-order security. It excludes the generic proposed repair. [MaskedHLSVerif](https://arxiv.org/html/2603.18939v1)

9. **Resource/timing contracts and control-flow decomposition as the centerpiece.** Existing CGRA mapping, Filament, and the 2026 timeline-type proposal already supply substantial machinery. The residual challenge is an algorithm for the coupled choices, not merely a contract or interface. [CGRA mapping](https://arxiv.org/html/2508.02167v1), [Filament](https://arxiv.org/abs/2304.10646)

10. **ECO support enumeration or schedule-preserving change transport without a distinct operation.** The former has a strong DAC 2025 baseline; the latter returns to the previous pass's excluded equivalence and proof-reuse territory. That overlap was treated as a reason to stop, not as a renamed candidate. [DAC support-selection work](https://62dac.conference-program.com/presentation/?id=RESEARCH1943&sess=sess129), [HLS ECO limitations, April 2026](https://arxiv.org/html/2604.14248v1)

Other early exclusions—joint clock/data optimization, SAT-assisted NoC routing, bounded-cutwidth approximate-error computation, and simulation-guided approximate synthesis—are recorded in the timing/compiler notes. They were not promoted as serious near-misses after direct collisions were found.

**Why this is a KILL at the present gate**

The failure is not an inability to prove field-wide uniqueness. A clearly stated new mechanism, explicit assumptions, no obvious prior-art defeat, a cheap killer, and credible new capability would have been enough to advance. The stronger formulations examined here lacked that distinct computational step after the adjacent-field checks.

The first falsifications are inexpensive: an algebraic reduction to an existing operator, a small pair of indistinguishable histories with a separating continuation, or a comparison of the proposed rule against an already published composition theorem. The serious mechanisms were evaluated against those tests. None justified asking the user to spend effort on a Claude/Codex review yet.

Confidence is high in the direct prior-art collisions and more limited in the broader negative judgment about the unification hypothesis. No probability is assigned to the existence or absence of a suitable project elsewhere. Commercial and patent coverage is preliminary; proprietary completeness is not assumed. Reported results were not reproduced, and a few sources were available only as abstracts or institutional records. None of those limitations is used as positive evidence of novelty.

The gate remains **SEARCHING**. No standard survivor brief or independent-review prompts are issued because no candidate survived. Reopening an excluded family would require a specific new computational rule and a demonstrable distinction from its strongest threat, rather than another implementation plan.

**Preserved detailed records**

The following records contain the per-mechanism baseline, exact limitation, fundamental-versus-engineering assessment, proposed operation, adjacent-field attack, cheap falsification, and prospective reusable object:

- [Physical analysis, reliability, PDN, and chiplet notes](<C:/Users/meetb/OneDrive/Documents/GhostForge/ideation v2/SEARCHING-pass2-coupled-physics-notes.md>)
- [Diagnosis, test/DFT, and ECO notes](<C:/Users/meetb/OneDrive/Documents/GhostForge/ideation v2/SEARCHING-pass2-silicon-test-notes.md>)
- [Timing, compiler, security, and boundary checks](<C:/Users/meetb/OneDrive/Documents/GhostForge/ideation v2/SEARCHING-pass2-timing-compiler-notes.md>)
- [Previous pass, retained as exclusions](<C:/Users/meetb/OneDrive/Documents/GhostForge/ideation v2/SEARCHING-verdict-2026-09-11.md>)

KILL
