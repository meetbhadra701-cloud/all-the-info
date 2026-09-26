# MUXWISE Experiment 01

This directory contains the zero-commitment feasibility experiment for selective resource sharing. It is intentionally not an implementation of a new optimization engine.

## Reproduce

The experiment uses Docker Desktop through `docker.exe` because the WSL distro did not have Linux-side Docker integration. The wrapper builds the pinned Debian Bookworm image on first use.

```text
./scripts/formal/run_formal.sh
python3 scripts/synthesis/run_synthesis.py
python3 scripts/analysis/collect_metrics.py
```

The synthesis runner executes the exact generated Yosys scripts under `work/ys_scripts/`. Logs are under `logs/`, intermediate RTLIL/JSON netlists are under `work/flows/`, and CSV summaries are under `results/`.

## Controlled variables

Baseline modules are `rtl/unshared.v` and `rtl/shared.v`. Baseline widths are 8, 16, 32, and 64. The additional combinational design is `rtl/multi_operator.v` at W=16.

Flows include early RTLIL, explicit `opt_share`, explicit `share` with documented flag variants, an `opt_share`-then-`opt` diagnostic, a coarse share flow, a manual techmap/ABC flow, `synth -noshare`, and normal `synth`.

The structural comparison is a name-independent Weisfeiler–Lehman-style connectivity signature over Yosys JSON. It is evidence about structure, not a substitute for formal equivalence. The formal proof is recorded separately in `logs/formal_equivalent.log`.

## Result status

The main report is [EXPERIMENT_REPORT.md](EXPERIMENT_REPORT.md). The selected disposition is **A — BASIC IDEA ALREADY COVERED**, limited to the basic RTL resource-sharing transformation tested here. OpenROAD and physical design were not executed because no compatible OpenROAD environment was available.

