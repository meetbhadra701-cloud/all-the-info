"""Harness tests: unit behaviour, and equivalence with the validated UBP originals on committed and on-disk data.

Tiers (a missing tier is skipped, never faked):
  committed   only files in the repository (the Week-2 snapshot, the git history)
  cache       + the pinned SKY130 corner libraries (14_FABLE_5_1_SCIENTIFIC_DISCOVERY/ubpgen_cache/pdk)
  runs        + the regenerable UBP run directories (ubpgen_runs/, not committed) and docker with the ORFS image

    cd SUPPORTING_ARTIFACTS/research_harness && python3 -m pytest -q -p no:cacheprovider tests
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

HARNESS_ROOT = Path(__file__).resolve().parents[1]
REPO = HARNESS_ROOT.parents[1]
UBP = REPO / '14_FABLE_5_1_SCIENTIFIC_DISCOVERY'
W2 = UBP / 'ubpgen' / 'results' / 'week2'
RUNS = UBP / 'ubpgen_runs'
PDK = UBP / 'ubpgen_cache' / 'pdk'
sys.path.insert(0, str(HARNESS_ROOT))
sys.path.insert(0, str(UBP))
sys.path.insert(0, str(UBP / 'experiments' / 'scripts'))    # the UBP originals (as ubpgen/_legacy.py does), for equivalence

from harness import accounting, decision, liberty, oracle, orfs, prereg, records, sky130, sta  # noqa: E402


def _docker_ok() -> bool:
    if shutil.which('docker') is None:
        return False
    return subprocess.run(['docker', 'image', 'inspect', orfs.IMAGE], capture_output=True).returncode == 0


need_cache = pytest.mark.skipif(not sky130.available(PDK), reason='SKY130 corner cache absent')
need_runs = pytest.mark.skipif(not (RUNS / 'w2_b60').exists() or not _docker_ok(), reason='UBP run dirs or docker absent')


# ----------------------------------------------------------------------------------------------------- records
def test_config_hash_equals_ubpgen():
    from ubpgen import config
    for p in sorted((UBP / 'ubpgen' / 'configs').glob('*.json')):
        if p.name.startswith('suite_'):
            continue
        c = config.load(p)
        assert records.config_sha256(c.raw) == c.sha256(), p.name


def test_committed_records_hash_their_config():
    n = 0
    for f in W2.glob('*/records/*.jsonl'):
        for line in f.read_text().splitlines():
            r = json.loads(line)
            assert records.config_sha256(r['config']) == r['config_sha256'], f
            n += 1
    assert n > 50


def test_append_and_latest(tmp_path):
    p = tmp_path / 'r.jsonl'
    for i, tag in enumerate(['w1', 'w2', 'w1']):
        records.append(p, {'result': {'tag': tag, 'i': i}})
    assert records.latest_by(p, 'tag') == {'w1': {'tag': 'w1', 'i': 2}, 'w2': {'tag': 'w2', 'i': 1}}


def test_git_state_reports_this_repo():
    g = records.git_state(REPO, ('SUPPORTING_ARTIFACTS/research_harness/harness',))
    assert len(g['commit']) == 40 and isinstance(g['tree_dirty'], bool)


# ---------------------------------------------------------------------------------------------------- decision
def _week2():
    return json.loads((W2 / 'week2.json').read_text())


def test_decision_reproduces_week2_kill():
    wk = _week2()
    ds, dec = wk['designs'], wk['decision']
    comps = {k: d['AxT']['conservative'] for k, d in ds.items() if d and d['role'] == 'competitor' and d['complete']}
    out = decision.ratio_rule(ds['B60']['AxT']['conservative'], comps, threshold=1.5,
                              required=['AR2', 'P2R3', 'P2R2'], candidate_valid=dec['B_valid'])
    assert out['verdict'] == 'KILL' and dec['verdict'] == 'KILL'
    assert out['strongest'] == dec['conservative']['strongest'] == 'AR2'
    assert out['R'] == pytest.approx(dec['conservative']['R'], rel=1e-12)
    assert out['all'] == pytest.approx(dec['conservative']['all'], rel=1e-12)
    assert round(out['R'], 3) == 1.473


def test_decision_sensitivities_reproduce_week2():
    wk = _week2()
    ds, dec = wk['designs'], wk['decision']
    variants = {'nominal_w1': 'nominal_w1', 'conservative_A_incr': 'sens_A_incr', 'conservative_A_phys': 'sens_A_phys',
                'conservative_conv_2site': 'sens_conv_2site', 'ff_worst': 'ff'}
    comps = {k: d['AxT'] for k, d in ds.items() if d and d['role'] == 'competitor' and d['complete']}
    s = decision.sensitivities({v: ds['B60']['AxT'][v] for v in variants}, comps)
    for v, key in variants.items():
        assert s[v]['R'] == pytest.approx(dec[key]['R'], rel=1e-12), v
        assert s[v]['strongest'] == dec[key]['strongest'], v


def test_decision_rule_controls():
    assert decision.ratio_rule(10.0, {'a': 20.0, 'b': None}, 1.5, required=['a', 'b'])['verdict'] == 'INCOMPLETE'
    assert decision.ratio_rule(10.0, {'a': 16.0, 'b': 30.0}, 1.5)['verdict'] == 'PASS'
    assert decision.ratio_rule(10.0, {'a': 14.9, 'b': 30.0}, 1.5)['verdict'] == 'KILL'
    assert decision.ratio_rule(10.0, {'a': 16.0}, 1.5, candidate_valid={'drc': False})['verdict'] == 'KILL'
    assert decision.ratio_rule(30.0, {'a': 18.0}, 1.5, higher_is_better=True)['R'] == pytest.approx(30 / 18)


# ----------------------------------------------------------------------------------------------------- sky130
def test_sky130_pins_equal_ubpgen():
    from ubpgen import pdk
    assert sky130.CORNERS == pdk.CORNERS and sky130.URL == pdk.URL and sky130.TARBALL_SHA256 == pdk.TARBALL_SHA256
    assert sky130.ORFS_TT_SHA256 == pdk.ORFS_TT_SHA256 and sky130.MEMBER == pdk.MEMBER


# ---------------------------------------------------------------------------------------------------- liberty
@need_cache
def test_liberty_reader_equals_ubpgen():
    from ubpgen import liberty as ul
    txt = sky130.lib_path('ss', PDK).read_text()
    for cell in ('sky130_fd_sc_hd__buf_2', 'sky130_fd_sc_hd__buf_8', 'sky130_fd_sc_hd__dfxtp_4'):
        cb, ucb = liberty.cell_block(txt, cell), ul.cell_block(txt, cell)
        assert cb == ucb and liberty.area(cb) == ul.area(ucb)
    cb = liberty.cell_block(txt, 'sky130_fd_sc_hd__buf_4')
    assert liberty.pin_cap(cb, 'A') == ul.pin_cap(cb, 'A')
    for slew, cap in ((0.05, 0.01), (0.3, 0.2), (1.2, 0.9)):
        assert liberty.output_transition(txt, 'sky130_fd_sc_hd__buf_4', 'X', slew, cap) == \
            ul.output_transition('sky130_fd_sc_hd__buf_4', 'X', slew, cap, corner='ss')


@need_cache
def test_liberty_edits_equal_ubp_originals():
    import g2_cells
    from ubpgen import access
    txt = sky130.lib_path('ff', PDK).read_text()
    buf = g2_cells.extract_cell(txt, 'sky130_fd_sc_hd__buf_4')
    assert liberty.extract_cell(txt, 'sky130_fd_sc_hd__buf_4') == buf
    assert liberty.clone_cell(buf, 'LTAP', 3.68 * 2.72, {'X': 'Z'}) == g2_cells.lib_cell(buf, 'LTAP', 3.68 * 2.72, {'X': 'Z'})
    c = liberty.clone_cell(buf, 'T', 1.0, {'X': 'Z'})
    assert liberty.set_input_max_transition(c, 'A', 0.3) == access._set_input_max_transition(c, 'A', 0.3)
    assert liberty.header(txt, 'x') == access._lib_header(txt, 'x')


@need_cache
def test_max_transition_edit_leaves_exactly_one_value():
    """The UBP Week-2 defect: an inserted attribute before buf_k's own 1.5 ns is ignored (last wins)."""
    txt = sky130.lib_path('ss', PDK).read_text()
    c = liberty.clone_cell(liberty.cell_block(txt, 'sky130_fd_sc_hd__buf_2'), 'T', 1.0, {'X': 'Z'})
    assert liberty.pin_attribute_values(c, 'A', 'max_transition') == ['1.5000000000']
    e = liberty.set_input_max_transition(c, 'A', 0.3)
    assert liberty.pin_attribute_values(e, 'A', 'max_transition') == ['0.3000']
    lib = liberty.clone_library(txt, 'lib_ss', [{'from': 'sky130_fd_sc_hd__buf_2', 'name': 'T2', 'area': 5.0,
                                                  'rename': {'X': 'Z'}, 'max_transition': {'A': 0.3}}])
    assert liberty.pin_attribute_values(liberty.cell_block(lib, 'T2'), 'A', 'max_transition') == ['0.3000']
    assert lib.count('cell (') == 1 and lib.rstrip().endswith('}')


