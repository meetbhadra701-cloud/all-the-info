"""Generator regression tests that run Yosys in the ORFS container (small designs; a few minutes in total).

  * determinism: the same configuration generates byte-identical artifacts;
  * functional: every generated design, every program, matches numpy W@x (pre-PnR), for all three fabrics and
    several (g, K, m != n) points;
  * mutation controls: oracle mutation and program mutation are both detected;
  * weight independence at the netlist level: the base netlist and placement plan do not depend on the programs;
  * R3 access rule: every programmable net stays within one row segment and has exactly one tap;
  * spine-driver option: only the line-driver cells change, and the design still computes W@x.
"""
import json
import re
import shutil
from pathlib import Path

import numpy as np
import pytest

from ubpgen import access, arch, config as C, pipeline, verify

pytestmark = pytest.mark.skipif(shutil.which('docker') is None, reason='needs docker + ORFS image')

PROGS = [{'tag': 'a', 'seed': 11, 'p0': 0.4}, {'tag': 'b', 'seed': 12, 'p0': 0.1},
         {'tag': 'c', 'seed': 13, 'p0': 0.8}, {'tag': 'd', 'seed': 14, 'p0': 0.4, 'same_rows': True}]
POINTS = {
    'ubp_g3_k4': dict(fabric='ubp', n=9, m=8, g=3, access={'taps_per_line': 4}),
    'ubp_g2_k2_mneqn': dict(fabric='ubp', n=7, m=6, g=2, access={'taps_per_line': 2}),
    'ubp_g4_k1': dict(fabric='ubp', n=8, m=5, g=4, access={'taps_per_line': 1}),
    'g1_k4': dict(fabric='g1', n=6, m=8, access={'taps_per_line': 4}),
    'pc2_k2': dict(fabric='pc2', n=6, m=4, access={'taps_per_line': 2}),
}


def cfg_of(name, **kw):
    return C.resolve({'name': name, 'programs': PROGS, **POINTS[name], **kw})


@pytest.fixture(scope='module')
def built(tmp_path_factory):
    out = {}
    for name in POINTS:
        c = cfg_of(name)
        root = tmp_path_factory.mktemp(name)
        pipeline.generate(c, root)
        out[name] = (c, root)
    return out


@pytest.mark.parametrize('name', list(POINTS))
def test_functional_and_mutations(built, name):
    c, root = built[name]
    for rec in pipeline.verify_prepnr(c, root):
        assert rec['matches_numpy'], rec
        assert rec['oracle_mutation_detected'], rec
        assert rec['program_mutation_detected'], rec


def test_determinism(built, tmp_path):
    c, root = built['ubp_g3_k4']
    pipeline.generate(c, tmp_path)
    a = json.loads((root / 'generation.json').read_text())['files']
    b = json.loads((tmp_path / 'generation.json').read_text())['files']
    assert a == b


def test_base_is_independent_of_programs(built, tmp_path):
    c, root = built['ubp_g3_k4']
    c2 = c.with_overrides(programs=[{'tag': 'z', 'seed': 999, 'p0': 0.2}])
    pipeline.generate(c2, tmp_path)
    for f in ('netlist/netlist_base.v', 'layout/place_access.tcl', 'orfs/config.mk'):
        a, b = (root / f).read_text(), (tmp_path / f).read_text()
        if f == 'orfs/config.mk':      # the nickname follows the name only
            a, b = re.sub(r'NICKNAME = \S+', '', a), re.sub(r'NICKNAME = \S+', '', b)
        if f == 'layout/place_access.tcl':
            a, b = a.split('\n', 1)[1], b.split('\n', 1)[1]
        assert a == b, f


@pytest.mark.parametrize('name', list(POINTS))
def test_structure_and_access_rule(built, name):
    c, root = built[name]
    net = (root / 'netlist' / 'netlist_base.v').read_text()
    k = arch.counts(c)
    assert net.count('  LTAP2 lt_') == k['taps']
    assert len(re.findall(r'  VSITE_BUF vs_\d+_\d+ ', net)) == k['sites']
    assert len(re.findall(r'  VSITE_ZERO cst_\d+_\d+ ', net)) == k['const_sites']
    assert ' LTAP lt_' not in net
    plan = access.parse_plan((root / 'layout' / 'place_access.tcl').read_text())
    assert len(plan) == k['taps'] + k['sites']
    seg = c.m // c.K
    for spec in c.raw['programs']:
        prog = json.loads((root / 'programs' / spec['tag'] / 'prog.json').read_text())
        for netname, sites in prog['nets'].items():
            s = int(netname.rsplit('_s', 1)[1])
            assert all(int(v.split('_')[1]) // seg == s for v in sites), netname
            assert f'lt_{netname} ' in net
        W = np.load(root / 'programs' / spec['tag'] / 'W.npy')
        n_leaves = sum(len(v) for v in prog['nets'].values()) + len(prog['zeros'])
        assert n_leaves == k['sites']
        if c.fabric == 'pc2':
            assert len(prog['ones']) == sum(bin(int((W[i] < 0).sum())).count('1') for i in range(c.m))


@pytest.mark.parametrize('name', ['ubp_g3_k4', 'pc2_k2'])
def test_spine_driver_sizing(built, name, tmp_path):
    c, root = built[name]
    c4 = c.with_overrides(spine_driver='drive4')
    pipeline.generate(c4, tmp_path)
    mod = 'SNEG' if c.fabric == 'ubp' else 'PLINE'
    a = (root / 'rtl' / f'{mod}_gl.v').read_text()
    b = (tmp_path / 'rtl' / f'{mod}_gl.v').read_text()
    changed = [(x, y) for x, y in zip(a.splitlines(), b.splitlines()) if x != y]
    assert len(changed) == 2 and all(y.strip().split()[0].endswith('_4') for _, y in changed)
    for rec in pipeline.verify_prepnr(c4, tmp_path, tags=['a']):
        assert rec['pass'], rec
