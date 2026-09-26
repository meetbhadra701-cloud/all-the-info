#!/usr/bin/env python3
"""Collect only measured values from Yosys Liberty-mapped logs."""
from __future__ import annotations
import csv, re, sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
out = root / "results" / "standard_cell_mapping.csv"
rows = []
pat = re.compile(r"^(fir4|mixed|add_chain)_w(\d+)_(normal|arith_tree)\.log$")
area_re = re.compile(r"^\s*Chip area for module .*: ([0-9.eE+-]+)$")
cell_re = re.compile(r"^\s*([0-9]+)\s+([0-9.eE+-]+) cells$")
runtime_re = re.compile(r"MUXWISE_WALL_SECONDS=([0-9.]+)")
cell_line_re = re.compile(r"^ +([0-9]+) +([^ ]+) +([^ ]+)")
for log in sorted((root / "logs" / "mapping").glob("*.log")):
    m = pat.match(log.name)
    if not m:
        continue
    design, width, config = m.groups()
    text = log.read_text(errors="replace").splitlines()
    area = cells = runtime = ""
    types = []
    in_cells = False
    for line in text:
        ma = area_re.search(line)
        if ma: area = ma.group(1)
        mc = cell_re.search(line)
        if mc: cells = mc.group(1)
        mr = runtime_re.search(line)
        if mr: runtime = mr.group(1)
        if re.match(r"^\s*[0-9]+\s+[0-9.eE+-]+ cells$", line):
            in_cells = True
            continue
        if in_cells:
            mt = cell_line_re.match(line)
            if mt:
                types.append(f"{mt.group(3)}={mt.group(1)}")
            elif line.strip() and not line.lstrip().startswith("Chip area"):
                in_cells = False
    rows.append({
        "design": design, "width": width, "config": config,
        "yosys_version": "Yosys 0.69+77 (9ff27d29c-dirty)",
        "abc_version": "Yosys-embedded yosys-abc from OSS CAD Suite",
        "liberty": "NangateOpenCellLibrary_typical.lib",
        "cell_area": area, "combinational_cell_area": area,
        "cell_count": cells, "cell_types": ";".join(types),
        "synthesis_runtime_seconds": runtime,
        "formal_result": "SEE results/formal_comparison.csv", "netlist": str(root / "netlists" / log.name.replace('.log','.v')),
        "log": str(log), "status": "MEASURED" if area and cells else "FAILED_OR_UNPARSED",
    })
fields = list(rows[0]) if rows else ["design","width","config","status"]
with out.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader(); w.writerows(rows)
print(f"wrote {out} ({len(rows)} rows)")
