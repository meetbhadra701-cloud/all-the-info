#!/usr/bin/env python3
"""C1 / D2 cause-isolation runner. It reuses d1_run's mapping, evaluation and CEC functions.
Records go to experiments/results/c1_d2/<bench>.jsonl and netlists to experiments/outputs/c1/d2/."""
import os, sys, json
os.environ.setdefault("CEC_MODE", "two_stage")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import d1_run as R
R.OUT = R.W + "/experiments/outputs/c1/d2"
R.RES = R.W + "/experiments/results/c1_d2"


def main():
    os.makedirs(R.RES, exist_ok=True)
    for bench in sys.argv[1:]:
        os.makedirs("%s/%s" % (R.OUT, bench), exist_ok=True)
        fn = "%s/%s.jsonl" % (R.RES, bench)
        recs = {}
        if os.path.exists(fn):
            for l in open(fn):
                if l.strip():
                    d = json.loads(l); recs[d["tag"]] = d
        def once(tag, thunk):
            if tag not in recs:
                rec = thunk(); recs[tag] = rec
                with open(fn, "a") as f:
                    f.write(json.dumps(rec) + "\n")
            return recs[tag]
        for v in ("ab1", "ab2"):
            once("E:" + v, lambda v=v: R.run_mt(bench, "E:" + v, "drv_" + v, "map", 0.0))
        for v in ("ab1", "ab2"):
            dv = recs["E:" + v].get("eval_delay")
            if dv:
                once("I:initial@" + v, lambda dv=dv, v=v: R.run_mt(bench, "I:initial@" + v, "drv_initial", "map", dv))
        print("done", bench, flush=True)


if __name__ == "__main__":
    main()
