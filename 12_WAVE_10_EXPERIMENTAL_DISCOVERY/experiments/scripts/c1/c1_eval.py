#!/usr/bin/env python3
"""Wave 10 / C1 independent netlist evaluator. It shares no code with mockturtle or ABC.

Given a genlib, the reference AIG (binary AIGER) and a mapped structural Verilog netlist
(mockturtle write_verilog_with_binding output, or ABC write_verilog output), it:
  1. recomputes the cell area and the worst arrival time from the genlib, using its own
     parser and STA (pin delay = max(rise_block, fall_block), load-independent, PI arrival 0);
  2. writes a BLIF whose .names covers are irredundant SOPs (Minato-Morreale) of this module's
     own truth tables of the genlib expressions, each cover asserted equal to its truth table.
     The CEC run on this BLIF does not go through mockturtle's k-LUT functions;
  3. simulates the reference AIG and the netlist on random patterns (bit-parallel) and
     reports the first mismatching output together with a counterexample.
PIs and POs are matched by order, as in MappingEvolve's `cec -n`.

usage: c1_eval.py GENLIB REF.aig NETLIST.v OUT.blif [--patterns N] [--seed S]
Prints one JSON line. The simulation verdict is SIM_MISMATCH (a definite bug, with a
counterexample) or SIM_AGREE (no mismatch found; this is not a proof).
"""
import json
import random
import re
import sys

# ---------------- genlib ----------------

def _tokenize_expr(s):
    toks, i = [], 0
    while i < len(s):
        c = s[i]
        if c.isspace():
            i += 1
        elif c in "()!*+^'":
            toks.append(c); i += 1
        else:
            m = re.match(r"[A-Za-z_][A-Za-z0-9_\[\]\.]*", s[i:])
            if not m:
                raise ValueError("bad genlib expr near %r" % s[i:])
            toks.append(m.group(0)); i += len(m.group(0))
    return toks


class _P:
    """Recursive-descent parser: expr := xor ('+' xor)* ; xor := term ('^' term)* ;
    term := unary (('*' | juxtaposition) unary)* ; unary := '!' unary | atom "'"* ."""

    def __init__(self, toks):
        self.t, self.i = toks, 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def eat(self, x=None):
        tok = self.peek()
        if x is not None and tok != x:
            raise ValueError("expected %r got %r" % (x, tok))
        self.i += 1
        return tok

    def expr(self):
        n = self.xor()
        while self.peek() == "+":
            self.eat(); n = ("or", n, self.xor())
        return n

    def xor(self):
        n = self.term()
        while self.peek() == "^":
            self.eat(); n = ("xor", n, self.term())
        return n

    def term(self):
        n = self.unary()
        while True:
            p = self.peek()
            if p == "*":
                self.eat(); n = ("and", n, self.unary())
            elif p is not None and (p == "(" or p == "!" or re.match(r"[A-Za-z_]", p)):
                n = ("and", n, self.unary())
            else:
                return n

    def unary(self):
        if self.peek() == "!":
            self.eat(); return ("not", self.unary())
        n = self.atom()
        while self.peek() == "'":
            self.eat(); n = ("not", n)
        return n

    def atom(self):
        p = self.eat()
        if p == "(":
            n = self.expr(); self.eat(")"); return n
        if p == "CONST0":
            return ("c0",)
        if p == "CONST1":
            return ("c1",)
        return ("var", p)


def ev(node, env, mask):
    k = node[0]
    if k == "var":
        return env[node[1]]
    if k == "and":
        return ev(node[1], env, mask) & ev(node[2], env, mask)
    if k == "or":
        return ev(node[1], env, mask) | ev(node[2], env, mask)
    if k == "xor":
        return ev(node[1], env, mask) ^ ev(node[2], env, mask)
    if k == "not":
        return ~ev(node[1], env, mask) & mask
    if k == "c0":
        return 0
    if k == "c1":
        return mask
    raise ValueError(k)


