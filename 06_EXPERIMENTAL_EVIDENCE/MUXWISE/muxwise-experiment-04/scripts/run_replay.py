#!/usr/bin/env python3
"""Independent Icarus replay of the exported candidates and reference RTL."""
from __future__ import annotations
import csv, re, subprocess, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT.parent / "muxwise-experiment-02" / "work" / "oss-cad-suite"
IVERILOG = SUITE / "bin" / "iverilog"; VVP = SUITE / "bin" / "vvp"
TB = ROOT / "replay" / "testbench" / "tb_fir4.v"
RTL = ROOT / "rtl" / "original" / "fir4.v"
OUT = ROOT / "replay" / "results"; LOG = ROOT / "logs" / "replay"
VECTORS = {4: (7, 12, 9, 6), 8: (234, 22, 100, 0)}

def signed(v: int, width: int) -> int:
    v &= (1 << width) - 1
    return v - (1 << width) if v & (1 << (width - 1)) else v

def reference(xs: tuple[int, ...], w: int) -> int:
    ow = w + 16; mask = (1 << ow) - 1
    coeffs = (3, -2, 5, 1); acc = 0
    for x, c in zip(xs, coeffs):
        acc = (acc + signed(x, w) * c) & mask
    return acc

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True); LOG.mkdir(parents=True, exist_ok=True)
    rows = []
    for w, xs in VECTORS.items():
        for config in ("normal", "arith_tree"):
            candidate = ROOT / "intermediate" / f"{config}_w{w}" / "post_abc.v"
            stem = f"{config}_w{w}"; exe = OUT / (stem + ".vvp"); log = LOG / (stem + ".log")
            cmd = [str(IVERILOG), "-g2012", "-s", "tb", "-o", str(exe),
                   "-Ptb.W="+str(w)] + [f"-Ptb.X{i}={x}" for i, x in enumerate(xs)] + [str(TB), str(RTL), str(candidate)]
            start = time.perf_counter()
            cp = subprocess.run(cmd, cwd=OUT, text=True, capture_output=True, check=False)
            if cp.returncode == 0:
                run = subprocess.run([str(VVP), str(exe)], cwd=OUT, text=True, capture_output=True, check=False)
                log.write_text(cp.stdout + cp.stderr + run.stdout + run.stderr); text = run.stdout + run.stderr
            else:
                log.write_text(cp.stdout + cp.stderr); run = cp; text = cp.stderr
            m = re.search(r"gold=0x([0-9a-fA-F]+) gate=0x([0-9a-fA-F]+)", text)
            result = "PASS" if m and m.group(1).lower() == m.group(2).lower() else ("FAIL" if m else "INCONCLUSIVE")
            rows.append({"width": w, "config": config, "vector": repr(xs),
                         "reference_hex": f"{reference(xs,w):0{(w+16+3)//4}x}",
                         "gold_hex": m.group(1) if m else "", "gate_hex": m.group(2) if m else "",
                         "replay_result": result, "returncode": run.returncode,
                         "runtime_seconds": f"{time.perf_counter()-start:.6f}",
                         "command": " ".join(cmd), "log": str(log.relative_to(ROOT))})
    out = ROOT / "results" / "replay.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(*[f"{r['config']} W{r['width']} {r['replay_result']} gold={r['gold_hex']} gate={r['gate_hex']}" for r in rows], sep="\n")

if __name__ == "__main__":
    main()
