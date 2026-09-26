#!/usr/bin/env python3
"""C1 / D1 analysis. It follows experiments/results/c1_PREREGISTRATION.md.

Reads experiments/results/c1_d1/*.jsonl and writes:
  experiments/results/c1_d1_all.csv        one flattened row per (bench, config)
  experiments/results/c1_d1_isodelay.csv   one row per (bench, evolved variant), with the pre-registered ratios
  experiments/results/c1_d1_summary.json   suite geomeans, win counts, equivalence tallies, verdict inputs
It also prints a human-readable summary.

All areas and delays come from the independent evaluator (eval_area / eval_delay), never
from the mapper's self-report.
"""
import csv
import glob
import json
import math
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
RES = os.path.join(ROOT, "experiments", "results")
EPFL = "adder bar div hyp log2 max multiplier sin sqrt square arbiter cavlc ctrl dec i2c int2float mem_ctrl priority router voter".split()
IWLS = ("ac97_ctrl aes_core des_area des_perf DMA DSP ethernet iwls05_i2c iwls05_mem_ctrl pci_bridge32 RISC sasc "
        "simple_spi spi ss_pcm systemcaes systemcdes tv80 usb_funct usb_phy vga_lcd wb_conmax").split()
ISCAS = "c17 c432 c499 c880 c1355 c1908 c2670 c3540 c5315 c6288 c7552".split()
SUITES = {"EPFL-20": EPFL, "IWLS05-22": IWLS, "ISCAS85-11": ISCAS}
EVOLVED = ["gpt5_it29", "deepseek_it24", "qwen_it20"]
TOL = 1.001  # delay tolerance when deciding whether a baseline met the evolved delay


def gmean(xs):
    xs = [x for x in xs if x is not None and x > 0]
    return math.exp(sum(math.log(x) for x in xs) / len(xs)) if xs else None


def load():
    data = {}
    for fn in glob.glob(os.path.join(RES, "c1_d1", "*.jsonl")):
        b = os.path.basename(fn)[:-6]
        recs = {}
        for line in open(fn, encoding="utf-8"):
            if line.strip():
                d = json.loads(line)
                recs[d["tag"]] = d  # a later line with the same tag supersedes earlier ones
        data[b] = recs
    return data


def ok(r):
    """A netlist counts only if it was evaluated and not refuted. A CEC NEQ or a simulation mismatch refutes it."""
    return (r is not None and r.get("eval_area") is not None and r.get("sim_verdict") == "SIM_AGREE"
            and r.get("cec_verdict") != "NEQ")


def is_baseline(tag):
    return not tag.startswith("E:") or tag == "E:initial"


