# Evidence index — Wave 10

These are pointers to the primary evidence files, which are not copied here. Labels follow the Wave 10 convention.

| claim in the reports | evidence | label |
|---|---|---|
| Artifact provenance (MappingEvolve 308f5cc, mockturtle 420f027, benchmarks 82d8cc6) | `evidence/c1_provenance.txt` | OBSERVED |
| Binaries built from the stated sources | `experiments/outputs/c1/bin/MANIFEST.txt`, `MANIFEST_ablation.txt` | OBSERVED |
| R1: ISCAS85 rewards reproduced exactly | `experiments/results/c1_r1_iscas_orig.jsonl`, `c1_r1r2_tables.md` | OBSERVED |
| R2: paper EPFL columns (mockturtle, GPT-5) reproduced 20/20; DeepSeek 0/20 | `experiments/results/c1_r2_epfl_orig_*.jsonl`, `c1_r1r2_tables.md`, `experiments/inputs/c1/paper_table2_transcribed.csv` | OBSERVED (paper digits UNVERIFIED) |
| Pre-registration and deviation log | `experiments/results/c1_PREREGISTRATION.md`, `c6_PREREGISTRATION.md` | OBSERVED |
| Validator soundness (it can fail) | `experiments/logs/c1/t1_negative_control.log` | OBSERVED |
| D1: 1,855/1,855 netlists validated; iso-delay ratios; decomposition | `experiments/results/c1_d1/*.jsonl`, `c1_d1_all.csv`, `c1_d1_isodelay.csv`, `c1_d1_summary.json`, `c1_d1_tables.md` | OBSERVED |
| Paper's ABC column weaker than current `&nf` defaults | `c1_d1_tables.md` (last table) | OBSERVED (paper's ABC options UNVERIFIED) |
| No released DeepSeek operator state reproduces the paper's DeepSeek column | `experiments/results/c1_deepseek_provenance.txt`, `c1_r2_epfl_orig_ds_it*.jsonl` | OBSERVED (paper digits UNVERIFIED) |
| D2: the delay-round rule alone reproduces GPT-5 | `experiments/results/c1_d2/*.jsonl`, `c1_d2_summary.json`, `experiments/inputs/c1/ablation/` | OBSERVED |
| ABC `&nf -D` has no effect in this build | `experiments/scripts/c1/t2_nf_units.sh` (stdout summarized in 04 §3) | OBSERVED |
| GT2N gcd: 27/27 rules, +150.06 ps, leakage 5.2% | `experiments/outputs/orfs/gt2n/gcd/base/reports/gt2n/gcd/base/{metadata-check.log,6_finish.rpt}` | OBSERVED |
| kepler-formal SIGILL (no AVX-512) | `experiments/logs/screening/probe_cts_sigill.log`, `probe_lec.log` | OBSERVED |
| Dynamatic has no Gurobi | `experiments/logs/screening/probe_dynamatic.log` | OBSERVED |
| Local OpenROAD lacks `resynth_emap` | `experiments/logs/screening/probe_emap_openroad.log` | OBSERVED |
| C6 treatments | `experiments/outputs/c6/asap7/aes/*/metrics.json`, `experiments/logs/c1/c6_lane*.log` | OBSERVED |
