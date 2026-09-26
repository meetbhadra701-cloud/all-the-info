# Experimental Evidence Index

## MUXWISE Experiment 1 — baseline resource-sharing prosecution

- **Hypothesis:** repeated-expression/resource sharing might expose a new EDA opportunity.
- **Relevant files:** `MUXWISE/muxwise-experiment-01/EXPERIMENT_REPORT.md`, `README.md`, `results/`, `scripts/`.
- **Tools:** Yosys 0.23, git `7ce5011c24b`, ABC 1.01.
- **Input/design:** shared versus unshared arithmetic RTL, plus intentionally incorrect subtraction control.
- **Executed:** 99/99 synthesis runs; formal shared/unshared checks and negative control.
- **Observed:** formal positive controls passed and incorrect subtraction failed; normal Yosys+ABC erased the tested sharing difference.
- **Independent validation:** formal positive/negative controls.
- **Limitations:** no physical design; basic idea already covered.
- **Reproduction:** use the included scripts and results; original repository path is recorded in the manifest.

## MUXWISE Experiment 2 — arithmetic-tree mapping

- **Hypothesis:** `synth -arith_tree` may create a measurable family-sensitive mapping effect.
- **Relevant files:** `MUXWISE/muxwise-experiment-02/EXPERIMENT_02_REPORT.md`, `README.md`, `results/`, `scripts/`.
- **Tools:** Yosys 0.69+77, git `9ff27d29c-dirty`, ABC 1.01.
- **Input/design:** width/family benchmarks, including add chains, mixed arithmetic, FIR-like cases, and PicoRV32.
- **Executed:** 136 valid synthesis runs, seven formal checks, two PicoRV32 flows.
- **Observed:** real family-sensitive mapped differences; add chains sometimes improved and mixed/FIR sometimes worsened; PicoRV32 normal and arith-tree signatures matched at 9,171 cells.
- **Independent validation:** formal checks and current-flow signature comparison.
- **Limitations:** configuration observation, not a novel contribution; dirty provenance.

## MUXWISE Experiment 3 — physical-design prosecution

- **Hypothesis:** the arithmetic-tree mapping difference might yield a timing/physical-design advantage.
- **Relevant files:** `MUXWISE/muxwise-experiment-03/EXPERIMENT_03_REPORT.md`, `README.md`, `results/`, `scripts/`.
- **Tools:** Yosys 0.69+77 dirty; OpenROAD/ORFS image digest recorded in report.
- **Input/design:** selected width-8/width-16 arithmetic cases through placement/global routing.
- **Executed:** seeded mapping runs and unseeded repeat; formal and physical pilot.
- **Observed:** no validated timing benefit; equivalence incomplete; arith-tree counterexample real; seed sensitivity present.
- **Independent validation:** multiple seeded runs, but not a clean correctness closure.
- **Limitations:** conditional measurements, incomplete W16 equivalence, inherited manifest mislabeled `model found: FAIL` as PASS.

## MUXWISE Experiment 4 — Yosys arith-tree/FMA defect

- **Hypothesis:** the arithmetic-tree mismatch is a real semantic defect and can be localized and independently reproduced.
- **Relevant files:** `MUXWISE/muxwise-experiment-04/EXPERIMENT_04_REPORT.md`, `README.md`, `results/`, `scripts/`, `YOSYS_FMA/FINAL_REPORT.md`, `YOSYS_FMA/FINAL_VALIDATION_REPORT.md`.
- **Tools:** Yosys 0.69+77, git `9ff27d29c-dirty`; official shallow clone at same commit; simulator/reference flow.
- **Input/design:** signed FMA arithmetic-tree cases at widths 4 and 8; normal, arith-tree, and arith-tree `-no-fma` variants.
- **Executed:** formal equivalence, stage-localization, independent reference/simulation reproduction.
- **Observed:** normal W4/W8 pass; arith-tree fails; `-no-fma` passes; earliest divergence is immediately after arith-tree; downstream techmap/ABC preserve it. Independent outputs differ as W4 `0x00000` vs `0x00180`, W8 `0x000186` vs `0x001986`.
- **Independent validation:** independent reference/simulation and stage-local equivalence.
- **Limitations:** dirty binary provenance; clean rebuild and broader version/ownership analysis remain.

## PassWitness validation and reduction

- **Hypothesis:** a reproducible witness/localization/reduction workflow can package hardware failures with independent evidence.
- **Relevant files:** `PASSWITNESS/docs/`, `PASSWITNESS/research/`, `PASSWITNESS/fixtures/`, `PASSWITNESS/output_packages/`, `SUPPORTING_ARTIFACTS/PASSWITNESS/`.
- **Tools:** project-specific Python/Yosys/simulation/formal tooling; exact requirements are in `PASSWITNESS/docs/reproducibility.md` and `pyproject.toml`.
- **Input/design:** signed-FMA and injected-fault fixtures; pilot-zero/one/two cases.
- **Executed:** documented Phase 3/4 validation and localized clean/patched package generation.
- **Observed:** evidence packages and reducer/localizer artifacts exist; claims are bounded by the project’s limitation/prior-art docs.
- **Independent validation:** fixtures, formal/simulation paths, and release-package checks as documented.
- **Limitations:** do not infer novelty from implementation alone; use prior-art and limitation docs.
- **Reproduction:** `PASSWITNESS/docs/quickstart.md` and `reproducibility.md`.

## PPA-Delta C10 reducer comparison

- **Hypothesis:** coupled structural correspondence can improve hardware failure reduction beyond valid simple baselines.
- **Relevant files:** `../01_RESEARCH_OBJECTIVES_AND_STRATEGY/PPA_DELTA/analysis/`, `../01_RESEARCH_OBJECTIVES_AND_STRATEGY/PPA_DELTA/Experiment-Index.md`, `../01_RESEARCH_OBJECTIVES_AND_STRATEGY/PPA_DELTA/claude/`, `../07_REMAINING_RESEARCH_LEADS/PPA_DELTA/docs/`.
- **Tools/input:** six-method comparison, equal 200-candidate / 1800-second budgets, cache disabled; exact suite and commands are in the local reports.
- **Executed:** C10 comparison and repaired bugpoint baseline.
- **Observed:** coupled method beat valid baselines on 3/3; repaired bugpoint was NO_GAIN; one case reported 39 versus 60 candidates without matching.
- **Independent validation:** multiple baselines and review documents.
- **Limitations:** another review reports 0/3 cases meeting the >=20% bar and unsupported structural correspondence; external/broader validation remains.

## Older waves

Wave 3–6 experiments are indexed in `../04_EARLIER_RESEARCH_WAVES/CODEX_TRANSCRIPT_DERIVED_RESEARCH_HISTORY.md`. They are explicitly marked transcript-derived or inconclusive when the original artifacts were not recovered.