def main():
    data = load()
    # 1. flattened table
    cols = ["bench", "tag", "tool", "mode", "required_param", "relax_param", "tool_area", "tool_delay", "eval_area",
            "eval_delay", "instances", "gates", "depth", "sim_verdict", "cec_verdict", "cec_wall", "map_wall", "eval_wall",
            "mapping_error", "map_error", "eval_error"]
    with open(os.path.join(RES, "c1_d1_all.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for b in sorted(data):
            for t in sorted(data[b]):
                r = data[b][t]
                w.writerow([r.get(c, "") if not isinstance(r.get(c), (dict, list)) else json.dumps(r.get(c)) for c in cols])

    # 2. iso-delay comparison
    rows = []
    for b in sorted(data):
        recs = data[b]
        for v in EVOLVED:
            e = recs.get("E:" + v)
            if not ok(e):
                rows.append({"bench": b, "variant": v, "status": "evolved_missing_or_refuted"})
                continue
            Ae, De = e["eval_area"], e["eval_delay"]
            row = {"bench": b, "variant": v, "A_e": Ae, "D_e": De, "status": "ok",
                   "cec_e": e.get("cec_verdict"), "sim_e": e.get("sim_verdict")}
            best = None
            for name, tag in (("init", "I:initial@" + v), ("emap", "I:emap@" + v), ("nfp", "I:nfp@" + v)):
                r = recs.get(tag)
                if not ok(r):
                    row["A_" + name] = None; row["met_" + name] = None; row["r_" + name] = None
                    continue
                met = r["eval_delay"] <= De * TOL
                row["A_" + name] = r["eval_area"]; row["D_" + name] = r["eval_delay"]; row["met_" + name] = met
                row["r_" + name] = Ae / r["eval_area"] if met else None
                if met and (best is None or r["eval_area"] < best[1]):
                    best = (name, r["eval_area"])
            row["best_name"] = best[0] if best else None
            row["r_best"] = Ae / best[1] if best else None
            # secondary, post hoc: minimum area over ALL baseline configs whose delay met De
            front = [(t, r["eval_area"]) for t, r in recs.items() if is_baseline(t) and ok(r) and r["eval_delay"] <= De * TOL]
            if front:
                t, a = min(front, key=lambda x: x[1])
                row["front_tag"] = t; row["r_front"] = Ae / a
            else:
                row["front_tag"] = None; row["r_front"] = None
            # paper-style reproduction ratios against ABC &nf default and mockturtle initial
            for name, tag in (("abc", "B:nf"), ("mt", "E:initial")):
                r = recs.get(tag)
                if ok(r):
                    row["area_vs_" + name] = Ae / r["eval_area"]; row["delay_vs_" + name] = De / r["eval_delay"]
            # exact multiplicative decomposition of the headline area ratio:
            #   A_e/A_base(D0) = [A_base(De)/A_base(D0)] (relaxation) x [A_e/A_base(De)] (operator)
            for name, t0, tr in (("mt", "E:initial", "I:initial@" + v), ("abc", "B:nf", "I:nfp@" + v)):
                r0, rr = recs.get(t0), recs.get(tr)
                if ok(r0) and ok(rr) and rr["eval_delay"] <= De * TOL:
                    row["dec_%s_total" % name] = Ae / r0["eval_area"]
                    row["dec_%s_relax" % name] = rr["eval_area"] / r0["eval_area"]
                    row["dec_%s_oper" % name] = Ae / rr["eval_area"]
            rows.append(row)
    keys = ["bench", "variant", "status", "A_e", "D_e", "dec_mt_total", "dec_mt_relax", "dec_mt_oper", "dec_abc_total", "dec_abc_relax", "dec_abc_oper", "A_init", "D_init", "met_init", "r_init", "A_emap", "D_emap",
            "met_emap", "r_emap", "A_nfp", "D_nfp", "met_nfp", "r_nfp", "best_name", "r_best", "front_tag", "r_front",
            "area_vs_abc", "delay_vs_abc", "area_vs_mt", "delay_vs_mt", "cec_e", "sim_e"]
    with open(os.path.join(RES, "c1_d1_isodelay.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # 3. summary per suite and variant
    summary = {"suites": {}, "equivalence": {}}
    for s, benches in SUITES.items():
        present = [b for b in benches if b in data]
        summary["suites"][s] = {"benches_present": len(present), "benches_expected": len(benches), "variants": {}}
        for v in EVOLVED:
            rs = [r for r in rows if r["bench"] in present and r["variant"] == v and r.get("status") == "ok"]
            d = {"n": len(rs)}
            for k in ("r_init", "r_emap", "r_nfp", "r_best", "r_front", "area_vs_abc", "delay_vs_abc", "area_vs_mt", "delay_vs_mt",
                      "dec_mt_total", "dec_mt_relax", "dec_mt_oper", "dec_abc_total", "dec_abc_relax", "dec_abc_oper"):
                vals = [r.get(k) for r in rs if r.get(k) is not None]
                d["gmean_" + k] = gmean(vals)
                d["amean_" + k] = sum(vals) / len(vals) if vals else None
                d["n_" + k] = len(vals)
                d["wins_" + k] = sum(1 for x in vals if x < 1.0)
            d["baseline_missed_delay"] = sum(1 for r in rs for n in ("init", "emap", "nfp") if r.get("met_" + n) is False)
            summary["suites"][s]["variants"][v] = d
    tally = {}
    for b, recs in data.items():
        for t, r in recs.items():
            fam = t.split(":")[0] + ":" + t.split(":")[1].split("@")[0] if ":" in t else t
            k = tally.setdefault(fam, {})
            key = "%s|%s" % (r.get("sim_verdict"), r.get("cec_verdict"))
            k[key] = k.get(key, 0) + 1
    summary["equivalence"] = tally
    with open(os.path.join(RES, "c1_d1_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1)

    # 4. print
    for s, sd in summary["suites"].items():
        print("== %s (%d/%d benches)" % (s, sd["benches_present"], sd["benches_expected"]))
        for v, d in sd["variants"].items():
            def fm(x):
                return "  n/a " if x is None else "%.4f" % x
            print("  %-14s n=%2d | vs init@De %s (%d/%d<1) | vs emap@De %s (%d/%d) | vs nfp@De %s (%d/%d) | vs BEST %s (%d/%d) | FRONT %s (%d/%d) | area/ABC %s delay/ABC %s | area/mt %s delay/mt %s | missed %d" % (
                v, d["n"], fm(d["gmean_r_init"]), d["wins_r_init"], d["n_r_init"], fm(d["gmean_r_emap"]), d["wins_r_emap"], d["n_r_emap"],
                fm(d["gmean_r_nfp"]), d["wins_r_nfp"], d["n_r_nfp"], fm(d["gmean_r_best"]), d["wins_r_best"], d["n_r_best"],
                fm(d["gmean_r_front"]), d["wins_r_front"], d["n_r_front"], fm(d["amean_area_vs_abc"]), fm(d["amean_delay_vs_abc"]),
                fm(d["amean_area_vs_mt"]), fm(d["amean_delay_vs_mt"]), d["baseline_missed_delay"]))
    print("== decomposition (geomeans): total = relax x oper  [vs mockturtle initial | vs ABC &nf]")
    for s, sd in summary["suites"].items():
        for v, d in sd["variants"].items():
            g = lambda k: ("%.4f" % d["gmean_" + k]) if d.get("gmean_" + k) else " n/a "
            print("  %-10s %-14s mt: %s = %s x %s (n=%d) | abc: %s = %s x %s (n=%d)" % (
                s, v, g("dec_mt_total"), g("dec_mt_relax"), g("dec_mt_oper"), d["n_dec_mt_total"],
                g("dec_abc_total"), g("dec_abc_relax"), g("dec_abc_oper"), d["n_dec_abc_total"]))
    print("== equivalence tallies (sim|cec) by config family")
    for fam in sorted(tally):
        print("  %-14s %s" % (fam, tally[fam]))


if __name__ == "__main__":
    main()
