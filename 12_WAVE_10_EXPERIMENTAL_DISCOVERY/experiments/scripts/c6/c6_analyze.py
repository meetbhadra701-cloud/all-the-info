#!/usr/bin/env python3
"""C6 analysis: applies the pre-registered F/G conditions (experiments/results/c6_PREREGISTRATION.md).
Reads experiments/outputs/c6/asap7/aes/<treatment>/{metrics.json,equiv.txt}.
Writes experiments/results/c6_results.csv and c6_summary.json, and prints a table plus the verdict."""
import csv
import glob
import json
import os
import statistics

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
BASE = os.path.join(ROOT, "experiments", "outputs", "c6", "asap7", "aes")
RES = os.path.join(ROOT, "experiments", "results")


def main():
    rows = []
    for d in sorted(glob.glob(os.path.join(BASE, "*"))):
        mj = os.path.join(d, "metrics.json")
        if not os.path.exists(mj):
            continue
        m = json.load(open(mj))
        eq = open(os.path.join(d, "equiv.txt")).read().strip() if os.path.exists(os.path.join(d, "equiv.txt")) else "not_checked"
        if "EQUIV_ABC_PASS" in eq or "EQUIV_PASS" in eq:
            verdict = "PASS"
        elif "EQUIV_ABC_NEQ" in eq:
            verdict = "NEQ"
        elif "EQUIV_ABC_UNDECIDED" in eq or "EQUIV_NOT_PROVEN" in eq:
            verdict = "UNDECIDED"
        else:
            verdict = eq
        name = os.path.basename(d)
        stage = "unplaced" if name.startswith("unplaced_") else "placed"
        rows.append({"treatment": name, "stage": stage, "mode": m["mode"], "seed": m["seed"],
                     "before_wns": m["before_wns"], "after_wns": m["after_wns"], "d_wns": m["after_wns"] - m["before_wns"],
                     "before_tns": m["before_tns"], "after_tns": m["after_tns"],
                     "area_ratio": m["after_area"] / m["before_area"] if m["before_area"] else None,
                     "inst_delta": m["after_inst"] - m["before_inst"], "seconds": m["seconds"], "equiv": verdict})
    with open(os.path.join(RES, "c6_results.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print("%-28s %-8s %9s %9s %8s %11s %7s %7s %s" % ("treatment", "stage", "WNS0", "WNS1", "dWNS", "TNS1", "area", "sec", "equiv"))
    for r in rows:
        print("%-28s %-8s %9.2f %9.2f %8.2f %11.1f %7s %7.1f %s" % (r["treatment"], r["stage"], r["before_wns"], r["after_wns"], r["d_wns"],
                                                                   r["after_tns"], ("%.4f" % r["area_ratio"]) if r["area_ratio"] else "n/a", r["seconds"], r["equiv"]))
    P = [r for r in rows if r["stage"] == "placed"]
    ann = [r for r in P if r["mode"] == "annealing"]
    rt = next((r for r in P if r["mode"] == "repair_timing"), None)
    ar = [r for r in P if r["mode"] == "annealing_repair"]
    out = {"n_annealing": len(ann), "n_annealing_repair": len(ar)}
    if ann and rt:
        med = statistics.median(r["after_wns"] for r in ann)
        out.update({"median_annealing_wns": med, "repair_timing_wns": rt["after_wns"],
                    "annealing_minus_repair": med - rt["after_wns"],
                    "annealing_d_wns_signs": sorted({(r["d_wns"] > 0) - (r["d_wns"] < 0) for r in ann}),
                    "max_area_ratio_annealing": max(r["area_ratio"] for r in ann)})
        F1 = not (med - rt["after_wns"] > 5.0)
        F2 = len(out["annealing_d_wns_signs"]) > 1
        F3 = any(r["area_ratio"] > 1.05 and r["d_wns"] > 0 for r in ann)
        F4 = any(r["equiv"] not in ("PASS", "not_checked") for r in P if r["mode"] != "none")
        unchecked = [r["treatment"] for r in P if r["mode"] != "none" and r["equiv"] == "not_checked"]
        G_add = None
        if ar:
            G_add = statistics.median(r["after_wns"] for r in ar) - rt["after_wns"]
        G = (med - rt["after_wns"] > 10.0) and (G_add is not None and G_add > 10.0) and all(r["area_ratio"] <= 1.02 for r in ann) and not F4 and not unchecked
        out.update({"F1_not_better_than_repair_by_5ps": F1, "F2_sign_change": F2, "F3_area_cost": F3, "F4_equivalence_failure_or_unproven": F4,
                    "equiv_unchecked": unchecked, "additive_gain_vs_repair": G_add, "G": G,
                    "verdict": "KILL" if (F1 or F2 or F3 or F4) else ("ADVANCE" if G else "UNRESOLVED")})
    U = [r for r in rows if r["stage"] == "unplaced"]
    ua = [r for r in U if r["mode"] == "annealing"]
    if ua:
        out["unplaced_annealing_d_wns"] = [round(r["d_wns"], 2) for r in ua]
        out["unplaced_repair_d_wns"] = [round(r["d_wns"], 2) for r in U if r["mode"] == "repair_timing"]
    json.dump(out, open(os.path.join(RES, "c6_summary.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
