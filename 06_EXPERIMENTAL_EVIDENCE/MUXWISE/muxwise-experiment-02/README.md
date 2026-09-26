# MUXWISE Experiment 02

This experiment searches for measured optimization weaknesses rather than proposing a new EDA algorithm.

Primary report: [EXPERIMENT_02_REPORT.md](EXPERIMENT_02_REPORT.md)

Reproducible commands:

```text
python3 scripts/run_flows.py
python3 scripts/collect_metrics.py
python3 scripts/formal_equiv.py
```

The current Yosys toolchain is the official OSS CAD Suite extracted under `work/oss-cad-suite/`. The Experiment 1 Docker image remains available for cross-checks but is not the primary toolchain.

Results:

- `results/all_experiments.csv`: all 136 valid synthesis runs.
- `results/surviving_findings.csv`: retained technical finding record.
- `results/formal_manifest.csv`: formal checks and proof runtimes.
- `results/open_source.csv`: PicoRV32 sanity check.

No new synthesis pass or optimization engine was implemented.

