#!/usr/bin/env python3
"""Run only documented arith_tree option combinations on FIR4 W4."""
from __future__ import annotations
import csv, subprocess, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "scripts" / "run_yosys_current.sh"
SRC = ROOT / "rtl" / "original" / "fir4_gate.v"
WORK = ROOT / "work" / "configuration_isolation"; LOG = ROOT / "logs" / "configuration_isolation"
OPTIONS = {
    "default": "",
    "strategy_fa": "-strategy fa",
    "strategy_42": "-strategy 42",
    "final_ripple": "-final ripple",
    "final_prefix": "-final prefix",
    "no_fma": "-no-fma",
    "fa_ripple": "-strategy fa -final ripple",
    "fa_prefix": "-strategy fa -final prefix",
    "42_ripple": "-strategy 42 -final ripple",
    "42_prefix": "-strategy 42 -final prefix",
    "no_fma_ripple": "-no-fma -final ripple",
    "no_fma_prefix": "-no-fma -final prefix",
}

def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True); LOG.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, opts in OPTIONS.items():
        ys = WORK / f"{name}_w4.ys"; log = LOG / f"{name}_w4.log"; cand = WORK / f"{name}_w4.v"
        ys.write_text("\n".join([
            f"read_verilog -sv {SRC.relative_to(ROOT).as_posix()}",
            "chparam -set W 4 fir4_gate", "hierarchy -top fir4_gate",
            "proc", "check", "flatten", "opt_expr", "check", "opt_clean",
            "opt -nodffe -nosdff", "fsm", "opt", "wreduce", "peepopt",
            "opt_clean", "alumacc", f"arith_tree {opts}", "share", "opt",
            "memory -nomap", "opt_clean", "opt -fast -full", "memory_map",
            "opt -full", "techmap", "opt -fast", "abc", "opt -fast",
            f"write_verilog -noattr {cand.relative_to(ROOT).as_posix()}",
            "stat", "",
        ]))
        start = time.perf_counter()
        with log.open("w") as f:
            p = subprocess.run([str(RUN), "yosys", "-s", str(ys.relative_to(ROOT))], cwd=ROOT,
                               stdout=f, stderr=subprocess.STDOUT, check=False, timeout=180)
        rows.append({"option": name, "syntax": opts or "default", "width": 4,
                     "returncode": p.returncode, "runtime_seconds": f"{time.perf_counter()-start:.6f}",
                     "candidate": str(cand.relative_to(ROOT)) if cand.exists() else "",
                     "script": str(ys.relative_to(ROOT)), "log": str(log.relative_to(ROOT))})
        print(name, p.returncode, flush=True)
    out = ROOT / "results" / "configuration_isolation.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

if __name__ == "__main__":
    main()