# -------------------------------------------------------------------------------------------------------- sta
def _sta_logs():
    return sorted(W2.glob('*/signoff/*/sta_*.log'))


def test_sta_parser_equals_ubpgen_and_committed_records():
    """Identical to ubpgen's parser on every committed log, and to every committed record. The first sign-off run
    (golden_r3_ubp3_u60/w1) was recorded by an earlier path parser without per-stage rows: for it, every
    number (slacks, periods, path endpoints, transitions, spine drivers) must still match."""
    from ubpgen import signoff
    logs = _sta_logs()
    assert len(logs) >= 90
    early = set()
    for log in logs:
        out = log.read_text()
        h = sta.parse_sta(out, prog_net_prefix='pgm_', prog_pin_regex=r'lt_\S+/Z$')
        assert h == signoff.parse_sta(out), log
        rec = json.loads((log.parent / 'signoff.json').read_text())['corners'][h['corner']]
        assert sta.period(3.0, h) == pytest.approx(rec['T_ns'])
        if {k: v for k, v in rec.items() if k != 'T_ns'} == h:
            continue
        early.add(str(log.relative_to(W2).parent))
        scalars = ('corner', 'setup_ws_ns', 'hold_ws_ns', 'prog_setup_ws_ns', 'transitions', 'spine_drivers', 'hold_path')
        assert {k: h.get(k) for k in scalars} == {k: rec.get(k) for k in scalars}, log
        for p in ('setup_path', 'prog_path'):
            for k in ('startpoint', 'endpoint', 'slack_ns', 'through_programmable_net', 'n_stages'):
                assert h[p].get(k) == rec[p].get(k), (log, p, k)
            assert {k: h[p]['largest_stage'][k] for k in ('pin', 'cell', 'delay_ns')} == rec[p]['largest_stage']
    assert early == {'golden_r3_ubp3_u60/signoff/w1'}


