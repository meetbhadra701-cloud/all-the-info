"""Freeze the golden reference: sha256 of every historical artifact that produced the validated R3 results.

python3 ubpgen/golden/make_manifest.py   -> ubpgen/golden/manifest.json
The historical files stay where they are (experiments/); tests assert they still hash to these values, so the
reference cannot drift silently.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
EXP = ROOT / 'experiments'
R = EXP / 'results'

SETS = {
    'scripts (the validated chain)': [
        'scripts/e5_build.py', 'scripts/e6_build.py', 'scripts/g3_build.py', 'scripts/g2_cells.py', 'scripts/g2_build.py',
        'scripts/g2_struct.py', 'scripts/r3_build.py', 'scripts/e5_run.sh', 'scripts/orfs_patch/synth_odb.tcl',
        'scripts/g2_program.tcl', 'scripts/g2_run_program.sh', 'scripts/r3_run_program.sh', 'scripts/g2_verify.py',
        'scripts/r3_invariance.py', 'scripts/r3_collect.py'],
    'UBP3 modules (E6)': [f'results/E6/ubp3_n64/{f}' for f in (
        'SGEN1.v', 'SGEN1_gl.v', 'SGEN3.v', 'SGEN3_gl.v', 'SNEG.v', 'SNEG_gl.v', 'STREE_L22.v', 'STREE_L22_gl.v')],
    'P2 modules (G3)': [f'results/G3/pc2_n64/{f}' for f in (
        'CTRL.v', 'CTRL_gl.v', 'PLINE.v', 'PLINE_gl.v', 'PROW_pc2_L64.v', 'PROW_pc2_L64_gl.v')],
    'A modules (E6)': [f'results/E6/g1_n64/{f}' for f in ('SNEG.v', 'SNEG_gl.v', 'STREE_L64.v', 'STREE_L64_gl.v')],
    'cells': [f'results/G2/cells/{f}' for f in (
        'g2_cells.lef', 'g2_cells.lib', 'g2r3_cells.lef', 'g2r3_cells.lib', 'dont_touch_r3.tcl', 'pdn_m1rails.tcl',
        'struct_ubp3r3.tcl', 'struct_pc2r3.tcl')],
    'UBP3 logic base (G2/R2)': [f'results/G2/ubp3s/{f}' for f in ('top_base.v', 'netlist_base.v', 'mapping.json')],
    'UBP3 R3 base + programs': [f'results/G2/ubp3r3/{f}' for f in (
        ['netlist_base.v', 'mapping.json', 'config_u52r.mk', 'config_u60r.mk', 'constraint.sdc']
        + [f'{k}_{t}.{e}' for t in ('w1', 'w2', 'w3', 'w4', 'w5', 'w14') for k, e in (('prog', 'json'), ('prog', 'tcl'), ('W', 'npy'))])],
    'P2 R3 base + programs': [f'results/G2/pc2r3/{f}' for f in (
        ['netlist_base.v', 'mapping.json', 'config_u67r.mk', 'constraint.sdc']
        + [f'{k}_{t}.{e}' for t in ('w1', 'w2', 'w3', 'w4', 'w5') for k, e in (('prog', 'json'), ('prog', 'tcl'), ('W', 'npy'))])],
    'A logic base (G2)': [f'results/G2/g1s/{f}' for f in ('netlist_base.v', 'mapping.json')],
    'R3 records': ['results/G2/r3/r3_results.jsonl', 'results/G2/r3/r3_summary_u52.json', 'results/G2/r3/r3_summary_u60.json',
                   'results/G2/r3/base_sha256_ubp3r3_u52.txt', 'results/G2/r3/base_sha256_ubp3r3_u60.txt',
                   'results/G2/r3/base_sha256_pc2r3_u67.txt', 'results/G2/r3/fairness_summary.json'],
}

PARAMS = {
    'design': 'UBP3-serial (fabric ubp), n = m = 64, g = 3, INT8 activations, 14-bit output words, latency 8',
    'access': 'R3 segmented taps: K = 4 LTAP2 per line on a base spine, 4 row segments of 16, 22 bands',
    'physical': 'SKY130 HD, ORFS image sha256:69df744e..., NUM_CORES 2, NO_DCE, met1-rail PDN, base met1-met3, '
                'programs met4-met5, 3.0 ns clock, CORE_UTILIZATION 60 (decisive point 52), aspect 1, margin 2',
    'programs': 'W1..W5 = g2_build seeds 1001..1005 (p0 0.4, 0.4, 0.8, 0.1, 0.4 identical rows); W14 = seed 14',
    'validated_results': 'U60: 5/5 programs 0 DRT violations (13/13/7/13/1 it.), base setup/hold +1.022/+0.293 ns, '
                         'A x T 8.566e6 (1.663x vs A@75); U52: 5/5 (14/13/7/14/1), A x T 9.263e6',
    'historical_base_odb_sha256': {'ubp3r3_u60': '70add1cde3c5d12580ca52796776ef2188837eea3995aa9d2c744f3977fef026',
                                   'ubp3r3_u52': 'aefbdaff878a (see base_sha256_ubp3r3_u52.txt)',
                                   'pc2r3_u67': 'afde9bb09f05 (see base_sha256_pc2r3_u67.txt)'},
    'historical_command_chain': [
        'python3 scripts/e6_build.py $PWD/results/E6 64 g1 ubp3 ubp4  (+ reemit_a2.py: every instance kept)',
        'python3 scripts/g2_cells.py $PWD/results/G2/cells',
        'python3 scripts/g2_build.py base $PWD/results/G2 ubp3s $PWD/results/E6/ubp3_n64',
        'python3 scripts/g2_build.py program $PWD/results/G2 ubp3s w1 1001 0.4  (w2..w5, w14 likewise)',
        'python3 scripts/g2_struct.py $PWD/results/G2 ubp3s 60 52 45  (R2 configs, source of config_u52s.mk)',
        'python3 scripts/r3_build.py cells|base|programs $PWD/results/G2 ...',
        'NO_DCE=1 scripts/e5_run.sh $PWD/results/G2 ubp3r3:60r',
        'scripts/r3_run_program.sh ubp3r3 60 w1  (w2..w5)',
        'python3 scripts/r3_collect.py 60'],
}


def main():
    out = {'purpose': 'Golden reference of the validated R3 implementation (19_FINAL_UBP_DECISION.md). Frozen; do not edit.',
           'frozen_at_commit': subprocess.run(['git', '-C', str(ROOT), 'log', '-1', '--format=%H', '--',
                                               'experiments/results/G2/r3/r3_summary_u60.json'],
                                              capture_output=True, text=True).stdout.strip(),
           'parameters': PARAMS, 'files': {}}
    for group, files in SETS.items():
        out['files'][group] = {f: hashlib.sha256((EXP / f).read_bytes()).hexdigest() for f in files}
    (HERE / 'manifest.json').write_text(json.dumps(out, indent=1) + '\n')
    print(sum(len(v) for v in out['files'].values()), 'files hashed')


if __name__ == '__main__':
    main()