def parse_genlib(path):
    gates, cur = {}, None
    text = open(path, encoding="utf-8").read()
    for raw in text.splitlines():
        line = raw.split("#")[0].strip()
        if not line:
            continue
        if line.startswith("GATE"):
            m = re.match(r"GATE\s+(\S+)\s+([0-9.eE+-]+)\s+(\S+)\s*=\s*(.*?);", line)
            if not m:
                raise ValueError("bad GATE line: " + line)
            name, area, out, expr = m.group(1), float(m.group(2)), m.group(3), m.group(4)
            ast = _P(_tokenize_expr(expr)).expr()
            cur = {"name": name, "area": area, "out": out, "ast": ast, "pins": {}, "star": None}
            gates[name] = cur
        elif line.startswith("PIN") and cur is not None:
            f = line.split()
            # PIN name phase input_load max_load rise_block rise_fanout fall_block fall_fanout
            d = max(float(f[5]), float(f[7]))
            if f[1] == "*":
                cur["star"] = d
            else:
                cur["pins"][f[1]] = d
    return gates


def pin_delay(g, pin):
    if pin in g["pins"]:
        return g["pins"][pin]
    if g["star"] is not None:
        return g["star"]
    raise KeyError("no delay for pin %s of %s" % (pin, g["name"]))

# ---------------- irredundant SOP (Minato-Morreale) for the BLIF covers ----------------
# The BLIF used for CEC gets irredundant covers instead of minterm lists, which keeps the
# strashed AIG small. Every cover is re-evaluated and asserted to equal the cell's truth table.

_VM = {k: [sum(1 << t for t in range(1 << k) if (t >> x) & 1) for x in range(k)] for k in range(0, 7)}
_FULL = {k: (1 << (1 << k)) - 1 for k in range(0, 7)}


def _cof(f, x, k, val):
    vm, sh, full = _VM[k][x], 1 << x, _FULL[k]
    h = (f & ~vm & full) if val == 0 else ((f & vm) >> sh)
    return h | (h << sh)


def _isop(L, U, k):
    full = _FULL[k]
    if L == 0:
        return [], 0
    if U == full:
        return [dict()], full
    x = next(x for x in range(k - 1, -1, -1)
             if _cof(L, x, k, 0) != _cof(L, x, k, 1) or _cof(U, x, k, 0) != _cof(U, x, k, 1))
    L0, L1, U0, U1 = _cof(L, x, k, 0), _cof(L, x, k, 1), _cof(U, x, k, 0), _cof(U, x, k, 1)
    c0, R0 = _isop(L0 & ~U1 & full, U0, k)
    c1, R1 = _isop(L1 & ~U0 & full, U1, k)
    c2, R2 = _isop((L0 & ~R0 & full) | (L1 & ~R1 & full), U0 & U1, k)
    vm = _VM[k][x]
    R = (R0 & ~vm & full) | (R1 & vm) | R2
    return [{**c, x: 0} for c in c0] + [{**c, x: 1} for c in c1] + c2, R


def isop_cover(tt, k):
    cubes, R = _isop(tt, tt, k)
    full = _FULL[k]
    chk = 0
    for c in cubes:
        m = full
        for x, val in c.items():
            m &= _VM[k][x] if val else (~_VM[k][x] & full)
        chk |= m
    assert R == tt and chk == tt, "ISOP cover mismatch"
    return cubes


# ---------------- AIGER (binary) ----------------

def read_aiger(path):
    data = open(path, "rb").read()
    nl = data.index(b"\n")
    hdr = data[:nl].decode().split()
    if hdr[0] != "aig":
        raise ValueError("only binary AIGER supported")
    M, I, L, O, A = map(int, hdr[1:6])
    pos = nl + 1
    latches = []
    for _ in range(L):
        e = data.index(b"\n", pos); latches.append(int(data[pos:e].split()[0])); pos = e + 1
    outs = []
    for _ in range(O):
        e = data.index(b"\n", pos); outs.append(int(data[pos:e])); pos = e + 1
    ands = []

    def varint():
        nonlocal pos
        x, sh = 0, 0
        while True:
            b = data[pos]; pos += 1
            x |= (b & 0x7F) << sh
            if not b & 0x80:
                return x
            sh += 7
    for i in range(A):
        lhs = 2 * (I + L + i + 1)
        d0 = varint(); d1 = varint()
        r0 = lhs - d0; r1 = r0 - d1
        ands.append((lhs, r0, r1))
    return {"I": I, "L": L, "O": O, "A": A, "outs": outs, "latch_next": latches, "ands": ands}


