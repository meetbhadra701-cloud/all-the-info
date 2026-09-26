#!/usr/bin/env python3
"""Compare the original RTL against re-imported Verilog export netlists."""
from __future__ import annotations
import csv, subprocess, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "scripts" / "run_yosys_current.sh"
GOLD = ROOT / "rtl" / "original" / "fir4_gold.v"
WRAP = ROOT / "formal" / "clean_miter" / "explicit_miter_flat.v"
WORK = ROOT / "work" / "export_miter"
LOGS = ROOT / "logs" / "export_miter"
WIT = ROOT / "witnesses"
CASES = [
    ("normal_w4", 4, ROOT / "intermediate" / "normal_w4" / "post_abc.v"),
    ("arith_tree_w4", 4, ROOT / "intermediate" / "arith_tree_w4" / "post_abc.v"),
    ("normal_w8", 8, ROOT / "intermediate" / "normal_w8" / "post_abc.v"),
    ("arith_tree_w8", 8, ROOT / "intermediate" / "arith_tree_w8" / "post_abc.v"),
]

def classify(text: str, rc: int) -> str:
    if "SAT proof finished - no model found: SUCCESS!" in text: return "PASS"
    if "SAT proof finished - model found: FAIL!" in text: return "FAIL"
    if rc != 0 or "ERROR:" in text: return "INCONCLUSIVE_SETUP"
    return "INCONCLUSIVE_NO_COMPLETION"

def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True); LOGS.mkdir(parents=True, exist_ok=True); WIT.mkdir(parents=True, exist_ok=True)
    rows = []
    for case, width, candidate in CASES:
        ys = WORK / f"{case}.ys"; log = LOGS / f"{case}.log"
        ys.write_text("\n".join([
            f"read_verilog -sv {GOLD.relative_to(ROOT).as_posix()}",
            f"chparam -set W {width} fir4_gold",
            f"read_verilog -sv {candidate.relative_to(ROOT).as_posix()}",
            "rename fir4_gate fir4_gate_flat",
            f"read_verilog -sv {WRAP.relative_to(ROOT).as_posix()}",
            f"chparam -set W {width} explicit_miter_flat",
            "hierarchy -top explicit_miter_flat", "prep -top explicit_miter_flat",
            "flatten", "prep -top explicit_miter_flat", "stat",
            f"sat -prove mismatch 0 -verify -set-def-inputs -show-ports -dump_json {(WIT/(case+'_export.json')).relative_to(ROOT).as_posix()} -dump_vcd {(WIT/(case+'_export.vcd')).relative_to(ROOT).as_posix()}",
            "",
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
        rows.append({"case": case, "width": width, "observed": result, "returncode": p.returncode,
                     "runtime_seconds": f"{time.perf_counter()-start:.6f}",
                     "script": str(ys.relative_to(ROOT)), "log": str(log.relative_to(ROOT)),
                     "candidate": str(candidate.relative_to(ROOT))})
    out = ROOT / "results" / "export_correctness.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(*[f"{r['case']} {r['observed']} rc={r['returncode']}" for r in rows], sep="\n")

if __name__ == "__main__":
    main()
