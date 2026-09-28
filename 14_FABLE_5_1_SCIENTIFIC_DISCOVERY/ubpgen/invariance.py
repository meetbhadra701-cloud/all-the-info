"""Weight-independence of the frozen base, checked automatically after every program.

Reuses the validated R3 check (experiments/scripts/r3_invariance.py):
  odb_unchanged, placement_identical, masters_ok, layers_ok (met4/met5 only, M4M5 vias, only pgm_* nets routed),
  specialnets_identical;
and adds the connectivity check:
  program_connectivity_ok: the routed programmable nets are exactly the program's nets, and every pin on them is a
  tap output (lt_*/Z) or a via-site input (vs_*/A) -- no other base pin is touched.
"""
from __future__ import annotations

import contextlib
import io
import json
import re
from pathlib import Path

from ._legacy import SCRIPTS  # noqa: F401

import r3_invariance  # noqa: E402


def program_connectivity(prog_def: str, prog: dict) -> dict:
    nets = r3_invariance.section(prog_def, '\nNETS', 'END NETS')
    found, bad = {}, []
    for blk in nets.split(';'):
        m = re.search(r'-\s+(pgm_\S+)', blk)
        if not m:
            continue
        pins = re.findall(r'\(\s*(\S+)\s+(\S+)\s*\)', blk.split('+')[0])
        name = m.group(1)[len('pgm_'):]
        found[name] = sorted(i for i, p in pins if i.startswith('vs_'))
        bad += [f'{i}/{p}' for i, p in pins if not ((i.startswith('lt_') and p == 'Z') or (i.startswith('vs_') and p == 'A'))]
        taps = [i for i, p in pins if i.startswith('lt_')]
        if taps != [f'lt_{name}']:
            bad.append(f'{m.group(1)}: taps {taps}')
    want = {k: sorted(v) for k, v in prog['nets'].items()}
    return {'program_nets_match': found == want, 'foreign_pins': bad[:10],
            'program_connectivity_ok': found == want and not bad}


def check(base_def: Path, prog_def: Path, prog_json: Path, odb: Path, odb_sha: str) -> dict:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):             # the validated script prints its record; it is not modified
        r3_invariance.main(str(base_def), str(prog_def), str(prog_json), str(odb), odb_sha)
    rec = json.loads(buf.getvalue().strip().splitlines()[-1])
    rec.update(program_connectivity(prog_def.read_text(), json.loads(prog_json.read_text())))
    rec['all_invariants_hold'] = rec['all_invariants_hold'] and rec['program_connectivity_ok']
    return rec