def sim_aiger(aig, pi_vals, mask):
    """Combinational simulation; latch outputs act as extra PIs and next-states as extra POs."""
    I, L = aig["I"], aig["L"]
    val = [0] * (2 * (I + L + aig["A"] + 1))
    val[1] = mask
    for k in range(I + L):
        v = 2 * (k + 1)
        val[v] = pi_vals[k]; val[v + 1] = ~pi_vals[k] & mask
    for lhs, r0, r1 in aig["ands"]:
        x = val[r0] & val[r1]
        val[lhs] = x; val[lhs + 1] = ~x & mask
    return [val[o] for o in aig["outs"]] + [val[n] for n in aig["latch_next"]]

# ---------------- structural Verilog ----------------

_ident = r"(?:\\\S+|[A-Za-z_][A-Za-z0-9_$]*(?:\[\d+\])?)"


def _norm(n):
    n = n.strip()
    if n.startswith("\\"):
        n = n[1:]
    return n.strip()


def parse_verilog(path):
    txt = open(path, encoding="utf-8").read()
    txt = re.sub(r"//[^\n]*", "", txt)
    txt = re.sub(r"/\*.*?\*/", "", txt, flags=re.S)
    stmts = [s.strip() for s in txt.split(";")]
    inputs, outputs, insts, assigns = [], [], [], []
    for s in stmts:
        if not s or s.startswith("endmodule"):
            s = s.replace("endmodule", "").strip()
            if not s:
                continue
        if s.startswith("module"):
            continue
        m = re.match(r"^(input|output|wire)\b(.*)$", s, flags=re.S)
        if m:
            body = m.group(2).strip()
            rng = re.match(r"^\[(\d+):(\d+)\](.*)$", body, flags=re.S)
            names = [x.strip() for x in (rng.group(3) if rng else body).split(",") if x.strip()]
            if rng:
                hi, lo = int(rng.group(1)), int(rng.group(2))
                step = -1 if hi >= lo else 1
                exp = []
                for nme in names:
                    for b in range(lo, hi + 1) if hi >= lo else range(lo, hi - 1, -1):
                        exp.append("%s[%d]" % (_norm(nme), b))
                names = exp
            names = [_norm(x) for x in names]
            if m.group(1) == "input":
                inputs += names
            elif m.group(1) == "output":
                outputs += names
            continue
        m = re.match(r"^assign\s+(.+?)\s*=\s*(.+)$", s, flags=re.S)
        if m:
            assigns.append((_norm(m.group(1)), _norm(m.group(2))))
            continue
        m = re.match(r"^(\S+)\s+([^\s(]+)\s*\((.*)\)\s*$", s, flags=re.S)
        if m:
            cell, conns = m.group(1), m.group(3)
            pins = {}
            for pm in re.finditer(r"\.(\w+)\s*\(\s*(" + _ident + r"|1'b[01])\s*\)", conns):
                pins[pm.group(1)] = _norm(pm.group(2))
            if len(pins) != conns.count("."):
                raise ValueError("pin parse mismatch in: %r" % s[:160])
            insts.append((cell, pins))
            continue
        raise ValueError("unparsed statement: %r" % s[:120])
    return inputs, outputs, insts, assigns


def build(genlib, inputs, outputs, insts, assigns):
    """Return (drivers dict net->('inst',idx)|('pi',k)|('const',0/1)|('alias',net), area)."""
    drv, area = {}, 0.0
    for k, n in enumerate(inputs):
        drv[n] = ("pi", k)
    drv["1'b0"] = ("const", 0); drv["1'b1"] = ("const", 1)
    for idx, (cell, pins) in enumerate(insts):
        g = genlib[cell]
        area += g["area"]
        o = pins[g["out"]]
        if o in drv:
            raise ValueError("multiply driven net " + o)
        drv[o] = ("inst", idx)
    for lhs, rhs in assigns:
        if lhs in drv:
            raise ValueError("multiply driven net " + lhs)
        drv[lhs] = ("alias", rhs)
    return drv, area


def topo_eval(genlib, inputs, outputs, insts, drv, fn_inst, fn_leaf):
    """Generic memoized evaluation over the netlist DAG (iterative, no recursion)."""
    memo = {}
    for root in outputs:
        stack = [root]
        while stack:
            n = stack[-1]
            if n in memo:
                stack.pop(); continue
            d = drv.get(n)
            if d is None:
                raise ValueError("undriven net " + n)
            if d[0] in ("pi", "const"):
                memo[n] = fn_leaf(d); stack.pop(); continue
            if d[0] == "alias":
                if d[1] in memo:
                    memo[n] = memo[d[1]]; stack.pop()
                else:
                    stack.append(d[1])
                continue
            cell, pins = insts[d[1]]
            g = genlib[cell]
            missing = [net for p, net in pins.items() if p != g["out"] and net not in memo]
            if missing:
                stack.extend(missing); continue
            memo[n] = fn_inst(g, {p: memo[net] for p, net in pins.items() if p != g["out"]})
            stack.pop()
    return [memo[o] for o in outputs]


