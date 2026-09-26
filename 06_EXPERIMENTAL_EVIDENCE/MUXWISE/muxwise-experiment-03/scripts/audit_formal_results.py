#!/usr/bin/env python3
"""Audit proof logs without treating a zero Yosys exit code as a proof PASS."""
from __future__ import annotations
import csv
from pathlib import Path
root=Path(__file__).resolve().parents[1]
cases=[
 ('fir4',8,'normal','logs/formal/fir4_w8_normal.log','direct in-process proof'),
 ('fir4',8,'arith_tree','logs/formal/fir4_w8_arith_tree.log','direct in-process proof'),
 ('fir4',16,'normal','logs/formal/fir4_w16_normal.log','direct proof interrupted before completion'),
 ('fir4',16,'arith_tree','', 'not completed'),
 ('mixed',16,'normal','', 'not completed'),('mixed',16,'arith_tree','', 'not completed'),
 ('mixed',32,'normal','', 'not completed'),('mixed',32,'arith_tree','', 'not completed'),
 ('add_chain',16,'normal','', 'not completed'),('add_chain',16,'arith_tree','', 'not completed'),
 ('add_chain',64,'normal','', 'not completed'),('add_chain',64,'arith_tree','', 'not completed'),
]
rows=[]
for design,width,config,rel,method in cases:
  text=(root/rel).read_text(errors='replace') if rel and (root/rel).exists() else ''
  if 'interrupted' in method: result='INCONCLUSIVE_INTERRUPTED'
  elif 'SAT proof finished - no model found: SUCCESS!' in text: result='PASS'
  elif 'SAT proof finished - model found: FAIL!' in text: result='FAIL'
  elif 'ERROR:' in text and rel: result='INCONCLUSIVE_SETUP_OR_INTERRUPTED'
  else: result='NOT_EXECUTED'
  rows.append({'design':design,'width':width,'config':config,'result':result,'method':method,'evidence_log':rel or ''})
out=root/'results'/'formal_comparison.csv'
with out.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(f'wrote {out} ({len(rows)} rows)')
