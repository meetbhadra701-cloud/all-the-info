#!/usr/bin/env python3
"""Wave 11 / E1: shared pieces of the exact-covering experiment.

- the covering space over mockturtle `map`'s OWN dumped cut-match candidates (full, or eps-restricted);
- reconstruction of `map`'s own final cover from the dump, done the way mockturtle's finalize_cover() builds it;
- re-check of any cover (every used leaf implemented, no double implementation, acyclic) and structural Verilog
  emission in the format of mockturtle's write_verilog_with_binding.

e1_exact.py (the z3 attempt) predates this module. It is kept unchanged as the record of the z3 runs.
Areas and pin delays in asap7.genlib have at most 2 decimals, so every quantity is an exact integer after x100
(i100). Area and delay are never taken from here for comparison: c1_eval_w11.py recomputes them independently."""
import json
import os
import re
import sys

sys.path.insert(0, "/r/12_WAVE_10_EXPERIMENTAL_DISCOVERY/experiments/scripts/c1")
try:
    import c1_eval  # genlib parser (output pin names, areas)
except ImportError:  # host-side import path
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..",
                                    "12_WAVE_10_EXPERIMENTAL_DISCOVERY", "experiments", "scripts", "c1"))
    import c1_eval


def i100(x):
    return int(round(float(x) * 100))


