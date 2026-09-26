#!/usr/bin/env python3
"""Run reproducible Yosys flows for the MUXWISE feasibility experiment."""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUN_YOSYS = ROOT / "scripts" / "run_yosys.sh"
YS_DIR = ROOT / "work" / "ys_scripts"
LOG_DIR = ROOT / "logs" / "synthesis"
FLOW_DIR = ROOT / "work" / "flows"


def prep(top: str, width: int, multi: bool = False) -> str:
    extra = f"\nchparam -set SH 4 {top}" if multi else ""
    return f"""read_verilog -sv rtl/{top}.v
chparam -set W {width} {top}{extra}
hierarchy -top {top}
proc
flatten
opt_expr
opt_clean
"""


def coarse(top: str, width: int, multi: bool = False) -> str:
    return prep(top, width, multi) + """opt -nodffe -nosdff
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
"""


def flow_script(flow: str, top: str, width: int, out_json: Path, out_rtlil: Path, multi: bool = False) -> str:
    if flow == "early":
        body = prep(top, width, multi)
    elif flow == "opt_share":
        body = prep(top, width, multi) + "opt_share\nopt_clean\n"
    elif flow == "explicit_share":
        body = prep(top, width, multi) + "share\nopt_clean\n"
    elif flow == "explicit_share_aggressive":
        body = prep(top, width, multi) + "share -aggressive\nopt_clean\n"
    elif flow == "explicit_share_force":
        body = prep(top, width, multi) + "share -force\nopt_clean\n"
    elif flow == "explicit_share_force_aggressive":
        body = prep(top, width, multi) + "share -force -aggressive\nopt_clean\n"
    elif flow == "opt_share_then_opt":
        body = prep(top, width, multi) + "opt_share\nopt\nopt_clean\n"
    elif flow == "coarse_share":
        body = coarse(top, width, multi)
    elif flow == "mapped_manual":
        body = coarse(top, width, multi) + "techmap\nabc -fast\nopt -fast\n"
    elif flow == "synth_noshare":
        body = f"read_verilog -sv rtl/{top}.v\nchparam -set W {width} {top}\n"
        if multi:
            body += f"chparam -set SH 4 {top}\n"
        body += f"synth -top {top} -noshare\n"
    elif flow == "synth_normal":
        body = f"read_verilog -sv rtl/{top}.v\nchparam -set W {width} {top}\n"
        if multi:
            body += f"chparam -set SH 4 {top}\n"
        body += f"synth -top {top}\n"
    else:
        raise ValueError(flow)

    return body + f"write_json {out_json.relative_to(ROOT).as_posix()}\nwrite_rtlil {out_rtlil.relative_to(ROOT).as_posix()}\nstat\n"


def run_case(case: str, top: str, width: int, flow: str, multi: bool = False) -> dict:
    case_dir = FLOW_DIR / case
    case_dir.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    YS_DIR.mkdir(parents=True, exist_ok=True)
    stem = f"{top}_{flow}_w{width}"
    out_json = case_dir / f"{stem}.json"
    out_rtlil = case_dir / f"{stem}.rtlil"
    ys_path = YS_DIR / f"{case}_{stem}.ys"
    log_path = LOG_DIR / f"{case}_{stem}.log"
    script = flow_script(flow, top, width, out_json, out_rtlil, multi)
    ys_path.write_text(script)
    start = time.perf_counter()
    proc = subprocess.run(
        [str(RUN_YOSYS), "yosys", "-s", str(ys_path.relative_to(ROOT))],
        cwd=ROOT,
        stdout=log_path.open("w"),
        stderr=subprocess.STDOUT,
        check=False,
    )
    elapsed = time.perf_counter() - start
    return {
        "case": case,
        "top": top,
        "width": width,
        "flow": flow,
        "returncode": proc.returncode,
        "runtime_seconds": f"{elapsed:.6f}",
        "script": str(ys_path.relative_to(ROOT)),
        "log": str(log_path.relative_to(ROOT)),
        "json": str(out_json.relative_to(ROOT)) if out_json.exists() else "",
        "rtlil": str(out_rtlil.relative_to(ROOT)) if out_rtlil.exists() else "",
    }


def main() -> int:
    widths = [8, 16, 32, 64]
    flows = [
        "early",
        "opt_share",
        "explicit_share",
        "explicit_share_aggressive",
        "explicit_share_force",
        "explicit_share_force_aggressive",
        "opt_share_then_opt",
        "coarse_share",
        "mapped_manual",
        "synth_noshare",
        "synth_normal",
    ]
    records = []
    for width in widths:
        for top in ("unshared", "shared"):
            for flow in flows:
                records.append(run_case("baseline", top, width, flow))
    for flow in flows:
        records.append(run_case("multi_operator", "multi_operator", 16, flow, multi=True))

    manifest = ROOT / "results" / "run_manifest.csv"
    with manifest.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)
    failures = [r for r in records if r["returncode"] != 0]
    print(json.dumps({"runs": len(records), "failures": len(failures), "manifest": str(manifest)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
