#!/usr/bin/env python3
"""Wave 11 / E1: exact delay-constrained minimum-area covering over mockturtle `map`'s OWN cut-match space.

Input: a dump JSON written by drv_dump (C1_DUMP), the genlib, a delay bound D, and optionally a candidate restriction eps:
  eps < 0 : full space (every dumped candidate);
  eps >= 0: per (node, phase), keep only candidates whose area flow (in the mapper's own final state) is at most
            (1 + eps) x the best candidate's flow for that (node, phase), plus the heuristic's own chosen candidate.
            Inverter options are always allowed.

Model (SMT-LIB2 for the z3 binary; weighted MaxSAT objective plus linear real arithmetic timing):
  u[n,p]  : (node n, phase p) must be implemented            (Bool)
  x[k]    : candidate k implements its (node, phase)          (Bool, soft cost = cell area)
  v[n,p]  : (n,p) implemented as an inverter of (n,1-p)       (Bool, soft cost = inverter area)
  w[i]    : primary input i is needed in negative phase       (Bool, soft cost = inverter area)
  a[n,p]  : arrival time of (n,p)                            (Real)
  sum(x over (n,p)) + v[n,p] == [u[n,p]]  (exactly one implementation iff needed)
  x[k] -> need(leaf, leaf phase) for all leaves; v[n,p] -> u[n,1-p]
  x[k] -> a[n,p] >= arr(leaf, q) + pin delay;  v[n,p] -> a[n,p] >= a[n,1-p] + inv delay
  every primary output's driver phase is needed and has a <= D
Positive primary inputs cost nothing and have arrival 0; the negative phase is an inverter (arrival = inverter delay),
exactly as mockturtle's init_nodes() / finalize_cover() model it. Outputs driven by a positive PI get a buffer, as in
mockturtle's finalize_cover(); that fixed cost is added outside the solver.

The chosen model is re-checked in Python and written as a structural Verilog cell netlist in the same format as
mockturtle's write_verilog_with_binding. Area and delay are NEVER taken from the solver for comparison: the Wave 10
independent evaluator c1_eval.py recomputes them, and simulation plus CEC check function.

usage: e1_exact.py DUMP.json GENLIB D EPS TIMEOUT_S OUT_PREFIX [Z3_BINARY]
Prints one JSON line."""
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, "/r/12_WAVE_10_EXPERIMENTAL_DISCOVERY/experiments/scripts/c1")
try:
    import c1_eval  # genlib parser (output pin names)
except ImportError:  # host-side import path
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..",
                                    "12_WAVE_10_EXPERIMENTAL_DISCOVERY", "experiments", "scripts", "c1"))
    import c1_eval


def r2(x):
    return int(round(float(x) * 100))  # genlib areas have 2 decimals


