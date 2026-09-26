#!/usr/bin/env python3
from __future__ import annotations
import csv, subprocess, time
from pathlib import Path

root=Path(__file__).resolve().parents[1]
run=root/'scripts'/'run_current.sh'
ysdir=root/'work'/'formal_ys'; logdir=root/'logs'/'formal'
ysdir.mkdir(parents=True,exist_ok=True); logdir.mkdir(parents=True,exist_ok=True)
cases=[('fir4',8,'fir4.v','fir4'),('fir4',16,'fir4.v','fir4'),('mixed',16,'mixed_arith.v','mixed_left'),('mixed',32,'mixed_arith.v','mixed_left'),('add_chain',16,'add_chain.v','add_chain'),('add_chain',64,'add_chain.v','add_chain')]
records=[]
for design,width,source,top in cases:
  for config in ('normal','arith_tree'):
    tag=f'{design}_w{width}_{config}'
    ys=ysdir/f'{tag}.ys'; log=logdir/f'{tag}.log'
    tree=' -arith_tree' if config == 'arith_tree' else ''
    ys.write_text(f'''read_verilog -sv reproducers/{source}
chparam -set W {width} {top}
prep -top {top}
design -stash gold
design -reset
read_verilog -sv reproducers/{source}
chparam -set W {width} {top}
synth -top {top} -noabc{tree}
design -stash gate
design -copy-from gold -as gold {top}
design -copy-from gate -as gate {top}
miter -equiv -flatten gold gate miter
prep -top miter
sat -prove trigger 0 -set-def-inputs
''')
    start=time.perf_counter()
    try:
      with log.open('w') as f:
        p=subprocess.run([str(run),'yosys','-s',str(ys.relative_to(root))],cwd=root,stdout=f,stderr=subprocess.STDOUT,timeout=120,check=False)
      proof=log.read_text(errors='replace')
      if 'SAT proof finished - no model found: SUCCESS!' in proof:
        result='PASS'
      elif 'SAT proof finished - model found: FAIL!' in proof:
        result='FAIL'
      else:
        result='INCONCLUSIVE_NO_COMPLETION' if p.returncode == 0 else 'FAIL_SETUP'
      rc=p.returncode
    except subprocess.TimeoutExpired:
      result='INCONCLUSIVE_TIMEOUT'; rc=124
      with log.open('a') as f: f.write('\nTIMEOUT: 120 seconds; proof is inconclusive.\n')
    records.append({'design':design,'width':width,'config':config,'result':result,'returncode':rc,'runtime_seconds':f'{time.perf_counter()-start:.6f}','netlist':'in-run Yosys synthesized design','script':str(ys.relative_to(root)),'log':str(log)})
out=root/'results'/'formal_comparison.csv'
with out.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(records[0])); w.writeheader(); w.writerows(records)
print(f'wrote {out} ({len(records)} rows)')
