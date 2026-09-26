# 04 — Experimental investigation

This document covers C1, LLM-evolved technology-mapping operators (MappingEvolve), in §1–6, and C6, OpenROAD search-based resynthesis, in §7.

Evidence labels:
- **OBSERVED:** we ran it; the files are cited.
- **PAPER:** stated by the authors.
- **INFERRED:** our reasoning.
- **UNVERIFIED:** not checked at the primary source.

Everything third-party ran inside `openroad/orfs:latest` with `--network none`. No LLM API was called. The study evaluates only the released, already-evolved operator code.

## 1. Object, claim, and why it was chosen

**Method.** MappingEvolve (arXiv 2604.26591; Flians/MappingEvolve @ `308f5cc`, MIT):
- It evolves three mockturtle `map` operators with an LLM: `match_phase` (delay / area-flow selection), `match_phase_exact` (exact-area selection) and `match_drop_phase` (phase unification).
- **Fitness:** the sum over the 11 ISCAS85 circuits of relative area and delay deltas, against hard-coded baselines produced by the initial operators, combined with α = 0.5. Delay is the load-independent genlib pin delay (ASAP7 genlib, 47 gates).
- **Equivalence:** ABC `cec -n` of the mapped k-LUT network (`write_bench`) against the original AIG.

**Claim (PAPER):**
- On EPFL, "10.04% area reduction versus ABC and 7.93% versus mockturtle", with a stated 4.46–6.50% delay trade-off. From the paper's own table averages, these are the delay increases *over mockturtle*: GPT-5 1.0369/0.9926 = +4.46%, DeepSeek 1.0571/0.9926 = +6.50%. Likewise "7.93% vs mockturtle" is (0.9771 − 0.8996)/0.9771.
- 0 equivalence failures.
- The headline mapper is GPT-5 iteration 29; its ISCAS85 S_overall is 0.298.
- There is no physical-design evaluation.

**Why it is worth testing (INFERRED).** Its evaluation leaves four doors open:
1. A scalarized area+delay fitness can reward moves along the area–delay trade-off rather than genuine improvements.
2. The baselines are mockturtle `map` and ABC `&nf` with default settings; mockturtle's newer `emap`, in the same repository, is absent.
3. Fitness uses only 11 small ISCAS85 circuits.
4. Equivalence is checked on the k-LUT abstraction, not the cell netlist.

## 2. Reproduction of the documented successful case (R1, R2): OBSERVED

**Build.** `experiments/scripts/c1_build.sh` builds 4 operator variants × {unmodified `main.cpp`, study driver} plus an `emap` driver in one CMake project (gcc 11.4.0, cmake 3.31.9, Release, `-O3`). Source and binary MD5s are in `experiments/outputs/c1/bin/MANIFEST.txt`.

**Variants** (the shipped `best_iteration` of each proactive run):

| variant | operators evolved | run dir |
|---|---|---|
| `initial` | none (repo `mapping/*.cpp`) | n/a |
| `gpt5_it29` | all three | `proactive_evolve_openevolve_gpt-5-2025-08-07_20251116_134740/iter_29` |
| `deepseek_it24` | `match_phase` only | `proactive_evolve_openevolve_deepseek-v3-241226_20251116_014457/iter_24` |
| `qwen_it20` | `match_phase`, `match_phase_exact` | `proactive_evolve_openevolve_qwen3-max_20251116_093335/iter_20` |

The full generated tables are in `experiments/results/c1_r1r2_tables.md` (`r_tables.py`).

**R1: ISCAS85 fitness.** Unmodified `main.cpp` default mode, two repetitions.
- All four variants reproduce the shipped `reward.json` raw values **exactly**:
  - gpt5_it29: area 1.097560, delay −0.500723;
  - deepseek_it24: 1.916248, −1.466161;
  - qwen_it20: 1.187989, −0.818704;
  - initial: 0 / 0, which confirms the hard-coded baselines are the initial mapper.
- nec = 0 throughout.
- Source: `experiments/results/c1_r1_iscas_orig.jsonl`.

