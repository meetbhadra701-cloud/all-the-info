# PassWitness portable evidence package

This directory contains the RTL, flow, generated checkpoints, formal scripts, logs, witnesses, result, and report from one investigation.

External tools are intentionally not bundled. Install the recorded Yosys version/source commit separately.

A reproduction command is:

```sh
passwitness analyze --rtl source/source.v --top fma_impl --flow flow/synthesis.ys --yosys /path/to/yosys --output-dir replay
```

The paths in result.json and report.md are relative to this package.
