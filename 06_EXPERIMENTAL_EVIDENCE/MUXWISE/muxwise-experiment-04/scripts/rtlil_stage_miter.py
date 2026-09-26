#!/usr/bin/env python3
"""Check RTLIL snapshots directly, before Verilog export."""
from __future__ import annotations
import csv, subprocess, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]; RUN = ROOT / "scripts" / "run_yosys_current.sh"
GOLD = ROOT / "rtl" / "original" / "fir4_gold.v"; WRAP = ROOT / "formal" / "clean_miter" / "explicit_miter_flat.v"
WORK = ROOT / "work" / "rtlil_miter"; LOG = ROOT / "logs" / "rtlil_miter"; WIT = ROOT / "witnesses"

def classify(t: str, rc: int) -> str:
    if "SAT proof finished - model found: FAIL!" in t: return "FAIL"
    if "ERROR:" in t: return "INCONCLUSIVE_SETUP"
    if "SAT proof finished - no model found: SUCCESS!" in t: return "PASS"
    if rc != 0 or "ERROR:" in t: return "INCONCLUSIVE_SETUP"
    return "INCONCLUSIVE_NO_COMPLETION"

def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True); LOG.mkdir(parents=True, exist_ok=True); WIT.mkdir(parents=True, exist_ok=True)
    rows = []
    for width in (4, 8):
        for config in ("normal", "arith_tree"):
            for stage in ("pre_arith_tree", "post_arith_tree"):
                case = f"{config}_w{width}_{stage}"; cand = ROOT / "intermediate" / f"{config}_w{width}" / f"{stage}.rtlil"
                ys = WORK / f"{case}.ys"; log = LOG / f"{case}.log"
                ys.write_text("\n".join([
                    f"read_verilog -sv {GOLD.relative_to(ROOT).as_posix()}", f"chparam -set W {width} fir4_gold",
                    f"read_rtlil {cand.relative_to(ROOT).as_posix()}", "rename fir4_gate fir4_gate_flat",
                    f"read_verilog -sv {WRAP.relative_to(ROOT).as_posix()}", f"chparam -set W {width} explicit_miter_flat",
                    "hierarchy -top explicit_miter_flat", "prep -top explicit_miter_flat", "flatten", "prep -top explicit_miter_flat",
                    f"sat -prove mismatch 0 -verify -set-def-inputs -show-ports -dump_json {(WIT/(case+'_rtlil.json')).relative_to(ROOT).as_posix()} -dump_vcd {(WIT/(case+'_rtlil.vcd')).relative_to(ROOT).as_posix()}", "",
                ]))
                start = time.perf_counter()
                with log.open("w") as f:
                    p = subprocess.run([str(RUN), "yosys", "-s", str(ys.relative_to(ROOT))], cwd=ROOT, stdout=f, stderr=subprocess.STDOUT, check=False, timeout=180)
                t = log.read_text(errors="replace"); result = classify(t, p.returncode)
                rows.append({"width": width, "config": config, "stage": stage, "result": result, "returncode": p.returncode,
                             "runtime_seconds": f"{time.perf_counter()-start:.6f}", "script": str(ys.relative_to(ROOT)), "log": str(log.relative_to(ROOT))})
                print(case, result, p.returncode, flush=True)
    out = ROOT / "results" / "rtlil_stage_correctness.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

if __name__ == "__main__":
    main()
