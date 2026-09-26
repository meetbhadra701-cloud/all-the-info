# C1 decisive experiment D1: pre-registration

Written 2026-09-25, before any D1 data existed. By this point R1 (ISCAS85 reward) and R2 (EPFL Table 2, unmodified pipeline) had already been reproduced.

## Object under test

The MappingEvolve evolved operators (arXiv 2604.26591; repo Flians/MappingEvolve @308f5cc):
- `gpt5_it29`: all three operators evolved; this is the paper's headline mapper.
- `deepseek_it24`: only `match_phase` evolved.
- `qwen_it20`: `match_phase` and `match_phase_exact` evolved.

In each case this is the shipped `best_iteration` of the proactive run.

## A. Hypothesis (the claim being tested)

The evolved operators are better mappers: at the same delay constraint they produce less area than the baselines.

The alternative is that the reported area gains (10.04% vs ABC, 7.93% vs mockturtle, paired with a 3.7–6.5% delay increase) are only a move along the area–delay trade-off. A move of that kind is also available from the baseline's own required-time knob.

## B. Baselines (all start from the byte-identical compress2 AIG)

1. `initial`: the original mockturtle `map` operators in the same framework with the same parameters, with `required_time` set to the evolved mapper's achieved delay. This is the in-framework iso-delay baseline, and the only difference from the evolved mapper is the operator code.
2. `emap`: upstream mockturtle emap at the same commit, `required_time` = the evolved delay.
3. `nfp`: ABC `&nf -p -D <evolved delay>` (yosys-abc from the ORFS image).

Sweeps are also recorded to draw fronts:
- `initial` relax r ∈ {2, 4, 6, 8, 10, 15, 20, 30, 50}% plus skip-delay-round;
- emap relax r ∈ {5, 10, 20}% plus area-oriented;
- ABC `&nf` default and `-p`.

## C. Variable

Operator code (evolved vs initial) compared with baseline mappers held at the same required time.

## D. Observables

For every netlist:
- area and worst arrival, recomputed by `c1_eval.py`, which is independent of the mapper;
- the ratio A_evolved / A_baseline@D_evolved, with its geometric mean over each suite;
- whether the baseline met the delay (D_baseline ≤ D_evolved × 1.001).

## E. Independent validation

Every netlist gets:
1. `c1_eval.py`, which uses its own genlib parser and STA to recompute area and delay (validated on c17 and adder, where it matched exactly);
2. 4096-pattern random simulation against the original, pre-compress2 AIG;
3. ABC `&cec` of the netlist, translated to BLIF by `c1_eval.py`, against the original AIG.

The CEC verdict fails closed. Only the literal line "Networks are equivalent" counts as PASS. Anything else is UNDECIDED or NEQ. Exit codes are never used as verdicts.

## Suites

- **EPFL-20:** the paper's evaluation suite.
- **IWLS05-22:** all IWLS'05 circuits in the mockturtle benchmark folder except the five over 500k AIG nodes (leon2, leon3, leon3_opt, leon3mp, netcard, excluded for compute budget). This suite is held out by both the paper and the evolution.
- ISCAS85-11 is the evolution's training set. It is reported, but no verdict rests on it.

## F. Kill condition

Suppose that, for each of the three evolved variants on EPFL-20:
- geomean(A_evolved / min over baselines of A_baseline@D_evolved) ≥ 0.99, i.e. less than a 1% area advantage at iso-delay over the best baseline; or
- the in-framework baseline alone (`initial`@D_evolved) is within 1% (geomean ratio ≥ 0.99).

Then the headline gain is explained by the delay relaxation. C1's premise that "LLM-evolved operators are better mappers" is KILLED at this QoR level.

A second, independent kill: any evolved netlist that is NEQ under independent validation, where the paper's own check passed. That would be a validation-gap finding. It would still be recorded as engineering unless it is systematic.

## G. Advance condition

At least one evolved variant must meet all three:
- geomean ratio ≤ 0.97 against the best baseline at iso-delay on EPFL-20, with ≥ 14/20 circuits below 1.0;
- geomean ≤ 0.98 on IWLS05-22;
- every netlist equivalent (CEC PASS or no mismatch).

Only then is it worth isolating the mechanism, testing post-route (ORFS asap7) and running targeted prior art.

## In between

UNRESOLVED. The next test is post-route PPA on a subset.

## Deviation log

