#!/usr/bin/env python3
"""Wave 11 / E1 orchestrator. Runs inside openroad/orfs:latest (--network none).

usage: e1_run.py PHASE BENCH [BENCH ...]      PHASE = A | B
  A: map dumps at D0 and D1 (map itself is the first baseline), model-fidelity controls, same-D baselines (emap,
     ABC &nf -p, &nf -p -a), the full-space exact model at D0 and D1, and the no-timing lower bound.
  B: the eps-restricted exact models (EPS_LIST, default "0.05 0 0.2") at D0 and D1.
Budgets (env): T_FULL (600 s), T_EPS (300 s), T_LB (300 s), WORKERS (4 CP-SAT workers).

Every netlist, heuristic or solver-derived, is evaluated by e1_eval_netlist.sh: the Wave 10 evaluator (copy with a
cycle guard: c1_eval_w11.py) for area, STA and 4096-pattern simulation against the ORIGINAL AIG, then ABC `cec` of
its own BLIF against the original AIG. One JSON line per tag in experiments/results/e1/<bench>.jsonl; resumable."""
import gzip
import json
import math
import os
import shutil
import subprocess
import sys
import time

W10 = "/r/12_WAVE_10_EXPERIMENTAL_DISCOVERY"
W11 = "/r/13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION"
MT = W10 + "/third_party/MappingEvolve/third-party/mockturtle/experiments"
G = MT + "/cell_libraries/asap7.genlib"
C2 = W10 + "/experiments/inputs/c1/c2"
BIN10 = W10 + "/experiments/outputs/c1/bin"
DUMPBIN = W11 + "/experiments/bin/drv_dump"
SC = W11 + "/experiments/scripts"
SET = os.environ.get("E1_SET", "")  # empty for the real runs; a name for smoke tests (separate directories)
OUT = W11 + "/experiments/outputs/e1/" + (SET or "runs")
RES = W11 + "/experiments/results/e1" + ("_" + SET if SET else "")
T_FULL = int(os.environ.get("T_FULL", "600"))
T_EPS = int(os.environ.get("T_EPS", "300"))
T_LB = int(os.environ.get("T_LB", "300"))
WORKERS = int(os.environ.get("WORKERS", "4"))
EPS_LIST = [float(e) for e in os.environ.get("EPS_LIST", "0.05 0 0.2").split()]


def sh(cmd, timeout=7200, env=None):
    t0 = time.time()
    e = dict(os.environ)
    if env:
        e.update(env)
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, env=e)
        return p.returncode, p.stdout, p.stderr, time.time() - t0
    except subprocess.TimeoutExpired as ex:
        so = ex.stdout.decode() if isinstance(ex.stdout, bytes) else (ex.stdout or "")
        return "TIMEOUT", so, "", time.time() - t0


