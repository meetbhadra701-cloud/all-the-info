#!/usr/bin/env bash
# Identity of the ABC binary used by cec_pre_post.sh and abc_steps.sh (appended to evidence/provenance.txt)
HERE="$(cd "$(dirname "$0")/.." && pwd)"
A=/mnt/c/Users/meetb/Documents/Codex/2026-09-20/muxwise-experiment-1-zero-commitment-eda/outputs/muxwise-experiment-02/work/oss-cad-suite/bin/yosys-abc
{
  echo "=== ABC used for &cec (cec_pre_post.sh) and single-step isolation (abc_steps.sh)"
  echo "path: $A"
  "$A" -c "version" 2>&1 | grep -v '^$' | head -3
  echo "wrapper sha256: $(sha256sum "$A" | cut -c1-64)"
  R="$(dirname "$A")/../libexec/yosys-abc"
  [ -f "$R" ] && echo "binary (libexec) sha256: $(sha256sum "$R" | cut -c1-64)"
  Y="$(dirname "$A")/yosys"; [ -x "$Y" ] && echo "bundled yosys: $("$Y" -V 2>&1 | head -1)"
} | tee -a "$HERE/evidence/provenance.txt"