**R2: EPFL, the paper's Table 2 setting.** Unmodified `main.cpp` single-file mode on all 20 EPFL circuits × 4 variants.
- The **mockturtle column matches 20/20** and the **GPT-5 column matches 20/20**, area and delay to two decimals. These are the paper's digits as transcribed by the fetch summarizer; they are stored in `experiments/inputs/c1/paper_table2_transcribed.csv`.
- MappingEvolve's own `cec -n` passes on all 80 runs.
- The paper's **DeepSeek column matches 0/20** against the shipped DeepSeek `best_iteration` 24. Some areas are close (voter 705.43 vs 705.63), but the delays differ (voter 948.16 vs 843.44). A follow-up scan built **every distinct operator state** of the released DeepSeek run (5 states across iterations 1–30; iterations 1–4 are byte-identical to the initial operators) and ran each through the same pipeline. It also checked the released direct-OpenEvolve DeepSeek runs. None reproduces the column:
  - the best is the initial mapper itself, at 3/20, on circuits where the column equals mockturtle's;
  - the paper's adder value (76.94 / 2583.24) is produced by no released state.

  Source: `experiments/results/c1_deepseek_provenance.txt`. The column's source is **UNRESOLVED**, possibly an unreleased run. It does not touch the headline (GPT-5) claim.
- From our reproduced GPT-5 numbers and the paper's ABC column, the mean area ratio is 0.8996 (→ "10.04%") and the mean delay ratio is 1.0369. So the headline "10.04% vs ABC" is the GPT-5 it29 mapper.
- Source: `experiments/results/c1_r2_epfl_orig_*.jsonl`.

## 3. Validation apparatus (OBSERVED)

### Identical inputs

`p0_preprocess.sh` runs MappingEvolve's exact compress2 command string once per circuit: 58 circuits (EPFL 20, ISCAS 11, IWLS05 27). Every mapper starts from the same bytes. MD5s and AIG stats are in `experiments/results/c1_p0_preprocess.csv`. Our driver, fed these AIGs, reproduces R2's values exactly (adder 92.42 / 2574.36, for example), so the harness does not perturb the object under test.

### Independent evaluator (`experiments/scripts/c1/c1_eval.py`)