def main():
    dump_path, genlib_path, D, eps, tmo, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
    z3 = sys.argv[7] if len(sys.argv) > 7 else "/oss/bin/z3"
    dump = json.load(open(dump_path))
    genlib = c1_eval.parse_genlib(genlib_path)
    inv_area, inv_delay = float(dump["inv"]["area"]), float(dump["inv"]["delay"])
    buf_area = float(dump["buf"]["area"])
    gate_info = {int(k): v for k, v in dump["gates"].items()}  # id -> [name, [pin names]]
    pis = dump["pis"]
    pi_pos = {n: i for i, n in enumerate(pis)}
    nodes = {nd["i"]: nd for nd in dump["nodes"]}

    # candidate list per (node, phase), with the restriction applied
    cands = []          # (node, phase, leaves, gid, area, pol, delays, perm, flow)
    by_np = {}
    n_full = 0
    for n, nd in nodes.items():
        for p in (0, 1):
            cs = [c for c in nd["cands"] if c[0] == p]
            n_full += len(cs)
            if not cs:
                continue
            best = nd["best"][p]
            if eps >= 0:
                fmin = min(c[8] for c in cs)
                keep = [c for c in cs if c[8] <= (1.0 + eps) * fmin + 1e-9
                        or (best is not None and c[1] == best[0] and c[3] == best[1] and c[5] == best[2])]
            else:
                keep = cs
            for c in keep:
                k = len(cands)
                cands.append((n, p, c[2], c[3], float(c[4]), int(c[5]), c[6], c[7], float(c[8])))
                by_np.setdefault((n, p), []).append(k)

    def is_pi(x):
        return x in pi_pos

    def is_const(x):
        return x == 0 and x not in nodes and not is_pi(x)

    enc = os.environ.get("E1_ENC", "pb")
    notiming = os.environ.get("E1_NOTIMING") == "1"  # lower-bound mode: no arrival constraints at all
    L = ["(set-option :produce-models true)", "(set-option :timeout %d)" % (tmo * 1000)]
    if os.environ.get("E1_ARITH"):
        L.append("(set-option :smt.arith.solver %s)" % os.environ["E1_ARITH"])
    for n in nodes:
        for p in (0, 1):
            L.append("(declare-const u_%d_%d Bool)(declare-const v_%d_%d Bool)(declare-const a_%d_%d Real)(assert (>= a_%d_%d 0.0))" % (n, p, n, p, n, p, n, p))
    for i in pis:
        L.append("(declare-const w_%d Bool)" % i)
    for k in range(len(cands)):
        L.append("(declare-const x_%d Bool)" % k)

    def arr_term(leaf, q):
        if is_pi(leaf):
            return "0.0" if q == 0 else repr(inv_delay)
        if leaf in nodes:
            return "a_%d_%d" % (leaf, q)
        return "0.0"  # constant

    def need_term(leaf, q):
        if is_pi(leaf):
            return None if q == 0 else "w_%d" % leaf
        if leaf in nodes:
            return "u_%d_%d" % (leaf, q)
        return None

    for n in nodes:
        for p in (0, 1):
            ks = by_np.get((n, p), [])
            if enc == "pb":
                lits = ["x_%d" % k for k in ks] + ["v_%d_%d" % (n, p), "(not u_%d_%d)" % (n, p)]
                L.append("(assert ((_ pbeq 1 %s) %s))" % (" ".join("1" for _ in lits), " ".join(lits)))
            else:
                terms = " ".join("(ite x_%d 1 0)" % k for k in ks)
                L.append("(assert (= (+ 0 %s (ite v_%d_%d 1 0)) (ite u_%d_%d 1 0)))" % (terms, n, p, n, p))
            L.append("(assert (=> v_%d_%d u_%d_%d))" % (n, p, n, 1 - p))
            if p == 0:  # a node's two phases may not be inverters of each other (a cycle that computes nothing)
                L.append("(assert (not (and v_%d_0 v_%d_1)))" % (n, n))
            if not notiming:
                L.append("(assert (=> v_%d_%d (>= (- a_%d_%d a_%d_%d) %r)))" % (n, p, n, p, n, 1 - p, inv_delay))
    for k, (n, p, leaves, gid, area, pol, dl, perm, flow) in enumerate(cands):
        conj = []
        for j, leaf in enumerate(leaves):
            q = (pol >> j) & 1
            nt = need_term(leaf, q)
            if nt:
                conj.append(nt)
            at = arr_term(leaf, q)
            if notiming:
                continue
            if at.startswith("a_"):
                conj.append("(>= (- a_%d_%d %s) %r)" % (n, p, at, float(dl[j])))
            else:
                conj.append("(>= a_%d_%d %r)" % (n, p, float(at) + float(dl[j])))
        if conj:
            L.append("(assert (=> x_%d (and %s)))" % (k, " ".join(conj)))
    fixed_area = 0.0
    for (drv, c) in dump["pos"]:
        if is_pi(drv):
            if c == 1:
                L.append("(assert w_%d)" % drv)
            else:
                fixed_area += buf_area
        elif drv in nodes:
            L.append("(assert u_%d_%d)" % (drv, c) + ("" if notiming else "(assert (<= a_%d_%d %r))" % (drv, c, D)))
    bound = os.environ.get("E1_BOUND")
    if bound is None:
        for k, cnd in enumerate(cands):
            L.append("(assert-soft (not x_%d) :weight %d :id area)" % (k, r2(cnd[4])))
        for n in nodes:
            for p in (0, 1):
                L.append("(assert-soft (not v_%d_%d) :weight %d :id area)" % (n, p, r2(inv_area)))
        for i in pis:
            L.append("(assert-soft (not w_%d) :weight %d :id area)" % (i, r2(inv_area)))
        L.append("(check-sat)(get-objectives)(get-model)")
    else:
        # decision query: total cell area (x100, excluding the fixed PO buffers) <= bound
        lits, ws = [], []
        for k, cnd in enumerate(cands):
            lits.append("x_%d" % k); ws.append(r2(cnd[4]))
        for n in nodes:
            for p in (0, 1):
                lits.append("v_%d_%d" % (n, p)); ws.append(r2(inv_area))
        for i in pis:
            lits.append("w_%d" % i); ws.append(r2(inv_area))
        L.append("(assert ((_ pble %d %s) %s))" % (int(float(bound)), " ".join(str(w) for w in ws), " ".join(lits)))
        L.append("(check-sat)(get-model)")
    smt = out + ".smt2"
    open(smt, "w").write("\n".join(L) + "\n")

    t0 = time.time()
    try:
        pr = subprocess.run([z3, smt], capture_output=True, text=True, timeout=tmo + 120)
        so = pr.stdout
    except subprocess.TimeoutExpired as e:
        so = (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
    wall = time.time() - t0
    first = so.strip().splitlines()[0] if so.strip() else ""
    res = {"dump": os.path.basename(dump_path), "D": D, "eps": eps, "enc": enc, "arith": os.environ.get("E1_ARITH", "default"), "notiming": notiming, "bound_x100": os.environ.get("E1_BOUND"), "n_cands_full": n_full, "n_cands_model": len(cands),
           "solver_status": first, "solver_wall": round(wall, 2), "fixed_area": fixed_area}
    om = re.search(r"\(area\s+([0-9.]+)\)", so)
    res["objective_x100"] = float(om.group(1)) if om else None
    if first != "sat":
        res["verdict"] = "NO_SOLUTION_OR_TIMEOUT"
        print(json.dumps(res))
        return
    val = dict(re.findall(r"\(define-fun (\w+) \(\) Bool\s+(true|false)\)", so))
    xs = [k for k in range(len(cands)) if val.get("x_%d" % k) == "true"]
    # --- Python re-check of the model, then netlist emission -------------------------------------
    impl = {}
    for k in xs:
        n, p = cands[k][0], cands[k][1]
        if (n, p) in impl:
            res["verdict"] = "MODEL_ERROR_DOUBLE_IMPL"; print(json.dumps(res)); return
        impl[(n, p)] = ("cell", k)
    for n in nodes:
        for p in (0, 1):
            if val.get("v_%d_%d" % (n, p)) == "true":
                if (n, p) in impl:
                    res["verdict"] = "MODEL_ERROR_DOUBLE_IMPL"; print(json.dumps(res)); return
                impl[(n, p)] = ("inv", None)
    need_pi_neg = {i for i in pis if val.get("w_%d" % i) == "true"}
    # structural re-check: the implementation graph must be acyclic
    deps = {}
    for (n, p), (kind, k) in impl.items():
        if kind == "inv":
            deps[(n, p)] = [(n, 1 - p)]
        else:
            deps[(n, p)] = [(l, (cands[k][5] >> j) & 1) for j, l in enumerate(cands[k][2]) if l in nodes]
    state = {}
    for s0 in deps:
        if state.get(s0) == 2:
            continue
        stack = [(s0, iter(deps.get(s0, [])))]
        state[s0] = 1
        while stack:
            node_, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                state[node_] = 2; stack.pop(); continue
            if state.get(nxt) == 1:
                res["verdict"] = "MODEL_ERROR_CYCLE"; print(json.dumps(res)); return
            if state.get(nxt) is None and nxt in deps:
                state[nxt] = 1; stack.append((nxt, iter(deps[nxt])))
    lines, inst = [], 0
    ins = ["x%d" % pi_pos[i] for i in pis]
    outs = ["y%d" % j for j in range(len(dump["pos"]))]

    def sig(leaf, q):
        if is_pi(leaf):
            if q == 0:
                return "x%d" % pi_pos[leaf]
            if leaf not in need_pi_neg:
                raise ValueError("PI negative phase used but not provided")
            return "xn%d" % pi_pos[leaf]
        if leaf in nodes:
            if (leaf, q) not in impl:
                raise ValueError("leaf (%d,%d) used but not implemented" % (leaf, q))
            return "n%d_%d" % (leaf, q)
        return "1'b0" if q == 0 else "1'b1"

    inv_name = gate_info.get(int(dump["inv"]["id"]), [None])[0]
    if inv_name is None:  # inverter may not appear among candidate gates; look it up by function in the genlib
        inv_name = next(g for g, v in genlib.items() if re.fullmatch(r"INV.*", g) and abs(v["area"] - inv_area) < 1e-6)
    buf_name = next(g for g, v in genlib.items() if re.fullmatch(r"BUF.*", g) and abs(v["area"] - buf_area) < 1e-6)
    try:
        for i in sorted(need_pi_neg):
            lines.append("  %s g%d ( .A (x%d), .%s (xn%d) );" % (inv_name, inst, pi_pos[i], genlib[inv_name]["out"], pi_pos[i])); inst += 1
        for (n, p), (kind, k) in sorted(impl.items()):
            if kind == "inv":
                lines.append("  %s g%d ( .A (%s), .%s (n%d_%d) );" % (inv_name, inst, sig(n, 1 - p), genlib[inv_name]["out"], n, p)); inst += 1
                continue
            _, _, leaves, gid, area, pol, dl, perm, flow = cands[k]
            name, pins = gate_info[gid]
            conn = [None] * len(pins)
            for j, leaf in enumerate(leaves):
                conn[perm[j]] = sig(leaf, (pol >> j) & 1)
            if any(c is None for c in conn):
                raise ValueError("unconnected pin in %s" % name)
            args = ", ".join(".%s (%s)" % (pins[j], conn[j]) for j in range(len(pins)))
            lines.append("  %s g%d ( %s, .%s (n%d_%d) );" % (name, inst, args, genlib[name]["out"], n, p)); inst += 1
        for j, (drv, c) in enumerate(dump["pos"]):
            if is_pi(drv) and c == 0:
                lines.append("  %s g%d ( .A (x%d), .%s (y%d) );" % (buf_name, inst, pi_pos[drv], genlib[buf_name]["out"], j)); inst += 1
            else:
                lines.append("  assign y%d = %s;" % (j, sig(drv, c)))
    except (ValueError, KeyError) as e:
        res["verdict"] = "MODEL_ERROR"; res["error"] = str(e); print(json.dumps(res)); return
    with open(out + ".v", "w") as f:
        f.write("module top( %s );\n" % " , ".join(ins + outs))
        f.write("  input %s ;\n  output %s ;\n" % (" , ".join(ins), " , ".join(outs)))
        f.write("\n".join(lines) + "\nendmodule\n")
    res["verdict"] = "SOLVED" if "unknown" not in first else "PARTIAL"
    res["n_cells"] = inst
    res["n_impl"] = len(impl)
    print(json.dumps(res))


if __name__ == "__main__":
    main()
