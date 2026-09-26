import sys, glob, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aigtool
for p in sorted(glob.glob(os.path.join('netlists', '*', '*_pre.aig'))):
    aig = aigtool.read_aig(p)
    cf = sum(1 for l, r0, r1 in aig['ands'] if r0 in (0, 1) or r1 in (0, 1))
    co = sum(1 for o in aig['outputs'] if o in (0, 1))
    print(f"{p.replace(os.sep, '/'):<48} constfanin_ANDs={cf:<3} const_outputs={co}")
