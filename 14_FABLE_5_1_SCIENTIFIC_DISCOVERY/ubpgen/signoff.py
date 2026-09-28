"""Sign-off timing of a routed program (Week 2, 21_WEEK2_TIMING_CLOSURE.md 1.6).

1. Merged database: the base's routed 6_final.def (all base nets and wires, fill, power) with the program's
   COMPONENTS (identical placement; the program's master swaps) and the program's routed pgm_* nets appended.
2. OpenRCX extraction of the merged database with the platform rules, exactly as the ORFS final report (EXTRACTED;
   one RC corner: the rules file has one).
3. OpenSTA of the merged database, one session per corner (tt: the ORFS library the bases were built with;
   ss_100C_1v60 / ff_n40C_1v95: the pinned volare build, see pdk.py), base SDC, propagated clocks.
Everything is recorded; the merged SPEF/ODB are deleted afterwards (size), the merged DEF too.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from . import access, orfs, pdk
from ._legacy import IMAGE

RES = Path(__file__).resolve().parent / 'resources'
PLAT = '/OpenROAD-flow-scripts/flow/platforms/sky130hd'
TECH_LEFS = [f'{PLAT}/lef/sky130_fd_sc_hd.tlef', f'{PLAT}/lef/sky130_fd_sc_hd_merged.lef']
RCX_RULES = f'{PLAT}/rcx_patterns.rules'
CORNERS = ('tt', 'ss', 'ff')


def _section(text: str, start: str, end: str) -> tuple[int, int]:
    i = text.index(start)
    return i, text.index(end, i) + len(end)


def _via_blocks(text: str) -> dict:
    if '\nVIAS ' not in text:
        return {}
    i, j = _section(text, '\nVIAS ', 'END VIAS')
    body = text[i:j]
    return {m.group(1): m.group(0) for m in re.finditer(r'\n\s*-\s+(\S+)[^;]*;', body)}


def merge_def(base_def: Path, prog_def: Path, out: Path) -> dict:
    b, p = base_def.read_text(), prog_def.read_text()
    # components: the program's (same placement, verified by invariance; master swaps applied)
    bi, bj = _section(b, '\nCOMPONENTS ', 'END COMPONENTS')
    pi, pj = _section(p, '\nCOMPONENTS ', 'END COMPONENTS')
    merged = b[:bi] + p[pi:pj] + b[bj:]
    # vias: union (the program may use generated vias the base does not)
    bv, pv = _via_blocks(merged), _via_blocks(p)
    extra = {k: v for k, v in pv.items() if k not in bv}
    if extra:
        if '\nVIAS ' in merged:
            i, j = _section(merged, '\nVIAS ', 'END VIAS')
            n = int(re.match(r'\nVIAS (\d+)', merged[i:]).group(1))
            body = merged[i:j].replace(f'\nVIAS {n} ;', f'\nVIAS {n + len(extra)} ;', 1)
            body = body[:-len('END VIAS')] + ''.join(v.lstrip('\n') + '\n' for v in extra.values()) + 'END VIAS'
            merged = merged[:i] + body + merged[j:]
        else:
            k = merged.index('\nCOMPONENTS ')
            merged = merged[:k] + f'\nVIAS {len(extra)} ;\n' + ''.join(v.lstrip('\n') + '\n' for v in extra.values()) + 'END VIAS\n' + merged[k:]
    # nets: the base's + the program's pgm_* nets
    pn_i, pn_j = _section(p, '\nNETS ', 'END NETS')
    pnets = p[pn_i:pn_j]
    blocks = [m.group(0) for m in re.finditer(r'\n\s*-\s+pgm_\S+.*?;', pnets, flags=re.S)]
    ni, nj = _section(merged, '\nNETS ', 'END NETS')
    nets = merged[ni:nj]
    n = int(re.match(r'\nNETS (\d+)', nets).group(1))
    nets = nets.replace(f'\nNETS {n} ;', f'\nNETS {n + len(blocks)} ;', 1)
    nets = nets[:-len('END NETS')] + ''.join(x.lstrip('\n') + '\n' for x in blocks) + 'END NETS'
    merged = merged[:ni] + nets + merged[nj:]
    out.write_text(merged)
    return {'base_nets': n, 'pgm_nets': len(blocks), 'extra_vias': sorted(extra)}


def _docker(root: Path, script: str, env: dict, timeout=7200) -> str:
    cmd = ['docker', 'run', '--rm', '-v', f'{root}:/work', '-v', f'{RES}:/res:ro', '-v', f'{pdk.CACHE}:/pdk:ro']
    for k, v in env.items():
        cmd += ['-e', f'{k}={v}']
    cmd += ['-w', '/work', IMAGE, orfs.OPENROAD, '-no_init', '-threads', '1', '-exit', f'/res/{script}']
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return p.stdout + p.stderr


def corner_libs(root: Path, corner: str) -> list[str]:
    std = pdk.ORFS_TT if corner == 'tt' else f'/pdk/{pdk.CORNERS[corner][0]}'
    return [std] + [f'/work/{c}' for c in access.custom_libs(corner) if (root / c).exists()]


PIN_ROW = re.compile(r'^\s*(?:\d+\s+)?(?:[\d.]+\s+)?(?:[\d.]+\s+)?(-?[\d.]+)\s+(-?[\d.]+)\s+[\^v]\s+(\S+)\s+\((\S+)\)\s*$')
NET_ROW = re.compile(r'^\s+(\S+) \(net\)\s*$')


def parse_path(txt: str) -> dict:
    """Critical-path summary from an OpenSTA full report (-fields ... net): start/end, slack, every data stage
    (pin, cell, delay, driven net), whether the path traverses a programmable net (pgm_*, i.e. a tap output lt_*/Z),
    and the largest-delay stage with its net (for an input pin: the wire delay of the net arriving at it)."""
    if not txt.strip():
        return {}
    start = re.search(r'Startpoint:\s*(\S+)', txt)
    end = re.search(r'Endpoint:\s*(\S+)', txt)
    slack = re.search(r'(-?[\d.]+)\s+slack', txt)
    rows = []
    for line in txt.split('data arrival time')[0].splitlines():
        m = PIN_ROW.match(line)
        if m:
            rows.append({'pin': m.group(3), 'cell': m.group(4), 'delay_ns': float(m.group(1)), 'net': None})
            continue
        n = NET_ROW.match(line)
        if n and rows:
            rows[-1]['net'] = n.group(1)
    prog = [r['net'] for r in rows if r['net'] and r['net'].startswith('pgm_')]
    prog += [r['pin'] for r in rows if re.match(r'lt_\S+/Z$', r['pin']) and r['net'] is None]
    worst = None
    if rows:
        k = max(range(len(rows)), key=lambda i: rows[i]['delay_ns'])
        net = rows[k]['net'] or (rows[k - 1]['net'] if k > 0 else None)
        worst = {'pin': rows[k]['pin'], 'cell': rows[k]['cell'], 'delay_ns': rows[k]['delay_ns'], 'net': net,
                 'kind': 'cell' if rows[k]['net'] else 'wire'}
    return {'startpoint': start.group(1) if start else None, 'endpoint': end.group(1) if end else None,
            'slack_ns': float(slack.group(1)) if slack else None, 'through_programmable_net': bool(prog),
            'programmable_nets': prog[:4], 'n_stages': len(rows), 'largest_stage': worst, 'stages': rows}


def parse_sta(out: str) -> dict:
    ws = re.search(r'SIGNOFF_WS corner=(\w+) setup=(\S+) hold=(\S+)', out)
    if ws is None:
        raise RuntimeError('sign-off STA failed:\n' + out[-3000:])
    f = lambda s: float(s) * 1e9
    rec = {'corner': ws.group(1), 'setup_ws_ns': f(ws.group(2)), 'hold_ws_ns': f(ws.group(3))}
    pw = re.search(r'SIGNOFF_PROG_WS setup=(\S+)', out)
    rec['prog_setup_ws_ns'] = f(pw.group(1)) if pw and pw.group(1) != 'none' else None
    grab = lambda tag: out.split(f'{tag}_BEGIN', 1)[1].split(f'{tag}_END', 1)[0] if f'{tag}_BEGIN' in out else ''
    rec['setup_path'] = parse_path(grab('SIGNOFF_SETUP_PATH'))
    rec['prog_path'] = parse_path(grab('SIGNOFF_PROG_PATH'))
    hp = parse_path(grab('SIGNOFF_HOLD_PATH'))
    rec['hold_path'] = {k: hp.get(k) for k in ('startpoint', 'endpoint', 'slack_ns')}
    sl = re.search(r'SIGNOFF_SLEW tap_input_max=(\S+) tap_input_pin=(\S*) site_input_max=(\S+) site_input_pin=(\S*)', out)
    if sl:
        rec['transitions'] = {'tap_input_max_ns': float(sl.group(1)), 'tap_input_pin': sl.group(2),
                              'site_input_max_ns': float(sl.group(3)), 'site_input_pin': sl.group(4)}
    sd = re.search(r'SIGNOFF_SPINE_DRIVERS (.*)', out)
    if sd:
        toks = sd.group(1).split()
        rec['spine_drivers'] = {toks[i]: int(toks[i + 1]) for i in range(0, len(toks) - 1, 2)}
    return rec


def run(cfg, root: Path, tag: str, keep=False) -> dict:
    """Extract the merged base + program and time it at tt, ss, ff. Returns the sign-off record."""
    pdk.require()
    root = root.resolve()
    bp = orfs.base_paths(cfg, root)
    pd = root / 'programs' / tag
    so = pd / 'signoff'
    so.mkdir(exist_ok=True)
    merged = so / 'merged.def'
    mrec = merge_def(bp['def'], pd / 'pnr_program.def', merged)
    rel = lambda p: '/work/' + str(Path(p).relative_to(root))
    lefs = ' '.join(TECH_LEFS + [f'/work/{p}' for p in access.orfs_lefs(cfg)])
    out = _docker(root, 'signoff_extract.tcl', {'LEFS': lefs, 'MERGED_DEF': rel(merged), 'RCX_RULES': RCX_RULES,
                                                 'OUT_SPEF': rel(so / 'merged.spef'), 'OUT_ODB': rel(so / 'merged.odb')})
    (so / 'extract.log').write_text(out)
    ex = re.search(r'SIGNOFF_EXTRACT nets_with_wires=(\d+) pgm_nets=(\d+) insts=(\d+)', out)
    if ex is None or not (so / 'merged.spef').exists():
        raise RuntimeError('sign-off extraction failed:\n' + out[-3000:])
    rec = {'tag': tag, 'merge': mrec, 'extraction': {'tool': 'OpenRCX', 'rules': RCX_RULES, 'process_corner_index': 0,
                                                    'nets_with_wires': int(ex.group(1)), 'pgm_nets': int(ex.group(2)),
                                                    'instances': int(ex.group(3)),
                                                    'spef_bytes': (so / 'merged.spef').stat().st_size},
           'corners': {}}
    for c in CORNERS:
        o = _docker(root, 'signoff_sta.tcl', {'ODB': rel(so / 'merged.odb'), 'LIBS': ' '.join(corner_libs(root, c)),
                                              'SDC': rel(bp['sdc']), 'SPEF': rel(so / 'merged.spef'), 'CORNER': c})
        (so / f'sta_{c}.log').write_text(o)
        rec['corners'][c] = parse_sta(o)
        rec['corners'][c]['T_ns'] = cfg.raw['clock_ns'] - rec['corners'][c]['setup_ws_ns']
    if not keep:
        for f in ('merged.spef', 'merged.odb', 'merged.def'):
            (so / f).unlink(missing_ok=True)
    (so / 'signoff.json').write_text(json.dumps(rec, indent=1))
    return rec
