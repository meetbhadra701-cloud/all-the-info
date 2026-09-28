"""Week-2 driver sizing, physical taps and sign-off (21_WEEK2_TIMING_CLOSURE.md).

  * illegal driver / access configurations are rejected (pure Python);
  * the sizing rule is deterministic: the same configuration regenerates the same driver choice and the same files;
  * the weights do not affect the choice: other programs give the same class, base netlist, plan and flow config;
  * an explicit drivers.tap_class that differs from the rule's choice is refused at generation;
  * the sized base differs from the unsized one ONLY by the tap master (logic, plan, sites unchanged);
  * the golden unsized designs are unchanged: every Week-1 generated file keeps its Week-1 sha256 (additions only),
    and the only configuration change is the explicit new defaults;
  * the generalized Verilog programming equals the validated routine on historical-tap netlists;
  * tap cells: area = 2-site pad + the buffer's sites, pin A max_transition = S, timing = the buffer's, per corner;
    the per-corner clone procedure reproduces the historical custom-cell Liberty files byte for byte at tt;
  * the sign-off DEF merge keeps every base net and adds exactly the program's nets; the path parser.
"""
import json
import re
import shutil
from pathlib import Path

import pytest

from ubpgen import access, config as C, liberty, pdk, pipeline, programs, signoff
from ubpgen._legacy import extract_cell

HERE = Path(__file__).resolve().parents[1]
CFG = HERE / 'configs'
WEEK1 = HERE / 'results' / 'week1_r3_tables'
G2CELLS = HERE.parent / 'experiments' / 'results' / 'G2' / 'cells'
docker = pytest.mark.skipif(shutil.which('docker') is None, reason='needs docker + ORFS image')


def small(**kw):
    d = {'name': 't', 'fabric': 'ubp', 'n': 9, 'm': 8, 'g': 3}
    d.update(kw)
    return d


# ------------------------------------------------------------------------------------------ configuration (no docker)
@pytest.mark.parametrize('bad, msg', [
    (dict(access={'mode': 'r2', 'taps_per_line': 4}), 'exactly one tap per line'),
    (dict(access={'mode': 'r4'}), 'access.mode must be one of'),
    (dict(drivers={'policy': 'fastest'}), 'drivers.policy must be one of'),
    (dict(drivers={'tap_class': 'buf_2'}), 'only meaningful with w2_load_rule'),
    (dict(drivers={'policy': 'w2_load_rule', 'tap_class': 'buf_3'}), 'must be null or one of'),
    (dict(drivers={'policy': 'w2_load_rule', 'tap_class': 'sky130_fd_sc_hd__buf_2'}), 'must be null or one of'),
    (dict(drivers={'policy': 'w2_load_rule', 'slew_target_ns': 0.01}), r'in \[0.05, 1.5\]'),
    (dict(drivers={'policy': 'w2_load_rule', 'slew_target_ns': 3.0}), r'in \[0.05, 1.5\]'),
    (dict(drivers={'policy': 'w2_load_rule', 'slew_target_ns': '0.3'}), r'in \[0.05, 1.5\]'),
    (dict(drivers={'policy': 'w2_load_rule'}, spine_driver='drive4'), 'drive4'),
    (dict(drivers={'policy': 'w2_load_rule', 'margin': 0.1}), 'unknown configuration keys'),
    (dict(drivers={'policy': 'w2_load_rule', 'post_build_step': 2}), 'must be 0 or 1'),
    (dict(drivers={'policy': 'w2_load_rule', 'post_build_step': True}), 'must be 0 or 1'),
    (dict(drivers={'post_build_step': 1}), 'only meaningful with w2_load_rule'),
])
def test_illegal_driver_configurations_are_rejected(bad, msg):
    with pytest.raises(C.ConfigError, match=msg):
        C.resolve(small(**bad))


def test_driver_defaults_are_the_historical_policy():
    c = C.resolve(small())
    assert c.raw['drivers'] == {'policy': 'historical', 'slew_target_ns': 0.3, 'tap_class': None, 'post_build_step': 0}
    assert c.raw['access']['mode'] == 'r3'
    for f in CFG.glob('golden_*.json'):
        assert C.load(f).raw['drivers']['policy'] == 'historical', f.name


