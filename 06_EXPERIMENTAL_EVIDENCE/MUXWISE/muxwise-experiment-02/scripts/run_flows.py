#!/usr/bin/env python3
"""Run bounded current-Yosys experiments for Experiment 02."""

from __future__ import annotations

import csv
import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "scripts" / "run_current.sh"
YS_DIR = ROOT / "work" / "ys_scripts"
LOG_DIR = ROOT / "logs" / "synthesis"
FLOW_DIR = ROOT / "work" / "flows"


def header(top: str, width: int) -> str:
    return f"read_verilog -sv reproducers/{SOURCE[top]}\nchparam -set W {width} {top}\nhierarchy -top {top}\n"


SOURCE = {
    "add_chain": "add_chain.v",
    "add_balanced": "add_balanced.v",
    "mixed_left": "mixed_arith.v",
    "mixed_grouped": "mixed_arith.v",
    "trim_wide": "width_trim.v",
    "trim_narrow": "width_trim.v",
    "fir4": "fir4.v",
    "fir4_grouped": "fir4.v",
    "mapping_datapath": "mapping_datapath.v",
    "multi_operator": "multi_operator.v",
}


def prep(top: str, width: int) -> str:
    return header(top, width) + "proc\nflatten\nopt_expr\nopt_clean\n"


def pre_map(top: str, width: int) -> str:
    # Current synth help, copied as an explicit pre-ABC flow so only ABC mode varies.
    return header(top, width) + """proc
check
flatten
opt_expr
check
opt_clean
opt -nodffe -nosdff
fsm
opt
wreduce
peepopt
opt_clean
alumacc
share
opt
memory -nomap
opt_clean
opt -fast -full
memory_map
opt -full
techmap
opt -fast
"""


def body(top: str, width: int, flow: str) -> str:
    if flow == "early":
        return prep(top, width)
    if flow == "wreduce":
        return prep(top, width) + "wreduce\nopt_clean\n"
    if flow == "explicit_share":
        return prep(top, width) + "share\nopt_clean\n"
    if flow == "explicit_share_aggressive":
        return prep(top, width) + "share -aggressive\nopt_clean\n"
    if flow == "opt_share":
        return prep(top, width) + "opt_share\nopt_clean\n"
    if flow == "synth_normal":
        return header(top, width) + f"synth -top {top}\n"
    if flow == "synth_arith_tree":
        return header(top, width) + f"synth -top {top} -arith_tree\n"
    if flow == "synth_noshare":
        return header(top, width) + f"synth -top {top} -noshare\n"
    if flow == "map_default":
        return pre_map(top, width) + "abc\nopt -fast\n"
    if flow == "map_simple":
        return pre_map(top, width) + "abc -g simple\nopt -fast\n"
    if flow == "map_gates":
        return pre_map(top, width) + "abc -g gates\nopt -fast\n"
    raise ValueError(flow)


def run_one(case: str, top: str, width: int, flow: str) -> dict:
    stem = f"{top}_{flow}_w{width}"
    yspath = YS_DIR / f"{case}_{stem}.ys"
    logpath = LOG_DIR / f"{case}_{stem}.log"
    jsonpath = FLOW_DIR / case / f"{stem}.json"
    rtlilpath = FLOW_DIR / case / f"{stem}.rtlil"
    verilogpath = FLOW_DIR / case / f"{stem}.v"
    yspath.parent.mkdir(parents=True, exist_ok=True)
    logpath.parent.mkdir(parents=True, exist_ok=True)
    jsonpath.parent.mkdir(parents=True, exist_ok=True)
    script = body(top, width, flow)
    script += f"write_json {jsonpath.relative_to(ROOT).as_posix()}\n"
    script += f"write_rtlil {rtlilpath.relative_to(ROOT).as_posix()}\n"
    if flow in ("synth_normal", "synth_arith_tree", "map_default", "map_simple", "map_gates"):
        script += f"write_verilog -noattr {verilogpath.relative_to(ROOT).as_posix()}\n"
    script += "stat\n"
    yspath.write_text(script)
    start = time.perf_counter()
    with logpath.open("w") as log:
        proc = subprocess.run([str(RUN), "yosys", "-s", str(yspath.relative_to(ROOT))], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=False)
    elapsed = time.perf_counter() - start
    return {
        "case": case, "top": top, "width": width, "flow": flow,
        "returncode": proc.returncode, "runtime_seconds": f"{elapsed:.6f}",
        "script": str(yspath.relative_to(ROOT)), "log": str(logpath.relative_to(ROOT)),
        "json": str(jsonpath.relative_to(ROOT)) if jsonpath.exists() else "",
        "rtlil": str(rtlilpath.relative_to(ROOT)) if rtlilpath.exists() else "",
        "verilog": str(verilogpath.relative_to(ROOT)) if verilogpath.exists() else "",
    }


def main() -> int:
    jobs: list[tuple[str, str, list[int], list[str]]] = [
        ("arith_tree", "add_chain", [4, 8, 16, 32, 64], ["synth_normal", "synth_arith_tree", "map_default", "map_simple", "map_gates"]),
        ("arith_tree", "add_balanced", [4, 8, 16, 32, 64], ["synth_normal", "synth_arith_tree", "map_default", "map_simple", "map_gates"]),
        ("mixed_arith", "mixed_left", [16, 32], ["synth_normal", "synth_arith_tree", "map_default", "map_simple", "map_gates"]),
        ("mixed_arith", "mixed_grouped", [16, 32], ["synth_normal", "synth_arith_tree", "map_default", "map_simple", "map_gates"]),
        ("width_trim", "trim_wide", [8, 16, 32], ["early", "wreduce", "synth_normal"]),
        ("width_trim", "trim_narrow", [8, 16, 32], ["early", "wreduce", "synth_normal"]),
        ("fir4", "fir4", [4, 8, 16], ["synth_normal", "synth_arith_tree", "map_default", "map_simple", "map_gates"]),
        ("fir4", "fir4_grouped", [4, 8, 16], ["synth_normal", "synth_arith_tree", "map_default", "map_simple", "map_gates"]),
        ("mapping", "mapping_datapath", [8, 16, 32], ["synth_normal", "map_default", "map_simple", "map_gates"]),
        ("resource_share", "multi_operator", [16], ["early", "opt_share", "explicit_share", "explicit_share_aggressive", "synth_noshare", "synth_normal"]),
    ]
    records = []
    for case, top, widths, flows in jobs:
        for width in widths:
            for flow in flows:
                records.append(run_one(case, top, width, flow))
    out = ROOT / "results" / "run_manifest.csv"
    out.parent.mkdir(exist_ok=True)
    with out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader(); writer.writerows(records)
    failures = [r for r in records if r["returncode"] != 0]
    print(json.dumps({"runs": len(records), "failures": len(failures), "manifest": str(out)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
