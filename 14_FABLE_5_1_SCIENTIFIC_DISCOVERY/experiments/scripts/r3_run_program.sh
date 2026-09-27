#!/usr/bin/env bash
# R3 decisive per-program run (pre-registered in 09, R3):  ./r3_run_program.sh DESIGN U TAG
#   DESIGN in {ubp3r3, pc2r3}; U = utilization (base nick g2r3_DESIGN_uU); TAG in w1..w5
#   1. route the program on met4-met5 only: GRT + DRT to normal completion (OpenROAD default, 64 iterations)
#   2. modeled timing (placement parasitics, 3.0 ns) of the complete programmed netlist; write the netlist
#   3. independent functional check vs numpy W@x + mutation control (g2_verify.py)
#   4. invariance check against the frozen base (r3_invariance.py) incl. sha256 of the base ODB
# One JSON line per program is appended to results/G2/r3/r3_results.jsonl.
set -u
cd "$(dirname "$0")/.."
D=$1; U=$2; T=$3
G2=$PWD/results/G2
NICK=g2r3_${D}_u${U}
BASE=$G2/orfs/results/sky130hd/$NICK/base
SHA=$(cat $G2/r3/base_sha256_${D}_u${U}.txt | cut -d' ' -f1)
DRT_ITERS=64 scripts/g2_run_program.sh $G2 $D ${U}r $T > $G2/r3/verify_${D}_${T}_u${U}.log 2>&1
R=$G2/$D/prog_${T}_u${U}r
python3 scripts/r3_invariance.py $BASE/6_final.def ${R}_program.def $G2/$D/prog_${T}.json $BASE/6_final.odb $SHA > $G2/r3/inv_${D}_${T}_u${U}.json
python3 - "$D" "$U" "$T" <<'PY'
import json, re, sys
d, u, t = sys.argv[1], sys.argv[2], sys.argv[3]
g2 = 'results/G2'
r = f'{g2}/{d}/prog_{t}_u{u}r'
route = open(f'{r}_route.log').read()
viol = [int(x) for x in re.findall(r'Number of violations = (\d+)', route)]
res = re.search(r'G2_RESULT drc=(\d+)', route)
cong = {}
m = route.split('Final congestion report')[-1] if 'Final congestion report' in route else ''
for layer in ('met4', 'met5'):
    mm = re.search(rf'\n{layer}\s+(\d+)\s+(\d+)\s+([\d.]+)%\s+(\d+)\s*/\s*(\d+)\s*/\s*(\d+)', m)
    if mm:
        cong[layer] = {'usage_pct': float(mm.group(3)), 'overflow': int(mm.group(6))}
wl = {L: float(x) for L, x in re.findall(r'Total wire length on LAYER (met4|met5) = ([\d.]+) um', route)[-2:]}
vias = re.findall(r'Total number of vias = (\d+)', route)
sta = open(f'{r}_sta.log').read()
ws = re.search(r'G2_TIMING setup_ws=(\S+) hold_ws=(\S+)', sta)
pws = re.search(r'G2_PROG_WS setup=(\S+)', sta)
ver = [json.loads(l) for l in open(f'{g2}/g2_verification.jsonl') if f'prog_{t}_u{u}r_programmed' in l and f'"design": "{d}"' in l]
inv = json.load(open(f'{g2}/r3/inv_{d}_{t}_u{u}.json'))
rec = {'design': d, 'U': int(u), 'tag': t,
       'drt_final': None if res is None else int(res.group(1)), 'drt_iterations_run': len(viol) - 1 if viol else None,
       'drt_trajectory_head_tail': viol[:3] + ['...'] + viol[-3:] if len(viol) > 6 else viol,
       'grt': cong, 'wirelength_um': wl, 'vias': int(vias[-1]) if vias else None,
       'setup_ws_ns': float(ws.group(1)) * 1e9 if ws else None, 'hold_ws_ns': float(ws.group(2)) * 1e9 if ws else None,
       'prog_setup_ws_ns': float(pws.group(1)) * 1e9 if pws and pws.group(1) != 'none' else None,
       'matches_numpy': ver[-1]['matches_numpy'] if ver else None, 'mutation_detected': ver[-1]['mutation_detected'] if ver else None,
       'invariance': inv}
print(json.dumps(rec))
open(f'{g2}/r3/r3_results.jsonl', 'a').write(json.dumps(rec) + '\n')
PY
