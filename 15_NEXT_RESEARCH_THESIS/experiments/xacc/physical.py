"""XACC-E2 physical implementation and decision (04 Part 1, pre-registered).

For each design x clock target (3.0 / 5.0 / 8.0 ns): ORFS sky130hd (default flow, CORE_UTILIZATION 50) -> OpenRCX
extraction of 6_final.odb -> OpenSTA tt/ss/ff (pinned libraries) -> area of 6_final.def (standard cells excluding
fill, decap and well taps) -> post-route functional verification of 6_final.v (verify_pe) -> record.

    python3 physical.py run  [design ...]      # build what is missing (resumable)
    python3 physical.py decide                 # decision table from the records
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / 'SUPPORTING_ARTIFACTS' / 'research_harness'))
sys.path.insert(0, str(HERE))
from harness import accounting, decision, liberty, orfs, records, sky130, sta  # noqa: E402
import verify_pe  # noqa: E402

PDK = REPO / '14_FABLE_5_1_SCIENTIFIC_DISCOVERY' / 'ubpgen_cache' / 'pdk'
RUNS = HERE / 'runs' / 'phys'
RESULTS = HERE / 'results'
DESIGNS = ['pe_exact', 'pe_fp32_rne1', 'pe_fp32_rz1', 'pe_fp32_rne_i2', 'readout60']
TARGETS = [3.0, 5.0, 8.0]
NON_LOGIC = re.compile(r'sky130_fd_sc_hd__(fill|decap|tapvpwrvgnd)_')
MERGED_LEF = '/OpenROAD-flow-scripts/flow/platforms/sky130hd/lef/sky130_fd_sc_hd_merged.lef'


def area_table():
    tt = liberty.image_file(orfs.IMAGE)
    return accounting.area_table([tt], liberty.image_file(orfs.IMAGE, MERGED_LEF))


def build(top: str, T: float) -> dict:
    root = RUNS / f'{top}_{T:.1f}'
    rec_path = root / 'record.json'
    if rec_path.exists():
        return json.loads(rec_path.read_text())
    root.mkdir(parents=True, exist_ok=True)
    (root / 'src').mkdir(exist_ok=True)
    shutil.copy(HERE / 'rtl' / 'xacc_pe.v', root / 'src' / 'xacc_pe.v')
    cfg = {'DESIGN_NAME': top, 'PLATFORM': 'sky130hd', 'VERILOG_FILES': '/work/src/xacc_pe.v', 'CORE_UTILIZATION': 50}
    orfs.write_config(root, cfg, T)
    rc = orfs.run_flow(root, num_cores=2)
    log = (root / 'physical' / 'orfs_base.log').read_text()
    bp = orfs.paths(root, top)
    out = {'top': top, 'clock_ns': T, 'orfs_rc': rc, 'gds': orfs.gds_status(log, rc)}
    if not bp['odb'].exists():
        out['error'] = 'flow failed: ' + (orfs.grt_failure(log) or log[-400:])
        rec_path.write_text(json.dumps(out, indent=1))
        return out
    out['orfs'] = orfs.metrics(root, top)
    out['route'] = orfs.drt_metrics(bp['route_log'].read_text()) if bp['route_log'].exists() else {}
    # extraction + three corners
    mounts = [f'{bp["results"]}:/base:ro', f'{PDK}:/pdk:ro']
    ex = sta.openroad(orfs.IMAGE, root, 'extract.tcl', {'ODB': '/base/6_final.odb', 'RCX_RULES': sta.RCX_RULES,
                                                        'OUT_SPEF': '/work/signoff.spef', 'OUT_ODB': '/work/signoff.odb'}, mounts)
    (root / 'extract.log').write_text(ex)
    out['extraction'] = sta.parse_extract(ex)
    libs = {'tt': [sky130.ORFS_TT], 'ss': [f'/pdk/{sky130.CORNERS["ss"][0]}'], 'ff': [f'/pdk/{sky130.CORNERS["ff"][0]}']}
    corners = sta.multi_corner(orfs.IMAGE, root, '/work/signoff.odb', '/base/6_final.sdc', libs, spef='/work/signoff.spef',
                               mounts=mounts)
    for c, r in corners.items():
        r['T_ns'] = sta.period(T, r)
        for k in ('setup_path', 'prog_path', 'hold_path'):
            if k in r and 'stages' in r[k]:
                r[k] = {kk: vv for kk, vv in r[k].items() if kk != 'stages'}
    out['corners'] = corners
    for f in ('signoff.odb',):
        (root / f).unlink(missing_ok=True)
    # area of the final layout (logic incl. flow-inserted buffers; no fill / decap / taps)
    area = area_table()
    comps = accounting.def_components(bp['def'].read_text())
    out['area_um2'] = round(sum(area[m] for _, m in comps if not NON_LOGIC.match(m)), 3)
    out['area_all_um2'] = round(sum(area[m] for _, m in comps), 3)
    # post-route functional verification
    if top != 'readout60':
        shutil.copy(bp['results'] / '6_final.v', root / '6_final.v')
        v = verify_pe.verify(root, '6_final.v', top, liberty=True, mutants=False)
        out['verify'] = {'matches_golden': v['matches_golden'], 'match': v['match']}
        (root / '6_final.v').unlink()
    else:
        out['verify'] = verify_readout(root, bp)
    out['valid'] = bool(out['verify'].get('matches_golden') and out['route'].get('drt_final') == 0
                        and all(c['hold_ws_ns'] >= 0 for c in corners.values()))
    orfs.prune(bp['results'])
    rec = records.record({'top': top, 'clock_ns': T, 'flow': cfg}, 'xacc-e2 build', out, REPO,
                         ('15_NEXT_RESEARCH_THESIS/experiments/xacc',),
                         tools={'image': orfs.IMAGE, 'image_id': orfs.image_id()})
    records.append(RESULTS / 'e2_records.jsonl', rec)
    rec_path.write_text(json.dumps(out, indent=1))
    return out


def verify_readout(root: Path, bp: dict) -> dict:
    """60-bit two's complement -> FP32 RNE of v * 2^-20: 1024 lanes x 400 cycles of random, near-tie and extreme
    values, against an exact-integer RNE model (latency 2)."""
    import numpy as np
    from aigsim import AIGSim, pack_bits, unpack_bits
    shutil.copy(bp['results'] / '6_final.v', root / '6_final.v')
    aag = verify_pe.to_aag(root, '6_final.v', 'readout60', '_ro.aag', True)
    (root / '6_final.v').unlink()
    sim = AIGSim(aag)
    rng = np.random.default_rng(5)
    T, lanes = 400, 1024
    mags = rng.integers(0, 60, size=(T, lanes))
    v = np.array([[int(rng.integers(0, 1 << max(m, 1))) for m in row] for row in mags], dtype=object)
    for t in range(0, T, 7):                                    # exact ties: ...1 followed by 100..0 below the 24 bits
        for L in range(0, lanes, 5):
            k = int(rng.integers(25, 58))
            v[t, L] = (int(rng.integers(1 << 23, 1 << 24)) << (k - 23)) | (1 << (k - 24))
    v[:, :8] = [(1 << 58) - 1, -(1 << 58), 1, -1, 0, (1 << 24) - 1, 1 << 24, -(1 << 40)]
    sign = rng.random((T, lanes)) < 0.5
    v = np.where(sign, -v, v)
    v = np.vectorize(lambda x: max(min(int(x), (1 << 59) - 1), -(1 << 59)))(v).astype(object)
    got = np.zeros((T, lanes), dtype=object)

    def drive(c):
        d = {'clk': np.zeros(lanes // 64, np.uint64)}
        u = [int(x) & ((1 << 60) - 1) for x in v[c]]
        for i in range(60):
            d[f'v[{i}]'] = pack_bits(np.array([(x >> i) & 1 for x in u], dtype=np.uint8))
        return d

    def sample(c, get):
        bits = np.stack([unpack_bits(get(f'f[{i}]')) for i in range(32)])
        got[c] = [int(sum(int(b) << i for i, b in enumerate(bits[:, L]))) for L in range(lanes)]
    sim.run(T, lanes // 64, drive, sample)
    aag.unlink()

    def ref(x: int) -> int:
        s = 1 if x < 0 else 0
        m = abs(x)
        if m == 0:
            return 0
        n = m.bit_length()
        if n > 24:
            sh = n - 24
            q, r = m >> sh, m & ((1 << sh) - 1)
            h = 1 << (sh - 1)
            if r > h or (r == h and q & 1):
                q += 1
            m = q << sh
        return int(np.float32(np.ldexp(float(m), -20)).view(np.uint32)) | (s << 31)
    bad = sum(1 for c in range(2, T) for L in range(lanes) if got[c, L] != ref(int(v[c - 2, L])))
    return {'matches_golden': bad == 0, 'match': {'cycles_checked': T - 2, 'streams': lanes, 'mismatches': bad}}


def decide():
    recs = {}
    for p in RUNS.glob('*/record.json'):
        r = json.loads(p.read_text())
        recs[(r['top'], r['clock_ns'])] = r
    rows, best = [], {}
    for (top, T), r in sorted(recs.items()):
        if 'corners' not in r:
            rows.append({'top': top, 'T_clk': T, 'error': r.get('error')})
            continue
        axt = {c: r['area_um2'] * r['corners'][c]['T_ns'] for c in ('tt', 'ss', 'ff')}
        row = {'top': top, 'T_clk': T, 'area_um2': r['area_um2'], 'T_tt': r['corners']['tt']['T_ns'],
               'T_ss': r['corners']['ss']['T_ns'], 'T_ff': r['corners']['ff']['T_ns'],
               'AxT_ss': axt['ss'], 'AxT_tt': axt['tt'], 'AxT_ff': axt['ff'], 'valid': r['valid'],
               'drt': r['route'].get('drt_final'), 'hold_min': min(c['hold_ws_ns'] for c in r['corners'].values()),
               'verified': r['verify'].get('matches_golden'),
               'ss_limit': r['corners']['ss']['setup_path'].get('largest_stage'),
               'ss_endpoint': r['corners']['ss']['setup_path'].get('endpoint')}
        rows.append(row)
        if r['valid'] and (top not in best or row['AxT_ss'] < best[top]['AxT_ss']):
            best[top] = row
    res = {'rows': rows, 'best': best}
    need = ['pe_exact', 'pe_fp32_rne1', 'pe_fp32_rz1', 'pe_fp32_rne_i2', 'readout60']
    if all(k in best for k in need):
        # the readout is off the accumulation loop and shared by N_share PEs (it converts one result per
        # K/16 cycles per PE), so its own period does not limit throughput: use its smallest valid area
        ro = min(r['area_um2'] for r in rows if r.get('top') == 'readout60' and r.get('valid'))
        res['readout_area_um2'] = ro
        ex = best['pe_exact']
        eff = {n: ex['area_um2'] + ro / n for n in (1, 16, 64)}
        comp = {k: best[k]['AxT_ss'] for k in ('pe_fp32_rne1', 'pe_fp32_rz1', 'pe_fp32_rne_i2')}
        res['decision'] = decision.ratio_rule(eff[16] * ex['T_ss'], comp, threshold=1.0 / 1.10,
                                              required=list(comp), higher_is_better=False)
        # ratio_rule reports competitor/candidate; the pre-registered R_cost is its inverse
        res['R_cost'] = 1.0 / res['decision']['R']
        res['R_cost_by_share'] = {n: eff[n] * ex['T_ss'] / min(comp.values()) for n in eff}
        # deviation D3 check: the same ratio with the readout point chosen by its own A x T_ss instead of min area
        ro2 = best['readout60']['area_um2']
        res['R_cost_readout_at_best_axt_point'] = (ex['area_um2'] + ro2 / 16) * ex['T_ss'] / min(comp.values())
        res['verdict'] = ('PASS (structural headroom)' if res['R_cost'] <= 0.90 else
                          'PASS (cost parity)' if res['R_cost'] <= 1.10 else 'KILL')
        for c in ('tt', 'ff'):
            res[f'R_cost_{c}'] = (eff[16] * ex[f'T_{c}']) / min(best[k][f'AxT_{c}'] for k in comp)
        res['area_ratio'] = eff[16] / min(best[k]['area_um2'] for k in comp)
    else:
        res['verdict'] = 'INCOMPLETE'
        res['missing'] = [k for k in need if k not in best]
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / 'e2_decision.json').write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k: v for k, v in res.items() if k != 'rows'}, indent=1, default=str))
    for row in rows:
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in row.items() if k not in ('ss_limit',)})


def loops():
    """Diagnostic (reported, never decisive): worst setup slack into the accumulator registers at tt and ss."""
    out = {}
    for p in sorted(RUNS.glob('pe_*/record.json')):
        r = json.loads(p.read_text())
        root = p.parent
        bp = orfs.paths(root, r['top'])
        mounts = [f'{bp["results"]}:/base:ro', f'{PDK}:/pdk:ro', f'{HERE}:/x:ro']
        libs = {'tt': sky130.ORFS_TT, 'ss': f'/pdk/{sky130.CORNERS["ss"][0]}'}
        rec = {}
        for c, lib in libs.items():
            o = sta.openroad(orfs.IMAGE, root, '/x/loop_paths.tcl', {'ODB': '/base/6_final.odb', 'LIBS': lib,
                                                                   'SDC': '/base/6_final.sdc', 'SPEF': '/work/signoff.spef',
                                                                   'CORNER': c}, mounts)
            m = re.search(r'LOOP_WS corner=\w+ setup=(\S+) regs=(\d+)', o)
            a = re.search(r'ALL_WS corner=\w+ setup=(\S+)', o)
            rec[c] = {'loop_ws_ns': float(m.group(1)) * 1e9 if m else None, 'acc_regs': int(m.group(2)) if m else None,
                      'all_ws_ns': float(a.group(1)) * 1e9 if a else None,
                      'loop_path_ns': (r['clock_ns'] - float(m.group(1)) * 1e9) if m else None}
        out[f"{r['top']}@{r['clock_ns']}"] = rec
        print(r['top'], r['clock_ns'], rec, flush=True)
    (RESULTS / 'e2_loop_paths.json').write_text(json.dumps(out, indent=1))


if __name__ == '__main__':
    if sys.argv[1] == 'loops':
        loops()
    elif sys.argv[1] == 'run':
        todo = [(d, T) for d in (sys.argv[2:] or DESIGNS) for T in TARGETS]
        with ThreadPoolExecutor(max_workers=2) as ex:
            for r in ex.map(lambda x: build(*x), todo):
                print(r.get('top'), r.get('clock_ns'), r.get('valid'), r.get('area_um2'), r.get('error'), flush=True)
    else:
        decide()