class Space:
    """cands[k] = (node, phase, leaves, gate id, area, leaf polarity bits, pin delays, pin permutation, area flow)."""

    def __init__(self, dump_path, genlib_path, eps):
        dump = json.load(open(dump_path))
        self.dump = dump
        self.genlib = c1_eval.parse_genlib(genlib_path)
        self.inv_area, self.inv_delay = float(dump["inv"]["area"]), float(dump["inv"]["delay"])
        self.buf_area = float(dump["buf"]["area"])
        self.gate_info = {int(k): v for k, v in dump["gates"].items()}  # id -> [name, [pin names]]
        self.pis = dump["pis"]
        self.pi_pos = {n: i for i, n in enumerate(self.pis)}
        self.nodes = {nd["i"]: nd for nd in dump["nodes"]}
        self.order = sorted(self.nodes)  # AIG node indices are topological
        self.cands, self.by_np, self.n_full = [], {}, 0
        self.cut_of = []  # the dump's cut index of cands[k] (needed to identify map's own best match)
        for n in self.order:
            nd = self.nodes[n]
            for p in (0, 1):
                cs = [c for c in nd["cands"] if c[0] == p]
                self.n_full += len(cs)
                if not cs:
                    continue
                best = nd["best"][p]
                if eps >= 0:
                    fmin = min(c[8] for c in cs)
                    keep = [c for c in cs if c[8] <= (1.0 + eps) * fmin + 1e-9 or self.is_best(c, best)]
                else:
                    keep = cs
                for c in keep:
                    k = len(self.cands)
                    self.cands.append((n, p, c[2], c[3], float(c[4]), int(c[5]), c[6], c[7], float(c[8])))
                    self.cut_of.append(c[1])
                    self.by_np.setdefault((n, p), []).append(k)
        # fixed cost outside any decision: a buffer for every output driven by a positive primary input
        self.fixed_area = sum(self.buf_area for d, c in dump["pos"] if self.is_pi(d) and c == 0)

    @staticmethod
    def is_best(c, best):
        return best is not None and c[1] == best[0] and c[3] == best[1] and c[5] == best[2]

    def is_pi(self, x):
        return x in self.pi_pos

    # ---------------------------------------------------------------------------------------------------------
    def heuristic_cover(self):
        """map's own final cover, following finalize_cover(): a node with map_refs[2] > 0 is in the cover; with
        same_match, its best phase gets the gate and the other phase (if referenced) an inverter; otherwise each
        referenced phase gets its own best gate. The dump records the best (cut, gate, polarity) but not the pin
        permutation, so among candidates sharing (cut, gate, polarity) the one with the smallest arrival is used
        (same area; never later than the mapper's own choice). Returns (impl, need_pi_neg) or raises ValueError."""
        impl = {}
        arr = {}
        inv_d = i100(self.inv_delay)

        def leaf_arr(leaf, q):
            if self.is_pi(leaf):
                return 0 if q == 0 else inv_d
            if leaf in self.nodes:
                if (leaf, q) not in arr:
                    raise ValueError("heuristic cover uses (%d,%d) before it is implemented" % (leaf, q))
                return arr[(leaf, q)]
            return 0

        def pick(n, p, best):
            ks = [k for k in self.by_np.get((n, p), []) if self.cut_of[k] == best[0] and self.cands[k][3] == best[1]
                  and self.cands[k][5] == best[2]]
            if not ks:
                raise ValueError("best match of (%d,%d) not among the candidates" % (n, p))
            scored = []
            for k in ks:
                c = self.cands[k]
                scored.append((max(leaf_arr(l, (c[5] >> j) & 1) + i100(c[6][j]) for j, l in enumerate(c[2])), k))
            t, k = min(scored)
            impl[(n, p)] = ("cell", k)
            arr[(n, p)] = t

        for n in self.order:
            nd = self.nodes[n]
            refs, best = nd["refs"], nd["best"]
            if refs[2] == 0:
                continue
            if nd["same"]:
                ph = 0 if best[0] is not None else 1
                pick(n, ph, best[ph])
                if refs[ph ^ 1] > 0:
                    impl[(n, ph ^ 1)] = ("inv", None)
                    arr[(n, ph ^ 1)] = arr[(n, ph)] + inv_d
            else:
                for p in (0, 1):
                    if refs[p] > 0:
                        if best[p] is None:
                            raise ValueError("referenced phase (%d,%d) has no match" % (n, p))
                        pick(n, p, best[p])
        need_pi_neg = set()
        for (n, p), (kind, k) in impl.items():
            if kind == "cell":
                c = self.cands[k]
                for j, l in enumerate(c[2]):
                    if self.is_pi(l) and (c[5] >> j) & 1:
                        need_pi_neg.add(l)
        for d, c in self.dump["pos"]:
            if self.is_pi(d) and c == 1:
                need_pi_neg.add(d)
        return impl, need_pi_neg

    # ---------------------------------------------------------------------------------------------------------
    def check(self, impl, need_pi_neg):
        """Structural re-check. Returns (area_x100, delay_x100) of the cover under the model's own delay model, or
        raises ValueError. The area includes the fixed PO buffers; the delay is the max arrival over outputs."""
        deps = {}
        for (n, p), (kind, k) in impl.items():
            if kind == "inv":
                deps[(n, p)] = [(n, 1 - p)]
            else:
                c = self.cands[k]
                if (c[0], c[1]) != (n, p):
                    raise ValueError("candidate %d does not implement (%d,%d)" % (k, n, p))
                deps[(n, p)] = [(l, (c[5] >> j) & 1) for j, l in enumerate(c[2]) if l in self.nodes]
        for s, ds in deps.items():
            for d in ds:
                if d not in impl:
                    raise ValueError("(%d,%d) uses (%d,%d), which is not implemented" % (s + d))
        for (n, p), (kind, k) in impl.items():
            if kind == "cell":
                c = self.cands[k]
                for j, l in enumerate(c[2]):
                    if self.is_pi(l) and (c[5] >> j) & 1 and l not in need_pi_neg:
                        raise ValueError("PI %d used in negative phase without an inverter" % l)
        # acyclicity + arrivals (iterative DFS)
        inv_d = i100(self.inv_delay)
        arr, state = {}, {}
        for s0 in deps:
            if s0 in arr:
                continue
            stack = [s0]
            while stack:
                s = stack[-1]
                if s in arr:
                    stack.pop()
                    continue
                state[s] = 1
                pend = [d for d in deps[s] if d not in arr]
                for d in pend:
                    if state.get(d) == 1:
                        raise ValueError("combinational cycle through (%d,%d)" % d)
                if pend:
                    stack.extend(pend)
                    continue
                kind, k = impl[s]
                if kind == "inv":
                    arr[s] = arr[(s[0], 1 - s[1])] + inv_d
                else:
                    c = self.cands[k]
                    t = 0
                    for j, l in enumerate(c[2]):
                        q = (c[5] >> j) & 1
                        la = (0 if q == 0 else inv_d) if self.is_pi(l) else (arr[(l, q)] if l in self.nodes else 0)
                        t = max(t, la + i100(c[6][j]))
                    arr[s] = t
                state[s] = 2
                stack.pop()
        area = i100(self.fixed_area) + i100(self.inv_area) * len(need_pi_neg)
        for (n, p), (kind, k) in impl.items():
            area += i100(self.inv_area) if kind == "inv" else i100(self.cands[k][4])
        delay = 0
        for d, c in self.dump["pos"]:
            if d in self.nodes:
                if (d, c) not in impl:
                    raise ValueError("output driver (%d,%d) not implemented" % (d, c))
                delay = max(delay, arr[(d, c)])
            elif self.is_pi(d):
                delay = max(delay, inv_d if c == 1 else i100(self.dump["buf"]["delay"]))
        return area, delay

    # ---------------------------------------------------------------------------------------------------------
    def emit(self, impl, need_pi_neg, path):
        """Structural Verilog cell netlist (inputs x0.., outputs y0..). Returns the number of instances."""
        genlib, dump = self.genlib, self.dump
        lines, inst = [], 0
        ins = ["x%d" % self.pi_pos[i] for i in self.pis]
        outs = ["y%d" % j for j in range(len(dump["pos"]))]

        def sig(leaf, q):
            if self.is_pi(leaf):
                if q == 0:
                    return "x%d" % self.pi_pos[leaf]
                if leaf not in need_pi_neg:
                    raise ValueError("PI negative phase used but not provided")
                return "xn%d" % self.pi_pos[leaf]
            if leaf in self.nodes:
                if (leaf, q) not in impl:
                    raise ValueError("leaf (%d,%d) used but not implemented" % (leaf, q))
                return "n%d_%d" % (leaf, q)
            return "1'b0" if q == 0 else "1'b1"

        inv_name = self.gate_info.get(int(dump["inv"]["id"]), [None])[0]
        if inv_name is None:
            inv_name = next(g for g, v in genlib.items() if re.fullmatch(r"INV.*", g) and abs(v["area"] - self.inv_area) < 1e-6)
        buf_name = next(g for g, v in genlib.items() if re.fullmatch(r"BUF.*", g) and abs(v["area"] - self.buf_area) < 1e-6)
        for i in sorted(need_pi_neg):
            lines.append("  %s g%d ( .A (x%d), .%s (xn%d) );" % (inv_name, inst, self.pi_pos[i], genlib[inv_name]["out"], self.pi_pos[i]))
            inst += 1
        for (n, p), (kind, k) in sorted(impl.items()):
            if kind == "inv":
                lines.append("  %s g%d ( .A (%s), .%s (n%d_%d) );" % (inv_name, inst, sig(n, 1 - p), genlib[inv_name]["out"], n, p))
                inst += 1
                continue
            _, _, leaves, gid, area, pol, dl, perm, flow = self.cands[k]
            name, pins = self.gate_info[gid]
            conn = [None] * len(pins)
            for j, leaf in enumerate(leaves):
                conn[perm[j]] = sig(leaf, (pol >> j) & 1)
            if any(c is None for c in conn):
                raise ValueError("unconnected pin in %s" % name)
            args = ", ".join(".%s (%s)" % (pins[j], conn[j]) for j in range(len(pins)))
            lines.append("  %s g%d ( %s, .%s (n%d_%d) );" % (name, inst, args, genlib[name]["out"], n, p))
            inst += 1
        for j, (drv, c) in enumerate(dump["pos"]):
            if self.is_pi(drv) and c == 0:
                lines.append("  %s g%d ( .A (x%d), .%s (y%d) );" % (buf_name, inst, self.pi_pos[drv], genlib[buf_name]["out"], j))
                inst += 1
            else:
                lines.append("  assign y%d = %s;" % (j, sig(drv, c)))
        with open(path, "w", newline="\n") as f:
            f.write("module top( %s );\n" % " , ".join(ins + outs))
            f.write("  input %s ;\n  output %s ;\n" % (" , ".join(ins), " , ".join(outs)))
            f.write("\n".join(lines) + "\nendmodule\n")
        return inst
