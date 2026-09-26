#!/usr/bin/env python3
"""Wave 11 / E1: size of the covering space and of its SOUND reductions (no solver involved).

For a dump and a delay bound D:
  full           : all dumped candidates
  dominance      : a candidate is removed if another candidate of the same (node, phase, cut, leaf-phase pattern) has
                   area <= and every per-leaf pin delay <= (ties broken by index); removal cannot change the optimum
  timing(D)      : exact minimum arrival A*(n,p) over the space (DP, delay model load-independent) and an upper bound
                   R_ub(n,p) on any feasible required time (backward DP taking the MAX over consumers, D at outputs);
                   a candidate whose earliest possible arrival exceeds R_ub is infeasible in every solution
  eps-restricted : per (node, phase), candidates with area flow <= (1+eps) * best flow, plus the heuristic's choice
Prints one JSON line per D. usage: e1_space_stats.py DUMP.json D [D ...]"""
import json
import sys


def main():
    dump = json.load(open(sys.argv[1]))
    Ds = [float(x) for x in sys.argv[2:]]
    inv_d = float(dump["inv"]["delay"])
    pis = set(dump["pis"])
    nodes = {nd["i"]: nd for nd in dump["nodes"]}
    order = sorted(nodes)  # AIG node indices are topological
    full = [(n, c) for n in order for c in nodes[n]["cands"]]

    # dominance pruning
    keep_dom = set()
    for n in order:
        groups = {}
        for idx, c in enumerate(nodes[n]["cands"]):
            key = (c[0], c[1], tuple(c[2]), c[5])  # phase, cut, leaves, polarity pattern
            groups.setdefault(key, []).append((idx, c))
        for key, cs in groups.items():
            for idx, c in cs:
                dominated = any((o[4] <= c[4] + 1e-9 and all(od <= cd + 1e-9 for od, cd in zip(o[6], c[6]))
                                 and (o[4] < c[4] - 1e-9 or any(od < cd - 1e-9 for od, cd in zip(o[6], c[6])) or oi < idx))
                                for oi, o in cs if oi != idx)
                if not dominated:
                    keep_dom.add((n, idx))

    # exact minimum arrival over the space
    INF = float("inf")
    A = {}

    def arr(leaf, q):
        if leaf in pis:
            return 0.0 if q == 0 else inv_d
        if leaf in nodes:
            return A[(leaf, q)]
        return 0.0

    for n in order:
        best = [INF, INF]
        for c in nodes[n]["cands"]:
            p, pol = c[0], c[5]
            t = max(arr(l, (pol >> j) & 1) + c[6][j] for j, l in enumerate(c[2]))
            best[p] = min(best[p], t)
        best = [min(best[0], best[1] + inv_d), min(best[1], best[0] + inv_d)]
        A[(n, 0)], A[(n, 1)] = best
    out = {"nodes": len(nodes), "full": len(full), "dominance_kept": len(keep_dom)}
    d0 = max(A[(d, c)] if d in nodes else (0.0 if c == 0 else inv_d) for d, c in dump["pos"])
    out["min_delay_over_space"] = round(d0, 4)
    out["mapper_delay"] = round(float(dump["delay"]), 4)
    res = []
    for D in Ds:
        R = {}
        for d, c in dump["pos"]:
            if d in nodes:
                R[(d, c)] = max(R.get((d, c), -INF), D)
        # backward: consumers first (reverse topological), taking max over consumers
        for n in reversed(order):
            for p in (0, 1):
                r = R.get((n, p), -INF)
                if r == -INF:
                    continue
                # propagate through inverter option: (n,p) from (n,1-p)
                R[(n, 1 - p)] = max(R.get((n, 1 - p), -INF), r - inv_d)
            for c in nodes[n]["cands"]:
                p, pol = c[0], c[5]
                r = R.get((n, p), -INF)
                if r == -INF:
                    continue
                for j, l in enumerate(c[2]):
                    if l in nodes:
                        key = (l, (pol >> j) & 1)
                        R[key] = max(R.get(key, -INF), r - c[6][j])
        kept_t = 0
        kept_td = 0
        for n in order:
            for idx, c in enumerate(nodes[n]["cands"]):
                p, pol = c[0], c[5]
                if R.get((n, p), -INF) == -INF:
                    continue
                t = max(arr(l, (pol >> j) & 1) + c[6][j] for j, l in enumerate(c[2]))
                if t <= R[(n, p)] + 1e-6:
                    kept_t += 1
                    if (n, idx) in keep_dom:
                        kept_td += 1
        eps_sizes = {}
        for eps in (0.0, 0.05, 0.2, 1.0):
            k = 0
            for n in order:
                nd = nodes[n]
                for p in (0, 1):
                    cs = [c for c in nd["cands"] if c[0] == p]
                    if not cs:
                        continue
                    fmin = min(c[8] for c in cs)
                    b = nd["best"][p]
                    k += sum(1 for c in cs if c[8] <= (1 + eps) * fmin + 1e-9 or (b is not None and c[1] == b[0] and c[3] == b[1] and c[5] == b[2]))
            eps_sizes[str(eps)] = k
        res.append({"D": D, "timing_kept": kept_t, "timing_and_dominance_kept": kept_td, "eps_kept": eps_sizes})
    out["per_D"] = res
    print(json.dumps(out))


if __name__ == "__main__":
    main()
