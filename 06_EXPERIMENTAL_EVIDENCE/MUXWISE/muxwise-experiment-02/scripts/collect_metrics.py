#!/usr/bin/env python3
"""Extract structural/resource metrics from current-Yosys JSON outputs."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def get_module(data: dict, top: str):
    modules = data.get("modules", {})
    if top in modules: return top, modules[top]
    for name, m in modules.items():
        if m.get("attributes", {}).get("top") in (1, "1", True): return name, m
    cand = [(n, m) for n, m in modules.items() if top in n]
    if len(cand) == 1: return cand[0]
    if len(modules) == 1: return next(iter(modules.items()))
    raise ValueError((top, list(modules)))


def signature(m: dict) -> str:
    edges = defaultdict(list); labels = {}
    def bk(bit): return f"b:{bit}"
    for port, info in m.get("ports", {}).items():
        for i, bit in enumerate(info.get("bits", [])):
            b = bk(bit); labels.setdefault(b, "net")
            edges[b].append((f"port:{info.get('direction')}:{port}:{i}", b))
    for name, cell in m.get("cells", {}).items():
        c = f"c:{name}"; params = tuple(sorted((str(k), str(v)) for k, v in cell.get("parameters", {}).items()))
        labels[c] = f"cell:{cell.get('type')}:{params}"
        for port, conn in sorted(cell.get("connections", {}).items()):
            for i, bit in enumerate(conn):
                b = bk(bit); labels.setdefault(b, "net")
                lab = f"cell:{port}:{i}"; edges[c].append((lab, b)); edges[b].append((lab, c))
    for k in labels: labels[k] += "|" + "|".join(sorted(x for x, _ in edges[k]))
    for _ in range(12):
        labels = {k: hashlib.sha256((v + repr(sorted((lab, labels.get(other, "missing")) for lab, other in edges[k]))).encode()).hexdigest() for k, v in labels.items()}
    return hashlib.sha256(repr(sorted(labels.values())).encode()).hexdigest()


def one(r):
    if not r["json"]:
        return {**r, "status":"MISSING", "module":"", "cells":"", "muxes":"", "arith":"", "cell_types":"", "signature":""}
    data=json.loads((ROOT/r["json"]).read_text()); mn,m=get_module(data,r["top"])
    types=Counter(c.get("type","") for c in m.get("cells",{}).values())
    mux=sum(n for t,n in types.items() if t in {"$mux","$pmux","$_MUX_","$_NMUX_"})
    toks=("$add","$sub","$mul","$div","$mod","$lt","$le","$eq","$ne","$ge","$gt","$shl","$shr","$sshl","$sshr","$shift")
    arith=sum(n for t,n in types.items() if any(t.startswith(x) for x in toks))
    return {**r,"status":"OK","module":mn,"cells":len(m.get("cells",{})),"muxes":mux,"arith":arith,"cell_types":";".join(f"{t}:{types[t]}" for t in sorted(types)),"signature":signature(m)}


def main():
    rows=[one(r) for r in csv.DictReader((ROOT/"results/run_manifest.csv").open())]
    fields=["case","top","width","flow","returncode","runtime_seconds","script","log","json","rtlil","verilog","status","module","cells","muxes","arith","cell_types","signature"]
    with (ROOT/"results/all_experiments.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    # Preserve only rows that passed execution and were structurally measurable.
    with (ROOT/"results/surviving_findings.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
    print(json.dumps({"rows":len(rows),"failures":sum(r["returncode"]!="0" for r in rows),"metrics":sum(r["status"]=="OK" for r in rows)},indent=2))


if __name__ == "__main__": main()

