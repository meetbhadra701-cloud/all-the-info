#!/usr/bin/env python3
"""C1 / D1 orchestrator. Runs inside openroad/orfs:latest (--network none).

usage: d1_run.py BENCH [BENCH ...]

For each benchmark it runs every configuration in the pre-registration
(experiments/results/c1_PREREGISTRATION.md). Each netlist is evaluated independently:
c1_eval.py (its own area/STA, plus random simulation against the ORIGINAL AIG), then
ABC &cec of the c1_eval BLIF against the original AIG.
It writes one JSON line per configuration to experiments/results/c1_d1/<bench>.jsonl.
The verdict fails closed: only the literal "Networks are equivalent" counts as a CEC PASS.
"""
import gzip
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time

W = "/w"
BIN = W + "/experiments/outputs/c1/bin"
MT = W + "/third_party/MappingEvolve/third-party/mockturtle/experiments"
G = MT + "/cell_libraries/asap7.genlib"
ORIG = MT + "/benchmarks"
C2 = W + "/experiments/inputs/c1/c2"
EVAL = W + "/experiments/scripts/c1/c1_eval.py"
OUT = W + "/experiments/outputs/c1/d1"
RES = W + "/experiments/results/c1_d1"
EVOLVED = ["gpt5_it29", "deepseek_it24", "qwen_it20"]
RELAX_INIT = [2, 4, 6, 8, 10, 15, 20, 30, 50]
RELAX_EMAP = [5, 10, 20]
RELAX_NF = [2, 5, 10, 20, 30]
CEC_T = int(os.environ.get("CEC_T", "900"))


def sh(cmd, timeout=7200):
    t0 = time.time()
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr, time.time() - t0
    except subprocess.TimeoutExpired as e:
        return "TIMEOUT", (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or ""), "", time.time() - t0