- **2026-09-25, before any EPFL or IWLS D1 data:** a smoke test (`t2_nf_units.sh`, adder) showed that ABC `&nf -D <x>` has no effect in this yosys-abc build; the area and delay stay identical for every x. The ABC iso-delay baseline therefore uses `&nf -p -R ⌊100·(D_evolved/D_nfp − 1)⌋`. This never gives ABC more slack than the evolved mapper had. An ABC relax sweep R ∈ {2, 5, 10, 20, 30} was added for the fronts. The earlier c17, ctrl and adder test records were discarded and rerun.
- **Secondary, post-hoc analysis, labelled as such:** a "front" baseline, the minimum area over *all* baseline configurations whose independently measured delay is ≤ D_evolved. It is reported alongside the pre-registered per-point comparison, never instead of it.
- **2026-09-25, early in D1:** the CEC engine was switched from `&cec` to ABC `cec -n -T 900 -C 100000` (FRAIG + SAT) for throughput. On the log2 netlist, `&cec` took 80–150 s or longer, while `cec -n` proved the same pair in about 9 s (`t3_cec_speed.sh`). Records already completed with `&cec` (mem_ctrl, vga_lcd) keep their `&cec` PASS verdicts. The verdict parse is unchanged and fails closed.
- **2026-09-25, during D1:** the `c1_eval.py` BLIF writer (used only for the CEC input) was changed from minterm covers to irredundant SOP covers (Minato–Morreale). Each cover is asserted equal to the cell truth table, and the change was unit-tested on 9,278 functions. Area, STA and simulation are unchanged. The motive was throughput: minterm covers bloated the hyp AIG and slowed `cec`. A first swap had a Python bug (`dict(**{int:…})`), and 6 configs ran with it and recorded EVAL_ERROR: des_perf R:initial:4; log2 I:emap@qwen_it20, I:nfp@qwen_it20, B:emap, B:emap_area, R:emap:5. These records are purged and rerun in a repair pass; no verdict uses them.
- **2026-09-25, during D1:** in this build ABC does not enforce `cec -T` on hyp; the direct CEC of E:gpt5_it29 took 1310 s and passed. The hyp + ISCAS group was therefore restarted with `CEC_MODE=two_stage`, which is sound by transitivity:
  - stage A checks original ≡ compress2-AIG once per benchmark, cached in `c1_d1_stageA_<bench>.json`;
  - stage B checks compress2-AIG ≡ netlist for each config.
  - On hyp this takes 26 s + 36 s (`t4_twostage_cec.sh`).
  - NEQ is reported if either stage is NEQ while the other is PASS; any other combination is UNDECIDED.
  - Records already completed with direct CEC keep their direct verdicts.

## D2 cause isolation: pre-registration

Written 2026-09-25, after D1 completed and before any D2 data existed.

**Question.** Is GPT-5 it29's delay relaxation caused by its delay-round acceptance rule? The rule has two parts:
- `match_phase`, `!DO_AREA` branch: a faster match is accepted only if its area flow is within 0.25·inv_area, or if it gains at least 0.5·inv_delay;
- `match_drop_phase`, delay branch: one phase plus an inverter is used only if that does not increase area flow.

**Variants.** They are generated by asserted substitution (`d2_make_ablations.py`; MD5s in `experiments/outputs/c1/bin/MANIFEST_ablation.txt`):
- `ab1` = GPT-5 it29 with the delay-round rule removed;
- `ab2` = initial operators plus only the delay-round rule.

**Runs.** On EPFL-20 and IWLS05-22:
- the default run (required = own best);
- `initial` `map` with required = that variant's own delay (iso-delay control).

Each netlist is validated as in D1, using two-stage CEC.

**Predictions.**
- **P1.** ab1: geomean(D/D_initial) is within ±1% of 1.00 on EPFL-20, i.e. no relaxation.
- **P2.** ab2: geomean(D/D_initial) > 1.02 on EPFL-20, and geomean(A_ab2 / A_initial@D_ab2) is within ±1.5% of 1.00, i.e. the rule is essentially a relaxation that the required-time knob reproduces.
- **P3.** ab1: geomean(A_ab1 / A_initial@D_ab1) < 1.00, i.e. the area-round rules carry the in-framework operator gain.

**Readout.** The cause is CONFIRMED if P1 and P2 hold. Otherwise it is recorded as ENTANGLED, and the report says which prediction failed.
