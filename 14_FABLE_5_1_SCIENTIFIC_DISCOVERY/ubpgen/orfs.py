"""OpenROAD-flow-scripts: configuration, the frozen-base build, and per-program routing / timing.

Mount convention: the design directory is /work inside the container; the validated program-routing script
(experiments/scripts/g2_program.tcl) is mounted read-only at /scripts, and with flow.no_dce the validated synthesis
patch (dead-logic elimination disabled) replaces the image's synth_odb.tcl.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

from ._legacy import IMAGE, SCRIPTS

SDC = """create_clock -name clk -period {period} [get_ports clk]
set_input_delay 0 -clock clk [delete_from_list [all_inputs] [get_ports clk]]
set_output_delay 0 -clock clk [all_outputs]
"""
OPENROAD = '/OpenROAD-flow-scripts/tools/install/OpenROAD/bin/openroad'


def sdc_text(cfg) -> str:
    return SDC.format(period=repr(float(cfg.raw['clock_ns'])))


def config_mk(cfg) -> str:
    lay = cfg.raw['layout']
    lines = {
        'DESIGN_NAME': 'top', 'PLATFORM': 'sky130hd',
        'SYNTH_NETLIST_FILES': '/work/netlist/netlist_base.v', 'VERILOG_FILES': '/work/netlist/netlist_base.v',
        'SDC_FILE': '/work/orfs/constraint.sdc',
        'CORE_ASPECT_RATIO': lay['core_aspect_ratio'], 'CORE_MARGIN': lay['core_margin'],
        'ADDITIONAL_LEFS': '/work/cells/g2_cells.lef /work/cells/g2r3_cells.lef',
        'ADDITIONAL_LIBS': '/work/cells/g2_cells.lib /work/cells/g2r3_cells.lib',
        'PDN_TCL': '/work/cells/pdn_m1rails.tcl', 'MAX_ROUTING_LAYER': 'met3', 'MIN_CLK_ROUTING_LAYER': 'met2',
        'POST_SYNTH_TCL': '/work/cells/dont_touch_r3.tcl',
        'DESIGN_NICKNAME': cfg.nickname, 'CORE_UTILIZATION': lay['util'],
        'PWR_NETS_VOLTAGES': '', 'GND_NETS_VOLTAGES': '',
        'POST_PDN_TCL': '/work/layout/place_access.tcl',
    }
    return ''.join(f'export {k} = {v}\n'.replace(' = \n', ' =\n') for k, v in lines.items())


def write(cfg, root: Path):
    od = root / 'orfs'
    od.mkdir(exist_ok=True)
    (od / 'config.mk').write_text(config_mk(cfg))
    (od / 'constraint.sdc').write_text(sdc_text(cfg))


def _docker(root: Path, args: list[str], extra_mounts: list[str] | None = None, workdir='/work', env=None, timeout=None):
    cmd = ['docker', 'run', '--rm', '-v', f'{root}:/work']
    for m in extra_mounts or []:
        cmd += ['-v', m]
    for k, v in (env or {}).items():
        cmd += ['-e', f'{k}={v}']
    cmd += ['-w', workdir, IMAGE] + args
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def image_id() -> str:
    p = subprocess.run(['docker', 'image', 'inspect', IMAGE, '--format', '{{.Id}}'], capture_output=True, text=True)
    return p.stdout.strip()


def check_image(cfg):
    got = image_id()
    want = cfg.raw['flow']['orfs_image_id']
    if got != want:
        raise RuntimeError(f'ORFS image mismatch: {IMAGE} is {got}, configuration requires {want}')


def base_paths(cfg, root: Path) -> dict:
    nick = cfg.nickname
    r = root / 'physical' / 'orfs' / 'results' / 'sky130hd' / nick / 'base'
    lg = root / 'physical' / 'orfs' / 'logs' / 'sky130hd' / nick / 'base'
    return {'results': r, 'logs': lg, 'odb': r / '6_final.odb', 'def': r / '6_final.def', 'sdc': r / '6_final.sdc',
            'report': lg / '6_report.json', 'route_log': lg / '5_2_route.log'}


def build_base(cfg, root: Path) -> dict:
    """Run the full ORFS flow once on the W-independent base; freeze it (sha256 of 6_final.odb)."""
    check_image(cfg)
    (root / 'physical').mkdir(exist_ok=True)
    mounts = []
    if cfg.raw['flow']['no_dce']:
        mounts.append(f'{SCRIPTS / "orfs_patch" / "synth_odb.tcl"}:/OpenROAD-flow-scripts/flow/scripts/synth_odb.tcl:ro')
    nc = cfg.raw['flow']['num_cores']
    p = _docker(root, ['bash', '-c', f'make DESIGN_CONFIG=/work/orfs/config.mk WORK_HOME=/work/physical/orfs '
                                     f'NUM_CORES={nc} > /work/physical/orfs_base.log 2>&1; echo $? > /work/physical/orfs_base.rc'],
                mounts, workdir='/OpenROAD-flow-scripts/flow')
    rc = int((root / 'physical' / 'orfs_base.rc').read_text().strip() or 1)
    bp = base_paths(cfg, root)
    gds = gds_status(root, rc)
    ok = bp['odb'].exists() and bp['report'].exists() and (rc == 0 or gds == 'expected-failure')
    if not ok:
        raise RuntimeError(f'ORFS base flow failed (rc {rc}, gds {gds}); see {root / "physical" / "orfs_base.log"}')
    sha = hashlib.sha256(bp['odb'].read_bytes()).hexdigest()
    (root / 'physical' / 'base_odb.sha256').write_text(sha + '\n')
    m = base_metrics(cfg, root)
    m.update({'orfs_rc': rc, 'gds_merge': gds})
    return m


def gds_status(root: Path, rc: int) -> str:
    """The via-site and tap cells are abstract (no GDS), so KLayout's final GDS merge (after 6_final.odb/def and
    6_report are written) fails with exactly these errors; the historical R3 runs have the same rc 2. Any other
    failure is a real failure."""
    if rc == 0:
        return 'ok'
    log = (root / 'physical' / 'orfs_base.log').read_text()
    errs = set(re.findall(r"\[ERROR\] LEF Cell '(\w+)' has no matching GDS", log))
    only_gds = ('do-gds-merged] Error' in log and errs and errs <= {'LTAP2', 'LTAP', 'VSITE_BUF', 'VSITE_ZERO', 'VSITE_ONE'}
                and log.count('] Error') == log.count('gds-merged] Error') + log.count('6_1_merged.gds] Error'))
    return 'expected-failure' if only_gds else 'unexpected-failure'


def base_metrics(cfg, root: Path) -> dict:
    bp = base_paths(cfg, root)
    rep = json.loads(bp['report'].read_text())
    drc = None
    for line in bp['route_log'].read_text().splitlines():
        if 'Number of violations =' in line:
            drc = int(line.split('=')[-1].strip().rstrip('.'))
    fp = json.loads((bp['logs'] / '2_1_floorplan.json').read_text())
    return {'odb_sha256': (root / 'physical' / 'base_odb.sha256').read_text().split()[0],
            'drc_final': drc, 'setup_ws_ns': rep.get('finish__timing__setup__ws'),
            'hold_ws_ns': rep.get('finish__timing__hold__ws'), 'core_area_um2': rep.get('finish__design__core__area'),
            'cell_area_um2': fp.get('floorplan__design__instance__area__stdcell'),   # the A x T area (R3 rule)
            'instance_count': rep.get('finish__design__instance__count')}


def run_program(cfg, root: Path, tag: str, mode: str) -> Path:
    """mode route: delete base nets (all <= met3), apply the program, GRT + DRT on met4-met5 only.
    mode sta: apply the program to the intact base, placement-parasitic STA, write the programmed netlist."""
    bp = base_paths(cfg, root)
    pd = root / 'programs' / tag
    out = f'/work/programs/{tag}/pnr'
    env = {'BASE_ODB': f'/work/{bp["odb"].relative_to(root)}', 'BASE_SDC': f'/work/{bp["sdc"].relative_to(root)}',
           'PROG_TCL': f'/work/programs/{tag}/prog.tcl', 'OUT': out, 'MODE': mode,
           'DRT_ITERS': str(cfg.raw['flow']['drt_iters'])}
    nc = cfg.raw['flow']['num_cores']
    p = _docker(root, [OPENROAD, '-no_init', '-threads', str(nc), '-exit', '/scripts/g2_program.tcl'],
                [f'{SCRIPTS}:/scripts:ro'], env=env)
    log = pd / f'pnr_{mode}.log'
    log.write_text(p.stdout + p.stderr)
    return log


def route_metrics(pd: Path) -> dict:
    route = (pd / 'pnr_route.log').read_text()
    viol = [int(x) for x in re.findall(r'Number of violations = (\d+)', route)]
    res = re.search(r'G2_RESULT drc=(\d+)', route)
    cong = {}
    m = route.split('Final congestion report')[-1] if 'Final congestion report' in route else ''
    for layer in ('met4', 'met5'):
        mm = re.search(rf'\n{layer}\s+(\d+)\s+(\d+)\s+([\d.]+)%\s+(\d+)\s*/\s*(\d+)\s*/\s*(\d+)', m)
        if mm:
            cong[layer] = {'usage_pct': float(mm.group(3)), 'overflow': int(mm.group(6))}
    wl = {L: float(x) for L, x in re.findall(r'Total wire length on LAYER (met4|met5) = ([\d.]+) um', route)[-2:]}
    vias = re.findall(r'Total number of vias = (\d+)', route)
    return {'drt_final': None if res is None else int(res.group(1)), 'drt_iterations_run': len(viol) - 1 if viol else None,
            'drt_trajectory': viol, 'grt': cong, 'wirelength_um': wl, 'vias': int(vias[-1]) if vias else None}


def sta_metrics(pd: Path) -> dict:
    sta = (pd / 'pnr_sta.log').read_text()
    ws = re.search(r'G2_TIMING setup_ws=(\S+) hold_ws=(\S+)', sta)
    pws = re.search(r'G2_PROG_WS setup=(\S+)', sta)
    f = lambda s: float(s) * 1e9
    return {'setup_ws_ns': f(ws.group(1)) if ws else None, 'hold_ws_ns': f(ws.group(2)) if ws else None,
            'prog_setup_ws_ns': f(pws.group(1)) if pws and pws.group(1) != 'none' else None}
