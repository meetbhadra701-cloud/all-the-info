"""OpenROAD-flow-scripts runner (docker) and parsers of its metrics and logs.

Origin: ubpgen/orfs.py (docker invocation, freeze, stage metrics, DRT / GRT parsers). Decoupled: the design's
config.mk is supplied by the caller (write_config), nothing assumes UBP cells, and the "expected failure" of the
final GDS merge for abstract (LEF-only) custom cells is opt-in via `abstract_cells`.

Pinned image used for every UBP result: openroad/orfs:latest, id sha256:69df744e... (check with image_id()).
A flow run is recorded by its rc file; the frozen artifact is identified by the sha256 of 6_final.odb.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from .records import sha256_file

IMAGE = 'openroad/orfs:latest'
FLOW = '/OpenROAD-flow-scripts/flow'
OPENROAD = '/OpenROAD-flow-scripts/tools/install/OpenROAD/bin/openroad'
SDC = """create_clock -name clk -period {period} [get_ports clk]
set_input_delay 0 -clock clk [delete_from_list [all_inputs] [get_ports clk]]
set_output_delay 0 -clock clk [all_outputs]
"""
KEEP = ('6_final.odb', '6_final.def', '6_final.sdc', '6_final.spef', '6_final.v', '1_synth.v', '1_2_yosys.v')


def image_id(image: str = IMAGE) -> str:
    p = subprocess.run(['docker', 'image', 'inspect', image, '--format', '{{.Id}}'], capture_output=True, text=True)
    return p.stdout.strip()


def docker(root: Path, args: list[str], mounts: list[str] = (), workdir: str = '/work', env: dict | None = None,
           image: str = IMAGE, timeout: int | None = None) -> subprocess.CompletedProcess:
    cmd = ['docker', 'run', '--rm', '-v', f'{Path(root).resolve()}:/work']
    for m in mounts:
        cmd += ['-v', m]
    for k, v in (env or {}).items():
        cmd += ['-e', f'{k}={v}']
    return subprocess.run(cmd + ['-w', workdir, image] + list(args), capture_output=True, text=True, timeout=timeout)


def write_config(root: Path, variables: dict, clock_ns: float, sdc: str | None = None) -> Path:
    """root/orfs/config.mk (DESIGN_NAME, PLATFORM, VERILOG_FILES, CORE_UTILIZATION, ... as given) + constraint.sdc.
    SDC_FILE defaults to /work/orfs/constraint.sdc."""
    od = Path(root) / 'orfs'
    od.mkdir(parents=True, exist_ok=True)
    v = {'SDC_FILE': '/work/orfs/constraint.sdc', **variables}
    (od / 'config.mk').write_text(''.join(f'export {k} = {x}\n'.replace(' = \n', ' =\n') for k, x in v.items()))
    (od / 'constraint.sdc').write_text(sdc if sdc is not None else SDC.format(period=repr(float(clock_ns))))
    return od / 'config.mk'


def paths(root: Path, nickname: str, variant: str = 'base', platform: str = 'sky130hd') -> dict:
    r = Path(root) / 'physical' / 'orfs' / 'results' / platform / nickname / variant
    lg = Path(root) / 'physical' / 'orfs' / 'logs' / platform / nickname / variant
    return {'results': r, 'logs': lg, 'odb': r / '6_final.odb', 'def': r / '6_final.def', 'sdc': r / '6_final.sdc',
            'spef': r / '6_final.spef', 'report': lg / '6_report.json', 'route_log': lg / '5_2_route.log',
            'floorplan': lg / '2_1_floorplan.json'}


def run_flow(root: Path, num_cores: int = 4, mounts: list[str] = (), image: str = IMAGE, target: str = '',
             variant: str = 'base') -> int:
    """make the full flow (or `target`) on root/orfs/config.mk; log + rc under root/physical/."""
    (Path(root) / 'physical').mkdir(exist_ok=True)
    docker(root, ['bash', '-c', f'make DESIGN_CONFIG=/work/orfs/config.mk WORK_HOME=/work/physical/orfs FLOW_VARIANT={variant} '
                                f'NUM_CORES={num_cores} {target} > /work/physical/orfs_{variant}.log 2>&1; '
                                f'echo $? > /work/physical/orfs_{variant}.rc'],
           mounts, workdir=FLOW, image=image)
    return int((Path(root) / 'physical' / f'orfs_{variant}.rc').read_text().strip() or 1)


def gds_status(log: str, rc: int, abstract_cells: set[str] = frozenset(), abstract_regex: str | None = None) -> str:
    """Custom cells with LEF but no GDS make KLayout's final GDS merge fail AFTER 6_final.* are written. That, and
    only that, is an expected failure; anything else is a real failure."""
    if rc == 0:
        return 'ok'
    errs = set(re.findall(r"\[ERROR\] LEF Cell '(\w+)' has no matching GDS", log))
    ok = lambda e: e in abstract_cells or (abstract_regex is not None and re.fullmatch(abstract_regex, e))
    only_gds = ('do-gds-merged] Error' in log and errs and all(ok(e) for e in errs)
                and log.count('] Error') == log.count('gds-merged] Error') + log.count('6_1_merged.gds] Error'))
    return 'expected-failure' if only_gds else 'unexpected-failure'


def metrics(root: Path, nickname: str, variant: str = 'base') -> dict:
    """Final-report metrics of a completed run (+ the floorplan instance area, the UBP A x T area of record)."""
    bp = paths(root, nickname, variant)
    rep = json.loads(bp['report'].read_text())
    drc = None
    if bp['route_log'].exists():
        for line in bp['route_log'].read_text().splitlines():
            if 'Number of violations =' in line:
                drc = int(line.split('=')[-1].strip().rstrip('.'))
    fp = json.loads(bp['floorplan'].read_text()) if bp['floorplan'].exists() else {}
    return {'odb_sha256': sha256_file(bp['odb']) if bp['odb'].exists() else None,
            'drc_final': drc, 'setup_ws_ns': rep.get('finish__timing__setup__ws'),
            'hold_ws_ns': rep.get('finish__timing__hold__ws'), 'core_area_um2': rep.get('finish__design__core__area'),
            'cell_area_um2': fp.get('floorplan__design__instance__area__stdcell'),
            'instance_count': rep.get('finish__design__instance__count')}


def prune(results: Path, keep: tuple[str, ...] = KEEP) -> list[str]:
    """Delete regenerable intermediate stage databases (.odb/.gds) after freezing; keep 6_final.*, netlists, logs."""
    gone = []
    for p in Path(results).iterdir():
        if p.is_file() and p.name not in keep and p.suffix in ('.odb', '.gds'):
            p.unlink()
            gone.append(p.name)
    return gone


def drt_metrics(route_log: str) -> dict:
    """Detailed-routing trajectory (violations per iteration), final count, met4/met5 GRT usage and overflow,
    wire length and via count, from an OpenROAD routing log."""
    viol = [int(x) for x in re.findall(r'Number of violations = (\d+)', route_log)]
    cong = {}
    m = route_log.split('Final congestion report')[-1] if 'Final congestion report' in route_log else ''
    for layer in ('met1', 'met2', 'met3', 'met4', 'met5'):
        mm = re.search(rf'\n{layer}\s+(\d+)\s+(\d+)\s+([\d.]+)%\s+(\d+)\s*/\s*(\d+)\s*/\s*(\d+)', m)
        if mm:
            cong[layer] = {'usage_pct': float(mm.group(3)), 'overflow': int(mm.group(6))}
    wl = {L: float(x) for L, x in re.findall(r'Total wire length on LAYER (met\d) = ([\d.]+) um', route_log)}
    vias = re.findall(r'Total number of vias = (\d+)', route_log)
    return {'drt_final': viol[-1] if viol else None, 'drt_iterations_run': len(viol) - 1 if viol else None,
            'drt_trajectory': viol, 'grt': cong, 'wirelength_um': wl, 'vias': int(vias[-1]) if vias else None}


def grt_failure(log: str) -> str | None:
    """The global-routing error code of an unroutable design (e.g. GRT-0116 / GRT-0232), else None."""
    m = re.search(r'\[ERROR (GRT-\d+)\]', log)
    return m.group(1) if m else None
