"""MR-SIGNOFF (04 Part 1, pre-registered): exact metamorphic invariance of OpenRCX extraction + OpenSTA timing.

MR0 identical rerun; MR1 permuted DEF COMPONENTS / NETS sections (seed 1); MR2 consistent renaming of every net and
instance (ports kept). Each variant: LEF+DEF -> OpenRCX (harness extract.tcl) -> SPEF + ODB -> OpenSTA tt (harness
sta_corner.tcl). Compared per net (names mapped back): total capacitance, total coupling capacitance, total resistance;
and the setup / hold worst slack.

    python3 mr_signoff.py d1|d2
"""
from __future__ import annotations

import json
import random
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / 'SUPPORTING_ARTIFACTS' / 'research_harness'))
from harness import orfs, sky130, sta  # noqa: E402

UBP = REPO / '14_FABLE_5_1_SCIENTIFIC_DISCOVERY'
PDK = UBP / 'ubpgen_cache' / 'pdk'

DESIGNS = {
    'd1': {  # frozen UBP W2 B60 base (regenerable from ubpgen/configs/w2_b60.json)
        'results': UBP / 'ubpgen_runs/w2_b60/physical/orfs/results/sky130hd/ubpgen_w2_b60/base',
        'cells': UBP / 'ubpgen_runs/w2_b60/cells', 'lefs': ['g2_cells.lef', 'w2_cells.lef'],
        'libs': ['g2_cells.lib', 'w2_cells.lib']},
    'd2': {  # ORFS sky130hd gcd, built with ORFS defaults
        'results': HERE / 'runs/gcd/results/sky130hd/gcd/base', 'cells': None, 'lefs': [], 'libs': []},
}


# ------------------------------------------------------------------------------------------------ DEF transforms
def section(text: str, name: str):
    m = re.search(rf'^{name} (\d+) ;\n', text, re.M)
    return m.end(), text.index(f'END {name}', m.end())


def entries(body: str) -> list[str]:
    starts = [m.start() for m in re.finditer(r'^\s*- ', body, re.M)]
    return [body[a:b] for a, b in zip(starts, starts[1:] + [len(body)])]


def mr1_permute(text: str, seed: int = 1) -> str:
    rnd = random.Random(seed)
    for name in ('COMPONENTS', 'NETS'):
        b, e = section(text, name)
        ents = entries(text[b:e])
        rnd.shuffle(ents)
        text = text[:b] + ''.join(ents) + text[e:]
    return text


PAIR = re.compile(r'\(\s+(\S+)\s+(\S+)\s+\)')


def mr2_rename(text: str):
    b, e = section(text, 'COMPONENTS')
    comps = [re.match(r'\s*-\s+(\S+)', x).group(1) for x in entries(text[b:e])]
    b2, e2 = section(text, 'NETS')
    nets = [re.match(r'\s*-\s+(\S+)', x).group(1) for x in entries(text[b2:e2])]
    cmap = {c: f'mru{i}' for i, c in enumerate(comps)}
    nmap = {n: f'mrn{i}' for i, n in enumerate(nets)}
    pairs = lambda s: PAIR.sub(lambda m: f'( {cmap.get(m.group(1), m.group(1))} {m.group(2)} )', s)
    out = []
    # COMPONENTS
    b, e = section(text, 'COMPONENTS')
    body = ''.join(re.sub(r'^(\s*-\s+)(\S+)', lambda m: m.group(1) + cmap[m.group(2)], x, count=1) for x in entries(text[b:e]))
    text = text[:b] + body + text[e:]
    # NETS: the net name and the instance names of its connections
    b, e = section(text, 'NETS')
    body = ''.join(pairs(re.sub(r'^(\s*-\s+)(\S+)', lambda m: m.group(1) + nmap[m.group(2)], x, count=1)) for x in entries(text[b:e]))
    text = text[:b] + body + text[e:]
    # SPECIALNETS: instance names in connections
    b, e = section(text, 'SPECIALNETS')
    text = text[:b] + pairs(text[b:e]) + text[e:]
    # PINS: the net each port connects to
    b, e = section(text, 'PINS')
    text = text[:b] + re.sub(r'(\+ NET )(\S+)', lambda m: m.group(1) + nmap.get(m.group(2), m.group(2)), text[b:e]) + text[e:]
    return text, cmap, nmap


# ------------------------------------------------------------------------------------------------ SPEF comparison
def parse_spef(path: Path) -> dict[str, tuple[float, float, float]]:
    """net name (backslashes removed) -> (total C, total coupling C, total R)."""
    txt = path.read_text()
    nm_block = txt.split('*NAME_MAP', 1)[1].split('\n\n', 1)[0]
    nmap = dict(line.split(' ', 1) for line in nm_block.strip().splitlines() if line.startswith('*'))
    out = {}
    for m in re.finditer(r'^\*D_NET (\S+) (\S+)\n(.*?)^\*END', txt, re.M | re.S):
        name = nmap.get(m.group(1), m.group(1)).replace('\\', '')
        body = m.group(3)
        cap_s = body.split('*CAP', 1)[1].split('*RES', 1)[0] if '*CAP' in body else ''
        res_s = body.split('*RES', 1)[1] if '*RES' in body else ''
        cc = sum(float(p[3]) for p in (l.split() for l in cap_s.strip().splitlines()) if len(p) == 4)
        rr = sum(float(p[3]) for p in (l.split() for l in res_s.strip().splitlines()) if len(p) == 4)
        out[name] = (float(m.group(2)), cc, rr)
    return out


