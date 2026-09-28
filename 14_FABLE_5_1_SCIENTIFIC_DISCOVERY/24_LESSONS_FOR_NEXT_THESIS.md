# 24 — Lessons for the next thesis (UBP closeout, Phase A4)

Each lesson has three parts:
- **Evidence:** what happened in UBP, with its record;
- **Practice:** what the next thesis does differently;
- a check where one exists in `SUPPORTING_ARTIFACTS/research_harness/`.

The short rule list derived from these lessons is `SUPPORTING_ARTIFACTS/NEXT_THESIS_RESEARCH_RULES.md`. Numbered lessons 1–12 in `01_RESEARCH_HISTORY.md` are the in-flight lessons; this list is the retrospective one.

**The one-paragraph version.**
- UBP was correct, reproducible and physically real, and it still lost.
- Its advantage was measured first against weak baselines, then under idealized physical costs, and only at the end with full cost on both sides.
- Each step down in idealization removed part of an advantage that never had enough headroom to spare.
- The mechanism went through six revisions, each rescuing the last.
- What made the ending clean was the pre-registered rule and the independent validation. What would have made the project cheaper is a strongest baseline and a full-cost evaluator in the first week.

---

### 1. Put the strongest baseline in place from day one

**Evidence.**
- The origin claim compared UBP with per-input adder trees: 1.8–3.7× fewer adders (E1).
- With structural hashing, the default synthesis behaviour, the gap fell to 1.07–1.20×, and weight-specific CSE (da4ml) was better. The full-custom claim (F) was withdrawn (13_FABLE).
- The frontier-style popcount fabric P2 entered only at Gate 3. The competitor that eventually decided the kill, A-R2 (per-input serial with structured access), was first built at R2.
- In Week 2, UBP and every competitor, A-R2 included, received the same full physical treatment for the first time, and R moved from the R3 figure of 1.66 to 1.47.

**Practice.**
- Name the strongest baseline B before the first candidate number: the best published or default-tool approach for the same problem, under the same constraints.
- Implement B through the same evaluator.
- Whenever the candidate gets a new treatment (sizing, corners, access style), B gets it in the same run.
- A candidate number quoted without B under identical treatment is not a result.

**Check.** `decision.ratio_rule(required=[...])` returns INCOMPLETE until every required competitor is complete.

### 2. Count the physical costs early

**Evidence.** Costs that were idealized until late:
- **Taps.** 2,192 of them, drawn as 2-site cells with `buf_4` timing, i.e. buffers without area. As real cells: +10,971 µm², **+6.5%** of UBP's area, against +0.7% for A-R2 (21 §3.3).
- **Spine drivers.** Unsized until Week 2; then 551 violating nets, 609 repeaters, and utilization after placement rising from 60.4% to 64.1%.
- **Reachability.** 4.33× more potential programmable connections than a per-input fabric (DERIVED). It was invisible in cell counts and only surfaced when the placer had to realize it (G2).
- **Corners.** Single-corner (tt) timing until Week 2. The ss corner moved R by about 0.15.
- **Routing at the target utilization.** P2 at 67% stopped routing once sized (GRT-0116 / GRT-0232).
- **Congestion from the placer.** A generic placer clustered the taps and "manufactured" a collapse (G2).

**Practice.**
- The first physical experiment includes one **full-cost** configuration, crude if necessary: every cell real with its area, the flow's own sizing and repair on, extracted parasitics, the slow corner, and the target utilization.
- Idealized models are used only as upper bounds on the candidate, never as the comparison.
- The costs to enumerate are buffers, taps and ports, routing and congestion, placement changes, clock and control distribution, realistic cells, and corners.

**Check.** `accounting.flow_changes` shows what the flow added after the floorplan metric; `sta.multi_corner` gives tt/ss/ff for every design.

### 3. A local improvement can lose globally

**Evidence.**
- The Week 2 rule fixed exactly what it targeted: the tap-input transition fell from 1.32 to 0.30 ns, and programmable paths left the critical path at every corner.
- The slow-corner period was then set by a path the mechanism never touched: the W-independent tree-start broadcast `st_tree`, one flop driving the first adder stage of all 64 rows.
- The flow's tt-driven buffering left UBP's flop driving 25 loads and 256 fF (1.471 ns at ss, T_ss = 4.180 ns), against 10 loads and 59 fF in A-R2 (T_ss = 3.888 ns).
- That 7.5% period difference, on a shared control net, decided a 1.47 vs 1.50 outcome.

