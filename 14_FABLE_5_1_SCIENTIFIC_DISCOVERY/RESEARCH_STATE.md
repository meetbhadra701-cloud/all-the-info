# RESEARCH_STATE — Wave 14 (compaction-safe working memory)

**Labels:**
- **HIST-OBS:** a previous experiment directly established it.
- **HIST-INT:** previous reasoning.
- **NEW-OBS:** established this session.
- **NEW-INF:** inferred this session.
- **NEW-HYP:** proposed, not established.

## Objective (the researcher's)

- Develop and test ONE technically distinct mechanism for a consequential semiconductor/EDA problem.
- Build the evaluator around OUR mechanism against the strongest baseline.
- Allow at most 2 evolution iterations, and write a mandatory meta-review.
- Commit locally only. **No push without the researcher's authorization.**
- Budget guideline: about $75–80.

## Established historical facts (do not re-derive)

- **HIST-OBS (Waves 3–11):** no research survivor. TRACE/Yosys was engineering. MappingEvolve and OpenROAD resynthesis were killed. Wave 11's covering headroom is ≈ 2–3% over the best heuristic.
- **HIST-OBS (`13_FABLE_5_1_…`, previous session):** a problem in **regime (V)**, i.e. hardwired inference silicon whose base layers are weight-independent (HNLPU M8–M11-only programmability; Taalas 2 metal layers; Ankhdjet via-mask).
  - **Mechanism UBP-g:** universal block-pattern generators (all signed subset sums of g inputs), plus ⌈n/g⌉-leaf row trees, plus via selection of lines.
  - **Adders:** exact closed form ≈ g× fewer than the per-input universal fabric, W-independent.
  - **E3 (cell area, iso-delay, SKY130, bit-parallel, weight-independent components):** 1.95× (n=128) and 2.49× (n=1024) at g=4; 14/14 components validated.
  - **Wiring was MODELLED only:** g=3 robust at ≈ 2×; g=4 wire-sensitive.
  - **Theorem 1 (port bound; proven):** UBP meets it with equality.
- **HIST-OBS correction:** in regime (F) (full-custom), synthesis structural hashing gives plain per-input trees most of the benefit (UBP only 1.04–1.20× better), and da4ml is better. The (F) claim was withdrawn.
- **HIST-INT:** scope is ternary/binary only; int4 is wire-bound.
- **NEW-OBS (this session, 22:1x UTC):** arxiv.org, ACM, HF, yongwei.site and emergentmind are still blocked (HTTP 403 policy). Every retrieved HNLPU summary describes grouping **within** a neuron (16 value regions, POPCNT, distributive law); none mentions cross-neuron sharing. **Novelty stays PROVISIONAL.**
- **NEW-OBS:** dockerd can be started and Docker Hub pulls work, so the ORFS container (OpenROAD + SKY130) is obtainable. `conda.anaconda.org` (litex-hub) is also reachable.

## Problem tree (see 03_RESEARCH_TREE.md)

- **P1 (primary):** accumulation hardware in regime (V).
  - H1.1 bit-parallel UBP: cell level passed.
  - H1.2 bit-serial UBP: evolution candidate.
  - H1.3 cross-matrix generator sharing: a design rule, merged.
- **P2 (reserve):** functional yield of hardwired weights (adapter-as-redundancy). Not testable here (no checkpoints, no defect data).
- **P3 (considered):** a hashing-friendly CMVM ordering in (F). Merged into the known CSE literature during proximity analysis.

## Next authorized action

- **E5:** a physical falsifier for the wiring risk. OpenROAD place-and-route of weight-independent, hierarchy-preserved fabrics (g1_V vs UBP3_V vs UBP4_V, n=m=64, SKY130).
- Pre-register first (09_PREREGISTRATION.md).
