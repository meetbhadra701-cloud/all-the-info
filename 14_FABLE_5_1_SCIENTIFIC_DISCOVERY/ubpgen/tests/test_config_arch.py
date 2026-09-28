"""Pure-Python tests (no containers): configuration validation and the architecture's exactness."""
import json
from pathlib import Path

import numpy as np
import pytest

from ubpgen import arch, config as C
from ubpgen._legacy import canon_patterns

CFG = Path(__file__).resolve().parents[1] / 'configs'


def base(**kw):
    d = {'name': 't', 'fabric': 'ubp', 'n': 9, 'm': 8, 'g': 3}
    d.update(kw)
    return d


@pytest.mark.parametrize('bad, msg', [
    (dict(g=None), 'g in 2..4'),
    (dict(g=1), 'g in 2..4'),
    (dict(g=5), 'g in 2..4'),
    (dict(n=2, g=3), 'g must not exceed n'),
    (dict(fabric='g1', g=3), 'only meaningful'),
    (dict(fabric='nope'), 'fabric must be'),
    (dict(access={'taps_per_line': 3}), 'must divide m'),
    (dict(access={'taps_per_line': 0}), '>= 1'),
    (dict(layout={'util': 95}), 'layout.util'),
    (dict(activation_bits=4), 'activation_bits'),
    (dict(spine_driver='huge'), 'spine_driver'),
    (dict(fabric='pc2', g=None, n=65, m=64), 'n too large'),
    (dict(programs=[{'tag': 'a', 'seed': 1, 'p0': 0.4}, {'tag': 'a', 'seed': 2, 'p0': 0.4}]), 'duplicate'),
    (dict(programs=[{'tag': 'a', 'seed': 1, 'p0': 1.5}]), 'p0'),
    (dict(programs=[{'tag': 'a', 'p0': 0.5}]), 'needs seed'),
    (dict(programs=[{'tag': 'A!', 'seed': 1, 'p0': 0.5}]), 'tag'),
    (dict(bogus=1), 'unknown configuration keys'),
    (dict(layout={'utilization': 60}), 'unknown configuration keys'),
])
def test_illegal_configurations_are_rejected(bad, msg):
    d = base(**bad)
    if d.get('g') is None:
        d.pop('g')
    with pytest.raises(C.ConfigError, match=msg):
        C.resolve(d)


def test_defaults_are_explicit_and_stable():
    c = C.resolve(base())
    assert c.K == 4 and c.util == 60 and c.raw['clock_ns'] == 3.0 and c.nickname == 'ubpgen_t'
    assert C.resolve(json.loads(c.to_json())).sha256() == c.sha256()      # round trip


@pytest.mark.parametrize('f', sorted(p.name for p in CFG.glob('*.json')))
def test_shipped_configs_load(f):
    C.load(CFG / f)


def test_golden_counts():
    c = C.load(CFG / 'golden_r3_ubp3_u60.json')
    k = arch.counts(c)
    assert (k['lines'], k['taps'], k['sites'], k['bands'], k['segment_rows'], k['output_width']) == (548, 2192, 1408, 22, 16, 14)
    assert arch.serial_latency(c) == 8
    a = C.load(CFG / 'r3_g1_u75.json')
    assert arch.counts(a)['lines'] == 128 and arch.serial_latency(a) == 7


@pytest.mark.parametrize('g', [2, 3, 4])
def test_canonical_patterns_cover_every_ternary_vector_exactly_once(g):
    pats = canon_patterns(g)
    assert len(pats) == (3 ** g - 1) // 2
    import itertools
    for q in itertools.product((-1, 0, 1), repeat=g):
        if any(q):
            hits = [(s, p) for p in pats for s in (1, -1) if tuple(s * v for v in p) == q]
            assert len(hits) == 1


@pytest.mark.parametrize('fabric, g, n', [('ubp', 3, 64), ('ubp', 2, 7), ('ubp', 4, 10), ('g1', None, 9), ('pc2', None, 9)])
def test_selection_rule_is_exact(fabric, g, n):
    """Arithmetic model of the programmed fabric: y_i = sum_leaves (+-pattern . x_block) must equal W @ x."""
    d = {'name': 't', 'fabric': fabric, 'n': n, 'm': 8}
    if g:
        d['g'] = g
    c = C.resolve(d)
    rng = np.random.default_rng(0)
    for p0 in (0.0, 0.4, 0.9):
        W = rng.choice(np.array([-1, 0, 1], dtype=np.int8), size=(c.m, c.n), p=[(1 - p0) / 2, p0, (1 - p0) / 2])
        x = rng.integers(-127, 128, size=c.n)
        blocks = arch.blocks(c)
        for i in range(c.m):
            acc = 0
            for k, cols in enumerate(blocks):
                L = arch.leaf_source(c, W, i, k)
                if L is None:
                    continue
                if fabric == 'ubp':
                    pol, rest = L[1], L[2:]
                    b, idx = map(int, rest.split('_'))
                    p = canon_patterns(len(blocks[b]))[idx]
                    v = sum(pv * int(x[cc]) for pv, cc in zip(p, blocks[b]))
                else:
                    pol, j = L[1], int(L[2:])
                    v = int(x[j])
                acc += v if pol == 'p' else -v
            assert acc == int(W[i].astype(int) @ x)


def test_band_order_matches_validated_placer():
    c = C.load(CFG / 'golden_r3_ubp3_u60.json')
    assert list(arch.band_lines(c))[:4] == [0, 10, 11, 12]    # string order of 'pn0_', 'pn10_', ...; golden plan agrees
