#!/usr/bin/env python3
"""Extract cell/resource metrics and structural signatures from Yosys JSON."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "results" / "run_manifest.csv"


def module_for(data: dict, top: str) -> tuple[str, dict]:
    modules = data.get("modules", {})
    if top in modules:
        return top, modules[top]
    for name, module in modules.items():
        attrs = module.get("attributes", {})
        if attrs.get("top") in (1, "1", True):
            return name, module
    if len(modules) == 1:
        name, module = next(iter(modules.items()))
        return name, module
    # Parameterized Yosys names sometimes contain the source top name.
    candidates = [(name, module) for name, module in modules.items() if top in name]
    if len(candidates) == 1:
        return candidates[0]
    raise ValueError(f"cannot identify top {top}; modules={list(modules)}")


def node_signature(module: dict) -> str:
    """A name-independent WL-style signature of the module connectivity."""
    nodes: dict[str, tuple[str, list[tuple[str, str]]]] = {}
    bit_nodes: dict[str, str] = {}
    edges: dict[str, list[tuple[str, str]]] = defaultdict(list)

    def bit_key(bit) -> str:
        return f"b:{bit}"

    for port, info in module.get("ports", {}).items():
        direction = info.get("direction", "")
        for index, bit in enumerate(info.get("bits", [])):
            key = bit_key(bit)
            bit_nodes.setdefault(key, key)
            label = f"port:{direction}:{port}:{index}"
            edges[key].append((label, key))

    for cell_name, cell in module.get("cells", {}).items():
        ckey = f"c:{cell_name}"
        params = tuple(sorted((str(k), str(v)) for k, v in cell.get("parameters", {}).items()))
        nodes[ckey] = (f"cell:{cell.get('type')}:{params}", [])
        for port, conn in sorted(cell.get("connections", {}).items()):
            for index, bit in enumerate(conn):
                bkey = bit_key(bit)
                bit_nodes.setdefault(bkey, bkey)
                label = f"cell:{port}:{index}"
                edges[ckey].append((label, bkey))
                edges[bkey].append((label, ckey))

    labels: dict[str, str] = {}
    for key in set(bit_nodes) | set(nodes):
        if key in nodes:
            labels[key] = nodes[key][0]
        else:
            labels[key] = "net"
        if key in edges:
            labels[key] += "|" + "|".join(sorted(label for label, _ in edges[key]))

    for _ in range(12):
        updated = {}
        for key in labels:
            neighbors = []
            for edge_label, other in edges.get(key, []):
                neighbors.append((edge_label, labels.get(other, "missing")))
            raw = labels[key] + "|" + repr(sorted(neighbors))
            updated[key] = hashlib.sha256(raw.encode()).hexdigest()
        labels = updated
    digest = hashlib.sha256(repr(sorted(labels.values())).encode()).hexdigest()
    return digest


def metrics(record: dict) -> dict:
    path = ROOT / record["json"]
    if not path.exists():
        return {**record, "module": "", "total_cells": "", "muxes": "", "arithmetic_operators": "", "cell_types": "", "structure_signature": "", "metric_status": "MISSING_JSON"}
    data = json.loads(path.read_text())
    module_name, module = module_for(data, record["top"])
    cells = module.get("cells", {})
    types = Counter(cell.get("type", "") for cell in cells.values())
    mux_types = {"$mux", "$pmux", "$_MUX_", "$_NMUX_"}
    arith_tokens = ("$add", "$sub", "$mul", "$div", "$mod", "$lt", "$le", "$eq", "$ne", "$ge", "$gt", "$shl", "$shr", "$sshl", "$sshr", "$shift")
    muxes = sum(n for t, n in types.items() if t in mux_types)
    arithmetic = sum(n for t, n in types.items() if any(t.startswith(token) for token in arith_tokens))
    return {
        **record,
        "module": module_name,
        "total_cells": len(cells),
        "muxes": muxes,
        "arithmetic_operators": arithmetic,
        "cell_types": ";".join(f"{t}:{types[t]}" for t in sorted(types)),
        "structure_signature": node_signature(module),
        "metric_status": "OK",
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    fields = [
        "case", "top", "width", "flow", "returncode", "runtime_seconds", "script", "log", "json", "rtlil",
        "module", "total_cells", "muxes", "arithmetic_operators", "cell_types", "structure_signature", "metric_status",
    ]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    records = list(csv.DictReader(MANIFEST.open()))
    rows = [metrics(r) for r in records]
    baseline = [r for r in rows if r["case"] == "baseline"]
    multi = [r for r in rows if r["case"] == "multi_operator"]
    write_csv(ROOT / "results" / "all_metrics.csv", rows)
    write_csv(ROOT / "results" / "baseline.csv", baseline)
    write_csv(ROOT / "results" / "multi_operator.csv", multi)

    width_rows = []
    for r in baseline:
        if r["top"] == "unshared":
            peer = next((p for p in baseline if p["top"] == "shared" and p["width"] == r["width"] and p["flow"] == r["flow"]), None)
            width_rows.append({
                "width": r["width"], "flow": r["flow"],
                "unshared_total_cells": r["total_cells"], "shared_total_cells": peer["total_cells"] if peer else "",
                "unshared_muxes": r["muxes"], "shared_muxes": peer["muxes"] if peer else "",
                "unshared_arithmetic_operators": r["arithmetic_operators"], "shared_arithmetic_operators": peer["arithmetic_operators"] if peer else "",
                "same_structure": str(bool(peer and r["structure_signature"] == peer["structure_signature"])).upper(),
                "unshared_status": r["metric_status"], "shared_status": peer["metric_status"] if peer else "MISSING_PEER",
            })
    with (ROOT / "results" / "width_sweep.csv").open("w", newline="") as f:
        fields = list(width_rows[0]) if width_rows else []
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(width_rows)

    # Stage convergence summary used directly by the report.
    convergence = []
    for width in sorted({r["width"] for r in baseline}, key=int):
        for flow in sorted({r["flow"] for r in baseline}):
            u = next((r for r in baseline if r["top"] == "unshared" and r["width"] == width and r["flow"] == flow), None)
            s = next((r for r in baseline if r["top"] == "shared" and r["width"] == width and r["flow"] == flow), None)
            convergence.append({"width": width, "flow": flow, "same_structure": bool(u and s and u["structure_signature"] == s["structure_signature"]), "unshared_cell_types": u["cell_types"] if u else "", "shared_cell_types": s["cell_types"] if s else ""})
    (ROOT / "results" / "convergence.json").write_text(json.dumps(convergence, indent=2) + "\n")
    print(json.dumps({"metrics": len(rows), "baseline": len(baseline), "multi_operator": len(multi), "convergence": str(ROOT / 'results' / 'convergence.json')}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

