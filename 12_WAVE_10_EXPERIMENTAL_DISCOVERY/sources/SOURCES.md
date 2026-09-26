# Sources consulted in Wave 10

All of these were accessed 2026-09-25. "Fetched" means the page was retrieved and summarized. "Search hit" means only the search-engine snippet was seen; those are **UNVERIFIED** at the primary source. No full-text PDFs were saved locally.

## Primary object of study (C1)

Fetched:
- **MappingEvolve: LLM-Driven Code Evolution for Technology Mapping.** R. Fu, Y. Liu, Q. Xu, T.-Y. Ho. arXiv 2604.26591v1, 2026-04-29.
  - https://arxiv.org/abs/2604.26591
  - https://arxiv.org/html/2604.26591v1 (Table 2 transcribed through the fetch summarizer: the GPT-5 and mockturtle columns were checked digit by digit against our reproduction, see `04_EXPERIMENTAL_INVESTIGATION.md`; the DeepSeek column could not be reproduced).
- Flians/MappingEvolve (MIT) @ `308f5cc41c1d7243c39fd2ddd02253c1343eb889`. https://github.com/Flians/MappingEvolve (local clone under `third_party/`, fetched 2026-09-25T08:41:59Z, see `evidence/c1_provenance.txt`).
- lsils/mockturtle @ `420f0271ab9f63a1644bf465ab47c970c173bd7b` (MappingEvolve submodule, MIT).

Local only:
- lsils/benchmarks @ `82d8cc6910419298e713a46644ed59fd3df53038` (MIT). The experiments used the copies bundled in mockturtle's `experiments/benchmarks`.

## Landscape and screening

Fetched:
- PPAPlace, arXiv 2608.13790: https://arxiv.org/abs/2608.13790
- Multi-Agent Self-Evolved ABC, arXiv 2604.15082: https://arxiv.org/abs/2604.15082
- AuDoPEDA, "Automated QoR improvement in OpenROAD with coding agents", arXiv 2601.06268: https://arxiv.org/abs/2601.06268
- OpenROAD issue #10900, repair_timing effort: https://github.com/The-OpenROAD-Project/OpenROAD/issues/10900
- Monomorphism-based CGRA Mapping via Space and Time Decoupling, arXiv 2512.02859: https://arxiv.org/abs/2512.02859

Search hits:
- ChiPBench, arXiv 2407.15026 / NeurIPS'25 D&B: https://arxiv.org/abs/2407.15026
- bazel-orfs study PRs #985, #987, #1020: https://github.com/The-OpenROAD-Project/bazel-orfs/pull/1020
- Parendi, ASPLOS'25: https://arxiv.org/pdf/2403.04714
- RepCut, ASPLOS'23: https://dl.acm.org/doi/10.1145/3582016.3582034
- RTeAAL Sim, arXiv 2601.18140
- CCSS, arXiv 2507.08406
- Encarsia, USENIX Security'25: https://dl.acm.org/doi/10.5555/3766078.3766211
- SoK ARCUS, arXiv 2608.23933
- SAT-MapIt: https://arxiv.org/abs/2512.02875
- Dynamatic resource- and phase-aware buffer placement, HEART'25: https://doi.org/10.1145/3728179.3728194
- Physically Aware Synthesis Revisited, arXiv 2408.07886
- LevelSyn, arXiv 2609.03594
- Rethinking Logic Optimization Operators (agentic source analysis), arXiv 2607.23672
- Critical Path Aware Timing-Driven Global Placement for Large-Scale Heterogeneous FPGAs, arXiv 2512.00038
- ZigZag: https://github.com/KULeuven-MICAS/zigzag
- Voyager, arXiv 2509.15205
- ISPD 2025 global routing contest: https://dl.acm.org/doi/abs/10.1145/3698364.3715706

Sources used for the C1 targeted prior art are listed in `03_STRONGEST_PRIOR_ART.md`.