def last_json(txt):
    for line in reversed(txt.strip().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                pass
    return None


CEC_MODE = os.environ.get("CEC_MODE", "direct")


def _cec_pair(a, b):
    rc, so, se, dt = sh('yosys-abc -q "cec -n -T %d -C 100000 %s %s"' % (CEC_T, a, b), CEC_T + 600)
    txt = so + se
    line = next((l for l in txt.splitlines() if "Networks are" in l or "UNDECIDED" in l.upper()), txt.strip()[-200:])
    if re.search(r"^Networks are equivalent", txt, flags=re.M):
        v = "PASS"
    elif "NOT EQUIVALENT" in txt:
        v = "NEQ"
    else:
        v = "UNDECIDED"
    return v, dt, line.strip()


def stage_a(bench):
    """Two-stage mode, stage A: the original AIG equals the compress2 AIG. Checked once per benchmark and cached."""
    fn = "%s/../c1_d1_stageA_%s.json" % (RES, bench)
    if os.path.exists(fn):
        return json.load(open(fn))["verdict"]
    v, dt, line = _cec_pair("%s/%s.aig" % (ORIG, bench), "%s/%s.aig" % (C2, bench))
    json.dump({"bench": bench, "verdict": v, "seconds": round(dt, 3), "line": line}, open(fn, "w"))
    return v


def cec(bench, prefix):
    """Returns (verdict, seconds, raw_line). The verdict is PASS, NEQ or UNDECIDED; it fails closed.
    Direct mode checks the original AIG against the netlist in one step. Two-stage mode (CEC_MODE=two_stage)
    checks original == compress2 AIG once (stage A) and compress2 AIG == netlist per config (stage B);
    the result follows by transitivity and is much faster on hyp (T4: 26 s + 36 s, against 1310 s direct)."""
    mine = prefix + "_mine.aig"
    rc, so, se, _ = sh('yosys-abc -q "read_blif %s.blif; strash; write_aiger %s"' % (prefix, mine), 1800)
    if not os.path.exists(mine):
        return "UNDECIDED", 0.0, "blif->aig failed: " + (so + se)[-200:]
    if CEC_MODE == "two_stage":
        va = stage_a(bench)
        vb, dt, lineb = _cec_pair("%s/%s.aig" % (C2, bench), mine)
        if va == "PASS" and vb == "PASS":
            v = "PASS"
        elif (va == "PASS" and vb == "NEQ") or (va == "NEQ" and vb == "PASS"):
            v = "NEQ"
        else:
            v = "UNDECIDED"
        return v, dt, "two-stage A(orig==c2)=%s; B(c2==netlist): %s" % (va, lineb)
    # ABC's old `cec` engine (FRAIG + SAT), matching by order. The T3 profile showed that on log2 it
    # finishes in about 9 s where &cec takes 80-150 s or longer. The netlist interpretation (c1_eval BLIF)
    # stays independent of mockturtle, and random simulation is the second, fully independent check.
    rc, so, se, dt = sh('yosys-abc -q "cec -n -T %d -C 100000 %s/%s.aig %s"' % (CEC_T, ORIG, bench, mine), CEC_T + 600)
    txt = so + se
    line = next((l for l in txt.splitlines() if "Networks are" in l or "UNDECIDED" in l.upper()), txt.strip()[-200:])
    if re.search(r"^Networks are equivalent", txt, flags=re.M):
        v = "PASS"
    elif "NOT EQUIVALENT" in txt:
        v = "NEQ"
    else:
        v = "UNDECIDED"
    return v, dt, line.strip()


def evaluate(bench, prefix, rec, do_cec=True):
    rc, so, se, dt = sh("python3 %s %s %s/%s.aig %s.v %s.blif" % (EVAL, G, ORIG, bench, prefix, prefix), 7200)
    ev = last_json(so)
    rec["eval_wall"] = round(dt, 3)
    if ev is None:
        rec["eval_error"] = (so + se)[-400:]
        rec["sim_verdict"] = "EVAL_ERROR"
    else:
        rec.update({"eval_area": ev["area"], "eval_delay": ev["delay"], "instances": ev["instances"],
                    "sim_verdict": ev["sim_verdict"], "cex": ev["cex"], "cells": ev["cells"]})
    if do_cec and ev is not None:
        v, t, line = cec(bench, prefix)
        rec.update({"cec_verdict": v, "cec_wall": round(t, 3), "cec_line": line})
    # keep the netlist (gzipped) as evidence; drop derivable intermediates
    if os.path.exists(prefix + ".v"):
        with open(prefix + ".v", "rb") as fi, gzip.open(prefix + ".v.gz", "wb") as fo:
            shutil.copyfileobj(fi, fo)
        os.remove(prefix + ".v")
    for ext in (".bench", ".blif", "_mine.aig"):
        if os.path.exists(prefix + ext):
            os.remove(prefix + ext)
    return rec


def run_mt(bench, tag, binary, mode, required, relax=None):
    prefix = "%s/%s/%s" % (OUT, bench, tag)
    cmd = "%s/%s %s %s/%s.aig %s %s %.6f" % (BIN, binary, G, C2, bench, prefix, mode, required)
    if relax is not None:
        cmd += " %.3f" % relax
    rc, so, se, dt = sh(cmd, 7200)
    r = last_json(so)
    rec = {"bench": bench, "tag": tag, "tool": binary, "mode": mode, "required_param": required, "relax_param": relax,
           "map_rc": rc, "map_wall": round(dt, 3)}
    if r is None:
        rec["map_error"] = (so + se)[-400:]
        return rec
    rec.update({"tool_area": r["area"], "tool_delay": r["delay"], "gates": r["gates"], "depth": r["depth"],
                "mapping_error": r["mapping_error"]})
    return evaluate(bench, prefix, rec)


def run_abc(bench, tag, opts):
    prefix = "%s/%s/%s" % (OUT, bench, tag)
    cmd = 'yosys-abc -q "read_genlib %s; read_aiger %s/%s.aig; &get -n; &nf %s; &put; print_stats; write_verilog %s.v"' % (
        G, C2, bench, opts, prefix)
    rc, so, se, dt = sh(cmd, 7200)
    rec = {"bench": bench, "tag": tag, "tool": "abc_nf", "mode": "&nf " + opts, "map_rc": rc, "map_wall": round(dt, 3)}
    m = re.search(r"area\s*=\s*([0-9.]+)\s+delay\s*=\s*([0-9.]+)", so + se)
    if m:
        rec.update({"tool_area": float(m.group(1)), "tool_delay": float(m.group(2))})
    if not os.path.exists(prefix + ".v"):
        rec["map_error"] = (so + se)[-400:]
        return rec
    return evaluate(bench, prefix, rec)


def main():
    os.makedirs(RES, exist_ok=True)
    for bench in sys.argv[1:]:
        os.makedirs("%s/%s" % (OUT, bench), exist_ok=True)
        fn = "%s/%s.jsonl" % (RES, bench)
        done = set()
        if os.path.exists(fn):
            done = {json.loads(l)["tag"] for l in open(fn) if l.strip()}
        recs = {}
        if os.path.exists(fn):
            for l in open(fn):
                if l.strip():
                    d = json.loads(l); recs[d["tag"]] = d

        def emit(rec):
            recs[rec["tag"]] = rec
            with open(fn, "a") as f:
                f.write(json.dumps(rec) + "\n")

        def once(tag, thunk):
            if tag not in done:
                emit(thunk())
                done.add(tag)
            return recs.get(tag)

        # 1. default (required = own best) runs of the initial and evolved operators
        for v in ["initial"] + EVOLVED:
            once("E:" + v, lambda v=v: run_mt(bench, "E:" + v, "drv_" + v, "map", 0.0))
        d_init = recs["E:initial"].get("eval_delay")
        # 2. in-framework relaxation sweep, plus the skip-delay-round mode
        for r in RELAX_INIT:
            once("R:initial:%d" % r, lambda r=r: run_mt(bench, "R:initial:%d" % r, "drv_initial", "map", d_init * (1 + r / 100.0)))
        once("N:initial", lambda: run_mt(bench, "N:initial", "drv_initial", "map_nodelay", 0.0))
        # 3. iso-delay baselines at each evolved variant's achieved delay.
        #    ABC &nf ignores -D in this build (T2 smoke test), so ABC gets -R = floor(100*(Dv/D_nfp - 1)),
        #    which never gives the baseline more slack than the evolved mapper had.
        once("B:nf", lambda: run_abc(bench, "B:nf", ""))
        once("B:nfp", lambda: run_abc(bench, "B:nfp", "-p"))
        d_nfp = recs["B:nfp"].get("eval_delay")
        for v in EVOLVED:
            dv = recs["E:" + v].get("eval_delay")
            if dv is None:
                continue
            once("I:initial@" + v, lambda dv=dv, v=v: run_mt(bench, "I:initial@" + v, "drv_initial", "map", dv))
            once("I:emap@" + v, lambda dv=dv, v=v: run_mt(bench, "I:emap@" + v, "drv_emap", "emap", dv, 0.0))
            if d_nfp:
                rr = max(0, int(math.floor(100.0 * (dv / d_nfp - 1.0) + 1e-9)))
                once("I:nfp@" + v, lambda rr=rr, v=v: run_abc(bench, "I:nfp@" + v, "-p -R %d" % rr))
        # 4. stronger-baseline reference points
        once("B:emap", lambda: run_mt(bench, "B:emap", "drv_emap", "emap", 0.0, 0.0))
        once("B:emap_area", lambda: run_mt(bench, "B:emap_area", "drv_emap", "emap_area", 0.0, 0.0))
        for r in RELAX_EMAP:
            once("R:emap:%d" % r, lambda r=r: run_mt(bench, "R:emap:%d" % r, "drv_emap", "emap", 0.0, float(r)))
        for r in RELAX_NF:
            once("R:nfp:%d" % r, lambda r=r: run_abc(bench, "R:nfp:%d" % r, "-p -R %d" % r))
        print("done", bench, flush=True)


if __name__ == "__main__":
    main()
