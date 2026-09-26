#!/usr/bin/env python3
"""Builds the R1/R2 reproduction tables (markdown) from the saved result files.

R1: experiments/results/c1_r1_iscas_orig.jsonl, compared against the shipped reward.json raw_result.
R2: experiments/results/c1_r2_epfl_orig_<variant>.jsonl, compared against the paper's Table 2 as
    transcribed by the fetch summarizer, stored in experiments/inputs/c1/paper_table2_transcribed.csv.
Output: experiments/results/c1_r1r2_tables.md
"""
import csv
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
RES = os.path.join(ROOT, "experiments", "results")
ME = os.path.join(ROOT, "third_party", "MappingEvolve", "output")
RUNS = {"gpt5_it29": ("proactive_evolve_openevolve_gpt-5-2025-08-07_20251116_134740", 29),
        "deepseek_it24": ("proactive_evolve_openevolve_deepseek-v3-241226_20251116_014457", 24),
        "qwen_it20": ("proactive_evolve_openevolve_qwen3-max_20251116_093335", 20)}
EPFL = "adder bar div hyp log2 max multiplier sin sqrt square arbiter cavlc ctrl dec i2c int2float mem_ctrl priority router voter".split()


def main():
    out = []
    out.append("## R1: ISCAS85 fitness reproduction (unmodified main.cpp, default mode)\n")
    out.append("Values are the sums over 11 ISCAS85 circuits of (baseline − result)/baseline against main.cpp's hard-coded baselines. Two repetitions were run and are identical.\n")
    out.append("| variant | area (ours) | area (reward.json) | delay (ours) | delay (reward.json) | nec (ours) | match |")
    out.append("|---|---|---|---|---|---|---|")
    r1 = [json.loads(l) for l in open(os.path.join(RES, "c1_r1_iscas_orig.jsonl"))]
    for v in ["initial", "gpt5_it29", "deepseek_it24", "qwen_it20"]:
        rs = [r for r in r1 if r["variant"] == v]
        a = {round(r["result"]["area"], 6) for r in rs}; d = {round(r["result"]["delay"], 6) for r in rs}
        nec = {r["result"]["nec"] for r in rs}
        if v == "initial":
            ra, rd = 0.0, 0.0
        else:
            run, it = RUNS[v]
            rw = json.load(open(os.path.join(ME, run, "iter_%d" % it, "reward.json")))["raw_result"]
            ra, rd = rw["area_score"], rw["delay_score"]
        match = (len(a) == 1 and len(d) == 1 and abs(list(a)[0] - ra) < 1e-5 and abs(list(d)[0] - rd) < 1e-5)
        out.append("| %s | %s | %.6f | %s | %.6f | %s | %s |" % (v, "/".join("%.6f" % x for x in a), ra, "/".join("%.6f" % x for x in d), rd,
                                                               "/".join(str(x) for x in nec), "EXACT" if match else "DIFF"))
    out.append("")
    paper = {}
    pt = os.path.join(ROOT, "experiments", "inputs", "c1", "paper_table2_transcribed.csv")
    for row in csv.DictReader(open(pt, encoding="utf-8")):
        paper[row["benchmark"]] = row
    out.append("## R2: EPFL reproduction (unmodified main.cpp, single-file mode) against the paper's Table 2\n")
    out.append("The paper's values were transcribed by the WebFetch summarizer from arxiv.org/html/2604.26591v1 (UNVERIFIED digits). A match is counted when |ours − paper| ≤ 0.011 for both area and delay. `nec` is MappingEvolve's own `cec -n` failure flag.\n")
    out.append("| bench | mockturtle (initial) ours | paper | GPT-5 it29 ours | paper | DeepSeek it24 ours | paper (DeepSeek col.) | Qwen it20 ours | nec (all 4) |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    r2 = {}
    for v in ["initial", "gpt5_it29", "deepseek_it24", "qwen_it20"]:
        for l in open(os.path.join(RES, "c1_r2_epfl_orig_%s.jsonl" % v)):
            d = json.loads(l); r2[(v, d["bench"])] = d["result"]
    counts = {"initial": 0, "gpt5_it29": 0, "deepseek_it24": 0}
    necs = 0
    for b in EPFL:
        p = paper.get(b, {})
        cells = []
        for v, pa, pd in (("initial", "mockturtle_area", "mockturtle_delay"), ("gpt5_it29", "MappingEvolve_GPT5_area", "MappingEvolve_GPT5_delay"),
                          ("deepseek_it24", "MappingEvolve_DeepSeek_area", "MappingEvolve_DeepSeek_delay")):
            r = r2.get((v, b))
            ours = "%.2f / %.2f" % (r["area"], r["delay"]) if r else "n/a"
            pap = "%s / %s" % (p.get(pa, "?"), p.get(pd, "?"))
            ok = r and p and abs(r["area"] - float(p[pa])) <= 0.011 and abs(r["delay"] - float(p[pd])) <= 0.011
            counts[v] += 1 if ok else 0
            cells += [ours + (" ✓" if ok else ""), pap]
        rq = r2.get(("qwen_it20", b))
        nec = sum(int(r2[(v, b)]["nec"]) for v in ["initial", "gpt5_it29", "deepseek_it24", "qwen_it20"] if r2.get((v, b)))
        necs += nec
        out.append("| %s | %s | %s | %s | %s | %s | %s | %s | %d |" % (b, cells[0], cells[1], cells[2], cells[3], cells[4], cells[5],
                                                                    "%.2f / %.2f" % (rq["area"], rq["delay"]) if rq else "n/a", nec))
    out.append("")
    out.append("Matches: mockturtle %d/20, GPT-5 it29 %d/20, DeepSeek it24 %d/20. Total MappingEvolve-cec failures over the 80 runs: %d.\n"
               % (counts["initial"], counts["gpt5_it29"], counts["deepseek_it24"], necs))
    open(os.path.join(RES, "c1_r1r2_tables.md"), "w", encoding="utf-8").write("\n".join(out))
    print("\n".join(out[-3:]))


if __name__ == "__main__":
    main()
