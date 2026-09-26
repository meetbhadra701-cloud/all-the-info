# 06 — Final decision (Wave 10)

The classes are the prompt's: KILLED / ENGINEERING ONLY / UNRESOLVED / ADVANCE TO RESEARCH DEVELOPMENT.

A candidate may advance only with all ten required items. **No candidate advances.**

## Decisions

### C1 — LLM-evolved technology-mapping operators (MappingEvolve): **KILLED**

- **Decisive experiment.** Pre-registered D1: 53 circuits × 35 configurations = 1,855 netlists, each independently validated.
- **Kill condition F** was met for all three evolved variants: geomean area vs the best baseline at the evolved mapper's own delay is ≥ 0.99.
  - EPFL-20: 1.0496 / 1.0435 / 1.0748;
  - held-out IWLS05-22: 1.0732 / 1.0758 / 1.1076.
- **What the headline was made of:**
  - Against ABC, GPT-5's EPFL area gain is entirely delay relaxation: operator factor 0.9957.
  - About half of the "10.04%" comes from an ABC baseline weaker than current `&nf` defaults, which give 5.2% less area at identical delays on 17/20 circuits.
- **Cause (D2).** One evolved delay-round acceptance rule is necessary and sufficient for GPT-5's whole effect. Its non-relaxation part (≈3.6% at iso-delay vs `map`) is the kind of effect mockturtle's own `emap` already delivers better.
- **What held up.** Correctness: 159/159 evolved netlists are equivalent.
- **Contribution test:** fails for A–E (`03_STRONGEST_PRIOR_ART.md`).
- **Residual (engineering):** a reproducible critique package: harness, independent validator, pre-registered tables, and the DeepSeek-column provenance gap. No released DeepSeek state reproduces that column. The user may choose to send it to the authors; nothing has been sent.

### C2 — GT2N multi-width/Vt usage in the open flow: **ENGINEERING ONLY**

- gcd on gt2n passes 27/27 rules at +150.06 ps.
- ELVT and ULVT cells are used despite the slack, and leakage is 5.2% of power.
- Vt/width recovery under slack is a known flow knob, and the effect is small. One design only.

### C3 — nextpnr placement: **KILLED at screening (occupied)**

- It is runnable locally.
- The obvious research question, the optimizer choice for the electrostatic placer, is already studied. No exact open claim was found to test.

### C4 — Dynamatic MILP buffer placement: **UNRESOLVED (blocked)**

- There is no Gurobi, so the MILP algorithms cannot run.
- Unblocking would need a licensed Gurobi, which is the user's decision to obtain.

### C5 — `emap` inside OpenROAD (`resynth_emap`): **UNRESOLVED (blocked)**

- The local OpenROAD lacks the command. Testing would need a from-source OpenROAD build.

### C6 — OpenROAD search-based post-placement resynthesis (`resynth_annealing` / `resynth_genetic`): **KILLED**

- **Decisive experiment.** Pre-registered, with Amendments 1–4, on placed ORFS asap7/aes (WNS −29.38 ps), default parameters.
  - **All 8** search runs end *worse than doing nothing*:
    - annealing, 5 seeds: −88.8 to −141.2 ps, median −113.7;
    - genetic, 3 seeds: −117.1 to −123.5 ps.
  - Standard `repair_timing -setup` reaches −5.53 ps in 4.7 s.
  - The fixed-script `resynth` reaches −193.5 ps.
  - Annealing then repair (3 seeds) ends 10.3 ps worse (median) than repair alone.
  - Details: 04 §7 and `experiments/results/c6_results.csv`.
- **Kill condition F1 is met.** Median annealing WNS is far worse than `repair_timing`, not better by more than 5 ps.
- **Mechanism, observed in the tool's own log.**
  - The search starts from a random 10-operation ABC script at −147 to −196 ps and climbs back for 100 iterations.
  - It then applies the best-found script even when that script is worse than the untouched netlist.
  - The tool's own start and end slack reports equal our measurements exactly.
- **Correctness.** All 19 treated netlists are functionally equivalent (ABC `cec` with register correspondence; checker validated on identical and mutated controls). The commands are *correct* but *harmful to timing* by default.
- **Published example.** It ran on an unplaced test netlist. It is *not reproduced* in an analogous unplaced setting on our AES netlist: 3/3 seeds end 3.6–21.1 ps worse than the start (−59.31 ps), against the blog's +51.5 ps.
- **Contribution test:** fails for A–E; the method class, ABC-script search, is occupied (03).
- **Residual (engineering):**
  - a do-no-harm acceptance check is missing;
  - `repair_timing` after `resynth_annealing` aborts with EST-0104 unless parasitics are re-estimated.
  - Even then it emits about 1,000 `RSZ-0075 makeBufferedNet failed for driver cut_…` warnings on the rmp-created cells and ends with RSZ-0062, "Unable to repair all setup violations".

  Both are issues you could file; nothing has been filed.

## Screening-level kills (from 02)

S-1 cross-stage placement, S-2 `repair_timing` effort, S-3 parallel RTL simulation, S-4 processor fuzzing, S-5 exact CGRA mapping scalability, S-6 accelerator-mapping DSE: all **KILLED at screening (occupied)**.

## Engineering findings recorded (not contributions)

1. **ABC.** In the ORFS image's yosys-abc, `&nf -D <x>` has no effect on the mapping (`t2_nf_units.sh`, adder).
   - `&nf -p -R <r>` works on 50/53 circuits.
   - It is completely inert, giving the same result for r = 2…30 and 37, on the three deepest: **div, hyp, sqrt** (D1 `R:nfp:*` records).
   - On those circuits the ABC iso-delay baseline got no relaxation. This is conservative in the evolved mapper's favour.
   - The same three circuits are the ones where our `&nf` delay differs from the paper's ABC column.
2. **mockturtle `map`/`emap` emit more inverters than ABC `&nf` on IWLS05** (OBSERVED, D1 default modes).
   - Geomean count ratio: 2.46× for `map` (range 0.97–9.68×) and 1.73× for `emap`.
   - Example: vga_lcd has 12,241 (`map`) and 12,605 (`emap`) inverters vs 1,264 (`&nf`).
   - Inverters are 6.6% (`map`) and 5.1% (`emap`) of cell area, vs 3.2% for ABC (arithmetic means).
   - INFERRED, not isolated experimentally: this excess is a plausible contributor to the mockturtle-family deficit vs ABC at iso-delay on this suite (GPT-5 / ABC@≤D_e = 1.028).
   - It is worth a mockturtle issue now that emap is entering OpenROAD.
3. **Mapper self-reports.** mockturtle's self-reported `st.area` can differ from the emitted netlist's cell area by −0.04% to +0.15%.
4. **ORFS.** `kepler-formal` LEC crashes with SIGILL on CPUs without AVX-512, and ORFS flows need `LEC_CHECK=0` there.

## Why no survivor, and what the evidence says about the discovery distribution

- **C1 was a good pick for an experimental-first wave.** It had an exact claim, a released artifact, and an evaluation with visible weak points. The experiment found real, reproducible limitations. The remedies for those limitations (iso-delay evaluation, the stronger baseline, multi-objective selection) are all established practice.
- **The pattern repeats the Session 1 audit.** Execution finds *evaluation* defects in recent claims much more readily than it finds *open technical problems*. Evaluation defects are engineering, not contributions.

See `00_EXECUTIVE_SUMMARY.md` for the recommendation.
