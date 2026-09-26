#!/usr/bin/env bash
# Extract ORFS CI metric expectations (rules-base.json) for every design: where does the open flow itself expect trouble?
D="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
"$D" run --rm --network none --entrypoint /bin/bash openroad/orfs:latest -c '
cd /OpenROAD-flow-scripts/flow/designs
python3 - <<PY
import json, glob, os
rows=[]
for f in sorted(glob.glob("*/*/rules-base.json")):
    pdk, des = f.split("/")[:2]
    try: r=json.load(open(f))
    except Exception as e: continue
    def g(k):
        v=r.get(k,{})
        return v.get("value") if isinstance(v,dict) else v
    rows.append((pdk,des,g("finish__timing__setup__ws"),g("finish__timing__setup__tns") if "finish__timing__setup__tns" in r else g("finish__timing__drv__setup_violation_count"),
                 g("detailedroute__route__drc_errors"),g("finish__design__instance__area"),g("cts__timing__setup__ws"),g("globalroute__timing__setup__ws")))
print("pdk,design,finish_setup_ws_rule,finish_setup_tns_or_viol_rule,drt_drc_rule,finish_area_rule,cts_ws_rule,grt_ws_rule")
for x in rows: print(",".join(str(v) for v in x))
PY
ls */*/rules-base.json | wc -l
cat asap7/ibex/rules-base.json | head -60
'