def test_extract_parser_matches_committed_records():
    for log in sorted(W2.glob('*/signoff/*/extract.log')):
        e = sta.parse_extract(log.read_text())
        rec = json.loads((log.parent / 'signoff.json').read_text())['extraction']
        assert (e['nets_with_wires'], e['prefixed_nets'], e['instances']) == \
               (rec['nets_with_wires'], rec['pgm_nets'], rec['instances']), log


def test_week2_decisive_path_is_the_tree_start_broadcast():
    """The kill's physical explanation, read by the harness parser from the committed B60 ss logs."""
    worst = max((sta.parse_sta(p.read_text()) for p in (W2 / 'w2_b60' / 'signoff').glob('*/sta_ss.log')),
                key=lambda r: -r['setup_ws_ns'])
    ls = worst['setup_path']['largest_stage']
    assert 'stt' in (ls['net'] or '') + ls['pin'] and 3.0 - worst['setup_ws_ns'] == pytest.approx(4.180, abs=5e-4)


# ------------------------------------------------------------------------------------------------- accounting
def test_flatten_and_def_components_small():
    v = ('module top (a);\n  input a;\n  sub u1 (\n  );\n  sky130_fd_sc_hd__buf_1 b0 (\n  );\nendmodule\n'
         'module sub ();\n  sky130_fd_sc_hd__inv_1 i0 (\n  );\nendmodule\n')
    assert accounting.flatten(v) == {'u1/i0': 'sky130_fd_sc_hd__inv_1', 'b0': 'sky130_fd_sc_hd__buf_1'}
    d = 'X\nCOMPONENTS 3 ;\n - u1/i0 sky130_fd_sc_hd__inv_2 + PLACED ( 0 0 ) N ;\n - b0 sky130_fd_sc_hd__buf_1 ;\n' \
        ' - rebuffer7 sky130_fd_sc_hd__buf_4 ;\nEND COMPONENTS\n'
    area = {'sky130_fd_sc_hd__inv_1': 3.0, 'sky130_fd_sc_hd__inv_2': 4.0, 'sky130_fd_sc_hd__buf_1': 3.5,
            'sky130_fd_sc_hd__buf_4': 7.5}
    r = accounting.flow_changes(v, d, area)
    assert r['resized']['delta_um2'] == 1.0 and r['inserted']['rebuffer']['count'] == 1
    assert r['sizing_area_um2'] == 8.5 and r['removed']['count'] == 0


