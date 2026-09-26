#!/usr/bin/env python3
"""Fail-closed explicit output-comparison checks for Experiment 4."""
from __future__ import annotations

import csv
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "scripts" / "run_yosys_current.sh"
GOLD = ROOT / "rtl" / "original" / "fir4_gold.v"
GATE = ROOT / "rtl" / "original" / "fir4_gate.v"
WRONG = ROOT / "rtl" / "negative_controls" / "fir4_wrong_gate.v"
MITER = ROOT / "formal" / "clean_miter" / "explicit_miter.v"
WORK = ROOT / "work" / "clean_miter"
LOGS = ROOT / "logs" / "clean_miter"
WIT = ROOT / "witnesses"

CASES = [
    ("rtl_self", "self", "PASS_EXPECTED"),
    ("wrong_rtl", "wrong", "FAIL_EXPECTED"),
]


def verdict(text: str, returncode: int) -> str:
    if "SAT proof finished - no model found: SUCCESS!" in text:
        return "PASS"
    if "SAT proof finished - model found: FAIL!" in text:
        return "FAIL"
    if "TIMEOUT" in text:
        return "INCONCLUSIVE_TIMEOUT"
    if returncode != 0 or "ERROR:" in text:
        return "INCONCLUSIVE_SETUP"
    return "INCONCLUSIVE_NO_COMPLETION"


def make_script(case: str, mode: str, width: int) -> str:
    candidate = WRONG if mode == "wrong" else GATE
    candidate_rel = candidate.relative_to(ROOT).as_posix()
    lines = [
        f"read_verilog -sv {GOLD.relative_to(ROOT).as_posix()}",
        f"read_verilog -sv {candidate_rel}",
        f"chparam -set W {width} fir4_gold",
        f"chparam -set W {width} fir4_gate",
    ]
    if mode == "normal":
        lines.append("synth -top fir4_gate")
    elif mode == "arith_tree":
        lines.append("synth -top fir4_gate -arith_tree")
    if mode in ("normal", "arith_tree"):
        lines.append(f"write_verilog -noattr { (WORK / (case + '_candidate.v')).relative_to(ROOT).as_posix() }")
        # synth -top prunes unreferenced gold modules; reload the exact gold
        # source after synthesis so the explicit miter cannot silently lose it.
        lines += [
            f"read_verilog -sv {GOLD.relative_to(ROOT).as_posix()}",
            f"chparam -set W {width} fir4_gold",
        ]
    lines += [
        f"read_verilog -sv {MITER.relative_to(ROOT).as_posix()}",
        f"chparam -set W {width} explicit_miter",
        "hierarchy -top explicit_miter",
        "prep -top explicit_miter",
        "flatten",
        "prep -top explicit_miter",
        "stat",
        (
            f"sat -prove mismatch 0 -verify -set-def-inputs -show-ports "
            f"-dump_json {(WIT / (case + '.json')).relative_to(ROOT).as_posix()} "
            f"-dump_vcd {(WIT / (case + '.vcd')).relative_to(ROOT).as_posix()}"
        ),
    ]
    return "\n".join(lines) + "\n"


def extract_signals(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        if line.startswith("\\") and "\t" in line:
            fields = line.split()
            if len(fields) >= 2:
                out[fields[0].lstrip("\\")] = fields[-1]
        elif line.startswith("  ") and re.search(r"\\(x[0-3]|gold_y|gate_y|mismatch)", line):
            fields = line.split()
            if len(fields) >= 2:
                out[fields[0].lstrip("\\")] = fields[-1]
    return out


def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    WIT.mkdir(parents=True, exist_ok=True)
    rows = []
    for case, mode, expected in CASES:
        width = 8 if case.endswith("w8") or case in ("rtl_self", "wrong_rtl") else 4
        script_path = WORK / f"{case}.ys"
        log_path = LOGS / f"{case}.log"
        script_path.write_text(make_script(case, mode, width))
        start = time.perf_counter()
        try:
            with log_path.open("w") as log:
                proc = subprocess.run(
                    [str(RUN), "yosys", "-s", str(script_path.relative_to(ROOT))],
                    cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                    check=False, timeout=180,
                )
            timed_out = False
        except subprocess.TimeoutExpired:
            proc = subprocess.CompletedProcess([], 124)
            timed_out = True
            with log_path.open("a") as log:
                log.write("\nTIMEOUT: 180 seconds; proof is inconclusive.\n")
        text = log_path.read_text(errors="replace")
        result = "INCONCLUSIVE_TIMEOUT" if timed_out else verdict(text, proc.returncode)
        sig = extract_signals(text)
        rows.append({
            "case": case, "width": width, "mode": mode, "expected": expected,
            "observed": result, "returncode": proc.returncode,
            "runtime_seconds": f"{time.perf_counter() - start:.6f}",
            "script": str(script_path.relative_to(ROOT)),
            "log": str(log_path.relative_to(ROOT)),
            "signals_from_log": repr(sig),
        })
    out = ROOT / "results" / "correctness_matrix.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    print(f"wrote {out}")
    for row in rows:
        print(row["case"], row["observed"], "rc", row["returncode"])


if __name__ == "__main__":
    main()
