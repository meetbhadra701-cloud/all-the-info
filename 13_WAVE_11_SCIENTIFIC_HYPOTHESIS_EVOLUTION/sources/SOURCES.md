# Wave 11 sources

This file was compiled from the session transcript's own tool-call record, not from memory.

**How to read the status column.**
- **PAPER:** text obtained from the document itself.
- **SEARCH SUMMARY:** only a search-engine snippet or summary was seen. Everything that rests on one of these is marked UNVERIFIED in `03`/`05`.
- **FAILED:** the retrieval did not return usable content.

**What is and is not stored here.** Full texts of third-party papers are not copied into this folder. For each PDF that was retrieved, only its URL, retrieval time (UTC), size and md5 are recorded. The session cache paths are given so that a local copy can be matched against the published file. The cache may be cleaned later, and the URLs are the durable reference.

## Documents retrieved in this wave

| # | Document (as cited in 03/05) | URL | Retrieved (UTC) | Status | Local evidence |
|---|---|---|---|---|---|
| S1 | Schmitt, Mishchenko, Brayton, *SAT-Based Area Recovery in Structural Technology Mapping*, ASP-DAC 2018 (`&satlut`) | https://people.eecs.berkeley.edu/~alanmi/publications/2018/aspdac18_satlut.pdf | 2026-09-25 22:07:09 | **PAPER.** The WebFetch summarizer could not read the PDF. The saved binary was text-extracted locally with `experiments/scripts/pdftext.py` (stdlib zlib). | PDF md5 `06647cb9a9e38a566639036ad6941c12`, 383,732 B (session cache `tool-results/webfetch-1790374029747-9mblly.pdf`). Extracted text md5 `b89e6304072e6381bc774fd35f2bc463` (scratchpad `satlut.txt`). |
| S2 | Costamagna, Tempia Calvino, Mishchenko, De Micheli, *Area-Oriented Optimization After Standard-Cell Mapping*, ASP-DAC 2025 | https://si2.epfl.ch/demichel/publications/archive/2025/ASPDAC25_Andrea.pdf (the ACM DL page https://dl.acm.org/doi/10.1145/3658617.3697722 returned HTTP 403) | 2026-09-25 22:12:59 | **PAPER** (local extraction as for S1). The extraction lost one decimal point: "5 47%". | PDF md5 `6c86dd052106656eed75407fb7e6943e`, 987,099 B (`tool-results/webfetch-1790374379934-nteh96.pdf`). Text md5 `d848b7064d81454b080301e6669d08a5` (`aspdac25.txt`). |
| S3 | Mishchenko, Brayton, Besson, Govindarajan, Arts, van Besouw, *Versatile SAT-based remapping for standard cells*, IWLS 2016 (`mfs3`) | https://people.eecs.berkeley.edu/~alanmi/publications/2016/iwls16_mfs3.pdf; talk slides: https://slidetodoc.com/versatile-satbased-remapping-for-standard-cells-alan-mishchenko/ | 2026-09-25 22:09:08 (PDF), 22:09:21 (slides) | The PDF uses a custom font encoding, and the local extraction is unreadable (`mfs3.txt`, md5 `48a6ee4323142aab86ef75e35eeb042f`). Claims come from the **talk slides** and are UNVERIFIED in detail. | PDF md5 `a561f85fbb1a47f794fbc26260578683`, 202,225 B (`tool-results/webfetch-1790374148025-8iyduo.pdf`). |
| S4 | Mishchenko publications index (title and venue confirmation for S1 and S3) | https://people.eecs.berkeley.edu/~alanmi/publications/ | 2026-09-25 22:08:57 | Index page read. | none |
| S5 | Ghiasi, Bozorgzadeh et al., *A Unified Theory of Timing Budget Management*, ICCAD 2004 | https://www.ece.ucdavis.edu/~soheil/publications/conference/ICCAD04.pdf | 2026-09-25 17:33:30 | The PDF was saved but not text-extracted. Claims are **SEARCH SUMMARY** (ResearchGate entry for the TCAD version). | PDF md5 `6241d3e2466c077b05400f861865eec0`, 170,840 B (`tool-results/webfetch-1790357632222-3k0r1p.pdf`). |
| S6 | Chaudhary, Pedram, *Computing the Area versus Delay Trade-off Curves in Technology Mapping* (DAC 1992; TCAD 1995) | https://mpedram.com/Papers/admap.pdf | 2026-09-25 17:33:10 | **FAILED** (TLS error: "unable to get local issuer certificate"). Claims are **SEARCH SUMMARY**. | none |
| S7 | Liu, Shelar, Hu, *Delay-optimal simultaneous technology mapping and placement with applications to timing optimization* (ICCAD 2008) / TCAD 2011 | https://ieeexplore.ieee.org/document/4681558/ | 2026-09-25 17:33:12 | **FAILED** (the IEEE Xplore page had no readable content). The title is confirmed by a search result. Claims are **SEARCH SUMMARY**, and the author list is UNVERIFIED. | none |

