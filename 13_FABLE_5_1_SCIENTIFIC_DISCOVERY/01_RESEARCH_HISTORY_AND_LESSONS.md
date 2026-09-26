# 01 — Research history and lessons (compact map)

Labels:
- **ARCHIVE:** established by an earlier wave's primary artifacts; the path is given.
- **OBSERVED:** re-read or re-computed in this session.
- **INFERRED:** my synthesis.

## 1. Territories investigated, and outcome

| Territory | Waves | Mechanisms tried | Outcome | Why |
|---|---|---|---|---|
| Formal verification (IC3/PDR, polynomial/algebraic, proof reuse, liveness, certificates) | 3–6, GhostForge, Session 1 | Property-directed refinement, certificate transport, L2S witness extraction | Killed or redefined | Existing composition sufficed (L2S). Mechanism proposed before a failing strongest method was shown (GhostForge). |
| Arithmetic verification of Yosys lowering | Session 1, TRACE (11_) | Checked datapath guidance; TRACE as oracle | ENGINEERING ONLY | TRACE plus stage-wise CEC already cover it. The failures were TRACE implementation defects (phase optimisation unsound), not a missing principle. |
| Constant-time/masked HLS, cross-stage security | 6, DITSpec-HLS | Guarantee carried through lowering | Redefined, never survived | Timing is not preserved by the formal rewrite. Tools were unavailable (Vitis). |
| Resource sharing / arith_tree | MUXWISE 1–4 | Sharing; `-arith_tree` timing | Killed; real FMA bug found (PR #6231) | Normal Yosys+ABC already erases the sharing. The defect is engineering. |
| Memory mapping / banking | 4A, 5B | Semantic-contract cliffs | Engineering | Retiming and memory-inference explain it. The first witness was malformed. |
| Physical design (ECO order, repair, resynthesis) | 3, W10 C6, W11 P3 | ECO ranking; SA/GA ABC-script search; LR/budgeting | Killed / engineering | repair_timing beats search. The global methods (LR sizing, budgeting) are occupied. |
| Technology mapping | W10 C1, W11 P1 | LLM-evolved operators; exact covering; ambiguity-restricted exact covering | Killed; W11 unfinished | The MappingEvolve gain was delay relaxation plus a weak baseline. The covering-level headroom over the best heuristic is small (see §3). |
| HLS buffering (Dynamatic) | W10 C4, W11 P2 | Critical-cycle greedy; min-cost flow; slot sharing | Occupied / blocked | TRETS'21 decomposition, slack-matching theory, HEART'25. Gurobi is not available. |
| Hardware reduction tools | PassWitness, PPA-Delta | Coupled reduction | Provisional | Below the pre-registered effect bar. |

## 2. Methods that produced real findings (keep)

Every real finding came from **executing tools** against independent oracles:
- the FMA `arith_tree` defect;
- `&acec` unsound verdicts;
- TRACE's unsound `-p`;
- the MappingEvolve delay-relaxation artifact;
- OpenROAD resynth doing harm.

The disciplines that made them trustworthy, reused here:
- pre-registration with a deviation log;
- fail-closed verdicts;
- an independent checker with mutation negative controls;
- iso-constraint comparison against the strongest baseline.

This session's first experiment already relied on that discipline. The independent checker exposed an input-layout hazard in da4ml 0.6.0 and a bug in my own evaluator, both before any number was used (`06_…` §E1 deviation log).

## 3. What Wave 11 left (not in the brief; re-read here, OBSERVED)

Wave 11's E1 Phase A ran exact CP-SAT covering over mockturtle `map`'s own cut/match space on 10 circuits. There is no final decision document.

Re-reading `13_WAVE_11_…/experiments/results/e1/*.jsonl`:
- Exact covering beats `map` itself by 0.4–14%.
- Against the **best** heuristic at the same delay (emap / ABC `&nf`), it wins by about 2–3% on roughly half the circuits (ctrl, c880, c1908, dec) and loses on others. For example, c499 at D0: &nf 31.08 vs exact UB 35.59. Phase B (the ε-restricted runs that test H1.6) never ran.
- Reading: the covering-algorithm headroom over the state of the art is small. The lever is the candidate space (choices, supergates), which is occupied. **I did not continue this line.**

## 4. Recurring mistakes (and the guard used this session)

| Mistake | Guard |
|---|---|
| Weak baseline manufactures progress (MappingEvolve) | The baseline is the strongest open CMVM method (da4ml), plus the scheme used by current hardwired silicon (per-input sharing). |
| Tool failure read as a missing method (TRACE, rmp) | The thesis rests on a cost structure, not on a bug. The da4ml layout hazard is filed as engineering. |
| Mechanism before evidence of need (GhostForge) | Necessary assumptions are tested first (E1) at the level where they can fail cheaply. |
| Routine combination claimed as novel | Prior art is split into "known ingredient" vs "same complete contribution" (`04_…`). The novelty claim is kept narrow. |
| Mining named future-work seams (occupied within weeks) | This session chose a regime created by a 2026 technology shift (hardwired-model silicon), where the strongest methods are months old. |

## 5. Settled conclusions (treat as established)

- TRACE/Yosys: ENGINEERING ONLY.
- MappingEvolve and OpenROAD search resynthesis: KILLED.
- Kill-DB items (MOSAIC, HBRoute, DITSpec-HLS original, DeltaRTL, ArchWitness, GhostForge, FPExtrema fixed-format, generic sharing/certificates): killed.
- Waves 8 and 9: **still missing locally.** Their recovery notes stand, and no inference was made.

## 6. Less-explored areas at the start of this session

- Hardware for AI inference, and specifically **model-specific (hardwired-weight) silicon**.
- Power effects in datapaths.
- Non-buffering HLS.

The first was chosen (`02_…`).
