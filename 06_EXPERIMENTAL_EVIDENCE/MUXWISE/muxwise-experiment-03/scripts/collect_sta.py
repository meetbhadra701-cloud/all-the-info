#!/usr/bin/env python3
from __future__ import annotations
import csv, re
from pathlib import Path
root = Path(__file__).resolve().parents[1]
rows=[]
tag_re=re.compile(r"^(fir4|mixed|add_chain)_w(\d+)_(normal|arith_tree)$")
arrival_re=re.compile(r"^\s*(-?[0-9.]+)\s+data arrival time\s*$", re.M)
slack_re=re.compile(r"worst slack\s+max\s+(-?[0-9.]+)", re.I)
tns_re=re.compile(r"tns\s+max\s+(-?[0-9.]+)", re.I)
for log in sorted((root/'logs'/'sta').glob('*.sdc.log')):
    mfile=re.match(r"^(.*)_(preliminary|relaxed|aggressive)\.sdc\.log$", log.name)
    if not mfile: continue
    tag, constraint_name=mfile.groups(); m=tag_re.match(tag)
    if not m: continue
    text=log.read_text(errors='replace')
    arrivals=[float(x) for x in arrival_re.findall(text)]
    slacks=[float(x) for x in slack_re.findall(text)]
    tnss=[float(x) for x in tns_re.findall(text)]
    constraint={'preliminary':'preliminary_100ns','relaxed':'relaxed_10ns','aggressive':'aggressive_1.5ns'}[constraint_name]
    rows.append({'design':m.group(1),'width':m.group(2),'config':m.group(3),'constraint':constraint,'sta_status':'PASS' if arrivals else 'FAILED','critical_path_delay_ns':max(arrivals) if arrivals else '','worst_slack_ns':slacks[-1] if slacks else '','total_negative_slack_ns':tnss[-1] if tnss else '','report':str(log)})
out=root/'results'/'timing_comparison.csv'
with out.open('w',newline='') as f:
    fields=list(rows[0]) if rows else ['design','width','config','constraint','sta_status']
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
print(f'wrote {out} ({len(rows)} rows)')
