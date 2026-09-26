#!/usr/bin/env bash
# Runs the D1 orchestrator in two-stage CEC mode (see the pre-registration deviation log).
CEC_MODE=two_stage python3 /w/experiments/scripts/c1/d1_run.py "$@"