def test_week2_configs_are_the_preregistered_designs():
    want = {'w2_b60': ('ubp', 'r3', 4, 60), 'w2_b52': ('ubp', 'r3', 4, 52), 'w2_ar2': ('g1', 'r2', 1, 75),
            'w2_p2r3': ('pc2', 'r3', 4, 67), 'w2_p2r2': ('pc2', 'r2', 1, 67), 'w2_ar3': ('g1', 'r3', 4, 75)}
    for name, (fab, mode, K, U) in want.items():
        c = C.load(CFG / f'{name}.json')
        assert (c.fabric, c.raw['access']['mode'], c.K, c.util) == (fab, mode, K, U), name
        assert c.raw['drivers']['policy'] == 'w2_load_rule' and c.raw['drivers']['slew_target_ns'] == 0.3, name
        assert [p['tag'] for p in c.raw['programs']] == ['w1', 'w2', 'w3', 'w4', 'w5'], name
        assert (c.n, c.m, c.raw['clock_ns']) == (64, 64, 3.0), name


# ------------------------------------------------------------------------------------------ sign-off helpers (no docker)
BASE_DEF = """VERSION 5.8 ;
DESIGN top ;
UNITS DISTANCE MICRONS 1000 ;
VIAS 1 ;
    - via_a + VIARULE M1M2 ;
END VIAS
COMPONENTS 2 ;
    - lt_a_s0 LTAP2 + FIRM ( 100 200 ) N ;
    - vs_0_0 VSITE_BUF + FIRM ( 300 200 ) N ;
END COMPONENTS
NETS 2 ;
    - a ( drv Q ) ( lt_a_s0 A ) + USE SIGNAL
      + ROUTED met2 ( 1 2 ) ( 3 2 ) ;
    - lf_0_0 ( vs_0_0 Z ) ( row0 B ) + USE SIGNAL ;
END NETS
END DESIGN
"""
PROG_DEF = """VERSION 5.8 ;
DESIGN top ;
UNITS DISTANCE MICRONS 1000 ;
VIAS 2 ;
    - via_a + VIARULE M1M2 ;
    - via_b + VIARULE M4M5 ;
END VIAS
COMPONENTS 2 ;
    - lt_a_s0 LTAP2 + FIRM ( 100 200 ) N ;
    - vs_0_0 VSITE_ZERO + FIRM ( 300 200 ) N ;
END COMPONENTS
NETS 1 ;
    - pgm_a_s0 ( lt_a_s0 Z ) ( vs_0_0 A ) + USE SIGNAL
      + ROUTED met4 ( 1 2 ) ( 3 2 ) via_b ;
END NETS
END DESIGN
"""


def test_merge_def(tmp_path):
    b, p, out = tmp_path / 'b.def', tmp_path / 'p.def', tmp_path / 'm.def'
    b.write_text(BASE_DEF)
    p.write_text(PROG_DEF)
    rec = signoff.merge_def(b, p, out)
    m = out.read_text()
    assert rec == {'base_nets': 2, 'pgm_nets': 1, 'extra_vias': ['via_b']}
    assert 'NETS 3 ;' in m and 'VIAS 2 ;' in m and m.count('- via_a ') == 1 and '- via_b + VIARULE M4M5' in m
    assert '- vs_0_0 VSITE_ZERO' in m and 'VSITE_BUF' not in m          # the program's master swap
    for blk in ('- a ( drv Q ) ( lt_a_s0 A ) + USE SIGNAL\n      + ROUTED met2 ( 1 2 ) ( 3 2 ) ;',
                '- lf_0_0 ( vs_0_0 Z ) ( row0 B ) + USE SIGNAL ;',
                '- pgm_a_s0 ( lt_a_s0 Z ) ( vs_0_0 A ) + USE SIGNAL\n      + ROUTED met4 ( 1 2 ) ( 3 2 ) via_b ;'):
        assert blk in m


RUN60 = HERE.parent / 'ubpgen_runs' / 'golden_r3_ubp3_u60'


def _net_names(text):
    i, j = signoff._section(text, '\nNETS ', 'END NETS')
    return re.findall(r'\n\s*-\s+(\S+)', text[i:j])


