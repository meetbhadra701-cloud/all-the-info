#!/usr/bin/env python3
"""Generate and formally check default/no-FMA FIR4 W8 candidates."""
from __future__ import annotations
import csv, subprocess, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "scripts" / "run_yosys_current.sh"; SRC = ROOT / "rtl" / "original" / "fir4_gate.v"
GOLD = ROOT / "rtl" / "original" / "fir4_gold.v"; WRAP = ROOT / "formal" / "clean_miter" / "explicit_miter_flat.v"
WORK = ROOT / "work" / "configuration_w8"; LOG = ROOT / "logs" / "configuration_w8"; WIT = ROOT / "witnesses"

def classify(t: str, rc: int) -> str:
    if "SAT proof finished - model found: FAIL!" in t: return "FAIL"
    if "ERROR:" in t: return "INCONCLUSIVE_SETUP"
    if "SAT proof finished - no model found: SUCCESS!" in t: return "PASS"
    if rc != 0 or "ERROR:" in t: return "INCONCLUSIVE_SETUP"
    return "INCONCLUSIVE_NO_COMPLETION"

def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True); LOG.mkdir(parents=True, exist_ok=True); WIT.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, opts in (("default", ""), ("no_fma", "-no-fma")):
        width = 8; case = f"{name}_w{width}"; cand = WORK / (case + ".v"); ys = WORK / (case + ".ys"); log = LOG / (case + ".log")
        ys.write_text("\n".join([
            f"read_verilog -sv {SRC.relative_to(ROOT).as_posix()}", "chparam -set W 8 fir4_gate", "hierarchy -top fir4_gate",
            "proc", "check", "flatten", "opt_expr", "check", "opt_clean", "opt -nodffe -nosdff",
            "fsm", "opt", "wreduce", "peepopt", "opt_clean", "alumacc", f"arith_tree {opts}", "share", "opt",
            "memory -nomap", "opt_clean", "opt -fast -full", "memory_map", "opt -full", "techmap", "opt -fast", "abc", "opt -fast",
            f"write_verilog -noattr {cand.relative_to(ROOT).as_posix()}", "",
        ]))
        start = time.perf_counter()
        with log.open("w") as f:
            p = subprocess.run([str(RUN), "yosys", "-s", str(ys.relative_to(ROOT))], cwd=ROOT, stdout=f, stderr=subprocess.STDOUT, check=False, timeout=180)
        rows.append({"option": name, "width": 8, "synth_result": "PASS" if p.returncode == 0 else "FAIL",
                     "synth_returncode": p.returncode, "synth_seconds": f"{time.perf_counter()-start:.6f}",
                     "candidate": str(cand.relative_to(ROOT)), "script": str(ys.relative_to(ROOT)), "log": str(log.relative_to(ROOT))})
    out = ROOT / "results" / "configuration_w8_generation.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

    formal_rows = []
    for r in rows:
        name = r["option"]; case = f"{name}_w8"; cand = ROOT / r["candidate"]; ys = WORK / (case + "_formal.ys"); log = LOG / (case + "_formal.log")
        ys.write_text("\n".join([
            f"read_verilog -sv {GOLD.relative_to(ROOT).as_posix()}", "chparam -set W 8 fir4_gold",
            f"read_verilog -sv {cand.relative_to(ROOT).as_posix()}", "rename fir4_gate fir4_gate_flat",
            f"read_verilog -sv {WRAP.relative_to(ROOT).as_posix()}", "chparam -set W 8 explicit_miter_flat",
            "hierarchy -top explicit_miter_flat", "prep -top explicit_miter_flat", "flatten", "prep -top explicit_miter_flat",
            f"sat -prove mismatch 0 -verify -set-def-inputs -show-ports -dump_json {(WIT/(case+'_config.json')).relative_to(ROOT).as_posix()} -dump_vcd {(WIT/(case+'_config.vcd')).relative_to(ROOT).as_posix()}", "",
        ]))
        start = time.perf_counter()
        try:
            with log.open("w") as f:
                p = subprocess.run([str(RUN), "yosys", "-s", str(ys.relative_to(ROOT))], cwd=ROOT, stdout=f, stderr=subprocess.STDOUT, check=False, timeout=240)
            result = classify(log.read_text(errors="replace"), p.returncode)
        except subprocess.TimeoutExpired:
            p = subprocess.CompletedProcess([], 124); result = "INCONCLUSIVE_TIMEOUT"
        formal_rows.append({"option": name, "width": 8, "result": result, "returncode": p.returncode,
                            "runtime_seconds": f"{time.perf_counter()-start:.6f}", "script": str(ys.relative_to(ROOT)), "log": str(log.relative_to(ROOT))})
        print(name, result, p.returncode, flush=True)
    out = ROOT / "results" / "configuration_w8_formal.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(formal_rows[0])); w.writeheader(); w.writerows(formal_rows)

if __name__ == "__main__":
    main()
