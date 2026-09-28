"""Design configuration: explicit, validated, hashable.

A configuration is a JSON file. Every field is documented in PARAMS (also rendered into README.md). Unknown keys
and illegal combinations raise ConfigError; nothing is silently defaulted except the documented defaults.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

FABRICS = ('ubp', 'g1', 'pc2')
SPINE_DRIVERS = ('as_synthesized', 'drive4')

# name -> (default, description). "REQUIRED" marks a mandatory field.
PARAMS = {
    'name': ('REQUIRED', 'design name; output directory name and default ORFS nickname stem'),
    'fabric': ('REQUIRED', "'ubp' = bit-serial UBP-g (B); 'g1' = per-input bit-serial fabric (A); "
                           "'pc2' = pipelined bit-plane popcount fabric (P2)"),
    'n': ('REQUIRED', 'inputs (columns of W)'),
    'm': (None, 'outputs / rows (rows of W); default n'),
    'g': (None, "UBP block size, 2..4 (fabric 'ubp' only; validated g = 3)"),
    'activation_bits': (8, 'signed activations, symmetric [-127, 127]; only 8 is supported (validated)'),
    'clock_ns': (3.0, 'SDC clock period'),
    'access.taps_per_line': (4, 'K: programmable taps per line (R3 segmented access); rows split into K segments; '
                                'K divides m'),
    'layout.util': (60, 'ORFS CORE_UTILIZATION (%)'),
    'layout.core_aspect_ratio': (1, 'ORFS CORE_ASPECT_RATIO'),
    'layout.core_margin': (2, 'ORFS CORE_MARGIN (um)'),
    'spine_driver': ('as_synthesized', "'as_synthesized' (validated R3) or 'drive4': every line (spine-root) "
                                       'driver cell upsized to the drive-4 member of its family, W-independent'),
    'programs': ([], 'weight programs: [{tag, seed, p0, same_rows}] (i.i.d. ternary, P(0) = p0, P(+1) = P(-1)) or '
                     '[{tag, file}] (a .npy int8 matrix, m x n, values in {-1,0,1})'),
    'flow.orfs_image': ('openroad/orfs:latest', 'container with Yosys, OpenROAD and ORFS (the only supported tag)'),
    'flow.orfs_image_id': ('sha256:69df744e2b5ce26a14950713fd2d74b96ec8c9bd8351d2719f9bb200388239ad',
                           'required image id (checked before any EDA step)'),
    'flow.num_cores': (2, 'ORFS NUM_CORES / OpenROAD threads (determinism depends on it)'),
    'flow.drt_iters': (64, 'detailed-routing iteration cap for programs (64 = OpenROAD default)'),
    'flow.no_dce': (True, 'disable ORFS dead-logic elimination (the fabric must never be pruned per W)'),
    'flow.nickname': (None, 'ORFS DESIGN_NICKNAME; default ubpgen_<name>'),
    'verify.words': (12, 'bit-serial: words simulated per check (bit-plane: 10)'),
    'verify.seed': (3, 'activation seed for the simulators'),
}


class ConfigError(ValueError):
    pass


def _get(d: dict, dotted: str):
    cur = d
    for k in dotted.split('.'):
        if not isinstance(cur, dict) or k not in cur:
            return None, False
        cur = cur[k]
    return cur, True


def _set(d: dict, dotted: str, v):
    ks = dotted.split('.')
    for k in ks[:-1]:
        d = d.setdefault(k, {})
    d[ks[-1]] = v


@dataclass(frozen=True)
class Config:
    raw: dict            # fully resolved (defaults filled)

    def __getitem__(self, dotted):
        v, ok = _get(self.raw, dotted)
        if not ok:
            raise KeyError(dotted)
        return v

    @property
    def name(self): return self.raw['name']
    @property
    def fabric(self): return self.raw['fabric']
    @property
    def n(self): return self.raw['n']
    @property
    def m(self): return self.raw['m']
    @property
    def g(self): return self.raw['g']
    @property
    def K(self): return self.raw['access']['taps_per_line']
    @property
    def util(self): return self.raw['layout']['util']
    @property
    def nickname(self): return self.raw['flow']['nickname']

    def to_json(self) -> str:
        return json.dumps(self.raw, indent=1, sort_keys=True)

    def sha256(self) -> str:
        return hashlib.sha256(json.dumps(self.raw, sort_keys=True).encode()).hexdigest()

    def with_overrides(self, **dotted) -> 'Config':
        raw = copy.deepcopy(self.raw)
        for k, v in dotted.items():
            _set(raw, k.replace('__', '.'), v)
        if 'flow.nickname' not in {k.replace('__', '.') for k in dotted}:
            raw['flow']['nickname'] = None
        return resolve(raw)


def _known_paths(d: dict, prefix=''):
    for k, v in d.items():
        p = f'{prefix}{k}'
        if isinstance(v, dict) and p not in ('programs',):
            yield from _known_paths(v, p + '.')
        else:
            yield p


def resolve(user: dict) -> Config:
    user = copy.deepcopy(user)
    user.pop('_comment', None)
    unknown = [p for p in _known_paths(user) if p not in PARAMS]
    if unknown:
        raise ConfigError(f'unknown configuration keys: {unknown}')
    raw: dict = {}
    for p, (default, _) in PARAMS.items():
        v, ok = _get(user, p)
        if not ok:
            if default == 'REQUIRED':
                raise ConfigError(f'missing required key {p!r}')
            v = copy.deepcopy(default)
        _set(raw, p, v)
    validate(raw)
    return Config(raw)


def load(path) -> Config:
    return resolve(json.loads(Path(path).read_text()))


def validate(c: dict):
    """Raise ConfigError on any illegal parameter or combination. Fills m, g and nickname defaults in place."""
    def need(cond, msg):
        if not cond:
            raise ConfigError(msg)

    need(isinstance(c['name'], str) and re.fullmatch(r'[A-Za-z0-9_]+', c['name']) is not None,
         'name: letters, digits and _ only')
    need(c['fabric'] in FABRICS, f'fabric must be one of {FABRICS}')
    for k in ('n', 'm'):
        need(c[k] is None or (isinstance(c[k], int) and not isinstance(c[k], bool)), f'{k} must be an integer')
    need(c['n'] >= 2, 'n must be >= 2')
    if c['m'] is None:
        c['m'] = c['n']
    need(c['m'] >= 1, 'm must be >= 1')
    if c['fabric'] == 'ubp':
        need(isinstance(c['g'], int) and 2 <= c['g'] <= 4, "fabric 'ubp' needs g in 2..4 (g = 1 is fabric 'g1')")
        need(c['g'] <= c['n'], 'g must not exceed n')
    else:
        need(c['g'] in (None, 1), f"g is only meaningful for fabric 'ubp' (got g = {c['g']} for {c['fabric']})")
        c['g'] = None
    need(c['activation_bits'] == 8, 'activation_bits: only 8 (symmetric INT8) is implemented and validated')
    need(isinstance(c['clock_ns'], (int, float)) and 0.5 <= c['clock_ns'] <= 50, 'clock_ns out of range [0.5, 50]')
    K = c['access']['taps_per_line']
    need(isinstance(K, int) and K >= 1, 'access.taps_per_line (K) must be an integer >= 1')
    need(c['m'] % K == 0, f'access.taps_per_line K = {K} must divide m = {c["m"]} (equal row segments)')
    u = c['layout']['util']
    need(isinstance(u, int) and 5 <= u <= 90, 'layout.util must be an integer percentage in [5, 90]')
    need(c['spine_driver'] in SPINE_DRIVERS, f'spine_driver must be one of {SPINE_DRIVERS}')
    if c['fabric'] == 'pc2':
        # 2 output bits/cycle over 7 cycles = 14-bit words; the per-row constant is 7 bits
        need(127 * c['n'] < 2 ** 13, 'pc2: n too large for its 14-bit output word (n <= 64)')
    tags = set()
    for p in c['programs']:
        need(isinstance(p, dict) and 'tag' in p, 'every program needs a tag')
        need(re.fullmatch(r'[a-z0-9_]+', p['tag']) is not None, f'program tag {p["tag"]!r}: [a-z0-9_]+')
        need(p['tag'] not in tags, f'duplicate program tag {p["tag"]}')
        tags.add(p['tag'])
        keys = set(p) - {'tag'}
        if 'file' in p:
            need(keys == {'file'}, f'program {p["tag"]}: a file program takes no other keys')
        else:
            need(keys <= {'seed', 'p0', 'same_rows'} and 'seed' in p and 'p0' in p,
                 f'program {p["tag"]}: needs seed and p0 (optional same_rows)')
            need(isinstance(p['seed'], int), f'program {p["tag"]}: seed must be an integer')
            need(0.0 <= p['p0'] <= 1.0, f'program {p["tag"]}: p0 must be in [0, 1]')
            p.setdefault('same_rows', False)
    f = c['flow']
    need(f['orfs_image'] == 'openroad/orfs:latest', 'flow.orfs_image: only openroad/orfs:latest is wired (pinned by flow.orfs_image_id)')
    need(isinstance(f['num_cores'], int) and f['num_cores'] >= 1, 'flow.num_cores >= 1')
    need(isinstance(f['drt_iters'], int) and f['drt_iters'] >= 1, 'flow.drt_iters >= 1')
    if f['nickname'] is None:
        f['nickname'] = f'ubpgen_{c["name"]}'
    need(re.fullmatch(r'[A-Za-z0-9_]+', f['nickname']) is not None, 'flow.nickname: letters, digits and _ only')
    need(isinstance(c['verify']['words'], int) and c['verify']['words'] >= 2, 'verify.words >= 2')
