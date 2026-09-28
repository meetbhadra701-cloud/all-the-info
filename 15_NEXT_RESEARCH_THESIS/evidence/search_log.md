# Search log (literature phases B4 and B9), 2026-09-28

**Access (checked with curl and the fetch tool).**
- Reachable:
  - web-search result summaries;
  - `github.com` pages through the fetch tool;
  - `raw.githubusercontent.com` through curl;
  - PyPI.
- Refused by the egress proxy: arxiv.org, huggingface.co, dblp.org, dl.acm.org, ieeexplore.ieee.org, semanticscholar.org, fmcad.org, hwmcc.github.io, openreview.net and eprint.iacr.org.

**Labels:**
- **[S]:** summary only;
- **[G]:** GitHub content read.

| # | Query | Main results (URLs as returned) | Used in |
|---|---|---|---|
| 1 | DAC 2026 best paper award EDA | dac.com/dac-2026-general-society-awards: best paper "Miter-Aware LUT Mapping…" (Zhu et al., CUHK); Most Influential "First-order incremental block-based statistical timing" [S] | 01 §1.1 |
| 2 | ICCAD 2026 accepted papers logic synthesis equivalence placement | iccad.com/2026 CFP; arxiv 2408.07886; arxiv 2609.03594 (LevelSyn); named ICCAD'26 papers CorrectRTL, Dr. RTL, E-Layout [S] | 01 §1.3 |
| 3 | FMCAD 2026 accepted papers hardware verification | fmcad.org/FMCAD26 (71 of 172 accepted; fetch refused) [S] | 01 |
| 4 | ISCA 2026 best paper hardware architecture | ISCA'26 best paper to SKKU; "Cerberus: Cross-Layer ECC Co-Design…" [S] | 01 §1.8 |
| 5 | NVFP4 dot product hardware exact accumulation deterministic batch invariant | arxiv 2509.25149 (NVFP4 pretraining); 2602.11287 (HiFloat4); 2609.02846 (UE5M3); github.com/sashakatne/nvfp4-dotprod-formal-dv [G] | 01 §1.5, 03, 05 |
| 6 | Kulisch accumulator FP8 matrix multiplication exact reproducible hardware 2025 | arxiv 2303.17951 (FP8 vs INT8); 2512.07004 (Khattak & Mikaitis); 2508.00441 and 2603.10634 (Ozaki); researchgate 272787384 (reproducible GPU matmul) [S] | 01 §1.5, 05 |
| 7 | training-inference mismatch reinforcement learning LLM nondeterminism GEMM reduction order 2026 | arxiv 2605.14220; 2606.29526; 2511.17826 (TBIK); 2609.25624; 2510.26788; github nanomaoli/llm_reproducibility [S] | 01 §1.4, 02 |
| 8 | MXDOTP microscaling dot product unit exact accumulation RISC-V 2025 | arxiv 2505.13159 (MXDOTP; MXFP8, E5M3 intermediate, 12 nm) [S] | 01 §1.5 |
| 9 | HiFloat4 hardware cost NVFP4 S10P2 integer accumulation block scale multiplier analysis | arxiv 2602.11287, 2604.08826, 2602.12635; github global-computing-consortium/HiFloat4; pith 2512.02010 [S] | 01 §1.5, 05 |
| 10 | tensor core exact fixed-point accumulation eliminates nondeterminism split-K "batch invariant" hardware proposal | arxiv 2609.25624; Thinking Machines blog; 2511.17826; 2606.23698; 2601.17768 (LLM-42); 2606.00279; 2609.11356 [S] | 01 §1.4, 05 |
| 11 | algorithm-based fault tolerance exact checksum low precision GEMM FP8 FP4 SDC threshold | arxiv 2502.12340; 2609.19758 (FP-Sketch); 2609.19743; 2006.04984 [S] | 01 §1.6 |
| 12 | hardware model checking competition HWMCC 2025 results unsolved benchmarks rIC3 | hwmcc.github.io/2025 (read via raw.githubusercontent.com [G]); arxiv 2502.13605 (rIC3), 2602.23389, 2604.03232, 2604.21688; Froleyks et al. CAV'25 [S] | 01 §1.2 |
| 13 | reset domain crossing verification research paper 2025 | Siemens Verification Horizons (2024); DVCon India 2023 [S] | 01 §1.8 |
| 14 | open challenges physical design survey 2026 routability timing closure OpenROAD | arxiv 2607.04758 (AgenticPD), 2607.16632 (CLOSER-Bench), 2408.07886 [S] | 01 §1.3 |
| 15 | OpenROAD flow scripts LEC step kepler-formal equivalence checking resizer 2026 | github ORFS PRs #4224, #4329, #4538; keplertech/kepler-formal [S] | 01 §1.1 |
| 16 | Khattak Mikaitis accurate models NVIDIA tensor cores Blackwell block scaled accumulation | arxiv 2512.07004 (TACO); 2609.14845 (AMD matrix cores) [S] | 01 §1.4, 05 |
| 17 | UE5M3 scale format Graphcore FP4 block scaling | arxiv 2609.02846 (ICML'26); 2601.19026; 2608.25188 [S] | 01 §1.5 |
| 18 | OpenRCX parasitic extraction order dependence determinism bug metamorphic | github vyges-tools/extract; OpenROAD rcx docs [S] | 01 §1.7 |
| 19 | equivalence checking XOR intensive circuits CRC parity SAT hardness Gaussian elimination | arxiv 2607.07164 (miter-aware LUT mapping); Springer "When SAT meets Gaussian elimination"; AAAI parity hardness; CryptoMiniSat notes [S] | 01 §1.1, 03, 05 |
| 20 | FPGA toolchain end-to-end verification bitstream to netlist equivalence | Yosys+nextpnr (FCCM'19); arxiv 2411.11060; 2604.16571 (EquivFusion) [S] | 01 §1.8 |
| 21 | metamorphic testing placement routing static timing analysis EDA tools | metamorphic testing of variability-analysis tools (19 bugs in 7 of 15 tools); no EDA sign-off application found [S] | 01 §1.7 |
| 22 | glitch power reduction multiplier accelerator 2025 2026 | semiengineering "Glitch power issues grow"; Shum & Anderson (FPGA glitch); arxiv 2609.05960 [S] | 01 §1.7 |
| 23 | functional safety ISO 26262 AI accelerator lockstep ABFT NPU | arxiv 2606.25296; 2604.10494; SCISSORS (TCAD'25) [S] | 01 §1.8 |
| 24 | "exact accumulation" block-scaled FP4 tensor core area cost vs FP32 accumulator | arxiv 2609.09095; 2603.28765; 2605.31035 (MixFP4); 2607.13898; 2303.17951 [S] | 01 §1.5 |
| 25 | deterministic tensor core hardware order-independent accumulation proposal 2026 | arxiv 2603.20421 (Hawkeye); 2609.11356; 2511.17826; 2606.00279; 2606.23698; 2609.25624 [S] | 05 |
| 26 | "FP8 is All You Need" Integer-Epilogue Wall minimal hardware | arxiv 2606.23698, 2606.06510 [S] | 01 §1.5, 05 |

**GitHub pages read [G]:**
- `sashakatne/nvfp4-dotprod-formal-dv` (README);
- `Gy-Hu/HW-Formal-Paper` (no 2025/26 entries);
- `hwmcc/hwmcc.github.io/2025/index.md` (raw).

**Archive documents used as the exclusion set:**
- `05_KILLED_CANDIDATES/RESEARCH_KILL_DATABASE.md`;
- `10_OPUS_5_5_INVESTIGATION_2026-09-23/INVESTIGATION_REPORT.md`;
- `11_TRACE_YOSYS_FRONTIER_PROSECUTION/INVESTIGATION_REPORT.md`;
- `12_WAVE_10_EXPERIMENTAL_DISCOVERY/06_FINAL_DECISION.md`;
- `13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION/04–06`;
- `01_RESEARCH_OBJECTIVES_AND_STRATEGY/PPA_DELTA/Existing-Research-Audit.md`;
- `14_FABLE_5_1_SCIENTIFIC_DISCOVERY/22–24`.
