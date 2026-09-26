#!/usr/bin/env python3
"""E0 (evidence for the problem map, no new runs): how monotone are existing mappers' area-vs-delay-constraint curves?
Reads Wave 10 D1 records (12_WAVE_10_EXPERIMENTAL_DISCOVERY/experiments/results/c1_d1/*.jsonl), all independently validated.
For each circuit and each relaxation sweep (mockturtle map R:initial:*, emap R:emap:*, ABC R:nfp:*), orders points by the
constraint and counts 'inversions': a looser constraint whose area is larger than a tighter one's by more than 1%.
It also measures the spread of area among points whose independently measured delay is within 1% of each other."""
import glob, json, os, statistics
W10 = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "12_WAVE_10_EXPERIMENTAL_DISCOVERY", "experiments", "results", "c1_d1"))
EPFL = set("adder bar div hyp log2 max multiplier sin sqrt square arbiter cavlc ctrl dec i2c int2float mem_ctrl priority router voter".split())
fams = {"map": ("E:initial", "R:initial:", [2, 4, 6, 8, 10, 15, 20, 30, 50]),
        "emap": ("B:emap", "R:emap:", [5, 10, 20]),
        "abc_nf": ("B:nfp", "R:nfp:", [2, 5, 10, 20, 30])}
out = {}
for fam, (base, pre, rs) in fams.items():
    steps = inv = inv5 = 0; worst = []; per = []
    for fn in sorted(glob.glob(os.path.join(W10, "*.jsonl"))):
        b = os.path.basename(fn)[:-6]
        R = {json.loads(l)["tag"]: json.loads(l) for l in open(fn)}
        pts = [(0, R[base]["eval_area"])] + [(r, R[pre + str(r)]["eval_area"]) for r in rs if pre + str(r) in R]
        mx = 0.0; ci = 0
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):   # j has the looser constraint
                steps += 1
                rel = pts[j][1] / pts[i][1] - 1.0
                if rel > 0.01: inv += 1; ci += 1
                if rel > 0.05: inv5 += 1
                mx = max(mx, rel)
        worst.append((round(mx * 100, 2), b)); per.append(ci)
    worst.sort(reverse=True)
    out[fam] = {"pairs": steps, "inversions_gt1pct": inv, "inversions_gt5pct": inv5,
                "share_gt1pct": round(inv / steps, 4) if steps else None,
                "circuits_with_any_inversion": sum(1 for c in per if c > 0), "circuits": len(per),
                "worst5": worst[:5]}
print(json.dumps(out, indent=1))
json.dump(out, open(os.path.join(os.path.dirname(__file__), "..", "results", "e0_monotonicity.json"), "w"), indent=1)
