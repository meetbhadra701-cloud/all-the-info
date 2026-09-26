#!/usr/bin/env python3
from __future__ import annotations
import csv, subprocess, time
from pathlib import Path
root=Path(__file__).resolve().parents[1]; run=root/'scripts'/'run_current.sh'
ysdir=root/'work'/'formal_ys'; logdir=root/'logs'/'formal'; ysdir.mkdir(exist_ok=True,parents=True); logdir.mkdir(exist_ok=True,parents=True)
cases=[('fir4_w4','fir4.v','fir4'),('add_chain_w4','add_chain.v','add_chain')]
rows=[]
for tag,source,top in cases:
  ys=ysdir/f'{tag}_default_arith_tree.ys'; log=logdir/f'{tag}_default_arith_tree.log'
  ys.write_text(f'''read_verilog -sv reproducers/{source}
chparam -set W 4 {top}
hierarchy -top {top}
prep -top {top}
design -stash gold
design -reset
read_verilog -sv reproducers/{source}
chparam -set W 4 {top}
hierarchy -top {top}
synth -top {top} -arith_tree
design -stash gate
design -copy-from gold -as gold {top}
design -copy-from gate -as gate {top}
miter -equiv -flatten gold gate miter
prep -top miter
sat -prove trigger 0 -set-def-inputs
''')
  start=time.perf_counter()
  try:
    with log.open('w') as f: p=subprocess.run([str(run),'yosys','-s',str(ys.relative_to(root))],cwd=root,stdout=f,stderr=subprocess.STDOUT,timeout=60,check=False)
    proof=log.read_text(errors='replace')
    if 'SAT proof finished - no model found: SUCCESS!' in proof:
      result='PASS'
    elif 'SAT proof finished - model found: FAIL!' in proof:
      result='FAIL'
    else:
      result='INCONCLUSIVE_NO_COMPLETION' if p.returncode == 0 else 'FAIL_SETUP'
  except subprocess.TimeoutExpired:
    result='INCONCLUSIVE_TIMEOUT'
    with log.open('a') as f: f.write('\nTIMEOUT: 60 seconds; proof is inconclusive.\n')
  rows.append({'check':tag,'result':result,'runtime_seconds':f'{time.perf_counter()-start:.6f}','script':str(ys.relative_to(root)),'log':str(log)})
with (root/'results'/'formal_controls.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(rows)