def compare(base: dict, other: dict, name_back: dict | None = None) -> dict:
    if name_back:
        other = {name_back.get(k, k): v for k, v in other.items()}
    missing = sorted(set(base) ^ set(other))
    rel = lambda a, b: abs(a - b) / max(abs(a), abs(b), 1e-30)
    diffs = []
    for k in set(base) & set(other):
        d = max(rel(x, y) for x, y in zip(base[k], other[k]))
        if d > 1e-9:
            diffs.append((d, k, base[k], other[k]))
    diffs.sort(reverse=True)
    return {'nets': len(base), 'nets_missing_or_extra': len(missing), 'missing_examples': missing[:5],
            'nets_differing': len(diffs), 'max_rel_diff': diffs[0][0] if diffs else 0.0,
            'worst': [{'net': k, 'base': b, 'variant': o, 'rel': d} for d, k, b, o in diffs[:8]]}


# ------------------------------------------------------------------------------------------------ runs
def run_variant(design: str, tag: str, def_text: str) -> dict:
    d = DESIGNS[design]
    work = HERE / 'runs' / f'{design}_{tag}'
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    (work / 'in.def').write_text(def_text)
    mounts = [f'{d["results"]}:/base:ro'] + ([f'{d["cells"]}:/cells:ro'] if d['cells'] else []) + [f'{PDK}:/pdk:ro']
    lefs = ' '.join(sta.TECH_LEFS + [f'/cells/{x}' for x in d['lefs']])
    ex = sta.openroad(orfs.IMAGE, work, 'extract.tcl', {'LEFS': lefs, 'DEF': '/work/in.def', 'RCX_RULES': sta.RCX_RULES,
                                                        'OUT_SPEF': '/work/out.spef', 'OUT_ODB': '/work/out.odb'}, mounts)
    (work / 'extract.log').write_text(ex)
    libs = [sky130.ORFS_TT] + [f'/cells/{x}' for x in d['libs']]
    so = sta.openroad(orfs.IMAGE, work, 'sta_corner.tcl', {'ODB': '/work/out.odb', 'LIBS': ' '.join(libs),
                                                           'SDC': '/base/6_final.sdc', 'SPEF': '/work/out.spef',
                                                           'CORNER': 'tt', 'THROUGH': ''}, mounts)
    (work / 'sta_tt.log').write_text(so)
    rec = sta.parse_sta(so)
    (work / 'out.odb').unlink(missing_ok=True)
    return {'tag': tag, 'extract': sta.parse_extract(ex), 'setup_ws_ns': rec['setup_ws_ns'], 'hold_ws_ns': rec['hold_ws_ns'],
            'setup_endpoint': rec['setup_path'].get('endpoint'), 'spef': str(work / 'out.spef')}


def main(design: str):
    d = DESIGNS[design]
    orig = (d['results'] / '6_final.def').read_text()
    res = {'design': design, 'def': str(d['results'] / '6_final.def'), 'runs': {}, 'comparisons': {}}
    res['runs']['T0a'] = run_variant(design, 'T0a', orig)
    res['runs']['T0b'] = run_variant(design, 'T0b', orig)
    res['runs']['MR1'] = run_variant(design, 'MR1', mr1_permute(orig))
    ren, cmap, nmap = mr2_rename(orig)
    res['runs']['MR2'] = run_variant(design, 'MR2', ren)
    base = parse_spef(Path(res['runs']['T0a']['spef']))
    back = {v.replace('\\', ''): k.replace('\\', '') for k, v in nmap.items()}
    for t in ('T0b', 'MR1', 'MR2'):
        c = compare(base, parse_spef(Path(res['runs'][t]['spef'])), back if t == 'MR2' else None)
        c['setup_ws_delta_ns'] = res['runs'][t]['setup_ws_ns'] - res['runs']['T0a']['setup_ws_ns']
        c['hold_ws_delta_ns'] = res['runs'][t]['hold_ws_ns'] - res['runs']['T0a']['hold_ws_ns']
        res['comparisons'][t] = c
    out = HERE / 'results'
    out.mkdir(exist_ok=True)
    (out / f'{design}.json').write_text(json.dumps(res, indent=1, default=str))
    for t, c in res['comparisons'].items():
        print(design, t, {k: c[k] for k in ('nets', 'nets_missing_or_extra', 'nets_differing', 'max_rel_diff',
                                             'setup_ws_delta_ns', 'hold_ws_delta_ns')}, flush=True)


if __name__ == '__main__':
    main(sys.argv[1])
