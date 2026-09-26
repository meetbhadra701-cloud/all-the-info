# RESEARCH_STATE — Wave 14 (compaction-safe working memory)

**Labels:**
- **HIST-OBS:** a previous experiment established it.
- **HIST-INT:** previous reasoning.
- **NEW-OBS:** established this session.
- **NEW-INF:** inferred this session.
- **NEW-HYP:** proposed, not established.

## Objective

- Develop and test ONE technically distinct mechanism for a consequential semiconductor/EDA problem, against the strongest baseline.
- At most 2 evolution iterations; a mandatory meta-review; one of the 7 decision classes.
- Commit locally only. **No push without the researcher's authorization.** Budget ≈ $75–80.

## Established historical facts (do not re-derive)

- **HIST-OBS:** Waves 3–11 produced no survivor (TRACE, MappingEvolve and OpenROAD resynthesis were killed; covering headroom ≈ 2–3%).
- **HIST-OBS (13_FABLE_5_1):** UBP-g in regime V.
  - Adders ≈ g× lower (exact); Theorem 1 (port bound, met with equality).
  - E3 cell area 1.95×/2.49× at an ABC-model iso-delay.
  - Wiring was only modelled. The (F) claim was withdrawn (hashing).
- **NEW-OBS:** E3 sized trees for w-bit leaves while negation outputs w + 1 bits. Its ratios are slightly conservative (01).

## Problem tree (details in 03)

- **P1 (primary):** accumulation hardware under weight-independent base layers (regime V).
  - **H1.1 (bit-parallel UBP):** tested by E5.
  - **H1.2 (bit-serial UBP):** evolution iteration 1, tested by E6.
  - H1.3: merged.
- **P2 (reserve):** functional yield via adapter-as-redundancy. Not executable here.
- **P3:** merged/killed (= Paar/da4ml CSE).

## Primary hypothesis and exact mechanism

- **Mechanism:**
  - GEN(g) per block of g inputs produces all (3^g − 1)/2 canonical signed subset sums, weight-independent.
  - A shared NEG per pattern line.
  - Each neuron is a TREE(⌈n/g⌉) whose leaves are connected by via/metal to a line, its negation, or zero.
- **Hypothesis:** routed area ≤ g1 routed area / 1.5 at matched constraints.
  - E5: bit-parallel, 20 ns clock, natural delay reported.
  - E6: bit-serial, 3.0 ns clock, equal throughput.

## Strongest prior art (07, evidence/prior_art_search_2026-09-26.md)

- **Runtime LUT accelerators** (TENET: mirror-half shared precompute + sign index; T-MAC; LUT Tensor Core; 2604.25183) have the same arithmetic, with runtime indices.
- **Hardwired silicon** (HNLPU, Taalas, Ankhdjet, BitROM, TOM) is g = 1 in every retrieved summary.
- **Combination:** not found, but **likely obvious**.
- **Untested competitor:** ROM-based distributed arithmetic as a via-ROM (regime-V compatible).
- Novelty is **provisional**: HNLPU's full text is unread.

## Critical assumptions

- (A1) Select wiring does not eat the logic saving. **Under test.**
- (A2) The fabric can be realized with fixed placement and upper-metal-only programmability. Not tested; the evaluator allows placement freedom.
- (A3) g1_V is the strongest regime-V baseline. **Challenged by DA-via-ROM** (not testable with standard-cell PnR).

## Experimental status (22:50 UTC)

- **E5** (n = 32; g1, ubp3, ubp4; U ∈ {60, 75}): running.
  - Build validated, mutation controls detect.
  - GRT at U = 60 shows no overflow for g1 and ubp3. ubp3 uses 54% of routing resources vs 45% for g1.
- **E6** (n = 64 bit-serial): the first launch failed at stage 1 (a netlist-format issue; D6.1). Fixed, rebuilt and re-validated; PnR is running.
  - Latency: g1 7 cycles; ubp3/ubp4 8 cycles. Throughput 14 cycles/word for all.

## Killed mechanisms and revisions

- **Killed:** H3.1 (hash-friendly pairing = known CSE).
- **Revision 1:** H1.1 → H1.2 (bit-serial), because bit-parallel UBP carries a 1.43× combinational delay penalty (9.37 vs 6.57 ns at n = 32) from generator/negator carry chains.

## Unresolved questions

- HNLPU full text (novelty).
- Fixed-placement, upper-metal-only routing.
- Strap demand in a via-ROM-style fabric.
- DA-via-ROM as a baseline.
- Scale (n ≥ 256).

## Next authorized action

1. Collect E5 and E6 (`e5_collect.py`) and run post-PnR validation on the U_max netlists.
2. Apply K5/A5 and K6/A6.
3. Write 10–14 and 00, then commit locally.