**Practice.**
- Every result table reports **what limits the figure of merit** for the candidate and for B (the critical path's largest stage at each corner, the congestion hot spot, the dominant area component), not only the path the mechanism improves.
- A mechanism that improves its own component has shown nothing about the system until the limiting component is identified in both designs.

**Check.** `sta.parse_path` returns every stage and the largest one; test `test_week2_decisive_path_is_the_tree_start_broadcast` reads the kill's cause from the committed logs.

### 4. Margin matters

**Evidence.**
- The idealized R3 result at 60% was 1.663×, against a threshold of 1.5: headroom 1.11×.
- The full-cost Week 2 result was 1.473×, so the realistic overheads together cost 1.663 / 1.473 = **1.13×**, more than the headroom.
- Accounting choices alone spanned more than the margin: 1.442 (flow-inclusive area), 1.473 (decisive), 1.557 (the historical 2-site tap convention), 1.62 (tt).
- The secondary operating point, 52%, gave 1.21.

**Practice.**
- Do not pick an arbitrary required speed-up.
- Instead, measure the overhead factor between the idealized and the full-cost evaluation on the **first** full-cost pilot (lesson 2).
- Require the idealized advantage to exceed the threshold by more than that factor, with room for the spread of accounting conventions.
- A thesis whose idealized advantage sits within one overhead factor of its threshold is a knife-edge. Treat it as not ready, or find a mechanism with structural headroom: an asymptotic or order-of-magnitude effect, or one that removes a whole cost class rather than shaving one.

### 5. Separate the mechanism from host artifacts, in both directions

**Evidence.**
- **Host artifacts that looked like mechanism failures:**
  - the placer's tap clustering (G2), fixed by W-blind placement (R2), not by changing UBP;
  - a 20-iteration routing cap below the tool default (lesson 8 in 01);
  - ORFS/Yosys dead-logic elimination silently making the "universal" fabric W-specific: up to 27% area understated (A2).
- **A host artifact that decided the outcome:** the unsized, W-independent control broadcast (lesson 3). It was part of the measured system, applied identically to all fabrics, and the pre-registered rule judged the system. Calling it an "artifact" after the fact would have been a rescue.

**Practice.**
- Before interpreting an effect, classify it by an ablation that holds the mechanism fixed and changes the host (placer, flow step, effort, control distribution), and vice versa.
- Decide **before** the decisive test which host components are part of the system being judged. Size or treat them identically for every design, and never reclassify them afterwards.

### 6. Pre-register the decisive experiments

**Evidence.**
- 09 (R3) and 21 §1 (Week 2) were committed before any build: metric, corners, competitors, fallbacks, threshold, primary operating point.
- Without them, 1.473 would have been "within noise of 1.5", the nominal 1.62 would have been the headline, and the 2-site convention's 1.557 would have been a pass.
- The post-hoc rigor checks of R3 (1.478–1.795) moved the claimed number without moving the classification. That was correct, but the "robust at 60%" headline they supported did not survive (01 lesson 12; withdrawn in 22 §8).

**Practice.**
- Commit the rule (metric, threshold, competitors, corners, operating point, fallbacks, validity conditions) before the first result. Afterwards, only deviations are logged, never changes.
- Pre-register tool effort at the tool's default.

**Check.** `prereg.audit` proves from git that the rule's commit precedes every result commit; `first_version` returns the rule of record.

### 7. Validate independently

**Evidence.**
- Every programmed netlist, including OpenROAD's routed one, went through Yosys and the Liberty functions to AIGER, into our own simulator, against numpy.
- Oracle and program mutants had to be rejected (every design and program, G2 through Week 2).
- Frozen-base invariance was checked by ODB sha256 and DEF section diffs after every program.
- Raw metrics were recorded per program, with 5 matrices, 2 utilizations and 3 corners.
- Two Week 2 flow defects were caught before any timing result existed:
  - The Liberty `max_transition` was inserted before `buf_k`'s own 1.5 ns (the last attribute wins), so the flow saw no violation. It was noticed because `repair_design` had changed nothing, and an OpenSTA probe confirmed it (21 §2.4).
  - `dont_touch` taps blocked `repair_design` (RSZ-3006).
- The kill is credible because nobody can attribute it to a bug.

**Practice.**
- The oracle shares no code with the generator.
- Every check is paired with a mutant it must reject.
- Every constraint written into a tool is read back and probed; a probe must show the tool reacting to it.
- Every scalar in a decision comes from more than one instance (inputs, seeds, programs).

**Check.** `oracle.checked` / `oracle.verdict` fail a check that is blind to its mutants; `liberty.pin_attribute_values` reads edits back.

### 8. A known ingredient does not occupy a contribution, but combining known ingredients is not automatically research

**Evidence.**
- Gate 1 found each ingredient of UBP known: activation-group / subexpression sharing across neurons, and via- or metal-programmable bases (structured ASICs; Taalas-style model-specific silicon).
- The composition was likely obvious, so novelty had to rest on a *physical characterization* (the reachability law, R3 access).
- That characterization then had to beat the strongest baseline under full cost, and it did not by the required margin.

**Practice.** In prior-art prosecution, separate:
- (a) the known ingredients;
- (b) the predictable result of combining them;
- (c) any **non-obvious interaction**: an effect that neither ingredient predicts, is measured, and is needed for the claim.

A thesis needs (c) or a genuinely new ingredient. "Nobody has combined X and Y" is not (c).

### 9. The problem survives the mechanism's failure, but stop mutating a failed mechanism

**Evidence.**
- The problem is still open: sharing arithmetic in weight-independent inference silicon without W-dependent base logic.
- The mechanism, however, went through E3 → E5 (bit-parallel) → E6 (bit-serial) → G2 (generic placement) → R2 (crossbar) → R3 (segmented) → Week 2 (sized).
- That is six substantive revisions, each rescuing the previous one's failure, and each spending the headroom the next step needed.

**Practice.**
- At most two substantive mechanism revisions per thesis, counted from the first decisive test.
- After that, either a different mechanism for the same problem, entering as a new candidate with its own baseline and falsifier, or a different problem.

### 10. The evaluator should help invent

**Evidence.**
- The most productive moments were diagnoses:
  - G2's overflow maps showed tap clustering;
  - the interval/track-demand model calibrated on R2's failure designed R3, the one revision that closed routing (met4 usage 47% → 16.5%);
  - Week 2's per-stage path decomposition named the control broadcast.
- The evaluator's *explanations* produced the next hypothesis; its scalars only produced verdicts.

**Practice.**
- Build evaluators that output causes: per-component cost breakdowns, limiting paths, congestion locations, and which constraint binds.
- Use them to generate candidate mechanisms early (within the revision budget of lesson 9), and to kill candidates cheaply.

### 11. Reproducibility before scale (become parametric earlier)

**Evidence.**
- G2, R2 and R3 were built by per-gate scripts. `ubpgen`, the parametric generator, arrived only in Week 1, and making it reproduce R3 bit-exactly took the whole week.
- Week 2 needed 6 sized designs × 5 programs × 3 corners, plus re-timed historical rows and two pre-registered fallbacks. That was feasible only because every step was config-driven, hashed, recorded and resumable.

**Practice.**
- The first experiment beyond a paper model already runs through a config → record pipeline: one command per stage, append-only records with config hash and git state, and regenerable databases kept out of git.
- The harness provides this from day one.

### 12. No rescue loops (a bounded evolution allowance)

**Evidence.**
- After the Week 2 kill, the available "fixes" were obvious and cheap: buffer the control broadcast, redesign the taps, count taps the historical way, or promote the tt reading.
- Each would have been a rescue: a change chosen after seeing which way the result went.
- The closeout forbids all of them (22 §10).

**Practice.**
- Allow at most **one bounded evolution** per decisive failure. It is declared in the pre-registration as a named fallback, before the result.
- A pre-registered kill is final for that thesis.
- Anything else learned becomes a lesson or a new candidate, which starts again at rule 1.

---

### Additional lessons (engineering, from the same record)

13. **Tools change the design silently; cross-check.**
    - Dead-logic elimination pruned "universal" logic (A2).
    - The last Liberty attribute wins.
    - `dont_touch` blocks repair.
    - DEF writes FIRM placements as FIXED.
    - Guard against all of these with an area cross-check (flow vs synthesis vs closed-form count) and read-back probes.
14. **Label every number** MEASURED / EXTRACTED / MODELED / DERIVED, and never form a ratio across labels. UBP's early ratios mixed ABC-model delay with measured area (E3), and were later withdrawn as physical evidence.
15. **The operating point is part of the claim.** 52% gave 1.21 and 60% gave 1.47. P2 at 67% did not route once sized. A claim names its operating point and the pre-registered fallback if that point fails.