@need_runs
def test_accounting_reproduces_committed_week2_record():
    rd = RUNS / 'w2_b60'
    nick = json.loads((rd / 'config.json').read_text())['flow']['nickname']
    tt = liberty.image_file(orfs.IMAGE)
    lef = liberty.image_file(orfs.IMAGE, '/OpenROAD-flow-scripts/flow/platforms/sky130hd/lef/sky130_fd_sc_hd_merged.lef')
    custom = [(rd / c).read_text() for c in ('cells/g2_cells.lib', 'cells/g2r3_cells.lib', 'cells/w2_cells.lib') if (rd / c).exists()]
    area = accounting.area_table([tt] + custom, lef)
    got = accounting.flow_changes((rd / 'netlist' / 'netlist_base.v').read_text(),
                                  orfs.paths(rd, nick)['def'].read_text(), area)
    want = json.loads((W2 / 'w2_b60' / 'records' / 'accounting.json').read_text())
    want.pop('base_odb_sha256')
    assert json.loads(json.dumps(got)) == want


# ------------------------------------------------------------------------------------------------------- orfs
@pytest.mark.skipif(not (RUNS / 'w2_p2r3').exists(), reason='UBP run dirs absent')
def test_grt_failure_codes_match_the_recorded_failed_points():
    failed = {f['config']: f['failure'] for f in _week2()['failed_points']}
    for d in ('w2_p2r3', 'w2_p2r2'):
        code = orfs.grt_failure((RUNS / d / 'physical' / 'orfs_base.log').read_text())
        assert code is not None and code in failed[f'{d}.json']
    assert orfs.grt_failure((RUNS / 'w2_b60' / 'physical' / 'orfs_base.log').read_text()) is None


@need_runs
def test_route_metrics_equal_ubpgen():
    from ubpgen import orfs as uo
    for pd in sorted((RUNS / 'w2_b60' / 'programs').iterdir()):
        if not (pd / 'pnr_route.log').exists():
            continue
        u, h = uo.route_metrics(pd), orfs.drt_metrics((pd / 'pnr_route.log').read_text())
        assert h['drt_trajectory'] == u['drt_trajectory'] and h['drt_final'] == u['drt_final'] == 0
        assert {k: h['grt'][k] for k in ('met4', 'met5')} == u['grt']
        assert {k: h['wirelength_um'][k] for k in u['wirelength_um']} == u['wirelength_um'] and h['vias'] == u['vias']


@need_runs
def test_gds_status_equals_ubpgen():
    from ubpgen import orfs as uo
    for rd in (RUNS / 'w2_b60', RUNS / 'w2_ar2'):
        rc = int((rd / 'physical' / 'orfs_base.rc').read_text().strip() or 1)
        log = (rd / 'physical' / 'orfs_base.log').read_text()
        h = orfs.gds_status(log, rc, {'LTAP2', 'LTAP', 'VSITE_BUF', 'VSITE_ZERO', 'VSITE_ONE'}, r'LTAPBW?\d+')
        assert h == uo.gds_status(rd, rc)


@need_runs
def test_sta_templates_reproduce_orfs_final_report():
    """End-to-end check of resources/extract.tcl + sta_corner.tcl on the frozen B60 base: OpenRCX extraction and tt
    STA reproduce the setup / hold worst slack of the ORFS final report of that base."""
    rd = RUNS / 'w2_b60'
    nick = json.loads((rd / 'config.json').read_text())['flow']['nickname']
    bp = orfs.paths(rd, nick)
    rep = json.loads(bp['report'].read_text())
    work = RUNS / '_harness_sta_check'
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir()
    try:
        mounts = [f'{bp["results"]}:/base:ro', f'{rd / "cells"}:/cells:ro']
        ex = sta.openroad(orfs.IMAGE, work, 'extract.tcl', {'ODB': '/base/6_final.odb', 'RCX_RULES': sta.RCX_RULES,
                                                            'OUT_SPEF': '/work/x.spef', 'OUT_ODB': '/work/x.odb'}, mounts)
        assert sta.parse_extract(ex)['instances'] == rep['finish__design__instance__count']
        libs = [sky130.ORFS_TT, '/cells/g2_cells.lib', '/cells/w2_cells.lib']
        r = sta.multi_corner(orfs.IMAGE, work, '/work/x.odb', '/base/6_final.sdc', {'tt': libs}, spef='/work/x.spef',
                             mounts=mounts)['tt']
        assert r['setup_ws_ns'] == pytest.approx(rep['finish__timing__setup__ws'], abs=2e-3)
        assert r['hold_ws_ns'] == pytest.approx(rep['finish__timing__hold__ws'], abs=2e-3)
    finally:
        shutil.rmtree(work, ignore_errors=True)


