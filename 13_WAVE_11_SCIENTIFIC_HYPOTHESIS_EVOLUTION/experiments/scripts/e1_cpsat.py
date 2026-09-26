#!/usr/bin/env python3
"""Wave 11 / E1: exact delay-constrained minimum-area covering over mockturtle `map`'s OWN cut-match space,
solved with OR-tools CP-SAT (the sat_runner 9.14 binary shipped in the openroad/orfs image, run network-off).

This is the same model as e1_exact.py (the z3 attempt, which returned unknown on ctrl within 300-600 s), in integer
units (x100: every area and pin delay in asap7.genlib has at most 2 decimals, so the scaling is exact):
  u[n,p] need, x[k] candidate chosen, v[n,p] inverter from the other phase, w[i] PI negative phase, a[n,p] arrival
  sum(x over (n,p)) + v[n,p] - u[n,p] == 0;  x[k] -> need(leaf, leaf phase);  v[n,p] -> u[n,1-p];  not(v[n,0] & v[n,1])
  x[k] -> a[n,p] - a[leaf,q] >= pin delay (constant leaf arrivals folded);  v[n,p] -> a[n,p] - a[n,1-p] >= inv delay
  outputs: driver phase needed, a <= floor(100 D); PI negative phase at a primary output: w asserted
  minimise sum(area x) + inv area (sum v + sum w);  fixed PO buffers are added outside.
E1_NOTIMING=1 drops all arrival variables (the pre-registered no-timing lower-bound problem).

map's own final cover, rebuilt from the dump (e1_model.heuristic_cover), is (a) re-checked against the model and
written as <out>_heur.v for the independent evaluator (model-fidelity control) and (b) given to CP-SAT as a hint.
CP-SAT's best_objective_bound is reported as a solver-proven lower bound; it is a solver claim, not independently
checked. Every solution netlist IS independently checked (c1_eval_w11 STA + simulation, ABC cec).

usage: e1_cpsat.py DUMP.json GENLIB D EPS TIMEOUT_S WORKERS OUT_PREFIX
Prints one JSON line."""
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e1_model  # noqa: E402

SAT_RUNNER = os.environ.get("SAT_RUNNER", "/opt/or-tools/bin/sat_runner")
BIG = 10 ** 12


class Cp:
    def __init__(self):
        self.nv, self.vars, self.cons = 0, [], []

    def var(self, lo, hi):
        self.vars.append("variables { domain: [%d, %d] }" % (lo, hi))
        self.nv += 1
        return self.nv - 1

    @staticmethod
    def neg(i):
        return -i - 1

    @staticmethod
    def _enf(enf):
        return "" if enf is None else "enforcement_literal: %d " % enf

    def bool_or(self, lits, enf=None):
        self.cons.append("constraints { %sbool_or { literals: [%s] } }" % (self._enf(enf), ", ".join(map(str, lits))))

    def bool_and(self, lits, enf=None):
        self.cons.append("constraints { %sbool_and { literals: [%s] } }" % (self._enf(enf), ", ".join(map(str, lits))))

    def linear(self, vs, cs, lo, hi, enf=None):
        self.cons.append("constraints { %slinear { vars: [%s] coeffs: [%s] domain: [%d, %d] } }" % (
            self._enf(enf), ", ".join(map(str, vs)), ", ".join(map(str, cs)), lo, hi))