@pytest.mark.skipif(not (RUN60 / 'programs' / 'w1' / 'pnr_program.def').exists(), reason='Week-1 run directory not present')
def test_merge_def_on_a_routed_program(tmp_path):
    from ubpgen import orfs
    c = C.load(CFG / 'golden_r3_ubp3_u60.json')
    bdef = orfs.base_paths(c, RUN60)['def']
    rec = signoff.merge_def(bdef, RUN60 / 'programs' / 'w1' / 'pnr_program.def', tmp_path / 'm.def')
    prog = json.loads((RUN60 / 'programs' / 'w1' / 'prog.json').read_text())
    assert rec['pgm_nets'] == prog['n_prog_nets']
    m = (tmp_path / 'm.def').read_text()
    base_nets, merged_nets = _net_names(bdef.read_text()), _net_names(m)
    assert merged_nets[:len(base_nets)] == base_nets and len(merged_nets) == len(base_nets) + prog['n_prog_nets']
    assert sorted(merged_nets[len(base_nets):]) == sorted(f'pgm_{k}' for k in prog['nets'])


STA_SAMPLE = """SIGNOFF_WS corner=ss setup=-1.1251897e-09 hold=6.221e-10
SIGNOFF_SETUP_PATH_BEGIN
Startpoint: ng16_4/_8_ (rising edge-triggered flip-flop clocked by clk)
Endpoint: row1/_156_ (rising edge-triggered flip-flop clocked by clk)
Fanout       Cap      Slew     Delay      Time   Description
                    0.0596    0.0000    0.9596 ^ ng16_4/_8_/CLK (sky130_fd_sc_hd__dfxtp_1)
     4    0.0733    1.6800    2.0594    3.0190 ^ ng16_4/_8_/Q (sky130_fd_sc_hd__dfxtp_1)
                                                 pn16_4 (net)
                    1.6900    0.0400    3.0590 ^ lt_pn16_4_s0/A (LTAP2)
     5    0.0271    0.0932    0.5000    3.5590 ^ lt_pn16_4_s0/Z (LTAP2)
                                                 pgm_pn16_4_s0 (net)
                    0.2612    0.0017    4.0000 v row1/_156_/D (sky130_fd_sc_hd__dfxtp_1)
                                        4.0000   data arrival time
                                        3.9707 ^ row1/_156_/CLK (sky130_fd_sc_hd__dfxtp_1)
                                       -1.1252   slack (VIOLATED)
SIGNOFF_SETUP_PATH_END
SIGNOFF_HOLD_PATH_BEGIN
Startpoint: x[2] (input port clocked by clk)
Endpoint: gen0/_122_ (rising edge-triggered flip-flop clocked by clk)
             0.6221   slack (MET)
SIGNOFF_HOLD_PATH_END
SIGNOFF_PROG_WS setup=-1.1251897e-09
SIGNOFF_SLEW tap_input_max=1.69 tap_input_pin=lt_pn16_4_s0/A site_input_max=0.12 site_input_pin=vs_1_16/A
SIGNOFF_SPINE_DRIVERS sky130_fd_sc_hd__dfxtp_1 2192
"""


def test_signoff_parser():
    r = signoff.parse_sta(STA_SAMPLE)
    assert r['corner'] == 'ss' and abs(r['setup_ws_ns'] + 1.1251897) < 1e-6 and abs(r['hold_ws_ns'] - 0.6221) < 1e-6
    sp = r['setup_path']
    assert (sp['startpoint'], sp['endpoint'], sp['slack_ns'], sp['n_stages']) == ('ng16_4/_8_', 'row1/_156_', -1.1252, 5)
    assert sp['through_programmable_net'] and sp['programmable_nets'] == ['pgm_pn16_4_s0']
    assert sp['largest_stage'] == {'pin': 'ng16_4/_8_/Q', 'cell': 'sky130_fd_sc_hd__dfxtp_1', 'delay_ns': 2.0594,
                                   'net': 'pn16_4', 'kind': 'cell'}
    assert r['hold_path'] == {'startpoint': 'x[2]', 'endpoint': 'gen0/_122_', 'slack_ns': 0.6221}
    assert r['transitions'] == {'tap_input_max_ns': 1.69, 'tap_input_pin': 'lt_pn16_4_s0/A',      # slew_max: ns
                                'site_input_max_ns': 0.12, 'site_input_pin': 'vs_1_16/A'}
    assert r['spine_drivers'] == {'sky130_fd_sc_hd__dfxtp_1': 2192}


