#!/usr/bin/env python3
"""Formal validation of every documented W4 arith_tree configuration."""
from __future__ import annotations
import csv, subprocess, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "scripts" / "run_yosys_current.sh"
GOLD = ROOT / "rtl" / "original" / "fir4_gold.v"
WRAP = ROOT / "formal" / "clean_miter" / "explicit_miter_flat.v"
SRC = ROOT / "work" / "configuration_isolation"
WORK = ROOT / "work" / "configuration_formal"; LOG = ROOT / "logs" / "configuration_formal"; WIT = ROOT / "witnesses"
OPTIONS = ("default","strategy_fa","strategy_42","final_ripple","final_prefix","no_fma",
           "fa_ripple","fa_prefix","42_ripple","42_prefix","no_fma_ripple","no_fma_prefix")

def classify(text: str, rc: int) -> str:
    if "SAT proof finished - model found: FAIL!" in text: return "FAIL"
    if "ERROR:" in text: return "INCONCLUSIVE_SETUP"
    if "SAT proof finished - no model found: SUCCESS!" in text: return "PASS"
    if rc != 0 or "ERROR:" in text: return "INCONCLUSIVE_SETUP"
    return "INCONCLUSIVE_NO_COMPLETION"

def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True); LOG.mkdir(parents=True, exist_ok=True); WIT.mkdir(parents=True, exist_ok=True)
    rows = []
    for name in OPTIONS:
        case = name + "_w4"; candidate = SRC / (case + ".v"); ys = WORK / (case + ".ys"); log = LOG / (case + ".log")
        ys.write_text("\n".join([
            f"read_verilog -sv {GOLD.relative_to(ROOT).as_posix()}",
            "chparam -set W 4 fir4_gold",
            f"read_verilog -sv {candidate.relative_to(ROOT).as_posix()}",
            "rename fir4_gate fir4_gate_flat",
            f"read_verilog -sv {WRAP.relative_to(ROOT).as_posix()}",
            "chparam -set W 4 explicit_miter_flat", "hierarchy -top explicit_miter_flat",
            "prep -top explicit_miter_flat", "flatten", "prep -top explicit_miter_flat",
            f"sat -prove mismatch 0 -verify -set-def-inputs -show-ports -dump_json {(WIT/(case+'_config.json')).relative_to(ROOT).as_posix()} -dump_vcd {(WIT/(case+'_config.vcd')).relative_to(ROOT).as_posix()}", "",
        ]))
        start = time.perf_counter()
        try:
            with log.open("w") as f:
                p = subprocess.run([str(RUN), "yosys", "-s", str(ys.relative_to(ROOT))], cwd=ROOT,
                                   stdout=f, stderr=subprocess.STDOUT, check=False, timeout=180)
            result = classify(log.read_text(errors="replace"), p.returncode)
        except subprocess.TimeoutExpired:
            p = subprocess.CompletedProcess([], 124); result = "INCONCLUSIVE_TIMEOUT"
            with log.open("a") as f: f.write("\nTIMEOUT: 180 seconds; proof is inconclusive.\n")
        rows.append({"option": name, "width": 4, "result": result, "returncode": p.returncode,
                     "runtime_seconds": f"{time.perf_counter()-start:.6f}",
                     "script": str(ys.relative_to(ROOT)), "log": str(log.relative_to(ROOT)),
                     "candidate": str(candidate.relative_to(ROOT))})
        print(name, result, p.returncode, flush=True)
    out = ROOT / "results" / "configuration_formal.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

if __name__ == "__main__":
    main()