## Items known only from search results (no document retrieved)

Each of these is labelled as a search summary or UNVERIFIED where it is used.

- Kukimoto et al., *Delay-Optimal Technology Mapping by DAG Covering* (DAC 1998). Search result title (ResearchGate).
- Josipović et al., *Buffer Placement and Sizing for High-Performance Dataflow Circuits* (FPGA 2020 / ACM TRETS 2021). Search result, EPFL LAP PDF link seen but not fetched.
- R-HLS, arXiv 2408.08712. Search summary.
- Beerel et al., *Slack Matching Asynchronous Designs* (ASYNC 2006); *Performance Estimation and Slack Matching …* (ICCAD 2008). Search summaries.
- *Resource and Phase Awareness for Dynamically Scheduled HLS* (HEART 2025). Wave 10 search summary.
- Priority cuts: Mishchenko et al. (ICCAD 2007); PRAETOR (Cong et al.); SLAP; *Revisiting Priority Cuts* (2026); *FPGA technology mapping with encoded libraries and staged priority cuts* (ACM TRETS). Titles only.
- *Revisit Choice Network for Synthesis and Technology Mapping*, arXiv 2508.14068. Search summary.
- Lagrangian-relaxation gate sizing: *Gate sizing by Lagrangian relaxation revisited*; *Fast and efficient LR-based discrete gate sizing*; *Fast LR-based multithreaded gate sizing*. Titles only.
- *Delay driven AIG restructuring using slack budget management*; *Delay budgeting for a timing-closure-driven design method* (ICCAD 2000). Titles only.

## Web searches issued in this wave (UTC, verbatim queries)

| Time | Query |
|---|---|
| 17:32:43 | Lagrangian relaxation technology mapping area minimization under delay constraint cut-based |
| 17:32:43 | delay-constrained area-optimal technology mapping integer linear programming exact DAG covering standard cell |
| 17:32:43 | slack budgeting technology mapping area recovery delay budget LUT mapping |
| 17:33:10 | "budget management" delay budgeting mapping smaller cells area power reduction Bozorgzadeh Ghiasi Sarrafzadeh |
| 17:33:30 | "Delay-optimal simultaneous technology mapping and placement with applications to timing optimization" Lagrangian relaxation |
| 17:34:40 | Chaudhary Pedram "area versus delay trade-off curves" technology mapping DAG extension near optimal algorithm minimizing area under delay constraints |
| 17:34:40 | SAT-based exact technology mapping standard cell window resynthesis area recovery mapped netlist optimal covering |
| 17:34:40 | ABC &nf SAT-based area-oriented mapping experimental Mishchenko 2024 2025 technology mapping exact area |
| 22:08:57 | "Versatile SAT-based remapping for standard cells" Mishchenko Brayton IWLS 2016 |
| 22:10:09 | slack matching NP-complete asynchronous pipelines buffer insertion throughput marked graph mixed integer |
| 22:10:09 | dataflow circuits buffer placement heuristic without MILP scalable dynamatic 2023 2024 2025 throughput buffering fast |
| 22:12:41 | technology mapping candidate pruning exact covering restricted choices near-optimal matches global optimization standard cell SAT ILP "area recovery" |
| 22:12:41 | Tempia Calvino Mishchenko De Micheli 2024 2025 technology mapping area recovery exact standard cells emap improvements |
| 22:12:41 | Monte Carlo tree search OR beam search technology mapping standard cell cover selection area delay 2023 2024 2025 |
| 22:13:40 | optimality gap heuristic technology mapping standard cell exact ILP small circuits area delay-constrained comparison ABC map optimal |
| 22:13:40 | "priority cuts" OR "cut ranking" pruning exact SAT LUT mapping whole circuit restricted candidates optimal area depth FPGA |

None of these searches returned a published measurement of the optimality gap of a cut-based standard-cell mapper against the exact optimum over its own cut-match space. **This is recorded as an absence of search results. It is not evidence that no such measurement exists, and no novelty is claimed from it.**

## Artifacts inherited from earlier waves

- **Mapper sources:** `12_WAVE_10_EXPERIMENTAL_DISCOVERY/third_party/MappingEvolve/`, which includes mockturtle (`map`, `emap`), the asap7 genlib and the benchmark AIGs. Their provenance is recorded in the Wave 10 `sources/` and `REPRODUCTION.md`.
- **Wave 10 evaluator:** `12_…/experiments/scripts/c1/c1_eval.py`, unmodified. Wave 11 uses a copy with a cycle guard, `experiments/scripts/c1_eval_w11.py`.
- **Solvers inside the network-off `openroad/orfs:latest` container:**
  - OR-tools 9.14 CP-SAT `/opt/or-tools/bin/sat_runner` (md5 `358d567c2bf14e88f18aebb631024127`);
  - `yosys-abc` from the same image;
  - z3 4.15.5 from the OSS CAD Suite, mounted read-only.