# ------------------------------------------------------------------------------------------ cells (docker: tt library)
@docker
def test_tap_cells_physical_accounting(tmp_path):
    tt = liberty.text('tt')
    lef = access.w2_lef()
    lib = access.w2_lib(tt, 'w2_cells', 0.3)
    for tc in C.TAP_CLASSES:
        k = tc.split('_')[1]
        buf = liberty.cell_block(tt, f'sky130_fd_sc_hd__{tc}')
        nsites = 2 + round(liberty.area(buf) / access.SITE_AREA)
        assert nsites == access.tap_sites(tc)
        for name in (f'LTAPB{k}', f'LTAPBW{k}'):
            cb = liberty.cell_block(lib, name)
            assert abs(liberty.area(cb) - nsites * access.SITE_AREA) < 1e-3, name
            assert re.search(r'pin\s*\(\s*"A"\s*\)\s*\{\s*max_transition : 0\.3000;', cb), name
            assert 'dont_use : true' in cb
            for kind in ('cell_rise', 'cell_fall', 'rise_transition', 'fall_transition'):
                assert liberty.tables(cb, 'Z', kind) == liberty.tables(buf, 'X', kind), (name, kind)
            assert liberty.pin_cap(cb, 'A') == liberty.pin_cap(buf, 'A')
            mac = lef[lef.index(f'MACRO {name}\n'):lef.index(f'END {name}\n')]
            assert f'SIZE {nsites * access.SITE_W:.2f} BY 2.72' in mac, name
            assert re.search(r'PIN Z.*?LAYER met4', mac, re.S) and re.search(r'PIN A.*?LAYER li1', mac, re.S)


@docker
@pytest.mark.skipif(not pdk.available(), reason='corner libraries not fetched (python3 -m ubpgen.pdk fetch)')
def test_corner_clones():
    tt = liberty.text('tt')
    # the clone procedure reproduces the historical custom-cell Liberty files at tt, byte for byte
    assert access.clone_g2_lib(tt, 'g2_cells') == (G2CELLS / 'g2_cells.lib').read_text()
    assert access.clone_g2r3_lib(tt, 'g2r3_cells') == (G2CELLS / 'g2r3_cells.lib').read_text()
    for corner in ('ss', 'ff'):
        src = liberty.text(corner)
        g2, w2 = access.clone_g2_lib(src, f'g2_cells_{corner}'), access.w2_lib(src, f'w2_cells_{corner}', 0.3)
        for cell, ref, pin in (('VSITE_BUF', 'buf_1', 'X'), ('LTAP', 'buf_4', 'X')):
            assert liberty.tables(liberty.cell_block(g2, cell), 'Z', 'cell_rise') == \
                liberty.tables(liberty.cell_block(src, f'sky130_fd_sc_hd__{ref}'), pin, 'cell_rise')
        assert liberty.tables(liberty.cell_block(w2, 'LTAPB2'), 'Z', 'rise_transition') == \
            liberty.tables(liberty.cell_block(src, 'sky130_fd_sc_hd__buf_2'), 'X', 'rise_transition')
        assert liberty.tables(liberty.cell_block(w2, 'LTAPB2'), 'Z', 'rise_transition') != \
            liberty.tables(liberty.cell_block(tt, 'sky130_fd_sc_hd__buf_2'), 'X', 'rise_transition')


# ------------------------------------------------------------------------------------------ generation (docker)
W_VARIANT = [{'tag': 'z', 'seed': 999, 'p0': 0.2}, {'tag': 'y', 'seed': 5, 'p0': 0.9, 'same_rows': True}]


@pytest.fixture(scope='module')
def gen(tmp_path_factory):
    """Generated designs shared by the tests below (about 15 s each)."""
    cache = {}

    def get(key, cfg):
        if key not in cache:
            root = tmp_path_factory.mktemp(key)
            pipeline.generate(cfg, root)
            cache[key] = root
        return cache[key]
    return get


