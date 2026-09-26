# Living research state (working memory; survives context compaction)

Labels: **OBSERVED** (run/read here) · **ARCHIVE** (established by an earlier wave's primary evidence) · **PAPER** · **INFERRED** · **UNVERIFIED** · **HYPOTHESIS** (proposed, not shown).

## Objective (the researcher's request, unchanged)
One defensible, original semiconductor/EDA research thesis: a consequential problem, a technically distinct mechanism, prior-art prosecution that states the exact delta, and a first experiment that tests OUR mechanism against the STRONGEST baseline. The results must be reusable and plausibly publishable. Do not fabricate a survivor. Everything is done inline, with no subagents (the user's explicit instruction). Advisory budget ≈ $80 of a $100 allowance.

## Settled prior conclusions (ARCHIVE; do not reopen)
- TRACE/Yosys arithmetic verification: ENGINEERING ONLY (11_). PR #6231 is a real bug fix, not research.
- Wave 10: MappingEvolve KILLED (the gain was delay relaxation plus a weak baseline; emap wins at iso-delay). OpenROAD resynth annealing/genetic KILLED (harmful; repair_timing is better).
- Wave 11 (not in the brief, found in the archive): standard-cell mapping area recovery. Every mechanism (LR pricing, trade-off curves, exact windows, budgeting, tolerance) was OCCUPIED. Evolved H1.6 (ambiguity-restricted exact covering) was only partly tested. E1 Phase A data exists (10 circuits); there is no final decision document and Phase B (ε runs) was never run.
  - My reading of the E1 data (OBSERVED from `13_WAVE_11.../experiments/results/e1/*.jsonl`): exact covering over `map`'s space beats `map` by roughly 0.4–14%. Against the BEST heuristic (emap / &nf) it wins by about 2–3% on roughly half the circuits and loses on others (c499: &nf 31.08 vs exact UB 35.59 at D0). The covering-level headroom over the state of the art is small. The lever, if any, is the candidate space, which is occupied (choices, supergates).
- Earlier kills (kill DB): MOSAIC, HBRoute, DITSpec-HLS (original form), DeltaRTL, ArchWitness, GhostForge, FPExtrema (fixed format), generic resource sharing, generic certificates/liveness, memory-mapper cliffs (engineering).
- Session 1 methodology audit: literature-first discovery produced 0 survivors in about 45 probes. Real findings came from execution. The field rewards "known ingredients + a new capability + strong evidence".
- Waves 8/9: missing locally (recovery notes). Not reconstructed.

## Territories heavily mined by the archive (avoid unless new evidence)
Formal/IC3/PDR/certificates; arithmetic verification; constant-time/masked HLS; tech-mapping covering/area recovery; post-placement repair and resynthesis; memory mapping; ECO ordering; Dynamatic buffering (Gurobi-blocked); LLM-evolved heuristics.

## Less-explored territories to probe this session
Hardware for AI inference and arithmetic synthesis; power/physical effects in datapaths; HLS/compilation (non-buffering); architecture/co-design.

## Environment (OBSERVED)
4 CPUs, 15 GB RAM, about 28 GB of free disk, Docker, gcc/clang/cmake, Python 3.11. pip works: ortools 9.15, python-sat, networkx, numpy, scipy. GitHub is reachable. No yosys/abc installed yet.

## Candidate problems / hypotheses (see 02_/03_)
- **Problem A (PRIMARY):** minimum accumulation hardware for hardwired (fixed-weight) linear layers when the base layers must be weight-independent (via/metal-programmable model silicon: Taalas HC1, HNLPU ASPLOS'26, Ankhdjet 2608.26206).
  - **A1 (OUR mechanism):** universal block-pattern generators (UBP-g). The table-lookup mux of runtime LUT-GEMM becomes a via, so g is set by row count and wiring.
  - **A2:** the price of universality vs weight-specific CSE (da4ml) is small.
  - **A3:** CBP, a weight-specific block-pattern control.
  - **A4:** codebook-constrained blocks. Untestable here.
- **Problem B:** functional yield of hardwired weights (B1 encodings, B2 adapter-as-redundancy, B3 bias compensation). Generated and reviewed, not tested.
- **Problem C:** inherited standard-cell mapping. Closed on the Wave 11 evidence re-read.

## Evidence so far (OBSERVED)
- **E1 interim (i.i.d. ternary, all constructions independently checked):**
  - g1/UBP* = 1.78× (n=64, p0=.33), 2.12× (n=128, p0=.33), 1.47×/1.66× (p0=.5).
  - UBP*/da4ml = 1.22–1.37.
  - CBP*/da4ml = 1.21–1.31. So universality itself costs only 1–4%; the rest of the gap is da4ml's non-block sharing.
  - da4ml wall time: 0.5 s at n=64, about 10 s at n=128, and over 600 s at n=256 (so far).
- **Engineering finding:** da4ml 0.6.0 silently solves Kᵀ for F-ordered inputs (`evidence/da4ml_layout_hazard.txt`). Not reported externally.
- **Own-bug caught:** the integer evaluator initially ignored operand shifts. The float trace exposed it; it was fixed before any da4ml number was used.

## Known risks
- The novelty of A1 depends on the HNLPU/Ankhdjet full texts. arXiv is blocked; ★ in 04_.
- Via-select wiring in bit-parallel fabrics may eat the gain (wire model: g≥4 is wire-dominated at SKY130 pitches). Bit-serial is the favourable regime.
- There are no real checkpoints (HF blocked), so all results are i.i.d. ternary.

## Rejected this session
- Generic CSE for hardwired layers (occupied by da4ml / Tridgell).
- Block precompute as a new principle (Four Russians, Lupanov, T-MAC, LUT Tensor Core).
- Via-programmable model silicon as a concept (Taalas, HNLPU, Ankhdjet).
- Glitch-aware MAC (no distinct mechanism).
- Standard-cell covering (Wave 11 data).

## FINAL STATUS (about 11:05 UTC)
- **Decision:** RESEARCH THESIS READY FOR INITIAL PROTOTYPE, scoped to regime (V) (via/metal-programmable, weight-independent base layers) and ternary/binary weights. It is conditional on a full-text novelty check of HNLPU / Ankhdjet / 2604.25183, which the egress block prevented here.
- **E3 (the regime-V test, pre-registered after the diagnosis):** cell area at iso-delay on SKY130 is 1.95× (n=128) and 2.49× (n=1024) smaller at g=4. With modelled wiring on the measured cells, g=3 gives 1.81× and 2.06× (logic-bound at both pitches). 14/14 components valid.
- **Correction:** in regime (F), structural hashing of plain per-input trees recovers most of the sharing (the UBP gain is only 1.04–1.20×; E1-hashed), and da4ml is better. **The (F) claim is withdrawn.** E2 (F, gate level) was stopped after the delay stage (D3) and is consistent.
- **E1 registered verdicts:** K1 and K2 not triggered; the registered advance was NOT met (UBP/da4ml 1.34 > 1.25). E1 was stopped at 4096/p0=.5 with 2 of 3 seeds (D5).
- **All processes stopped.** Everything is committed and pushed on branch `claude/compassionate-edison-91b73q`.

## Next authorized action (for the next session)
1. Allow arxiv.org and dl.acm.org, then read the ★ papers (novelty check).
2. Run OpenROAD/ORFS PnR of 256×256 via-programmable macros (g1_V vs UBP3_V vs UBP4_V), bit-parallel and bit-serial.
3. Build a bit-serial generator.

