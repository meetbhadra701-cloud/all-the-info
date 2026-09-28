"""Extraction + multi-corner static timing, and the parsers of their reports.

Origin: ubpgen/signoff.py (parse_path, parse_sta, the docker invocation) and ubpgen/resources/signoff_*.tcl.
Decoupled: the design-specific notions ("programmable" nets pgm_*, tap outputs lt_*/Z, the tap cell class) are
parameters; the TCL templates in resources/ carry no UBP cell names.

Method of record (UBP Week 2): OpenRCX-extract the routed database once, then one OpenSTA session per corner with
that corner's standard library AND every custom library cloned to that corner (harness.liberty.clone_library), the
design's SDC and propagated clocks. The period is T = clock - worst setup slack; the conservative figure of merit
uses the slowest corner.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

RES = Path(__file__).resolve().parent / 'resources'
OPENROAD = '/OpenROAD-flow-scripts/tools/install/OpenROAD/bin/openroad'
PLAT = '/OpenROAD-flow-scripts/flow/platforms/sky130hd'
TECH_LEFS = [f'{PLAT}/lef/sky130_fd_sc_hd.tlef', f'{PLAT}/lef/sky130_fd_sc_hd_merged.lef']
RCX_RULES = f'{PLAT}/rcx_patterns.rules'

PIN_ROW = re.compile(r'^\s*(?:\d+\s+)?(?:[\d.]+\s+)?(?:[\d.]+\s+)?(-?[\d.]+)\s+(-?[\d.]+)\s+[\^v]\s+(\S+)\s+\((\S+)\)\s*$')
NET_ROW = re.compile(r'^\s+(\S+) \(net\)\s*$')


def openroad(image: str, work: Path, script: str, env: dict, mounts: list[str] = (), threads: int = 1,
             timeout: int = 7200) -> str:
    """Run a TCL script with OpenROAD in the image. `work` is mounted at /work, resources/ at /res (read-only);
    `script` is a /res/<name> template or any path visible in the container. Returns stdout + stderr."""
    cmd = ['docker', 'run', '--rm', '-v', f'{Path(work).resolve()}:/work', '-v', f'{RES}:/res:ro']
    for m in mounts:
        cmd += ['-v', m]
    for k, v in env.items():
        cmd += ['-e', f'{k}={v}']
    script = script if script.startswith('/') else f'/res/{script}'
    cmd += ['-w', '/work', image, OPENROAD, '-no_init', '-threads', str(threads), '-exit', script]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return p.stdout + p.stderr


def parse_extract(out: str) -> dict:
    ex = re.search(r'SIGNOFF_EXTRACT nets_with_wires=(\d+) pgm_nets=(\d+) insts=(\d+)', out)
    if ex is None:
        raise RuntimeError('extraction failed:\n' + out[-3000:])
    return {'tool': 'OpenRCX', 'nets_with_wires': int(ex.group(1)), 'prefixed_nets': int(ex.group(2)),
            'instances': int(ex.group(3))}


def parse_path(txt: str, prog_net_prefix: str | None = None, prog_pin_regex: str | None = None) -> dict:
    """Critical-path summary from an OpenSTA full report (-fields ... net): start/end, slack, every data stage
    (pin, cell, delay, driven net), the largest-delay stage (for an input pin: the wire delay of the net arriving
    at it), and -- when the design defines them -- whether the path traverses a designated net class
    (prog_net_prefix, e.g. 'pgm_') or pin class (prog_pin_regex, e.g. r'lt_\\S+/Z$')."""
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
    prog = [r['net'] for r in rows if prog_net_prefix and r['net'] and r['net'].startswith(prog_net_prefix)]
    prog += [r['pin'] for r in rows if prog_pin_regex and re.match(prog_pin_regex, r['pin']) and r['net'] is None]
    worst = None
    if rows:
        k = max(range(len(rows)), key=lambda i: rows[i]['delay_ns'])
        net = rows[k]['net'] or (rows[k - 1]['net'] if k > 0 else None)
        worst = {'pin': rows[k]['pin'], 'cell': rows[k]['cell'], 'delay_ns': rows[k]['delay_ns'], 'net': net,
                 'kind': 'cell' if rows[k]['net'] else 'wire'}
    return {'startpoint': start.group(1) if start else None, 'endpoint': end.group(1) if end else None,
            'slack_ns': float(slack.group(1)) if slack else None, 'through_programmable_net': bool(prog),
            'programmable_nets': prog[:4], 'n_stages': len(rows), 'largest_stage': worst, 'stages': rows}


def parse_sta(out: str, prog_net_prefix: str | None = None, prog_pin_regex: str | None = None) -> dict:
    """One corner's STA log (sta_corner.tcl or the UBP signoff_sta.tcl) -> worst slacks (ns) and critical paths."""
    ws = re.search(r'SIGNOFF_WS corner=(\w+) setup=(\S+) hold=(\S+)', out)
    if ws is None:
        raise RuntimeError('STA failed:\n' + out[-3000:])
    f = lambda s: float(s) * 1e9
    pp = lambda t: parse_path(t, prog_net_prefix, prog_pin_regex)
    rec = {'corner': ws.group(1), 'setup_ws_ns': f(ws.group(2)), 'hold_ws_ns': f(ws.group(3))}
    pw = re.search(r'SIGNOFF_PROG_WS setup=(\S+)', out)
    rec['prog_setup_ws_ns'] = f(pw.group(1)) if pw and pw.group(1) != 'none' else None
    grab = lambda tag: out.split(f'{tag}_BEGIN', 1)[1].split(f'{tag}_END', 1)[0] if f'{tag}_BEGIN' in out else ''
    rec['setup_path'] = pp(grab('SIGNOFF_SETUP_PATH'))
    rec['prog_path'] = pp(grab('SIGNOFF_PROG_PATH'))
    hp = pp(grab('SIGNOFF_HOLD_PATH'))
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


def period(clock_ns: float, rec: dict) -> float:
    """Achieved period of record: T = clock - worst setup slack (negative slack lengthens T)."""
    return clock_ns - rec['setup_ws_ns']


def multi_corner(image: str, work: Path, odb: str, sdc: str, libs_by_corner: dict[str, list[str]],
                 spef: str | None = None, through: str | None = None, mounts: list[str] = (), **parse_kw) -> dict:
    """Time one database at every corner (paths as seen inside the container); returns {corner: record}."""
    out = {}
    for corner, libs in libs_by_corner.items():
        env = {'ODB': odb, 'LIBS': ' '.join(libs), 'SDC': sdc, 'CORNER': corner, 'SPEF': spef or '', 'THROUGH': through or ''}
        out[corner] = parse_sta(openroad(image, work, 'sta_corner.tcl', env, mounts), **parse_kw)
    return out
