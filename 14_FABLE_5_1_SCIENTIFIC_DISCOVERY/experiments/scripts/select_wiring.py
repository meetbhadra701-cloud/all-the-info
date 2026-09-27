"""Decompose the ROUTED wirelength of a finished ORFS run into select wiring vs module-internal wiring.

The thesis' central assumption is that select wiring (line drivers -> row leaves; the W-dependent, via-programmed
connections) does not eat the logic saving. Total wirelength only tests this indirectly; this script measures it.

Method (from 6_final.def, signal NETS only; DEF units from UNITS DISTANCE):
  * each net's routed length = sum of Manhattan segment lengths of its ROUTED/NEW statements;
  * top-level repair/CTS buffers and delay cells are TRANSPARENT: nets joined through them form one super-net;
  * each super-net is classified by the groups of its non-transparent endpoints
    (group = top-level instance prefix before '/', or IO pin, or top-level tie / flip-flop / diode):
      intra   : all endpoints inside ONE module instance (row, gen, neg/ng)
      select  : touches >= 1 row AND >= 1 line source (neg/ng/gen instance or x input pin)  <- via-programmed wiring
      tie     : ties -> rows only (zero leaves; an artifact of standard-cell modelling)
      output  : rows -> y pins only
      input   : x pins -> neg/ng/gen only
      fabric  : generator -> negator (and alignment flip-flops): W-independent inter-module wiring
      clock   : contains the clk pin
      control : everything else (start distribution, top-level alignment flip-flops, ...)

python3 select_wiring.py EDIR N DESIGN UTIL [serial]      (appends to EDIR/select_wiring.jsonl)
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

TRANSPARENT = re.compile(r'sky130_fd_sc_hd__(buf|clkbuf|clkdlybuf4s\d+|dlygate4sd\d|dlymetal6s\d|dlybuf|bufbuf|clkinv|inv)_\d+')


def parse_def(path: Path):
    units = 1000.0
    master = {}
    nets = {}
    section = None
    cur = None
    last = None
    with open(path) as fh:
        for raw in fh:
            ln = raw.strip()
            if ln.startswith('UNITS DISTANCE MICRONS'):
                units = float(ln.split()[3])
            if ln.startswith('COMPONENTS '):
                section = 'C'; continue
            if ln.startswith('END COMPONENTS'):
                section = None; continue
            if ln.startswith('NETS '):
                section = 'N'; continue
            if ln.startswith('END NETS'):
                section = None; cur = None; continue
            if section == 'C' and ln.startswith('- '):
                t = ln.split()
                master[t[1]] = t[2]
            elif section == 'N':
                if ln.startswith('- '):
                    t = ln.split()
                    cur = t[1]
                    nets[cur] = {'pins': [], 'len': 0.0}
                    last = None
                    ln = ln[len(t[0]) + len(t[1]) + 2:]
                if cur is None:
                    continue
                # pins: ( inst pin ) or ( PIN name )
                if '+ ROUTED' not in ln and 'NEW ' not in ln and '+ ' not in ln[:2]:
                    for a, b in re.findall(r'\(\s*(\S+)\s+(\S+)\s*\)', ln):
                        if not re.fullmatch(r'-?\d+', a):
                            nets[cur]['pins'].append((a, b))
                m = re.search(r'(?:\+ ROUTED|NEW)\s+(\S+)(.*)', ln)
                if m:
                    pts = re.findall(r'\(\s*(\S+)\s+(\S+)(?:\s+\S+)?\s*\)', m.group(2))
                    prev = None
                    for xs, ys in pts:
                        x = prev[0] if xs == '*' else float(xs)
                        y = prev[1] if ys == '*' else float(ys)
                        if prev is not None:
                            nets[cur]['len'] += abs(x - prev[0]) + abs(y - prev[1])
                        prev = (x, y)
                if ln.endswith(';'):
                    cur = None
    for v in nets.values():
        v['len'] /= units
    return master, nets


def group_of(inst: str, pin: str, master: dict) -> str | None:
    if inst == 'PIN':
        base = re.sub(r'\[.*', '', pin)
        return f'IO:{base}'
    mst = master.get(inst, '')
    if 'conb' in mst:          # split tie cells are named after their load (row5/_123__7): classify by cell type
        return 'TIE'
    if '/' in inst:
        return inst.split('/')[0]
    if 'diode' in mst:
        return None
    if 'conb' in mst:
        return 'TIE'
    if 'df' in mst:
        return 'FF'
    return f'TOP:{inst}'


def kind(g: str) -> str:
    if g.startswith('row'):
        return 'row'
    if re.match(r'(neg|ng|gen)\d', g):
        return 'src'
    if g in ('IO:x',):
        return 'xin'
    if g == 'IO:y':
        return 'yout'
    if g == 'IO:clk':
        return 'clk'
    return g


def classify(groups: set[str]) -> str:
    ks = {kind(g) for g in groups}
    if 'clk' in ks:
        return 'clock'
    if len(groups) == 1 and next(iter(ks)) in ('row', 'src'):
        return 'intra'
    if 'row' in ks and ({'src', 'xin'} & ks):
        return 'select'
    if ks <= {'row', 'TIE'} and 'TIE' in ks:
        return 'tie'
    if ks <= {'row', 'yout'} and 'yout' in ks:
        return 'output'
    if ks <= {'xin', 'src'} and 'xin' in ks:
        return 'input'
    if ks <= {'src', 'FF'} and 'src' in ks:
        return 'fabric'   # W-independent inter-module wiring: generator -> (alignment FF) -> negator
    return 'control'


def main(edir: Path, n: int, design: str, util: int, mode: str):
    nick = f"{'s_' if mode == 'serial' else ''}{design}_n{n}_u{util}"
    master, nets = parse_def(edir / 'orfs' / 'results' / 'sky130hd' / nick / 'base' / '6_final.def')
    # union-find over nets joined by transparent top-level instances
    parent = {k: k for k in nets}
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    by_inst = defaultdict(list)
    for name, v in nets.items():
        for inst, pin in v['pins']:
            if inst != 'PIN' and '/' not in inst and TRANSPARENT.fullmatch(master.get(inst, '')):
                by_inst[inst].append(name)
    for inst, ns in by_inst.items():
        for other in ns[1:]:
            ra, rb = find(ns[0]), find(other)
            if ra != rb:
                parent[ra] = rb
    groups = defaultdict(set)
    length = defaultdict(float)
    for name, v in nets.items():
        r = find(name)
        length[r] += v['len']
        for inst, pin in v['pins']:
            if inst != 'PIN' and '/' not in inst and TRANSPARENT.fullmatch(master.get(inst, '')):
                continue
            g = group_of(inst, pin, master)
            if g:
                groups[r].add(g)
    out = defaultdict(float)
    cnt = defaultdict(int)
    for r, L in length.items():
        c = classify(groups[r]) if groups[r] else 'control'
        out[c] += L; cnt[c] += 1
    total = sum(out.values())
    rec = {'design': design, 'n': n, 'util': util, 'mode': mode, 'total_um': round(total),
           **{f'{k}_um': round(v) for k, v in sorted(out.items())}, **{f'{k}_nets': c for k, c in sorted(cnt.items())}}
    print(json.dumps(rec))
    with open(edir / 'select_wiring.jsonl', 'a') as fh:
        fh.write(json.dumps(rec) + '\n')


if __name__ == '__main__':
    main(Path(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), sys.argv[5] if len(sys.argv) > 5 else 'parallel')
