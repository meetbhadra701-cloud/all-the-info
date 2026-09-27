"""R3 invariance check of one weight program against its frozen base (pre-registered in 09, R3).

python3 r3_invariance.py BASE_DEF PROGRAM_DEF PROG_JSON ODB_PATH ODB_SHA256
Checks, and prints one JSON record:
  * odb_unchanged      : sha256(base 6_final.odb) equals the value recorded before any program was applied;
  * placement_identical: every instance has the same location, orientation and placement status in the program DEF
                         as in the base DEF (no cell added, removed or moved);
  * masters_ok         : master names differ ONLY for VSITE_BUF -> VSITE_ZERO (VSITE_ONE) swaps listed by the program;
  * layers_ok          : every routed segment of the program DEF is on met4/met5 and every via is a met4-met5 via;
                         only programmable nets (pgm_*) carry routing (no base net re-routed);
  * specialnets_identical: the power grid (SPECIALNETS) is byte-identical to the base.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys

COMP = re.compile(r'^\s*-\s+(\S+)\s+(\S+)\s+\+\s+(PLACED|FIRM|FIXED|COVER)\s+\(\s*(-?\d+)\s+(-?\d+)\s*\)\s+(\S+)', re.M)


def section(text: str, start: str, end: str) -> str:
    i = text.index(start)
    return text[i:text.index(end, i)]


def comps(defs: str) -> dict:
    return {m.group(1): (m.group(2), m.group(3), int(m.group(4)), int(m.group(5)), m.group(6))
            for m in COMP.finditer(section(defs, '\nCOMPONENTS', 'END COMPONENTS'))}


def main(base_def, prog_def, prog_json, odb, odb_sha):
    b = open(base_def).read()
    p = open(prog_def).read()
    prog = json.load(open(prog_json))
    rec = {}
    rec['odb_unchanged'] = hashlib.sha256(open(odb, 'rb').read()).hexdigest() == odb_sha
    cb, cp = comps(b), comps(p)
    same_set = set(cb) == set(cp)
    moved = [n for n in cb if n in cp and cb[n][1:] != cp[n][1:]]
    rec['n_instances'] = len(cb)
    rec['placement_identical'] = same_set and not moved
    rec['moved_or_changed_status'] = moved[:10]
    swapped = {n: (cb[n][0], cp[n][0]) for n in cb if n in cp and cb[n][0] != cp[n][0]}
    allowed = {z: ('VSITE_BUF', 'VSITE_ZERO') for z in prog['zeros']}
    allowed.update({o: ('VSITE_ZERO', 'VSITE_ONE') for o in prog.get('ones', [])})
    rec['n_master_swaps'] = len(swapped)
    rec['masters_ok'] = swapped == allowed
    nets = section(p, '\nNETS', 'END NETS')
    layers, vias, routed_non_pgm = set(), set(), []
    for blk in nets.split(';'):
        m = re.search(r'-\s+(\S+)', blk)
        if not m:
            continue
        segs = re.findall(r'(?:ROUTED|NEW)\s+(\w+)', blk)
        if not segs:
            continue
        if not m.group(1).startswith('pgm_'):
            routed_non_pgm.append(m.group(1))
        layers.update(segs)
        vias.update(re.findall(r'\)\s+(\w+)\s*(?=\n|NEW|$)', blk))
    via_names = {v for v in vias if not v.startswith(('met', 'li1'))}
    rec['routed_layers'] = sorted(layers)
    rec['via_masters'] = sorted(via_names)
    rec['routed_non_pgm_nets'] = routed_non_pgm[:10]
    rec['layers_ok'] = layers <= {'met4', 'met5'} and not routed_non_pgm and all(('M4M5' in v) or ('via4' in v.lower()) for v in via_names)
    rec['specialnets_identical'] = section(b, '\nSPECIALNETS', 'END SPECIALNETS') == section(p, '\nSPECIALNETS', 'END SPECIALNETS')
    rec['all_invariants_hold'] = all(rec[k] for k in ('odb_unchanged', 'placement_identical', 'masters_ok', 'layers_ok', 'specialnets_identical'))
    print(json.dumps(rec))


if __name__ == '__main__':
    main(*sys.argv[1:6])
