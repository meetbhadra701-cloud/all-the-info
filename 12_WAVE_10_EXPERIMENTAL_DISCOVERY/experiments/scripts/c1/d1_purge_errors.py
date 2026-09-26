#!/usr/bin/env python3
"""Purges D1 records that failed for infrastructure reasons, so that d1_run.py reruns them.

Infrastructure failures are EVAL_ERROR (evaluator crash) and map_error (mapper produced no output).
A purged line is moved to experiments/results/c1_d1_purged.jsonl together with the purge reason,
so nothing is silently discarded. Scientific outcomes (NEQ, SIM_MISMATCH, UNDECIDED) are never
purged. Prints the benchmarks that need a rerun.
"""
import glob
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
RES = os.path.join(ROOT, "experiments", "results")
purged_log = os.path.join(RES, "c1_d1_purged.jsonl")
rerun = []
for fn in sorted(glob.glob(os.path.join(RES, "c1_d1", "*.jsonl"))):
    keep, drop = [], []
    for line in open(fn, encoding="utf-8"):
        if not line.strip():
            continue
        d = json.loads(line)
        if d.get("sim_verdict") == "EVAL_ERROR" or d.get("eval_error") or d.get("map_error"):
            drop.append(d)
        else:
            keep.append(line if line.endswith("\n") else line + "\n")
    if drop:
        with open(purged_log, "a", encoding="utf-8") as f:
            for d in drop:
                d["purge_reason"] = "infrastructure failure (EVAL_ERROR/map_error); rerun by d1_run.py"
                f.write(json.dumps(d) + "\n")
        tmp = fn + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.writelines(keep)
        os.replace(tmp, fn)
        rerun.append(os.path.basename(fn)[:-6])
        print("purged %d from %s: %s" % (len(drop), os.path.basename(fn), [d["tag"] for d in drop]))
print("RERUN:", " ".join(rerun))