def main():
    a = sys.argv[1:]
    npat = int(a[a.index("--patterns") + 1]) if "--patterns" in a else 4096
    seed = int(a[a.index("--seed") + 1]) if "--seed" in a else 20260925
    genlib_path, ref_path, net_path, blif_path = a[0], a[1], a[2], a[3]
    genlib = parse_genlib(genlib_path)
    inputs, outputs, insts, assigns = parse_verilog(net_path)
    drv, area = build(genlib, inputs, outputs, insts, assigns)

    # 1. STA with load-independent pin delays
    arr = topo_eval(genlib, inputs, outputs, insts, drv,
                    lambda g, ins: max([ins[p] + pin_delay(g, p) for p in ins] or [0.0]),
                    lambda d: 0.0)
    delay = max(arr) if arr else 0.0

    # 2. BLIF from own truth tables
    with open(blif_path, "w", encoding="utf-8") as f:
        f.write(".model mapped\n.inputs %s\n.outputs %s\n" % (" ".join(inputs), " ".join(outputs)))
        f.write(".names c0_\n.names c1_\n1\n")
        def nm(n):
            return {"1'b0": "c0_", "1'b1": "c1_"}.get(n, n)
        for cell, pins in insts:
            g = genlib[cell]
            ins = [p for p in pins if p != g["out"]]
            k = len(ins)
            mask = (1 << (1 << k)) - 1
            env = {}
            for j, p in enumerate(ins):
                v = 0
                for t in range(1 << k):
                    if (t >> j) & 1:
                        v |= 1 << t
                env[p] = v
            tt = ev(g["ast"], env, mask)
            f.write(".names %s %s\n" % (" ".join(nm(pins[p]) for p in ins), nm(pins[g["out"]])))
            for cube in isop_cover(tt, k):
                f.write(("%s 1\n" % "".join("-" if j not in cube else str(cube[j]) for j in range(k))) if k else "1\n")
        for lhs, rhs in assigns:
            f.write(".names %s %s\n1 1\n" % (nm(rhs), nm(lhs)))
        f.write(".end\n")

    # 3. Random simulation against the reference AIG
    aig = read_aiger(ref_path)
    n_ci = aig["I"] + aig["L"]
    verdict, cex = "SIM_AGREE", None
    if n_ci != len(inputs) or aig["O"] + aig["L"] != len(outputs):
        verdict = "INTERFACE_MISMATCH"
    else:
        rng = random.Random(seed)
        mask = (1 << npat) - 1
        pis = [rng.getrandbits(npat) for _ in range(n_ci)]
        # pattern 0 = all zeros, pattern 1 = all ones
        pis = [(v & ~3 & mask) | 2 for v in pis]
        ref = sim_aiger(aig, pis, mask)
        env_pi = pis
        got = topo_eval(genlib, inputs, outputs, insts, drv,
                        lambda g, ins: ev(g["ast"], ins, mask),
                        lambda d: env_pi[d[1]] if d[0] == "pi" else (mask if d[1] else 0))
        for k, (r, gv) in enumerate(zip(ref, got)):
            diff = (r ^ gv) & mask
            if diff:
                bit = (diff & -diff).bit_length() - 1
                verdict = "SIM_MISMATCH"
                cex = {"po_index": k, "po_name": outputs[k], "pattern_bit": bit,
                       "pi_values": "".join(str((v >> bit) & 1) for v in pis),
                       "ref": (r >> bit) & 1, "mapped": (gv >> bit) & 1}
                break
    cells = {}
    for cell, _ in insts:
        cells[cell] = cells.get(cell, 0) + 1
    print(json.dumps({"area": round(area, 6), "delay": round(delay, 6), "instances": len(insts),
                      "inputs": len(inputs), "outputs": len(outputs), "sim_patterns": npat,
                      "sim_verdict": verdict, "cex": cex, "cells": cells}))


if __name__ == "__main__":
    main()