def _cfg(name, **over):
    c = C.load(CFG / f'{name}.json')
    return c.with_overrides(**over) if over else c


def _selection(root):
    return json.loads((root / 'records' / 'drivers.json').read_text())['selection']


@docker
@pytest.mark.parametrize('name', ['w2_b60', 'w2_ar2'])
def test_sizing_is_deterministic_and_weight_independent(gen, name, tmp_path):
    c = _cfg(name)
    a = gen(name, c)
    pipeline.generate(c, tmp_path / 'again')                       # same configuration again
    b = tmp_path / 'again'
    assert _selection(a) == _selection(b)
    fa = json.loads((a / 'generation.json').read_text())['files']
    fb = json.loads((b / 'generation.json').read_text())['files']
    assert fa == fb
    cw = c.with_overrides(programs=W_VARIANT)                      # other weights
    w = gen(name + '_w', cw)
    assert _selection(a) == _selection(w)
    assert json.loads((a / 'config.json').read_text())['drivers'] == json.loads((w / 'config.json').read_text())['drivers']
    for f in ('netlist/netlist_base.v', 'layout/place_access.tcl', 'orfs/config.mk', 'cells/w2_cells.lef', 'cells/w2_cells.lib'):
        x, y = (a / f).read_text(), (w / f).read_text()
        if f == 'layout/place_access.tcl':
            x, y = x.split('\n', 1)[1], y.split('\n', 1)[1]
        assert x == y, f
    if c.raw['drivers']['tap_class'] is not None:                  # the frozen class is the rule's choice
        assert _selection(a)['class'] == c.raw['drivers']['tap_class']


@docker
@pytest.mark.parametrize('sized, unsized, old, name', [('w2_b60', 'golden_r3_ubp3_u60', 'LTAP2', 'w2_b60'),
                                                       ('w2_ar2', 'golden_r2_g1_u75', 'LTAP', 'w2_ar2')])
def test_sized_base_differs_only_by_the_tap_master(gen, sized, unsized, old, name):
    a, u = gen(sized, _cfg(sized)), gen(unsized, _cfg(unsized))
    new = _selection(a)['tap_master']
    na, nu = (a / 'netlist' / 'netlist_base.v').read_text(), (u / 'netlist' / 'netlist_base.v').read_text()
    assert nu.count(f'  {old} lt_') > 0 and f'  {new} lt_' not in nu
    assert na == nu.replace(f'  {old} lt_', f'  {new} lt_')
    assert (a / 'netlist' / 'netlist_logic.v').read_text() == (u / 'netlist' / 'netlist_logic.v').read_text()
    pa, pu = (a / 'layout' / 'place_access.tcl').read_text(), (u / 'layout' / 'place_access.tcl').read_text()
    assert pa.split('\n', 1)[1] == pu.split('\n', 1)[1]            # the W-blind plan is unchanged
    for t in ('w1', 'w5'):
        assert (a / 'programs' / t / 'prog.tcl').read_text() == (u / 'programs' / t / 'prog.tcl').read_text()


@docker
def test_explicit_tap_class_must_equal_the_rule(tmp_path):
    c = C.resolve(small(drivers={'policy': 'w2_load_rule'}, programs=[{'tag': 'a', 'seed': 1, 'p0': 0.4}]))
    pipeline.generate(c, tmp_path / 'free')
    chosen = _selection(tmp_path / 'free')['class']
    assert json.loads((tmp_path / 'free' / 'config.json').read_text())['drivers']['tap_class'] == chosen
    other = next(t for t in C.TAP_CLASSES if t != chosen)
    with pytest.raises(RuntimeError, match='differs from the rule'):
        pipeline.generate(c.with_overrides(drivers__tap_class=other), tmp_path / 'forced')
    for rec in pipeline.verify_prepnr(c, tmp_path / 'free'):     # the sized small design still computes W@x
        assert rec['pass'], rec
    # the one permitted rebuild: the next larger class, recorded as such
    c1 = c.with_overrides(drivers__post_build_step=1)
    pipeline.generate(c1, tmp_path / 'step')
    sel = _selection(tmp_path / 'step')
    assert sel['rule_class'] == chosen and sel['class'] == C.TAP_CLASSES[C.TAP_CLASSES.index(chosen) + 1]
    assert sel['post_build_step'] == 1 and any(e['class'] == sel['class'] for e in sel['evaluations'])


