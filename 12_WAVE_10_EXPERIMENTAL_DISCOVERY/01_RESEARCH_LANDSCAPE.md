# 01 — Research landscape (Wave 10, compact)

This is a compact landscape, not a survey. Its job was to find *important existing methods* whose claims could be run and checked locally. Each entry carries an evidence label:

- **OBSERVED:** we ran it.
- **PAPER:** stated by the authors, read through the abstract or HTML.
- **INFERRED:** our reasoning from the above.
- **UNVERIFIED:** from a search-engine summary, not checked against the primary source.

Screening searches ran on 2026-09-25. The queries and returned summaries are preserved in the session transcript. The URLs are listed in [sources/SOURCES.md](sources/SOURCES.md).

## Selection rule used

A territory stays in play only if all three hold:
1. There is an important method with an exact, checkable claim.
2. The strongest implementation can run locally, inside a network-off container, within this wave.
3. A plausible limitation of it is not already occupied by 2024–2026 prior art.

The previous waves' lesson (see `10_OPUS_5_5_INVESTIGATION_2026-09-23/INVESTIGATION_REPORT.md`) is that time-to-occupation is shorter than one research cycle. So occupancy was checked first and cheaply.

## Territory table

### Physical design: placement, cross-stage PPA

- **Important methods:** RePlAce/gpl (OpenROAD); DREAMPlace 4.0; differentiable timing-driven placement (DAC'22).
- **Checkable claim:** AI placers improve PPA.
- **2024–2026 occupancy:**
  - **ChiPBench** (NeurIPS'25 D&B; arXiv 2407.15026) evaluates AI placers end to end in OpenROAD. It finds that HPWL is an unreliable proxy and that *every* AI placer degraded PPA relative to Hier-RTLMP. *PAPER/UNVERIFIED*
  - **PPAPlace** (arXiv 2608.13790, ICCAD'26) adds differentiable WNS/TNS surrogates trained on post-GR labels. *PAPER*
- **Screening outcome:** KILLED at screening; occupied.

### Timing optimization: gate sizing, repair

- **Important methods:** OpenROAD `rsz repair_timing`; LR-based sizing.
- **Checkable claim:** that `repair_timing` grinds.
- **2024–2026 occupancy:**
  - OpenROAD issue **#10900** (2026-07-13) already measured effort levels (low: 316 s / −647.8 ps; high: 817 s / −602.7 ps) and proposed `-effort explore|tapeout`. *PAPER (issue text)*
  - **bazel-orfs "study" PRs** #985, #987 and #1020 ("repair_timing's information is better, its ranking is not…") already quantify this. *UNVERIFIED (titles only)*
  - **AuDoPEDA** (arXiv 2601.06268): coding agents already improve OpenROAD QoR (up to 5.9% wirelength, 10% clock period, 19.4% power). *PAPER (abstract)*
- **Screening outcome:** KILLED at screening; occupied by the maintainers themselves.

### Routing

- **Important methods:** TritonRoute/drt, FastRoute; ISPD'24/'25 GPU global-routing contests.
- **Checkable claim:** GPU/ML routing gains.
- **2024–2026 occupancy:** contest-driven and saturated. *UNVERIFIED*
- **Screening outcome:** Not pursued; no local checkable gap found in screening.

### Logic synthesis and technology mapping

- **Important methods:** ABC (`&nf`, `amap`, `map`); mockturtle (`map`, `emap`).
- **Checkable claim:** **MappingEvolve** (arXiv 2604.26591): LLM-evolved mockturtle mapping operators give "10.04% area reduction versus ABC and 7.93% versus mockturtle" on EPFL, all netlists pass ABC `cec`. *PAPER*
- **2024–2026 occupancy:**
  - Multi-Agent Self-Evolved ABC (2604.15082, abstract only; no numbers). *PAPER*
  - Physically-aware mapping: "Physically Aware Synthesis Revisited" (2408.07886), PigMap2 (2025), MapTune (2026), LevelSyn (2609.03594). *UNVERIFIED*
  - The paper itself says its evaluation is synthesis-level only (no P&R). *PAPER*
- **Screening outcome:** **SELECTED as C1.**
  - Released artifact (MIT) with per-iteration evolved code.
  - Runnable locally.
  - Its claims are exact and falsifiable.
  - Its evaluation (scalarized area+delay, load-independent genlib delay, ISCAS85-only fitness) has testable weak points.

### High-level synthesis

- **Important methods:** Dynamatic (dynamically scheduled HLS); MILP buffer placement (fpga20/fpl22).
- **Checkable claim:** buffer placement optimality and throughput.
- **2024–2026 occupancy:** resource- and phase-aware buffer placement (HEART'25: up to 40% fewer buffers). *UNVERIFIED*
- **Screening outcome:** **BLOCKED (C4):**
  - Local Dynamatic at `0cab874` (2024-03) has no Gurobi. `GUROBI_LIBRARY-NOTFOUND` (*OBSERVED*, `experiments/logs/screening/probe_dynamatic.log`).
  - The MILP buffer algorithms cannot run without it.

### RTL simulation

- **Important methods:** Verilator; RepCut (ASPLOS'23); Parendi (ASPLOS'25).
- **Checkable claim:** parallel RTL simulation scaling.
- **2024–2026 occupancy:** Parendi (thousand-way, IPU), RTeAAL Sim (2601.18140), CCSS (2507.08406). *PAPER/UNVERIFIED*
- **Screening outcome:** KILLED at screening; occupied, and it needs hardware we lack (IPU, GPU).

### Verification and security: processor fuzzing

- **Important methods:** Cascade (USENIX Sec'24); Encarsia (USENIX Sec'25).
- **Checkable claim:** fuzzer coverage and bug-finding.
- **2024–2026 occupancy:**
  - Encarsia already evaluates fuzzers by injecting 177-bug-derived faults.
  - SoK **ARCUS** (2608.23933) evaluates fuzzer efficiency and efficacy.
  - *PAPER/UNVERIFIED*
- **Screening outcome:** KILLED at screening; occupied by an SoK a month old.

### CGRA / HW-SW mapping

- **Important methods:** SAT-MapIt (DATE'23, JETC'24); CGRA-ME; Morpher.
- **Checkable claim:** exact mapping does not scale.
- **2024–2026 occupancy:** Monomorphism-based mapping (Tirelli, Otoni, Pozzi; arXiv 2512.02859) decouples time (SMT) from space (monomorphism) and reports "approximately 10^5× average compilation speedup" on 20×20 CGRAs. *PAPER*
- **Screening outcome:** KILLED at screening; the scalability gap was closed by the same group.

### Accelerator DSE and mapping

- **Important methods:** Timeloop; ZigZag; Voyager (2509.15205).
- **Checkable claim:** mapper optimality.
- **2024–2026 occupancy:** mature, crowded. *UNVERIFIED*
- **Screening outcome:** KILLED at screening; no local checkable gap.

### Advanced-node PDK usage in the open flow

- **Important method:** ORFS on **GT2N** (open 2 nm GAAFET PDK, backside power, w13/w31 × 5 Vt).
- **Checkable claim:** the open flow exploits multi-width/Vt.
- **Local observation:** gcd reproduced on gt2n with `LEC_CHECK=0`; all 27 CI metric rules pass. The flow uses ELVT/ULVT cells at +150.06 ps finish setup slack, and leakage is 5.2% of total power. *OBSERVED* (`experiments/outputs/orfs/gt2n/gcd/base/reports/.../metadata-check.log`, `6_finish.rpt`)
- **Screening outcome:** ENGINEERING ONLY (C2). Vt recovery with slack is a known flow knob (leakage recovery); the leakage share is too small to matter.

### FPGA placement and routing

- **Important methods:** nextpnr; VTR; DREAMPlaceFPGA; OpenPARF; AMF-Placer 2.0.
- **Checkable claim:** timing-driven analytical placement.
- **2024–2026 occupancy:** critical-path-aware TD placement for heterogeneous FPGAs (2512.00038). *UNVERIFIED*
- **Screening outcome:** Kept as C3, the next candidate if C1 died. It was re-screened after C1 died. It is runnable locally (OSS CAD Suite nextpnr, `probe_nextpnr.log`), but its obvious placer question is occupied by "Revisiting Gradient Direction Algorithms in Electrostatic Placers" (UNVERIFIED), and no exact open claim was found. **NOT PURSUED**; see the register.

### Added during progressive allocation, after C1 died

**In-flow logic resynthesis (OpenROAD `rmp`):**
- **Important methods:** `restructure`, `resynth`, and the SA/GA `resynth_annealing`/`resynth_genetic` (Antmicro 2025, in mainline).
- **Checkable claim:** AES/ASAP7 WNS −30.92 → +20.59 ps (blog; one example, no baseline).
- **2024–2026 occupancy:** ABC-script search for QoR (RL/bandit/SA) is crowded (UNVERIFIED).
- **Screening outcome:** C6. The commands are runnable locally (`probe_rmp.log`) and got a decisive experiment. See 04 §7.

**Technology mapping inside OpenROAD (`resynth_emap`):**
- **Important method:** mockturtle emap in `rmp` (Antmicro PR #9097).
- **Checkable claim:** 10% area on jpeg/SKY130 (blog).
- **2024–2026 occupancy:** new.
- **Screening outcome:** C5, BLOCKED. The local OpenROAD lacks the command.

## Environment facts that shaped the landscape (OBSERVED)

- **CPU:** Intel Core Ultra 7 258V, no AVX-512.
  - ORFS's `kepler-formal` LEC step dies with SIGILL ("child killed: illegal instruction") during CTS.
  - Flows therefore run with `LEC_CHECK=0` (`experiments/logs/screening/probe_cts_sigill.log`, `probe_lec.log`).
- **Isolation:** all third-party code runs in `openroad/orfs:latest` with `--network none` (gcc 11.4, cmake 3.31.9, Yosys 0.68+, yosys-abc).
- **Licensing:** no commercial tools and no Gurobi.
