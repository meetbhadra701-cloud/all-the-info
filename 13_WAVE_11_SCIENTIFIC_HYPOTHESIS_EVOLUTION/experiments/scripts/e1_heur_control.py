#!/usr/bin/env python3
"""Wave 11 / E1 model-fidelity control: rebuild map's own final cover from a dump, re-check it under the model, and
write it as a netlist for the independent evaluator. usage: e1_heur_control.py DUMP.json GENLIB OUT.v"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e1_model  # noqa: E402

sp = e1_model.Space(sys.argv[1], sys.argv[2], -1)
res = {"dump": os.path.basename(sys.argv[1]), "mapper_area": sp.dump["area"], "mapper_delay": sp.dump["delay"]}
try:
    impl, neg = sp.heuristic_cover()
    area, delay = sp.check(impl, neg)
    res.update({"model_area": area / 100.0, "model_delay": delay / 100.0, "instances": sp.emit(impl, neg, sys.argv[3]),
                "verdict": "OK"})
except ValueError as e:
    res.update({"verdict": "ERROR", "error": str(e)})
print(json.dumps(res))