def last_json(txt):
    for line in reversed(txt.strip().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                pass
    return None


def evaluate(bench, vpath, rec):
    if not os.path.exists(vpath):
        rec["eval"] = None
        return rec
    rc, so, se, dt = sh("bash %s/e1_eval_netlist.sh %s %s" % (SC, bench, vpath), 7200)
    ev = last_json(so)
    rec["eval"] = ev if ev is not None else {"error": (so + se)[-400:]}
    rec["eval_wall"] = round(dt, 2)
    return rec


def gz(path):
    if os.path.exists(path):
        with open(path, "rb") as fi, gzip.open(path + ".gz", "wb") as fo:
            shutil.copyfileobj(fi, fo)
        os.remove(path)


def run_dump(bench, dtag, required):
    d = "%s/%s" % (OUT, bench)
    prefix = "%s/map_%s" % (d, dtag)
    rc, so, se, dt = sh("%s %s %s/%s.aig %s map %.9f" % (DUMPBIN, G, C2, bench, prefix, required), 3600,
                        env={"C1_DUMP": "%s/%s.dump.json" % (d, dtag)})
    r = last_json(so)
    rec = {"bench": bench, "tag": "map:" + dtag, "required_param": required, "rc": rc, "wall": round(dt, 2), "tool": r}
    return evaluate(bench, prefix + ".v", rec)


def run_heur(bench, dtag):
    d = "%s/%s" % (OUT, bench)
    rc, so, se, dt = sh("python3 %s/e1_heur_control.py %s/%s.dump.json %s %s/heur_%s.v" % (SC, d, dtag, G, d, dtag), 3600)
    rec = {"bench": bench, "tag": "heur:" + dtag, "control": last_json(so), "stderr": se[-300:] if se else ""}
    return evaluate(bench, "%s/heur_%s.v" % (d, dtag), rec)


def run_cpsat(bench, tag, dtag, D, eps, tmo, notiming=False):
    d = "%s/%s" % (OUT, bench)
    prefix = "%s/%s" % (d, tag.replace(":", "_"))
    rc, so, se, dt = sh("python3 %s/e1_cpsat.py %s/%s.dump.json %s %.9f %s %d %d %s" % (
        SC, d, dtag, G, D, eps, tmo, WORKERS, prefix), tmo + 3600, env={"E1_NOTIMING": "1" if notiming else "0"})
    rec = {"bench": bench, "tag": tag, "D": D, "eps": eps, "notiming": notiming, "wall": round(dt, 2),
           "solver": last_json(so), "stderr": se[-400:] if se else ""}
    gz(prefix + ".cpmodel.txt")
    gz(prefix + ".solver.log")
    if rec["solver"] and str(rec["solver"].get("verdict", "")).startswith("SOLVED"):
        evaluate(bench, prefix + ".v", rec)
    return rec


def run_emap(bench, dtag, D):
    prefix = "%s/%s/emap_%s" % (OUT, bench, dtag)
    rc, so, se, dt = sh("%s/drv_emap %s %s/%s.aig %s emap %.9f 0.0" % (BIN10, G, C2, bench, prefix, D), 3600)
    rec = {"bench": bench, "tag": "emap:" + dtag, "required_param": D, "rc": rc, "wall": round(dt, 2), "tool": last_json(so)}
    return evaluate(bench, prefix + ".v", rec)


def run_abc(bench, tag, opts):
    prefix = "%s/%s/%s" % (OUT, bench, tag.replace(":", "_"))
    cmd = 'yosys-abc -q "read_genlib %s; read_aiger %s/%s.aig; &get -n; &nf %s; &put; write_verilog %s.v"' % (G, C2, bench, opts, prefix)
    rc, so, se, dt = sh(cmd, 3600)
    rec = {"bench": bench, "tag": tag, "opts": "&nf " + opts, "rc": rc, "wall": round(dt, 2)}
    return evaluate(bench, prefix + ".v", rec)


def main():
    phase = sys.argv[1]
    os.makedirs(RES, exist_ok=True)
    for bench in sys.argv[2:]:
        os.makedirs("%s/%s" % (OUT, bench), exist_ok=True)
        fn = "%s/%s.jsonl" % (RES, bench)
        recs = {}
        if os.path.exists(fn):
            for line in open(fn):
                if line.strip():
                    r = json.loads(line)
                    recs[r["tag"]] = r

        def once(tag, thunk):
            if tag not in recs:
                r = thunk()
                recs[tag] = r
                with open(fn, "a") as f:
                    f.write(json.dumps(r) + "\n")
                print(time.strftime("%H:%M:%S"), bench, tag, "done", flush=True)
            return recs[tag]

        m0 = once("map:D0", lambda: run_dump(bench, "D0", 0.0))
        if not m0.get("tool"):
            print("map dump failed", bench, flush=True)
            continue
        D0 = float(m0["tool"]["delay"]) + 0.001
        D1 = 1.10 * D0
        once("map:D1", lambda: run_dump(bench, "D1", D1))
        Ds = {"D0": D0, "D1": D1}
        if phase == "A":
            for dtag in ("D0", "D1"):
                once("heur:" + dtag, lambda dtag=dtag: run_heur(bench, dtag))
            for dtag, D in Ds.items():
                once("emap:" + dtag, lambda dtag=dtag, D=D: run_emap(bench, dtag, D))
            nfp = once("nfp", lambda: run_abc(bench, "nfp", "-p"))
            d_nfp = (nfp.get("eval") or {}).get("delay")
            if d_nfp:
                for dtag, D in Ds.items():
                    rr = max(0, int(math.floor(100.0 * (D / d_nfp - 1.0) + 1e-9)))
                    once("nfp:" + dtag, lambda dtag=dtag, rr=rr: run_abc(bench, "nfp:" + dtag, "-p -R %d" % rr))
                    once("nfpa:" + dtag, lambda dtag=dtag, rr=rr: run_abc(bench, "nfpa:" + dtag, "-p -a -R %d" % rr))
            for dtag, D in Ds.items():
                once("full:" + dtag, lambda dtag=dtag, D=D: run_cpsat(bench, "full:" + dtag, dtag, D, -1, T_FULL))
            once("lb:D0", lambda: run_cpsat(bench, "lb:D0", "D0", 1e9, -1, T_LB, notiming=True))
        elif phase == "B":
            for eps in EPS_LIST:
                for dtag, D in Ds.items():
                    tag = "eps%g:%s" % (eps, dtag)
                    once(tag, lambda tag=tag, dtag=dtag, D=D, eps=eps: run_cpsat(bench, tag, dtag, D, eps, T_EPS))
        print("done", bench, phase, flush=True)


if __name__ == "__main__":
    main()
