# 01 — Research history (lineage and lessons that shaped Wave 14)

Full history: `13_FABLE_5_1_SCIENTIFIC_DISCOVERY/01_RESEARCH_HISTORY_AND_LESSONS.md`. This file records only what Wave 14 inherits and what it learned.

## Lineage

**Waves 3–11** (HIST-OBS): no research survivor.
- TRACE/Yosys work was engineering.
- MappingEvolve and OpenROAD resynthesis were killed.
- Wave 11's covering headroom was ≈ 2–3% over the best heuristic.

**Lesson:** optimization-heuristic ideas in mature EDA sub-problems are exhausted. Look for **new cost regimes** created by new product constraints.

**13_FABLE_5_1** (previous session; the single survivor):
- **Regime V:** hardwired inference silicon with weight-independent base layers.
- **Mechanism:** universal block-pattern generators, **UBP-g**.
- **Evidence:**
  - exact adder counts ≈ g× lower;
  - Theorem 1 (port bound, met with equality);
  - E3 cell area 1.95×/2.49× at iso-delay (bit-parallel, SKY130, ABC delay model).
- **Withdrawn:** the full-custom (F) claim. Structural hashing gives plain trees most of the gain.
- **Left open:** wiring (modelled only); novelty vs HNLPU (full text unread).

**Wave 14** (this session):
- The physical test of the open wiring question, bit-parallel (E5).
- One evolution iteration, bit-serial (E6).

## Lessons carried in

1. **The baseline decides the claim.** The (F) claim died because the baseline (unhashed trees) was weaker than what synthesis does by default. Here the baseline is the regime-V status quo at its best: the per-input universal fabric with shared negation, which is the HNLPU/Ankhdjet ternary form. It is synthesized with the same flow.
2. **Independent validation catches silent tool failures.** da4ml's F-order hazard (previous session) was caught only by our own checker. Here every netlist, including the final routed one, is simulated by our own AIG simulator against numpy.
3. **Pre-register, then log deviations** (09, D1–D4, D6.1).

## Lessons learned in this session (NEW-OBS)

1. **Historical defect found in the previous E3 (recorded, not hidden).**
   - E3 negated 8-bit lines into 9 bits (`NEG{w}` outputs w + 1 bits, since −(−128) = 128), but sized every tree's leaves at w bits.
   - Both fabrics' trees were therefore one bit too narrow for the extreme negative input. g1 has n leaves per row versus ⌈n/g⌉ for UBP, so g1's area was understated more.
   - The E3 ratios are thus **slightly conservative** (NEW-INF, not re-measured).
   - This session uses **symmetric INT8 [−127, 127]**, BitNet b1.58's activation range, so negation never overflows.
2. **Pre-placement module timing is not a sound iso-delay budget.**
   - OpenSTA on SKY130 gives module delays far above the ABC load-independent model: GEN3 3.59 ns; UBP3 path 9.37 ns vs g1 6.57 ns at n = 32.
   - A fixed 6 ns iso-clock would have measured timing repair, not wiring. Hence Amendment A1: a relaxed clock plus natural delay reported separately.
   - The E3 "iso-delay" ratios (ABC model) are therefore probably **optimistic for bit-parallel UBP**: its real generator/negator delay leaves less budget for its trees (NEW-INF).
3. **Generator/negator carry chains put a 1.43× delay penalty on bit-parallel UBP.** This is the reason for evolution iteration 1 (bit-serial, E6), where the penalty becomes +1 cycle of latency (7 → 8 cycles at n = 64).
4. **Default tool clean-ups silently made the "universal" fabric weight-specific (Amendment A2).**
   - Yosys `opt_clean -purge` dropped negators of unused lines, and ORFS's `eliminate_dead_logic` dropped generator logic feeding unused lines. Together they understated UBP area by up to 27% (ubp4, n = 32).
   - Nothing failed. The routed results looked clean and even validated functionally, because pruned logic is functionally dead.
   - It was caught only by an **area cross-check**: ORFS `synth__design__instance__area` against Yosys `stat -liberty` of the same netlist, plus a closed-form count of negator instances.
   - **Lesson for regime-V studies:** the invariant "fabric area does not depend on W" must be *checked*. Functional equivalence cannot detect its violation.
5. **Tool-format pitfalls** (engineering, recorded for reuse):
   - OpenSTA's Verilog reader rejects `signed`, wire initializers and behavioural processes. Re-emit through Yosys, strip `signed`, and instantiate top-level flip-flops as cells.
   - OpenROAD needs `read_lef` before `link_design`. `sta::worst_slack` returns seconds.

## Lessons from gates G1–G3 (2026-09-27, NEW-OBS)

6. **A layout that sees W hides the cost a weight-independent base must pay.**
   - E6 and G3 placed each line driver next to its 2–3 users. UBP's 5.8× select-wiring saving came from that.
   - A fixed base must make all 548 lines reachable from every row, and that reachability is the real cost.
   - **Lesson:** regime-V claims need a W-blind placement test (G2), not just a W-independent netlist (A2).
7. **A generic placer can manufacture a collapse.**
   - Connectivity-driven placement cannot see programmable nets. It clustered every line tap, and B failed at every utilization down to 8%.
   - The overflow maps (one vertical stripe through the tap cluster) exposed the cause.
   - A W-blind crossbar floorplan (R2) removed it for every design.
   - **Lesson:** diagnose where the overflow is before concluding a physical failure is intrinsic.
8. **A pre-registered effort cap below the tool default can manufacture a failure.**
   - The G2 protocol capped detailed routing at 20 iterations; ORFS uses 64.
   - B failed the 20-iteration criterion at U45–60. Post hoc, with 64 iterations, it closed at U45 but not at U52 (117 residual) or U60 (410): the cap was binding at 45 only.
   - The pre-registered classification stands. **Lesson:** pre-register tool effort at the tool's default unless there is a reason not to.
9. **Line count and line load trade off.** UBP's lines are 4.3× more numerous but lightly loaded (≈ 2.6 sinks), so they are the fastest programmable paths. The per-input popcount fabric's heavily loaded lines cost it 1.6–1.7 ns.
