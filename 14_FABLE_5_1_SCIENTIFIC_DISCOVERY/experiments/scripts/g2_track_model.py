"""Gate 2, DERIVED: programmable-track demand of each fabric in an IDEAL structured (crossbar) W-blind base.

python3 g2_track_model.py G2_DIR

Why: the measured G2 bases are placed by ORFS from base connectivity only. The programmable nets are invisible to
that placer, so their sinks end up scattered and their Steiner trees need a lot of horizontal met5, the coarsest
layer (3.4 um pitch). A designer could instead lay the base out as a regular crossbar without knowing W:
  * one vertical band per line group (UBP3: one per 3-input block, 26 lines; per-input fabrics: one per input, 2 lines);
  * the band's via sites stacked by row at y_i = (i + 0.5) H / 64; the line taps at the band's vertical centre;
  * programmable lines run vertically on met4 (0.92 um pitch); each site reaches its line by a short met5 stub.
The binding resource is then the met4 track density inside a band: a used line occupies the interval spanned by its
tap and its sinks, and a band needs as many tracks as the maximum number of overlapping intervals (interval-graph
colouring is exact). This bound is optimistic for every design (perfect regularity, perfect track assignment).

Output: per design and W, the maximum band density, and the utilisation at which the densest band would fill a given
fraction theta of its met4 tracks (square die, bands of equal width).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

MET4_PITCH = 0.92
N_ROWS = 64
SITE = re.compile(r'vs_(\d+)_(\d+)')


def band_density(prog: dict, tap_at: float = 0.5) -> tuple[int, dict]:
    """max over bands of the max interval overlap; rows mapped to y = (i + 0.5)/64, tap at y = tap_at."""
    bands: dict[int, list[tuple[float, float]]] = {}
    for src, sites in prog['nets'].items():
        ij = [tuple(map(int, SITE.fullmatch(s).groups())) for s in sites]
        ks = {k for _, k in ij}
        assert len(ks) == 1, (src, ks)                      # every line belongs to exactly one band
        ys = [(i + 0.5) / N_ROWS for i, _ in ij] + [tap_at]
        bands.setdefault(ks.pop(), []).append((min(ys), max(ys)))
    worst = 0
    per_band = {}
    for k, iv in bands.items():
        ev = sorted([(a, 1) for a, _ in iv] + [(b, -1) for _, b in iv], key=lambda t: (t[0], -t[1]))
        cur = best = 0
        for _, d in ev:
            cur += d
            best = max(best, cur)
        per_band[k] = best
        worst = max(worst, best)
    return worst, per_band


def main(g2: Path):
    designs = {'ubp3s': 22, 'pc2': 64, 'g1s': 64}          # bands = line groups (blocks / inputs)
    lines_per_band = {'ubp3s': 26, 'pc2': 2, 'g1s': 2}
    cell_area = {}
    for d in designs:
        fp = g2 / 'orfs' / 'logs' / 'sky130hd' / f'g2_{d}_u60' / 'base' / '2_1_floorplan.log'
        if fp.exists():
            m = re.search(r'Design area (\d+) um\^2', fp.read_text())
            cell_area[d] = int(m.group(1))
    out = {'met4_pitch_um': MET4_PITCH, 'model': 'ideal structured crossbar, taps at band centre', 'designs': {}}
    for d, nb in designs.items():
        if d not in cell_area:
            continue
        rec = {'bands': nb, 'lines_per_band_reserved': lines_per_band[d], 'base_cell_area_um2': cell_area[d], 'W': {}}
        worst_all = 0
        for tag in ['w1', 'w2', 'w3', 'w4', 'w5']:
            pf = g2 / d / f'prog_{tag}.json'
            if not pf.exists():
                continue
            prog = json.loads(pf.read_text())
            dens, per_band = band_density(prog)
            dens_top, _ = band_density(prog, tap_at=0.0)
            worst_all = max(worst_all, dens)
            rec['W'][tag] = {'used_lines': len(prog['nets']), 'sinks': sum(len(v) for v in prog['nets'].values()),
                             'max_band_density_tap_centre': dens, 'max_band_density_tap_top': dens_top,
                             'mean_band_density': round(float(np.mean(list(per_band.values()))), 2)}
        rec['max_density_all_W'] = worst_all
        umax = {}
        for theta in (0.6, 0.75, 0.9):
            w_min = nb * worst_all * MET4_PITCH / theta          # die width (um) so the densest band fits
            umax[str(theta)] = round(min(1.0, cell_area[d] / w_min ** 2) * 100, 1)
        rec['U_max_pct_by_theta'] = umax
        out['designs'][d] = rec
    (g2 / 'g2_track_model.json').write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main(Path(sys.argv[1]))
