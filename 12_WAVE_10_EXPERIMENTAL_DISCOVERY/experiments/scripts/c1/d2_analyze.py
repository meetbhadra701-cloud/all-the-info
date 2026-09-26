#!/usr/bin/env python3
"""C1 / D2 cause-isolation analysis (pre-registered predictions P1-P3 in c1_PREREGISTRATION.md).
Reads the D1 records for E:initial / E:gpt5_it29 and the D2 records for E:ab1, E:ab2, I:initial@ab1, I:initial@ab2.
Writes experiments/results/c1_d2_summary.json and prints the verdict."""
import glob
import json
import math
import os

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
RES = os.path.join(ROOT, "experiments", "results")
EPFL = "adder bar div hyp log2 max multiplier sin sqrt square arbiter cavlc ctrl dec i2c int2float mem_ctrl priority router voter".split()
IWLS = ("ac97_ctrl aes_core des_area des_perf DMA DSP ethernet iwls05_i2c iwls05_mem_ctrl pci_bridge32 RISC sasc "
        "simple_spi spi ss_pcm systemcaes systemcdes tv80 usb_funct usb_phy vga_lcd wb_conmax").split()


def load(d, b):
    fn = os.path.join(RES, d, b + ".jsonl")
    if not os.path.exists(fn):
        return {}
    return {json.loads(l)["tag"]: json.loads(l) for l in open(fn) if l.strip()}


def gm(xs):
    xs = [x for x in xs if x]
    return math.exp(sum(math.log(x) for x in xs) / len(xs)) if xs else None


def main():
    out = {"suites": {}, "validity": {"records": 0, "clean": 0}}
    for sname, benches in (("EPFL-20", EPFL), ("IWLS05-22", IWLS)):
        acc = {k: [] for k in ("D1/D0", "D2/D0", "Dg/D0", "A1/A0", "A2/A0", "Ag/A0", "A1/Ai1", "A2/Ai2", "Ag/Aig")}
        n = 0
        for b in benches:
            d1, d2 = load("c1_d1", b), load("c1_d2", b)
            need = [d1.get("E:initial"), d1.get("E:gpt5_it29"), d1.get("I:initial@gpt5_it29"), d2.get("E:ab1"), d2.get("E:ab2"),
                    d2.get("I:initial@ab1"), d2.get("I:initial@ab2")]
            for r in need[3:]:
                if r:
                    out["validity"]["records"] += 1
                    out["validity"]["clean"] += int(r.get("sim_verdict") == "SIM_AGREE" and r.get("cec_verdict") == "PASS")
            if not all(r and r.get("eval_area") for r in need):
                continue
            e0, eg, ig, a1, a2, i1, i2 = need
            n += 1
            acc["D1/D0"].append(a1["eval_delay"] / e0["eval_delay"]); acc["D2/D0"].append(a2["eval_delay"] / e0["eval_delay"])
            acc["Dg/D0"].append(eg["eval_delay"] / e0["eval_delay"])
            acc["A1/A0"].append(a1["eval_area"] / e0["eval_area"]); acc["A2/A0"].append(a2["eval_area"] / e0["eval_area"])
            acc["Ag/A0"].append(eg["eval_area"] / e0["eval_area"])
            if i1["eval_delay"] <= a1["eval_delay"] * 1.001:
                acc["A1/Ai1"].append(a1["eval_area"] / i1["eval_area"])
            if i2["eval_delay"] <= a2["eval_delay"] * 1.001:
                acc["A2/Ai2"].append(a2["eval_area"] / i2["eval_area"])
            if ig["eval_delay"] <= eg["eval_delay"] * 1.001:
                acc["Ag/Aig"].append(eg["eval_area"] / ig["eval_area"])
        s = {k: gm(v) for k, v in acc.items()}
        s.update({"n": n, "n_A1/Ai1": len(acc["A1/Ai1"]), "n_A2/Ai2": len(acc["A2/Ai2"])})
        out["suites"][sname] = s
    e = out["suites"]["EPFL-20"]
    p1 = e["D1/D0"] is not None and abs(e["D1/D0"] - 1.0) <= 0.01
    p2 = e["D2/D0"] is not None and e["D2/D0"] > 1.02 and e["A2/Ai2"] is not None and abs(e["A2/Ai2"] - 1.0) <= 0.015
    p3 = e["A1/Ai1"] is not None and e["A1/Ai1"] < 1.0
    out["predictions"] = {"P1": p1, "P2": p2, "P3": p3, "cause": "CONFIRMED" if (p1 and p2) else "ENTANGLED"}
    json.dump(out, open(os.path.join(RES, "c1_d2_summary.json"), "w"), indent=1)
    for sname, s in out["suites"].items():
        print("== %s (n=%d)" % (sname, s["n"]))
        for k in ("Dg/D0", "D1/D0", "D2/D0", "Ag/A0", "A1/A0", "A2/A0", "Ag/Aig", "A1/Ai1", "A2/Ai2"):
            print("   %-7s %s" % (k, "n/a" if s[k] is None else "%.4f" % s[k]))
    print("validity:", out["validity"]); print("predictions:", out["predictions"])


if __name__ == "__main__":
    main()