# ------------------------------------------------------------------------------------------------------ oracle
TOY = """aag 4 2 1 1 1
2
4
6 8
8
8 2 7
i0 a
i1 b
l0 q
o0 y[0]
c
toy: y = a & !q, q' = y
"""


def test_aag_reader_equals_legacy_and_simulator_is_exact(tmp_path):
    import e6_build
    p = tmp_path / 'toy.aag'
    p.write_text(TOY)
    a = oracle.read_aag_seq(p)
    assert a == e6_build.read_aag_seq(p)
    ain = [1, 1, 1, 0, 1, 1]
    tr = oracle.simulate(a, len(ain), lambda c, nm: ain[c] if nm == 'a' else 0)
    q, want = 0, []
    for x in ain:
        y = x & (1 - q)
        want.append(y)
        q = y
    assert list(tr['y[0]'].astype(int)) == want


def test_verdict_requires_detected_mutants():
    assert oracle.verdict(True, {'m': False})['pass']
    assert not oracle.verdict(True, {'m': True})['pass'] and oracle.verdict(True, {'m': True})['blind_to'] == ['m']
    assert not oracle.verdict(True, {})['pass']
    assert not oracle.verdict(False, {'m': False})['pass']
    r = oracle.checked(lambda d, r: d == r, 3, 3, design_mutants={'plus1': 4}, reference_mutants={'neg': -3})
    assert r['pass'] and r['mutants_detected'] == 2


@need_runs
def test_oracle_reproduces_ubp_functional_check_on_a_real_netlist():
    """The generic simulator + a 15-line UBP adapter reproduce ubpgen's recorded verdict (match, and the oracle
    mutation detected) on the smoke design's programmed netlist."""
    import e5_build
    import e6_build
    from ubpgen import arch, config, verify
    cfg = config.load(UBP / 'ubpgen' / 'configs' / 'smoke_ubp3_n9.json')
    rd = RUNS / 'smoke_ubp3_n9'
    libs = [e5_build.LIB] + [f'/work/{c}' for c in verify.CUSTOM_LIBS if (rd / c).exists()]
    aagp = oracle.netlist_to_aag(orfs.IMAGE, rd, 'programs/a/programmed_prepnr.v', 'programs/a/_harness.aag', libs)
    try:
        aag = oracle.read_aag_seq(aagp)
        W = np.load(rd / 'programs' / 'a' / 'W.npy')
        T, lat, K, seed = arch.output_width(cfg), arch.serial_latency(cfg), cfg.raw['verify']['words'], cfg.raw['verify']['seed']
        X = np.random.default_rng(seed).integers(-e5_build.XMAX, e5_build.XMAX + 1, size=(K, W.shape[1]), dtype=np.int64)

        def drive(cyc, nm):
            w, t = divmod(cyc, T)
            if nm == 'start':
                return t == 0 and w < K
            if nm == 'clk':
                return False
            j = int(nm[nm.index('[') + 1:-1])
            return bool(((X[w, j] if w < K else 0) >> min(t, 62)) & 1)
        y = oracle.bus(oracle.simulate(aag, K * T + lat + T, drive), 'y')

        def check(_, Wref):
            return all(oracle.serial_word(y[w * T + lat: w * T + lat + T, i]) == int(X[w] @ Wref[i].astype(np.int64))
                       for w in range(K) for i in range(Wref.shape[0]))
        r = oracle.checked(check, None, W, reference_mutants={'negate_first_nonzero': verify.oracle_mutation(W)})
        assert r['pass']
        assert r['matches_oracle'] == e6_build.sim_seq(aag, W, T, lat, K=K, seed=seed)
    finally:
        aagp.unlink(missing_ok=True)


# ------------------------------------------------------------------------------------------------------ prereg
def test_prereg_audit_of_week2():
    pre = '14_FABLE_5_1_SCIENTIFIC_DISCOVERY/21_WEEK2_TIMING_CLOSURE.md'
    res = ['14_FABLE_5_1_SCIENTIFIC_DISCOVERY/ubpgen/results/week2/week2.json']
    a = prereg.audit(REPO, pre, res)
    assert a['ok'] and a['commit'].startswith('3274c4c') and a['edited_since']
    assert 'kill' in prereg.first_version(REPO, pre).lower()
    # control: the auditor must reject a "pre-registration" committed after its results
    assert not prereg.audit(REPO, res[0], [pre])['ok']