def main():
    dump_path, genlib_path, D, eps, tmo, workers, out = (sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]),
                                                        int(sys.argv[5]), int(sys.argv[6]), sys.argv[7])
    notiming = os.environ.get("E1_NOTIMING") == "1"
    sp = e1_model.Space(dump_path, genlib_path, eps)
    I = e1_model.i100
    inv_a, inv_d = I(sp.inv_area), I(sp.inv_delay)
    D_int = int(D * 100 + 1e-6) if D < 1e8 else BIG  # floor: never gives the solver more slack than D
    res = {"dump": os.path.basename(dump_path), "D": D, "D_int": D_int, "eps": eps, "notiming": notiming,
           "n_cands_full": sp.n_full, "n_cands_model": len(sp.cands), "timeout": tmo, "workers": workers,
           "fixed_area": round(sp.fixed_area, 4)}

    # --- model-fidelity control: map's own cover, rebuilt from the dump ------------------------------------------
    hint = None
    try:
        h_impl, h_neg = sp.heuristic_cover()
        h_area, h_delay = sp.check(h_impl, h_neg)
        sp.emit(h_impl, h_neg, out + "_heur.v")
        res.update({"heur_area_model": h_area / 100.0, "heur_delay_model": h_delay / 100.0,
                    "heur_fits_D": notiming or h_delay <= D_int})
        hint = (h_impl, h_neg)
    except ValueError as e:
        res["heur_error"] = str(e)

    # --- CP-SAT model -------------------------------------------------------------------------------------------
    m = Cp()
    u, v, a, w, x = {}, {}, {}, {}, []
    for n in sp.order:
        for p in (0, 1):
            u[(n, p)] = m.var(0, 1)
            v[(n, p)] = m.var(0, 1)
            if not notiming:
                a[(n, p)] = m.var(0, D_int)
    for i in sp.pis:
        w[i] = m.var(0, 1)
    for _ in sp.cands:
        x.append(m.var(0, 1))

    def need_lit(leaf, q):
        if sp.is_pi(leaf):
            return None if q == 0 else w[leaf]
        if leaf in sp.nodes:
            return u[(leaf, q)]
        return None

    for n in sp.order:
        for p in (0, 1):
            ks = sp.by_np.get((n, p), [])
            m.linear([x[k] for k in ks] + [v[(n, p)], u[(n, p)]], [1] * len(ks) + [1, -1], 0, 0)
            m.bool_or([u[(n, 1 - p)]], enf=v[(n, p)])
            if not notiming:
                m.linear([a[(n, p)], a[(n, 1 - p)]], [1, -1], inv_d, BIG, enf=v[(n, p)])
        m.bool_or([m.neg(v[(n, 0)]), m.neg(v[(n, 1)])])
    for k, (n, p, leaves, gid, area, pol, dl, perm, flow) in enumerate(sp.cands):
        needs = []
        for j, leaf in enumerate(leaves):
            q = (pol >> j) & 1
            nl = need_lit(leaf, q)
            if nl is not None:
                needs.append(nl)
            if notiming:
                continue
            d = I(dl[j])
            if leaf in sp.nodes:
                m.linear([a[(n, p)], a[(leaf, q)]], [1, -1], d, BIG, enf=x[k])
            else:
                const = (0 if q == 0 else inv_d) if sp.is_pi(leaf) else 0
                m.linear([a[(n, p)]], [1], const + d, BIG, enf=x[k])
        if needs:
            m.bool_and(needs, enf=x[k])
    for drv, c in sp.dump["pos"]:
        if sp.is_pi(drv):
            if c == 1:
                m.bool_or([w[drv]])
        elif drv in sp.nodes:
            m.bool_or([u[(drv, c)]])  # a[drv,c] <= D_int is its domain
    obj_v, obj_c = [], []
    for k, cnd in enumerate(sp.cands):
        obj_v.append(x[k]); obj_c.append(I(cnd[4]))
    for n in sp.order:
        for p in (0, 1):
            obj_v.append(v[(n, p)]); obj_c.append(inv_a)
    for i in sp.pis:
        obj_v.append(w[i]); obj_c.append(inv_a)

    txt = ["# E1 exact covering; generated by e1_cpsat.py"] + m.vars + m.cons
    txt.append("objective { vars: [%s] coeffs: [%s] }" % (", ".join(map(str, obj_v)), ", ".join(map(str, obj_c))))
    if hint is not None and (notiming or res.get("heur_fits_D")):
        h_impl, h_neg = hint
        hv, hval = [], []
        chosen = {k for kind, k in h_impl.values() if kind == "cell"}
        for n in sp.order:
            for p in (0, 1):
                hv += [u[(n, p)], v[(n, p)]]
                hval += [1 if (n, p) in h_impl else 0, 1 if h_impl.get((n, p), ("", 0))[0] == "inv" else 0]
        for i in sp.pis:
            hv.append(w[i]); hval.append(1 if i in h_neg else 0)
        for k in range(len(sp.cands)):
            hv.append(x[k]); hval.append(1 if k in chosen else 0)
        txt.append("solution_hint { vars: [%s] values: [%s] }" % (", ".join(map(str, hv)), ", ".join(map(str, hval))))
        res["hint"] = True
    model_path = out + ".cpmodel.txt"
    with open(model_path, "w", newline="\n") as f:
        f.write("\n".join(txt) + "\n")
    res["n_vars"], res["n_cons"] = m.nv, len(m.cons)

    # --- solve --------------------------------------------------------------------------------------------------
    resp_path = out + ".response.txt"
    if os.path.exists(resp_path):
        os.remove(resp_path)
    params = "max_time_in_seconds:%d num_workers:%d log_search_progress:true random_seed:1" % (tmo, workers)
    env = dict(os.environ)
    env["LD_LIBRARY_PATH"] = "/opt/or-tools/lib:" + env.get("LD_LIBRARY_PATH", "")
    t0 = time.time()
    try:
        pr = subprocess.run([SAT_RUNNER, "--input=" + model_path, "--output=" + resp_path, "--params=" + params],
                            capture_output=True, text=True, timeout=tmo + 300, env=env)
        log = pr.stdout + pr.stderr
    except subprocess.TimeoutExpired as e:
        log = "HARD TIMEOUT\n" + ((e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or ""))
    res["solver_wall"] = round(time.time() - t0, 2)
    with open(out + ".solver.log", "w", newline="\n") as f:
        f.write(log)
    if not os.path.exists(resp_path):
        res["status"] = "NO_RESPONSE"
        res["verdict"] = "SOLVER_ERROR"
        print(json.dumps(res))
        return
    rt = open(resp_path).read()
    st = re.search(r"^status:\s*(\w+)", rt, flags=re.M)
    res["status"] = st.group(1) if st else "UNPARSED"
    ov = re.search(r"^objective_value:\s*([-0-9.e+]+)", rt, flags=re.M)
    bb = re.search(r"^best_objective_bound:\s*([-0-9.e+]+)", rt, flags=re.M)
    fixed = I(sp.fixed_area)
    res["objective"] = (float(ov.group(1)) + fixed) / 100.0 if ov else None
    res["bound"] = (float(bb.group(1)) + fixed) / 100.0 if bb else None
    sol = [int(s) for s in re.findall(r"^solution:\s*(-?\d+)", rt, flags=re.M)]
    if not sol:
        lst = re.search(r"^solution:\s*\[([^\]]*)\]", rt, flags=re.M)
        if lst:
            sol = [int(s) for s in lst.group(1).replace(",", " ").split()]
    if res["status"] not in ("OPTIMAL", "FEASIBLE") or len(sol) != m.nv:
        res["verdict"] = "NO_SOLUTION" if res["status"] in ("INFEASIBLE", "UNKNOWN") else "SOLVER_ERROR"
        res["n_solution_values"] = len(sol)
        print(json.dumps(res))
        return

    # --- re-check the solution in Python, then emit --------------------------------------------------------------
    impl = {}
    try:
        for k in range(len(sp.cands)):
            if sol[x[k]]:
                n, p = sp.cands[k][0], sp.cands[k][1]
                if (n, p) in impl:
                    raise ValueError("double implementation of (%d,%d)" % (n, p))
                impl[(n, p)] = ("cell", k)
        for n in sp.order:
            for p in (0, 1):
                if sol[v[(n, p)]]:
                    if (n, p) in impl:
                        raise ValueError("double implementation of (%d,%d)" % (n, p))
                    impl[(n, p)] = ("inv", None)
        need_neg = {i for i in sp.pis if sol[w[i]]}
        area, delay = sp.check(impl, need_neg)
        res["n_cells"] = sp.emit(impl, need_neg, out + ".v")
    except (ValueError, KeyError) as e:
        res["verdict"] = "MODEL_ERROR"
        res["error"] = str(e)
        print(json.dumps(res))
        return
    res["sol_area_model"] = area / 100.0
    res["sol_delay_model"] = delay / 100.0
    if res["objective"] is not None and abs(area / 100.0 - res["objective"]) > 1e-6:
        res["note"] = "re-computed area differs from the solver objective (dangling cells or accounting)"
    res["verdict"] = "SOLVED_OPTIMAL" if res["status"] == "OPTIMAL" else "SOLVED_FEASIBLE"
    print(json.dumps(res))


if __name__ == "__main__":
    main()
