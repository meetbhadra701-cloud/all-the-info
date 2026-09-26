#!/usr/bin/env python3
"""Wave 11 / E1 exploratory diagnostic (NOT a pre-registered test; reported as exploratory).

Where do the exact cover's decisions differ from map's own cover, and how far from a near-tie are they?
For one (bench, D) it rebuilds the CP-SAT variable indexing exactly as e1_cpsat.py allocates it (same Space, same
order), reads the solution from <prefix>.response.txt, and compares it with map's cover rebuilt from the dump.
For every (node, phase) that the exact cover implements with a cell whose (cut, gate, polarity) differs from map's
choice (or that map does not implement), it reports r = area flow of the chosen candidate / best area flow of that
(node, phase), from map's own final state (the quantity the eps restriction uses). r <= 1.05 means a near-tie.

usage: e1_diag.py DUMP.json GENLIB RESPONSE.txt [NOTIMING(0|1)]"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e1_model  # noqa: E402


def main():
    dump, genlib, resp = sys.argv[1], sys.argv[2], sys.argv[3]
    notiming = len(sys.argv) > 4 and sys.argv[4] == "1"
    sp = e1_model.Space(dump, genlib, -1)
    # variable allocation, identical to e1_cpsat.py (full space)
    nv = 0
    u, v, x, w = {}, {}, [], {}
    for n in sp.order:
        for p in (0, 1):
            u[(n, p)] = nv; nv += 1
            v[(n, p)] = nv; nv += 1
            if not notiming:
                nv += 1
    for i in sp.pis:
        w[i] = nv; nv += 1
    for _ in sp.cands:
        x.append(nv); nv += 1
    rt = open(resp).read()
    sol = [int(s) for s in re.findall(r"^solution:\s*(-?\d+)", rt, flags=re.M)]
    if len(sol) != nv:
        print(json.dumps({"error": "solution length %d != %d variables" % (len(sol), nv)}))
        return
    ex = {}
    for k in range(len(sp.cands)):
        if sol[x[k]]:
            ex[(sp.cands[k][0], sp.cands[k][1])] = ("cell", k)
    for key, var in v.items():
        if sol[var]:
            ex[key] = ("inv", None)
    heur, _ = sp.heuristic_cover()

    def sig(impl_entry):
        kind, k = impl_entry
        if kind == "inv":
            return ("inv",)
        return ("cell", sp.cut_of[k], sp.cands[k][3], sp.cands[k][5])

    best_flow = {}
    for k, c in enumerate(sp.cands):
        key = (c[0], c[1])
        best_flow[key] = min(best_flow.get(key, float("inf")), c[8])
    ratios, n_same, n_diff_cell, n_diff_inv, only_exact, only_heur = [], 0, 0, 0, 0, 0
    for key, e in ex.items():
        h = heur.get(key)
        if h is not None and sig(h) == sig(e):
            n_same += 1
            continue
        if h is None:
            only_exact += 1
        if e[0] == "inv":
            n_diff_inv += 1
            continue
        n_diff_cell += 1
        c = sp.cands[e[1]]
        bf = best_flow[key]
        ratios.append(c[8] / bf if bf > 0 else 1.0)
    only_heur = sum(1 for key in heur if key not in ex)
    ratios.sort()

    def frac(th):
        return round(sum(1 for r in ratios if r <= th + 1e-9) / len(ratios), 4) if ratios else None

    print(json.dumps({"dump": os.path.basename(dump), "response": os.path.basename(resp),
                      "exact_impl": len(ex), "heur_impl": len(heur), "same_decisions": n_same,
                      "differing_cell_decisions": n_diff_cell, "differing_inverter_decisions": n_diff_inv,
                      "implemented_only_by_exact": only_exact, "implemented_only_by_map": only_heur,
                      "flow_ratio_le_1.00": frac(1.0), "flow_ratio_le_1.05": frac(1.05), "flow_ratio_le_1.20": frac(1.2),
                      "flow_ratio_median": ratios[len(ratios) // 2] if ratios else None,
                      "flow_ratio_max": ratios[-1] if ratios else None}))


if __name__ == "__main__":
    main()
