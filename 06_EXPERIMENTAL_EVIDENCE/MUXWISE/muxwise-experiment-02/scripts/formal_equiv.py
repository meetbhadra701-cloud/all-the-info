#!/usr/bin/env python3
"""Run formal equivalence checks for RTL alternatives and mapped flow outputs."""

from __future__ import annotations

import csv
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "scripts" / "run_current.sh"
YS = ROOT / "work" / "formal_ys"
LOG = ROOT / "logs" / "formal"


def rtl_pair(name, file1, top1, file2, top2, width):
    return name, f"""read_verilog -sv reproducers/{file1}
chparam -set W {width} {top1}
prep -top {top1}
design -stash gold
read_verilog -sv reproducers/{file2}
chparam -set W {width} {top2}
prep -top {top2}
design -stash gate
design -copy-from gold -as gold {top1}
design -copy-from gate -as gate {top2}
equiv_make gold gate equiv
prep -top equiv
equiv_simple
equiv_status -assert
"""


def run(name, script):
    yspath = YS / f"{name}.ys"
    logpath = LOG / f"{name}.log"
    yspath.parent.mkdir(parents=True, exist_ok=True)
    logpath.parent.mkdir(parents=True, exist_ok=True)
    yspath.write_text(script)
    start = time.perf_counter()
    outcome = "PASS_OR_FAIL"
    try:
        with logpath.open("w") as f:
            p = subprocess.run([str(RUN), "yosys", "-s", str(yspath.relative_to(ROOT))], cwd=ROOT, stdout=f, stderr=subprocess.STDOUT, check=False, timeout=60)
        returncode = p.returncode
        outcome = "PASS" if returncode == 0 else "FAIL"
    except subprocess.TimeoutExpired:
        returncode = 124
        outcome = "TIMEOUT_INCONCLUSIVE"
        with logpath.open("a") as f:
            f.write("\nTIMEOUT: formal check exceeded 60 seconds; result is inconclusive.\n")
    return {"name": name, "returncode": returncode, "outcome": outcome, "runtime_seconds": f"{time.perf_counter()-start:.6f}", "script": str(yspath.relative_to(ROOT)), "log": str(logpath.relative_to(ROOT))}


def mapped_check(name, source_file, top, width, path):
    return name, f"""read_verilog -sv reproducers/{source_file}
chparam -set W {width} {top}
prep -top {top}
design -stash gold
design -reset
read_verilog -sv {path}
prep -top {top}
design -stash gate
design -copy-from gold -as gold {top}
design -copy-from gate -as gate {top}
miter -equiv -flatten gold gate miter
prep -top miter
sat -prove trigger 0 -set-def-inputs
"""


def main():
    jobs = []
    for w in (8,):
        jobs.append(rtl_pair(f"add_chain_vs_balanced_w{w}", "add_chain.v", "add_chain", "add_balanced.v", "add_balanced", w))
    for w in (8,):
        jobs.append(rtl_pair(f"trim_wide_vs_narrow_w{w}", "width_trim.v", "trim_wide", "width_trim.v", "trim_narrow", w))
    for w in (8,):
        jobs.append(rtl_pair(f"fir4_vs_grouped_w{w}", "fir4.v", "fir4", "fir4.v", "fir4_grouped", w))

    for top, source, case, w in (
        ("add_chain", "add_chain.v", "arith_tree", 4),
        ("fir4", "fir4.v", "fir4", 4),
    ):
        normal = f"work/flows/{case}/{top}_synth_normal_w{w}.v"
        tree = f"work/flows/{case}/{top}_synth_arith_tree_w{w}.v"
        jobs.append(mapped_check(f"{top}_normal_mapped_vs_rtl_w{w}", source, top, w, normal))
        jobs.append(mapped_check(f"{top}_arith_tree_mapped_vs_rtl_w{w}", source, top, w, tree))

    records = [run(name, script) for name, script in jobs]
    out = ROOT / "results/formal_manifest.csv"
    with out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    print({"checks": len(records), "failures": sum(r["returncode"] != 0 for r in records), "manifest": str(out)})


if __name__ == "__main__":
    main()
