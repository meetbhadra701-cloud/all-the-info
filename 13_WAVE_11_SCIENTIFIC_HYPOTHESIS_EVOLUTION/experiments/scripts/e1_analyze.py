#!/usr/bin/env python3
"""Wave 11 / E1 analysis. Reads experiments/results/e1/<bench>.jsonl (+ the dumps) and applies the pre-registered
verdict logic. Written before any Phase A (real-budget) result was read; aggregation rules that the registration left
implicit are fixed here and in the deviation log (entry 11):

  validated netlist : evaluator sim SIM_AGREE and ABC cec PASS; it counts at D only if its evaluated delay <= D + 0.01
  A_map(D)          : validated area of map at required_time D (map:D0 uses required 0, i.e. its own best delay)
  UB(D)             : smallest validated area among the exact-model solutions at D (full and eps models; an eps model's
                      space is a subset of the full space, so its solutions are valid full-space upper bounds)
  LB(D)             : max of CP-SAT's proven bound for the full timed model at D and, where the D1 dump's candidate set
                      equals the D0 dump's, the no-timing bound (lb:D0). Solver claims, not independently checked.
  pair verdict      : PROVEN_BELOW_2 if (A_map - LB)/A_map < 2%; DEMONSTRATED if (A_map - UB)/A_map >= 2%; else UNRESOLVED
  circuit verdict   : DEMONSTRATED if demonstrated at any D; PROVEN_BELOW_2 if proven at every D; else UNRESOLVED
  A1 kill           : PROVEN_BELOW_2 on the majority of circuits with a verdict and DEMONSTRATED on none
  A1 advance part   : DEMONSTRATED on at least half of the circuits with a verdict
  relevance         : at each demonstrated pair, UB(D) < min validated area among emap, &nf -p, &nf -p -a at D
                      (only baselines that meet D count); relevance kill if not below on most demonstrated circuits
                      (a circuit counts as "below" if UB < best baseline at any demonstrated D; kill if "not below" on more than half)
  A2 capture        : at demonstrated pairs, (A_map - A_eps)/(A_map - UB_full) with A_eps the validated eps=0.05 solution;
                      an upper bound on the capture uses the eps model's proven bound. A2 kill if capture is proven < 50%
                      (bound-based) on the majority of demonstrated pairs that have an eps=0.05 run
  A3 size           : eps=0.05 candidates kept / full candidates; A3 kill if > 50% on the majority of demonstrated pairs
Pair-level counts are reported next to circuit-level ones; if they disagree the decision takes the conservative reading.
usage: e1_analyze.py [RESULTS_DIR] [OUTPUTS_DIR]"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RES = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "results", "e1")
OUTS = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "outputs", "e1", "runs")
BASELINES = ("emap", "nfp", "nfpa")


def validated(rec, D):
    ev = (rec or {}).get("eval") or {}
    if ev.get("sim") != "SIM_AGREE" or ev.get("cec") != "PASS" or ev.get("area") is None or ev.get("delay") is None:
        return None
    if D is not None and ev["delay"] > D + 0.01:
        return None
    return ev


def cand_signature(path):
    d = json.load(open(path))
    return sorted((nd["i"], c[0], c[1], tuple(c[2]), c[3], c[5], tuple(c[6]), tuple(c[7])) for nd in d["nodes"] for c in nd["cands"])


def main():
    out = {"pairs": [], "circuits": []}
    for fn in sorted(os.listdir(RES)):
        if not fn.endswith(".jsonl"):
            continue
        bench = fn[:-6]
        recs = {}
        for line in open(os.path.join(RES, fn)):
            if line.strip():
                r = json.loads(line)
                recs[r["tag"]] = r
        m0 = recs.get("map:D0")
        if not m0 or not m0.get("tool"):
            continue
        D0 = float(m0["tool"]["delay"]) + 0.001
        Ds = {"D0": D0, "D1": 1.10 * D0}
        same_space = None
        p0, p1 = os.path.join(OUTS, bench, "D0.dump.json"), os.path.join(OUTS, bench, "D1.dump.json")
        if os.path.exists(p0) and os.path.exists(p1):
            same_space = cand_signature(p0) == cand_signature(p1)
        lb_nt = (recs.get("lb:D0") or {}).get("solver") or {}
        cverd = []
        for dtag, D in Ds.items():
            pr = {"bench": bench, "D": dtag, "D_value": round(D, 4)}
            mp = validated(recs.get("map:" + dtag), D)
            pr["A_map"] = mp["area"] if mp else None
            hc = validated(recs.get("heur:" + dtag), D)
            pr["heur_control_ok"] = bool(hc and mp and abs(hc["area"] - mp["area"]) < 1e-6)
            base = {}
            for b in BASELINES:
                rb = recs.get("%s:%s" % (b, dtag))
                ev = validated(rb, D)
                ev_any = (rb or {}).get("eval") or {}
                base[b] = {"area": ev["area"] if ev else None, "meets_D": ev is not None,
                           "raw_area": ev_any.get("area"), "raw_delay": ev_any.get("delay"),
                           "sim": ev_any.get("sim"), "cec": ev_any.get("cec")}
            pr["baselines"] = base
            valid_b = [v["area"] for v in base.values() if v["area"] is not None]
            pr["best_baseline"] = min(valid_b) if valid_b else None
            full = recs.get("full:" + dtag) or {}
            fs = full.get("solver") or {}
            pr["full_status"] = fs.get("status")
            pr["full_objective"] = fs.get("objective")
            pr["full_bound"] = fs.get("bound")
            pr["n_cands_full"] = fs.get("n_cands_full")
            fv = validated(full, D)
            ubs = []
            if fv:
                ubs.append(fv["area"])
            pr["UB_full"] = fv["area"] if fv else None
            eps_info = {}
            for tag, r in recs.items():
                if tag.startswith("eps") and tag.endswith(":" + dtag):
                    eps = float(tag[3:].split(":")[0])
                    s = r.get("solver") or {}
                    ev = validated(r, D)
                    eps_info[str(eps)] = {"status": s.get("status"), "area": ev["area"] if ev else None,
                                          "bound": s.get("bound"), "n_cands": s.get("n_cands_model"),
                                          "frac_cands": (s.get("n_cands_model") / s.get("n_cands_full")) if s.get("n_cands_full") else None}
                    if ev:
                        ubs.append(ev["area"])
            pr["eps"] = eps_info
            pr["UB"] = min(ubs) if ubs else None
            lbs = []
            if fs.get("bound") is not None:
                lbs.append(("timed_bound", fs["bound"]))
            if lb_nt.get("bound") is not None and (dtag == "D0" or same_space):
                lbs.append(("notiming_bound", lb_nt["bound"]))
            if lbs:
                src, lb = max(lbs, key=lambda t: t[1])
                pr["LB"], pr["LB_source"] = lb, src
            else:
                pr["LB"], pr["LB_source"] = None, None
            A = pr["A_map"]
            verdict = "NO_REFERENCE"
            if A:
                pr["headroom_demonstrated"] = (A - pr["UB"]) / A if pr["UB"] is not None else None
                pr["headroom_max"] = (A - pr["LB"]) / A if pr["LB"] is not None else None
                if pr["LB"] is not None and (A - pr["LB"]) / A < 0.02:
                    verdict = "PROVEN_BELOW_2"
                elif pr["UB"] is not None and (A - pr["UB"]) / A >= 0.02:
                    verdict = "DEMONSTRATED"
                else:
                    verdict = "UNRESOLVED"
            pr["verdict"] = verdict
            if verdict == "DEMONSTRATED":
                pr["UB_below_best_baseline"] = pr["best_baseline"] is None or pr["UB"] < pr["best_baseline"] - 1e-9
                e5 = eps_info.get("0.05")
                if e5:
                    gain = A - pr["UB"]
                    pr["capture_observed"] = (A - e5["area"]) / gain if e5["area"] is not None else None
                    pr["capture_upper"] = (A - e5["bound"]) / gain if e5["bound"] is not None else None
                    pr["eps005_frac_cands"] = e5["frac_cands"]
            out["pairs"].append(pr)
            cverd.append(pr)
        vs = [p["verdict"] for p in cverd]
        cv = "DEMONSTRATED" if "DEMONSTRATED" in vs else ("PROVEN_BELOW_2" if vs and all(v == "PROVEN_BELOW_2" for v in vs) else "UNRESOLVED")
        out["circuits"].append({"bench": bench, "verdict": cv, "same_space_D0_D1": same_space,
                                "UB_below_best_baseline_any_D": any(p.get("UB_below_best_baseline") for p in cverd if p["verdict"] == "DEMONSTRATED") if cv == "DEMONSTRATED" else None})
    C = out["circuits"]
    with_verdict = [c for c in C if c["verdict"] != "UNRESOLVED"]
    demo = [c for c in C if c["verdict"] == "DEMONSTRATED"]
    proven = [c for c in C if c["verdict"] == "PROVEN_BELOW_2"]
    dp = [p for p in out["pairs"] if p["verdict"] == "DEMONSTRATED"]
    dp_eps = [p for p in dp if p.get("capture_upper") is not None or p.get("capture_observed") is not None]
    s = {"n_circuits": len(C), "with_verdict": len(with_verdict), "demonstrated": len(demo), "proven_below_2": len(proven),
         "unresolved": len(C) - len(with_verdict),
         "pairs": len(out["pairs"]), "pairs_demonstrated": len(dp),
         "pairs_proven_below_2": sum(p["verdict"] == "PROVEN_BELOW_2" for p in out["pairs"]),
         "A1_kill": bool(with_verdict) and len(proven) * 2 > len(with_verdict) and not demo,
         "A1_advance_part": bool(with_verdict) and len(demo) * 2 >= len(with_verdict),
         "relevance_below_count": sum(1 for c in demo if c["UB_below_best_baseline_any_D"]),
         "relevance_kill": bool(demo) and (len(demo) - sum(1 for c in demo if c["UB_below_best_baseline_any_D"])) * 2 > len(demo),
         "A2_pairs_with_eps005": len(dp_eps),
         "A2_capture_proven_below_50": sum(1 for p in dp_eps if p.get("capture_upper") is not None and p["capture_upper"] < 0.5),
         "A3_frac_above_50": sum(1 for p in dp_eps if (p.get("eps005_frac_cands") or 0) > 0.5)}
    s["A2_kill"] = bool(dp_eps) and s["A2_capture_proven_below_50"] * 2 > len(dp_eps)
    s["A3_kill"] = bool(dp_eps) and s["A3_frac_above_50"] * 2 > len(dp_eps)

    # 06_EXPERIMENTAL_EVALUATOR.md states its kill conditions as medians over solved instances. With the exact optimum A*
    # proven only where CP-SAT reports OPTIMAL, H = (A_map - A*)/A_map is bracketed per pair by
    # H_lo = (A_map - UB)/A_map <= H <= H_hi = (A_map - LB)/A_map, so median(H) lies in [median(H_lo), median(H_hi)]
    # over the pairs that have both bounds. C(0.05) <= (A_map - bound_eps)/(A_map - UB) (capture_upper) and
    # R(0.05) is measured directly. Relevance: A* <= UB, so "UB below best baseline" proves "A* below best baseline".
    def med(xs):
        xs = sorted(x for x in xs if x is not None)
        if not xs:
            return None
        n = len(xs)
        return xs[n // 2] if n % 2 else 0.5 * (xs[n // 2 - 1] + xs[n // 2])
    both = [p for p in out["pairs"] if p.get("headroom_demonstrated") is not None and p.get("headroom_max") is not None]
    solved = [p for p in out["pairs"] if p.get("full_status") == "OPTIMAL"]
    s["m06_pairs_with_both_bounds"] = len(both)
    s["m06_pairs_proven_optimal"] = len(solved)
    s["m06_median_H_lower"] = med([p["headroom_demonstrated"] for p in both])
    s["m06_median_H_upper"] = med([p["headroom_max"] for p in both])
    s["m06_A1_kill_proven"] = s["m06_median_H_upper"] is not None and s["m06_median_H_upper"] < 0.02
    s["m06_A1_kill_excluded"] = s["m06_median_H_lower"] is not None and s["m06_median_H_lower"] >= 0.02
    s["m06_median_C005_upper"] = med([p.get("capture_upper") for p in dp_eps])
    s["m06_median_R005"] = med([p.get("eps005_frac_cands") for p in dp_eps])
    s["m06_relevance_UB_below_best_baseline_pairs"] = sum(1 for p in out["pairs"] if p.get("UB") is not None and p.get("best_baseline") is not None and p["UB"] < p["best_baseline"] - 1e-9)
    s["m06_relevance_pairs_with_UB_and_baseline"] = sum(1 for p in out["pairs"] if p.get("UB") is not None and p.get("best_baseline") is not None)
    out["summary"] = s
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