It shares no code with mockturtle or ABC. It contains:
- its own genlib expression parser and structural-Verilog parser, which handles both mockturtle and ABC netlists;
- its own load-independent STA (pin delay = max(rise, fall), matching mockturtle's model);
- its own 4096-pattern bit-parallel simulation of the **cell netlist** against the **original, pre-compress2 AIG**;
- its own BLIF translation, with irredundant-SOP covers asserted equal to each cell's truth table, for ABC `cec`.

Checks on the evaluator:
- **Recomputation matches the mapper.** On c17, ctrl and adder the recomputed area and delay equal the mapper's report. On larger circuits, mockturtle's self-reported `st.area` differs from the netlist's actual cell area by −0.04% to +0.15%. Examples: mem_ctrl 2716.20 reported vs 2715.20 in the netlist; vga_lcd 7351.58 vs 7362.92. A plain regex count of the netlist agrees with the evaluator. **All comparisons use the netlist area.**
- **Negative control (T1).** In `ctrl` and `i2c`, one NAND2 was changed into a NOR2 (`t1_negative_control.sh`, log `experiments/logs/c1/t1_negative_control.log`):
  - the evaluator reports `SIM_MISMATCH` with a concrete counterexample, e.g. ctrl PO y1 on input 0100010;
  - ABC reports `NOT EQUIVALENT`;
  - the unmutated netlists pass both checks.

### CEC engine

ABC `cec -n -T 900 -C 100000` (FRAIG + SAT), matching I/O by order. The parse fails closed: only the literal "Networks are equivalent" counts as PASS.
- `&cec` was the first choice but was 10–20× slower on log2 (`t3_cec_speed.sh`).
- The BLIF covers were changed from minterms to ISOP mid-run for the same reason.
- Both changes are logged in the pre-registration's deviation log.
- **Two-stage mode.** It is used for hyp and ISCAS because ABC did not enforce `-T` on hyp. It checks original ≡ compress2 AIG once and compress2 AIG ≡ netlist per config. It is sound by transitivity (`t4_twostage_cec.sh`: 26 s + 36 s on hyp, against 1,310 s direct).

### ABC delay knob

In this yosys-abc build, `&nf -D` has no effect (`t2_nf_units.sh`: identical area at every -D). `-R` (percentage relaxation) does work, so ABC iso-delay points use `-p -R ⌊100·(D_e/D_nfp − 1)⌋`. This never gives ABC more slack than the evolved mapper had.

## 4. Decisive experiment D1: pre-registered design

The full text is in `experiments/results/c1_PREREGISTRATION.md`, written before any D1 data, with a timestamped deviation log.

- **A (hypothesis).** The evolved operators are better mappers: at equal delay they produce less area than the baselines.
- **B (baselines, all at D_e).**
  - `initial` `map` with `required_time = D_e`: the in-framework control, where only the operator code differs;
  - `emap` with `required_time = D_e`;
  - ABC `&nf -p` relaxed to ≤ D_e.
  - Sweeps are also recorded to draw fronts: `initial` relax 2–50% and skip-delay; emap relax 5/10/20% and area mode; ABC `-R` 2–30.
- **C (variable).** Operator code vs the baselines' required-time knob.
- **D (observable).** Independent netlist area and delay; per-circuit ratio A_e / A_baseline@D_e; geomeans per suite.
- **E (independent validation).** Every netlist gets STA recomputation, simulation against the original AIG, and CEC.
- **F (kill).** For every evolved variant, geomean(A_e / best baseline@D_e) ≥ 0.99 on EPFL-20.
- **G (advance).** Some variant reaches ≤ 0.97 on EPFL-20 with ≥ 14/20 wins, and ≤ 0.98 on the held-out IWLS05-22, with all netlists equivalent.
- **Suites.** EPFL-20, the paper's evaluation set; IWLS05-22, held out by both the paper and the evolution; ISCAS85-11, the training set, reported but never used for a verdict.

## 5. D1 results (OBSERVED)

**Completeness.** 53 circuits × 35 configurations = **1,855 netlists**, with no duplicate and no failed record in the final set.
- 6 records hit an evaluator bug. They were purged to `c1_d1_purged.jsonl` and rerun.
- CEC ran directly on 1,437 netlists and in two-stage mode on 418. All 12 stage-A checks (original ≡ compress2 AIG) PASS.
- **Every one of the 1,855 netlists is `SIM_AGREE` and CEC `PASS`.**

**Sources:**
- per-record data: `experiments/results/c1_d1/*.jsonl` and the flattened `c1_d1_all.csv`;
- analysis: `c1_d1_isodelay.csv`, `c1_d1_summary.json` and `c1_d1_analysis_stdout.txt` (`d1_analyze.py`);
- tables: `c1_d1_tables.md` (`d1_tables.py`).

### 5.1 Pre-registered comparison: A_evolved / A_baseline at the evolved mapper's own delay D_e

The value is the geomean; the parenthesis gives wins, i.e. circuits with ratio < 1.

| suite | variant | vs initial@D_e | vs emap@D_e | vs ABC `&nf -p` @≤D_e | **vs best baseline** | vs front (post hoc) |
|---|---|---|---|---|---|---|
| EPFL-20 | gpt5_it29 | 0.9632 (16/20) | 1.0238 (7/20) | 0.9957 (10/19) | **1.0496 (5/20)** | 1.0562 (4/20) |
| EPFL-20 | deepseek_it24 | 0.9182 (16/20) | 1.0292 (5/20) | 0.9475 (13/20) | **1.0435 (3/20)** | 1.0528 (2/20) |
| EPFL-20 | qwen_it20 | 0.9711 (15/20) | 1.0517 (3/20) | 0.9939 (9/20) | **1.0748 (1/20)** | 1.0753 (1/20) |
| IWLS05-22 | gpt5_it29 | 0.9604 (20/22) | 1.0624 (2/21) | 1.0282 (2/15) | **1.0732 (3/22)** | 1.0763 (3/22) |
| IWLS05-22 | deepseek_it24 | 0.9512 (17/22) | 1.0531 (6/22) | 1.0341 (3/17) | **1.0758 (3/22)** | 1.0815 (1/22) |
| IWLS05-22 | qwen_it20 | 0.9825 (18/22) | 1.0751 (2/22) | 1.0622 (1/18) | **1.1076 (1/22)** | 1.1155 (1/22) |
| ISCAS85-11 (training) | gpt5_it29 | 0.9523 (8/11) | 0.9444 (6/11) | 0.9926 (5/10) | **1.0223 (4/11)** | 1.0249 (4/11) |
| ISCAS85-11 (training) | deepseek_it24 | 0.9008 (10/11) | 0.9641 (5/11) | 0.9591 (6/11) | **1.0162 (5/11)** | 1.0267 (4/11) |
| ISCAS85-11 (training) | qwen_it20 | 0.9557 (9/11) | 0.9742 (5/11) | 0.9612 (5/10) | **1.0253 (3/11)** | 1.0310 (3/11) |

The "best baseline" was emap on 14–16 of 20 EPFL circuits and 16–17 of 22 IWLS circuits. ABC `&nf -p` took the rest, except one IWLS case where the initial mapper was best (GPT-5 on vga_lcd, where only the initial mapper met D_e).

Baseline points whose best achievable delay was already slower than D_e were excluded. This is conservative in the evolved mapper's favour. For GPT-5: 1 exclusion on EPFL (ABC) and 8 on IWLS (7 ABC, 1 emap).

### 5.2 Where the headline gain comes from

The geomean ratio splits exactly: total = relaxation × operator.

| suite | variant | vs mockturtle `map`: total = relax × oper | vs ABC `&nf`: total = relax × oper |
|---|---|---|---|
| EPFL-20 | gpt5_it29 | 0.9186 = 0.9537 × 0.9632 | 0.9496 = 0.9537 × **0.9957** |
| EPFL-20 | deepseek_it24 | 0.8245 = 0.8980 × 0.9182 | 0.8490 = 0.8961 × 0.9475 |
| EPFL-20 | qwen_it20 | 0.9039 = 0.9309 × 0.9711 | 0.9308 = 0.9364 × 0.9939 |
| IWLS05-22 | gpt5_it29 | 0.9458 = 0.9848 × 0.9604 | 0.9808 = 0.9539 × 1.0282 |

Here "relaxation" means the baseline's own area when merely allowed the evolved mapper's delay.

- **Against ABC**, the headline mapper's entire area gain on EPFL is relaxation (operator factor 0.9957).
- **Against mockturtle `map`**, a little over half is relaxation, and a real operator gain of ≈3.7% remains.
  - That gain generalizes to the held-out IWLS05 suite (0.9604, 20/22 wins).
  - It is smaller than the gap between `map` and emap.

### 5.3 The paper's ABC baseline

On identical compress2 AIGs, our yosys-abc `&nf` (default) reproduces the paper's ABC *delays* exactly on 17/20 EPFL circuits (div, hyp and sqrt differ), but gives **5.2% less area** (mean our/paper = 0.9479).

- Against current `&nf` defaults, GPT-5's paper-style mean area ratio is 0.9487 (5.1% reduction), not 0.8996 (10.04%).
- The ABC version and options behind the paper's column are UNVERIFIED. The same-delay, larger-area pattern suggests less area recovery (INFERRED).

### 5.4 Pre-registered verdict for D1

- **F (kill) is met** for all three variants: the geomean vs the best baseline at iso-delay on EPFL-20 is 1.0496, 1.0435 and 1.0748, all ≥ 0.99. It is also ≥ 1.07 on the held-out IWLS05-22.
- **G (advance) is not met.**
- **Correctness is confirmed.** The paper's 0-failure equivalence claim holds on 159/159 evolved netlists (EPFL + IWLS + ISCAS), checked by independent simulation plus CEC.

## 6. D2: cause isolation (OBSERVED; pre-registered in `c1_PREREGISTRATION.md`)

Two ablations of GPT-5 it29 were generated by asserted substitution (`d2_make_ablations.py`; MD5s in `MANIFEST_ablation.txt`):
- `ab1` = GPT-5 minus its delay-round rule;
- `ab2` = the initial operators plus *only* GPT-5's delay-round rule.

Each was run on EPFL-20 and IWLS05-22 by default and against `initial`@own-delay. All 168 records are SIM_AGREE + CEC PASS. Sources: `experiments/results/c1_d2/*.jsonl`, `c1_d2_summary.json` (`d2_analyze.py`).

| geomean vs initial `map` | GPT-5 it29 | ab1 (no delay rule) | ab2 (delay rule only) |
|---|---|---|---|
| EPFL-20 delay | 1.0441 | **1.0000** | **1.0441** |
| EPFL-20 area | 0.9186 | 1.0010 | 0.9188 |
| EPFL-20 area vs initial@own delay | 0.9632 | 1.0010 | 0.9638 |
| IWLS05-22 delay | 1.0392 | 1.0000 | 1.0390 |
| IWLS05-22 area | 0.9458 | 0.9975 | 0.9446 |
| IWLS05-22 area vs initial@own delay | 0.9604 | 0.9975 | 0.9595 |

**Pre-registered readout.**
- P1 is TRUE: without the rule there is no relaxation.
- P2 is FALSE: the rule is not a pure relaxation, because at iso-delay ab2 still gains 3.6% over the relaxed initial mapper.
- P3 is FALSE: the area-round rules carry no gain.
- By the pre-registered rule the cause is therefore **ENTANGLED**.

**What the data show, more sharply than the prediction.** The single delay-round acceptance rule is **necessary and sufficient** for GPT-5's entire effect:
- ab2 reproduces GPT-5 within 0.1% on delay and within 0.3% on area, in both suites;
- ab1 falls back to the initial mapper within 0.25%.

GPT-5's two area-round edits and its exact-area edit are inert on these suites.

The rule's effect has two parts:
1. **Relaxation:** +4.4% delay on EPFL.
2. **An additional ≈3.6% area reduction at iso-delay** that the `required_time` knob does not reproduce. INFERRED: a more area-aware delay-round cover changes the starting point and required-time profile from which area recovery proceeds. Cut-based area recovery is path-dependent.

Part 2 is precisely the kind of effect emap's area-oriented match alternatives target, and emap still dominates at iso-delay (§5.1).

**Mechanism reading from the code diff (D2 tests it):** GPT-5's operators make the *delay round* deliberately non-delay-optimal:
- a faster match is accepted only if its area flow is within 0.25·inv_area, or if it gains ≥ 0.5·inv_delay;
- one-phase-plus-inverter is used only if area flow does not increase.

That raises the achieved delay, and the area-recovery rounds then spend the extra slack. The area rounds also get tolerance-gated rules: accept a faster match within 0.5·inv_area in area flow, and reject exact-area gains below 0.5·inv_area if they worsen arrival.

## 7. C6: OpenROAD search-based post-placement resynthesis (`resynth_annealing`)

Pre-registration: `experiments/results/c6_PREREGISTRATION.md`, including Amendment 1.

**Object and claim.** OpenROAD mainline `rmp`, Antmicro 2025:
- `resynth_annealing`: simulated annealing over ABC operation sequences applied to the logic below a slack threshold, with worst slack as the objective.
- `resynth_genetic`: the GA variant.
- Upstream C++ defaults (OpenROAD master `Restructure.h`; the image's own defaults are UNVERIFIED): 100 annealing iterations from a random 10-operation initial script; GA population 4 × 10 iterations.
- The published example (PAPER, Antmicro blog 2025-11): AES/ASAP7 WNS −30.92 → +20.59 ps, run with no parameters on an *unplaced* netlist from an OpenROAD test. No baseline, area, runtime or equivalence check was reported.

**Setup (OBSERVED).**
- The input is ORFS asap7/aes (`base`, `LEC_CHECK=0`) run to placement.
- Its `3_place.odb` has WNS −29.38 ps and TNS −568.9 ps under the placement parasitics estimate. That matches ORFS's own `detailedplace__timing__setup__ws`, and it is close to the blog's "before".
- The same ORFS run continued to finish: CTS WS −3.91 ps, GRT −10.55 ps, finish −10.80 ps, with all 27 metric rules passing. This is the standard flow's result without any resynthesis.
- Each treatment is applied by `c6_treat.tcl` through ORFS `make run`, on a private copy of the stage results. It writes `metrics.json`, `before.v`, `after.v` and `after.odb` to `experiments/outputs/c6/asap7/aes/<treatment>/`.

**Equivalence checker.** `c6_equiv.sh`: Yosys with ASAP7 liberty functional models, `equiv_make`/`equiv_struct`/`equiv_simple`/`equiv_induct`, registers matched by name. It fails closed. Self-test:
- identical netlists: 10,286/10,286 `$equiv` proven;
- a mutated copy (one NAND2 → NOR2): 1 unproven, localized to the D input of register `u9891`.

(Results table and verdict below are generated by `experiments/scripts/c6/c6_analyze.py` → `experiments/results/c6_results.csv`, `c6_summary.json`.)

**Equivalence checker actually used: v3.** The pre-registration's Amendments 2 and 4 cover the switch.
- Yosys lowers each netlist to BLIF, with flops as `.latch` named by their Q net. ABC `cec` then runs with latch correspondence by name (530 latches on each side).
- Controls: identical netlists PASS; the mutated netlist is NEQ, with a concrete counterexample on the cone of register `u9891`.
- **All 19 treated netlists PASS** (`experiments/logs/c1/c6_equiv_all_abc_final.out`).
- Checker v1 (Yosys `equiv_*`) gave a false NOT_PROVEN on the `repair_timing` netlist. It matched `<instance>.<pin>` wires, which pin swapping legitimately changes. v2 fixed that but was too slow. Both are archived.

### 7.1 Results (OBSERVED; `experiments/results/c6_results.csv`, `c6_summary.json`, `c6_analysis_stdout.txt`)

**Placed arm: ORFS asap7/aes `3_place.odb`, start WNS −29.38 ps, TNS −568.9 ps.**

| treatment | seeds | final WNS (ps) | ΔWNS vs start | area ratio | runtime | equivalent |
|---|---|---|---|---|---|---|
| none | n/a | −29.38 | 0 | n/a | n/a | PASS |
| **`repair_timing -setup`** | n/a | **−5.53** | **+23.85** | 1.0025 | 4.7 s | PASS |
| `resynth` (fixed script) | n/a | −193.49 | −164.11 | 0.934 | 0.9 s | PASS |
| `resynth_annealing` | 1–5 | −116.07, −88.79, −96.59, −113.73, −141.15 (median −113.73) | −59 to −112 | 0.897–1.081 | 914–1,863 s | PASS ×5 |
| `resynth_genetic` | 1–3 | −117.12, −123.52, −123.54 | −88 to −94 | 0.894–1.092 | 312–367 s | PASS ×3 |
| `resynth_annealing` → `estimate_parasitics` → `repair_timing` | 1–3 | −23.54, −15.64, −15.85 (median −15.85) | +6 to +14 | 0.908–1.043 | 711–1,459 s | PASS ×3 |

**Unplaced arm (Amendment 1): ORFS asap7/aes `1_synth.v`, ideal wires, start WNS −59.31 ps.**

| treatment | seeds | final WNS (ps) | ΔWNS vs start | area ratio | equivalent |
|---|---|---|---|---|---|
| none | n/a | −59.31 | 0 | 1.000 | PASS |
| `repair_timing -setup` | n/a | −43.30 | +16.02 | 1.024 | PASS |
| `resynth_annealing` | 1–3 | −62.95, −79.30, −80.45 | −3.6, −20.0, −21.1 | 0.904–1.042 | PASS ×3 |

Runtimes were measured on an oversubscribed 8-core host (up to about 10 concurrent single-CPU containers). They are indicative only.

### 7.2 Pre-registered verdict

- **F1 (kill): TRUE.** Median annealing WNS (−113.73 ps) minus `repair_timing` WNS (−5.53 ps) is −108.2 ps, far from the required +5 ps.
- **F2: FALSE.** The sign is consistent: every seed makes timing worse.
- **F3: FALSE.**
- **F4: FALSE.** All treated netlists are equivalent.
- **G: FALSE.** The additive arm is also negative: median(annealing → repair) − `repair_timing` = −10.33 ps.
- **Verdict: KILL.**

**Reproduction of the published example.** It is **not reproduced** in its own setting on our netlist: 3/3 unplaced seeds end *worse* than the start, against the blog's +51.5 ps. Caveat: the blog used the OpenROAD test netlist `aes_asap7.v`, which was not downloaded. Our unplaced start (−59.31 ps) differs from its −30.92 ps, so this is an analogous-setting reproduction, not an identical one.

**Mechanism (OBSERVED in the tool's own log; the tool-reported start and end slack equal our measurements to the femtosecond):**
- Each search starts from a random 10-operation ABC script whose slack is far worse: −147 to −196 ps on the placed design.
- It improves for 100 iterations (annealing) or 10 generations (GA).
- It then applies the best-found script *even when that script is worse than the untouched netlist*. No do-no-harm comparison is made.
- The tool is deterministic per seed: seed 2's annealing reproduced −88.79 ps exactly inside a separate `annealing_repair` run.

**Tool-interaction findings (engineering):**
- `repair_timing` directly after `resynth_annealing` aborts with `[ERROR EST-0104] inconsistent parasitics state` unless parasitics are re-estimated.
- With re-estimation it emits about 1,000 `RSZ-0075 makeBufferedNet failed for driver cut_…` warnings on the rmp-created cells, and ends with `RSZ-0062 Unable to repair all setup violations`.

**Observation, not a claim (one design).** Annealing followed by repair produced smaller netlists on 2/3 seeds (area 0.908 and 0.929) at a 10–18 ps WNS penalty against repair alone. No area-oriented baseline was run, so no area conclusion is drawn.
