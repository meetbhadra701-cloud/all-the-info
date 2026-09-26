#!/usr/bin/env python3
"""Reproduce synth's documented coarse/fine sequence and save boundaries."""
from __future__ import annotations
import csv, subprocess, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "scripts" / "run_yosys_current.sh"
SRC = ROOT / "rtl" / "original" / "fir4_gate.v"
BASE = ROOT / "intermediate"
YS = ROOT / "work" / "stage_isolation"
LOG = ROOT / "logs" / "stage_isolation"

def script(width: int, config: str) -> str:
    d = BASE / ("pre_arith_tree" if config == "normal" else "post_arith_tree")
    # Both configurations write the same named stage snapshots; per-run
    # directories avoid overwriting normal/tree artifacts.
    d = BASE / f"{config}_w{width}"
    d.mkdir(parents=True, exist_ok=True)
    def dump(tag: str) -> list[str]:
        return [
            f"write_rtlil { (d/(tag+'.rtlil')).relative_to(ROOT).as_posix()}",
            f"write_verilog -noattr { (d/(tag+'.v')).relative_to(ROOT).as_posix()}",
            "stat",
        ]
    lines = [
        f"read_verilog -sv {SRC.relative_to(ROOT).as_posix()}",
        f"chparam -set W {width} fir4_gate",
        "hierarchy -top fir4_gate",
        "proc", "check", "flatten", "opt_expr", "check", "opt_clean",
        "opt -nodffe -nosdff", "fsm", "opt", "wreduce", "peepopt",
        "opt_clean", "alumacc",
    ]
    lines += dump("pre_arith_tree")
    if config == "arith_tree":
        lines.append("arith_tree")
    lines += dump("post_arith_tree")
    lines += [
        "share", "opt", "memory -nomap", "opt_clean",
        "opt -fast -full", "memory_map", "opt -full", "techmap", "opt -fast",
    ]
    lines += dump("post_techmap")
    lines += ["abc", "opt -fast"]
    lines += dump("post_abc")
    return "\n".join(lines) + "\n"

def main() -> None:
    YS.mkdir(parents=True, exist_ok=True); LOG.mkdir(parents=True, exist_ok=True)
    rows = []
    for width in (4, 8):
        for config in ("normal", "arith_tree"):
            ys = YS / f"{config}_w{width}.ys"; log = LOG / f"{config}_w{width}.log"
            ys.write_text(script(width, config))
            start = time.perf_counter()
            with log.open("w") as f:
                p = subprocess.run([str(RUN), "yosys", "-s", str(ys.relative_to(ROOT))],
                                   cwd=ROOT, stdout=f, stderr=subprocess.STDOUT, check=False,
                                   timeout=180)
            rows.append({"width": width, "config": config, "returncode": p.returncode,
                         "runtime_seconds": f"{time.perf_counter()-start:.6f}",
                         "script": str(ys.relative_to(ROOT)), "log": str(log.relative_to(ROOT))})
    out = ROOT / "results" / "stage_isolation.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(*[f"{r['config']} W{r['width']} rc={r['returncode']}" for r in rows], sep="\n")

if __name__ == "__main__":
    main()