@docker
@pytest.mark.parametrize('name', ['golden_r3_ubp3_u60', 'golden_r3_ubp3_u52', 'golden_r3_pc2_u67', 'r3_g1_u75'])
def test_golden_unsized_designs_unchanged(gen, name):
    root = gen(name, _cfg(name))
    old = json.loads((WEEK1 / name / 'generation.json').read_text())['files']
    new = json.loads((root / 'generation.json').read_text())['files']
    assert {k: new.get(k) for k in old} == old                      # every Week-1 file, byte-identical
    added = set(new) - set(old)
    allowed = {'cells/dont_touch.tcl', 'cells/w2_cells.lef', 'cells/w2_cells.lib'} | \
              {f'cells/{c}_{k}.lib' for c in ('g2_cells', 'g2r3_cells', 'w2_cells') for k in ('ss', 'ff')}
    assert added <= allowed, added - allowed
    oc = json.loads((WEEK1 / name / 'config.json').read_text())
    nc = json.loads((root / 'config.json').read_text())
    assert nc.pop('drivers') == {'policy': 'historical', 'slew_target_ns': 0.3, 'tap_class': None, 'post_build_step': 0}
    assert nc['access'].pop('mode') == 'r3'
    assert nc == oc


@docker
@pytest.mark.parametrize('name', ['golden_r3_ubp3_u60', 'golden_r2_g1_u75', 'golden_r3_pc2_u67'])
def test_program_verilog_equals_validated_routine(gen, name):
    root = gen(name, _cfg(name))
    base = (root / 'netlist' / 'netlist_base.v').read_text()
    for spec in _cfg(name).raw['programs']:
        prog = json.loads((root / 'programs' / spec['tag'] / 'prog.json').read_text())
        assert programs.program_verilog(base, prog) == programs.program_verilog_legacy(base, prog), spec['tag']


# ------------------------------------------------------------------------------------------ area accounting
def test_flatten_hierarchical_netlist():
    from ubpgen import accounting
    v = ('module sub (a, y);\n  input a;\n  output y;\n  sky130_fd_sc_hd__inv_1 _1_ (\n    .A(a),\n    .Y(y)\n  );\nendmodule\n'
         'module top (x, z);\n  input x;\n  output z;\n  sub u0 (\n    .a(x),\n    .y(z)\n  );\n'
         '  sky130_fd_sc_hd__buf_1 \\esc[0]  (\n    .A(x),\n    .X(z)\n  );\nendmodule\n')
    assert accounting.flatten(v) == {'u0/_1_': 'sky130_fd_sc_hd__inv_1', 'esc[0]': 'sky130_fd_sc_hd__buf_1'}
    assert accounting._class('row3/place123') == 'place' and accounting._class('FILLER_0_12') == 'FILLER'


@docker
@pytest.mark.skipif(not (RUN60 / 'records' / 'base.json').exists(), reason='Week-1 run directory not present')
def test_accounting_matches_the_flow_report():
    """Every final instance is classified and priced: the logic area equals the flow's own final standard-cell area
    minus the well taps; the input area is the generated netlist's; no input instance disappears."""
    from ubpgen import accounting, orfs
    c = C.load(CFG / 'golden_r3_ubp3_u60.json')
    bp = orfs.base_paths(c, RUN60)
    r = accounting.flow_changes(RUN60, bp['def'])
    rep = json.loads(bp['report'].read_text())
    assert abs(r['final_logic_area_um2'] - (rep['finish__design__instance__area__stdcell']
                                            - rep['finish__design__instance__area__class:tap_cell'])) < 1.0
    assert r['removed']['count'] == 0 and r['input_instances'] == 13993
    assert abs(r['inserted']['FILLER']['area_um2'] - rep['finish__design__instance__area__class:fill_cell']) < 1.0
    assert r['inserted']['place']['kind'].startswith('resizer') and r['inserted']['clkbuf']['kind'].startswith('clock')
