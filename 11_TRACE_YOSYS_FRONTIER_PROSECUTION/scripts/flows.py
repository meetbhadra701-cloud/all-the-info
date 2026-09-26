#!/usr/bin/env python3
"""Emit one Yosys script per (build, design, architecture) and a job list per build.

Architectures
  norm         synth -top top                       (Yosys default lowering, then ABC)
  booth        synth -top top -booth
  tree         synth -top top -arith_tree
  *_pre        same flow with -noabc (pre-ABC netlist; diagnostic)
  tree_nofma   explicit replica of synth with 'arith_tree -no-fma'   (diagnostic)
  tree_fa      explicit replica with 'arith_tree -strategy fa'       (diagnostic)
  tree_ripple  explicit replica with 'arith_tree -final ripple'      (diagnostic)
  booth_lp     explicit replica with 'booth -lowpower'               (diagnostic, signed only)
  norm_rep / tree_rep  explicit replicas of the default flows, used only to prove the replica is faithful

Builds: MAIN = muxwise-yosys-current:exp6 (e8db64c6), PATCH = muxwise-yosys-patched:exp6 (30b851e6).
All paths inside the container are relative to /work (the experiment root).
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
man = list(csv.DictReader(open(os.path.join(ROOT, 'rtl', 'manifest.csv'))))

COARSE_PRE = ("hierarchy -check -top top; proc; opt_expr; check; opt_clean; opt -nodffe -nosdff; fsm; opt; "
              "wreduce; peepopt; opt_clean")
COARSE_POST = "share; opt; memory -nomap; opt_clean"
FINE = "opt -fast -full; memory_map; opt -full; techmap; opt -fast"


def replica(booth=None, tree=None, abc=True):
    s = COARSE_PRE + "; "
    if booth is not None:
        s += f"booth {booth}".strip() + "; "
    s += "alumacc; "
    if tree is not None:
        s += f"arith_tree {tree}".strip() + "; "
    s += COARSE_POST + "; " + FINE
    if abc:
        s += "; abc; opt -fast"
    return s + "; hierarchy -check; stat; check"


FLOWS = {
    'norm': "synth -top top",
    'booth': "synth -top top -booth",
    'tree': "synth -top top -arith_tree",
    'norm_pre': "synth -top top -noabc",
    'booth_pre': "synth -top top -booth -noabc",
    'tree_pre': "synth -top top -arith_tree -noabc",
    'tree_nofma': replica(tree='-no-fma'),
    'tree_fa': replica(tree='-strategy fa'),
    'tree_ripple': replica(tree='-final ripple'),
    'booth_lp': replica(booth='-lowpower'),
    'norm_rep': replica(),
    'tree_rep': replica(tree=''),
}


def plan():
    jobs = []
    for r in man:
        d, fam, kind, signs = r['design'], r['family'], r['kind'], r['signs']
        W = int(r['widths'].split(',')[0])
        signed = 's' in signs
        if fam == 'A':
            for a in ('norm', 'booth'):
                jobs.append(('MAIN', d, a))
            if W in (8, 16, 32):
                jobs += [('MAIN', d, 'norm_pre'), ('MAIN', d, 'booth_pre')]
                if signed:
                    jobs.append(('MAIN', d, 'booth_lp'))
            if W == 8:
                jobs.append(('MAIN', d, 'norm_rep'))
        elif fam == 'B':
            for a in ('norm', 'tree'):
                jobs.append(('MAIN', d, a))
            if signed:
                jobs.append(('PATCH', d, 'tree'))
            if W in (8, 16, 32):
                for a in ('tree_nofma', 'tree_fa', 'tree_ripple', 'tree_pre', 'norm_pre'):
                    jobs.append(('MAIN', d, a))
                if kind == 'mac':
                    jobs.append(('MAIN', d, 'booth'))
                if signed:
                    jobs += [('PATCH', d, 'tree_pre'), ('PATCH', d, 'tree_fa'), ('PATCH', d, 'tree_ripple')]
            if W == 8:
                jobs.append(('MAIN', d, 'tree_rep'))
        elif fam == 'C':
            jobs += [('MAIN', d, 'norm'), ('MAIN', d, 'tree'), ('PATCH', d, 'tree')]
            if W <= 16:
                jobs += [('MAIN', d, 'tree_nofma'), ('PATCH', d, 'tree_pre'), ('MAIN', d, 'tree_pre')]
        elif fam == 'MUT':
            arches = ['norm', 'booth'] if kind == 'mul' else ['norm', 'tree']
            for a in arches:
                jobs.append(('MAIN', d, a))
    return jobs


def main():
    jobs = plan()
    by_build = {}
    for b, d, a in jobs:
        out_dir = os.path.join(ROOT, 'netlists', b)
        os.makedirs(out_dir, exist_ok=True)
        base = f"netlists/{b}/{d}__{a}"
        ys = (f"read_verilog -sv rtl/{d}.v\n{FLOWS[a].replace('; ', chr(10))}\n"
              f"aigmap\nopt_clean\nwrite_aiger -symbols -map {base}.map {base}.aig\n")
        open(os.path.join(ROOT, base + '.ys'), 'w', newline='\n').write(ys)
        by_build.setdefault(b, []).append(base)
    for b, lst in by_build.items():
        open(os.path.join(ROOT, 'netlists', f'jobs_{b}.txt'), 'w', newline='\n').write('\n'.join(lst) + '\n')
        print(b, len(lst), 'jobs')


if __name__ == '__main__':
    main()
