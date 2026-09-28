"""Golden reproduction of the validated implementation.

  * the historical reference has not drifted (manifest sha256);
  * the generator reproduces the validated R3 designs (UBP3 at 52% and 60%, P2-R3 at 67%) and the A logic base:
    byte-identical module netlists, cells, base netlists and program TCL; semantically identical plan/config/W;
  * invariance on the historical routed programs: the physically routed program DEFs of the validated R3 60% run,
    checked against the GENERATED program, satisfy every invariant (needs the local ORFS results; skipped if absent).
"""
import hashlib
import json
import shutil
from pathlib import Path

import pytest

from ubpgen import config as C, golden, invariance, pipeline

HERE = Path(__file__).resolve().parents[1]
MAN = json.loads((HERE / 'golden' / 'manifest.json').read_text())
EXP = HERE.parent / 'experiments'
docker = pytest.mark.skipif(shutil.which('docker') is None, reason='needs docker + ORFS image')


def test_reference_has_not_drifted():
    bad = [f for grp in MAN['files'].values() for f, h in grp.items()
           if hashlib.sha256((EXP / f).read_bytes()).hexdigest() != h]
    assert not bad, bad


@docker
@pytest.mark.parametrize('cfgname', ['golden_r3_ubp3_u60', 'golden_r3_ubp3_u52', 'golden_r3_pc2_u67', 'r3_g1_u75'])
def test_generator_reproduces_validated_design(cfgname, tmp_path):
    c = C.load(HERE / 'configs' / f'{cfgname}.json')
    pipeline.generate(c, tmp_path)
    r = golden.compare(c, tmp_path)
    assert r['pass'], r['failures']
    if cfgname != 'r3_g1_u75':
        assert r['results']['netlist/netlist_base.v'] == 'BYTE'
    assert r['results']['netlist/netlist_logic.v'] == 'BYTE'


G2 = EXP / 'results' / 'G2'
HIST_BASE = G2 / 'orfs' / 'results' / 'sky130hd' / 'g2r3_ubp3r3_u60' / 'base'


@docker
@pytest.mark.skipif(not (HIST_BASE / '6_final.def').exists(), reason='historical ORFS results not present locally')
@pytest.mark.parametrize('tag', ['w1', 'w2', 'w3', 'w4', 'w5'])
def test_invariance_on_historical_routed_programs(tag, tmp_path_factory):
    root = tmp_path_factory.getbasetemp() / 'g60'
    c = C.load(HERE / 'configs' / 'golden_r3_ubp3_u60.json')
    if not (root / 'generation.json').exists():
        pipeline.generate(c, root)
    sha = (G2 / 'r3' / 'base_sha256_ubp3r3_u60.txt').read_text().split()[0]
    rec = invariance.check(HIST_BASE / '6_final.def', G2 / 'ubp3r3' / f'prog_{tag}_u60r_program.def',
                           root / 'programs' / tag / 'prog.json', HIST_BASE / '6_final.odb', sha)
    assert rec['all_invariants_hold'], rec


@pytest.mark.skipif(not (HIST_BASE / '6_final.def').exists(), reason='historical ORFS results not present locally')
def test_invariance_detects_violations(tmp_path):
    """Negative controls: a moved cell, a re-routed base net, a foreign pin on a programmable net."""
    base_def = HIST_BASE / '6_final.def'
    prog_def = (G2 / 'ubp3r3' / 'prog_w5_u60r_program.def').read_text()
    prog_json = G2 / 'ubp3r3' / 'prog_w5.json'
    sha = (G2 / 'r3' / 'base_sha256_ubp3r3_u60.txt').read_text().split()[0]

    def run(text):
        p = tmp_path / 'p.def'
        p.write_text(text)
        return invariance.check(base_def, p, prog_json, HIST_BASE / '6_final.odb', sha)

    assert run(prog_def)['all_invariants_hold']
    import re
    m = re.search(r'(\n\s*-\s+vs_0_0\s+\S+\s+\+\s+\w+\s+\(\s*)(-?\d+)', prog_def)
    moved = prog_def[:m.start(2)] + str(int(m.group(2)) + 460) + prog_def[m.end(2):]
    r = run(moved)
    assert not r['placement_identical'] and not r['all_invariants_hold']
    r = run(prog_def.replace(' ROUTED met4 ', ' ROUTED met3 ', 1))
    assert not r['layers_ok'] and not r['all_invariants_hold']
    i = prog_def.index('- pgm_')
    j = prog_def.index('( vs_', i)
    foreign = prog_def[:j] + '( row0 clk ) ' + prog_def[j:]
    r = run(foreign)
    assert not r['program_connectivity_ok'] and not r['all_invariants_hold']
