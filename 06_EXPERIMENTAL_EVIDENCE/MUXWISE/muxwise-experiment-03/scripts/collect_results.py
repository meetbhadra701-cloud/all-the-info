#!/usr/bin/env python3
from __future__ import annotations
import csv, re
from pathlib import Path

root=Path(__file__).resolve().parents[1]
std={}
with (root/'results'/'standard_cell_mapping.csv').open() as f:
  for x in csv.DictReader(f): std[(x['design'],x['width'],x['config'])]=x
rows=[]
tag_re=re.compile(r'^(fir4|mixed|add_chain)_w(\d+)_(normal|arith_tree)_aggressive\.log$')
num_re=lambda word: re.compile(rf'{word} max (-?[0-9.]+)',re.I)
for log in sorted((root/'logs'/'physical').glob('*.log')):
  m=tag_re.match(log.name)
  if not m: continue
  design,width,config=m.groups(); text=log.read_text(errors='replace')
  areas=[float(x) for x in re.findall(r'Design area\s+([0-9.]+) um\^2',text)]
  arrivals=[float(x) for x in re.findall(r'^\s*(-?[0-9.]+)\s+data arrival time\s*$',text,re.M)]
  slacks=[float(x) for x in num_re('worst slack').findall(text)]
  tnss=[float(x) for x in num_re('tns').findall(text)]
  wire_section=text.split('Global route wire length by layer:')[-1].split('Startpoint:')[0]
  wires=[float(x) for x in re.findall(r'^metal\d+\s+([0-9.]+)um',wire_section,re.M)]
  runtimes=re.findall(r'MUXWISE_PHYSICAL_WALL_SECONDS=([0-9.]+)',text)
  base=std.get((design,width,config),{})
  rows.append({'design':design,'width':width,'config':config,'constraint':'aggressive_1.5ns','physical_stage':'global_route','liberty':'NangateOpenCellLibrary_typical.lib','mapped_cell_area_um2':base.get('cell_area',''),'placed_design_area_um2':areas[-1] if areas else '','cell_count':base.get('cell_count',''),'placement_delay_ns':arrivals[0] if len(arrivals)>0 else '','placement_worst_slack_ns':slacks[0] if len(slacks)>0 else '','placement_tns_ns':tnss[0] if len(tnss)>0 else '','global_route_delay_ns':arrivals[-1] if len(arrivals)>1 else '','global_route_worst_slack_ns':slacks[-1] if len(slacks)>1 else '','global_route_tns_ns':tnss[-1] if len(tnss)>1 else '','global_route_wirelength_um':sum(wires) if wires else '','physical_runtime_seconds':runtimes[-1] if runtimes else '','formal_result':'SEE formal_comparison.csv','log':str(log),'status':'MEASURED' if len(arrivals)>=2 and len(slacks)>=2 else 'FAILED_OR_UNPARSED'})
out=root/'results'/'physical_design.csv'
fields=list(rows[0]) if rows else ['design','width','config','status']
with out.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
print(f'wrote {out} ({len(rows)} rows)')
