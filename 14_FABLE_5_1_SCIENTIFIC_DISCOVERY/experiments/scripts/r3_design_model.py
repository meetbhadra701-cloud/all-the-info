"""R3 design model (DERIVED). Chooses the tap segmentation from DEVELOPMENT matrices only — never W1-W5.

python3 r3_design_model.py OUTDIR

Development matrices use the same generator as the G2 test set but fresh seeds:
  D1, D2 random p0 = 0.4 (seeds 2001, 2002); D3 sparse p0 = 0.8 (2003); D4 dense p0 = 0.1 (2004);
  D5 identical rows p0 = 0.4 (2005).
Model (per UBP3 band = 3-input block; 26 lines; 64 rows at y_i = (i + 0.5)/64 of the core height):
  * a line's programmable net(s) occupy vertical met4 span; with k taps per line, rows are split into k equal
    segments and each (line, segment) is its own programmable net, spanning [min(tap, sinks), max(tap, sinks)];
  * tap of (line t, segment s) at height (s + (t + 0.5)/26)/k   (k = 1 reproduces R2's spread taps);
  * demand = max over height of the number of overlapping nets in the band (interval-graph colouring number).
Supply: met4 tracks per band = floor(band width / 0.92 um) at utilisation U (square core, 22 bands), minus tracks
lost to pad columns (R2: site column 2 + tap column 4; R3: site columns 2, taps single-track, not a column).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from g2_build import leaf_source  # noqa: E402

N = 64
CELL_AREA = 169952.0
DEV = [('D1', 2001, 0.4, False), ('D2', 2002, 0.4, False), ('D3', 2003, 0.8, False), ('D4', 2004, 0.1, False),
       ('D5', 2005, 0.4, True)]


def dev_matrix(seed, p0, same_rows):
    rng = np.random.default_rng(seed)
    pw = [(1 - p0) / 2, p0, (1 - p0) / 2]
    if same_rows:
        return np.repeat(rng.choice(np.array([-1, 0, 1], dtype=np.int8), size=(1, N), p=pw), N, axis=0)
    return rng.choice(np.array([-1, 0, 1], dtype=np.int8), size=(N, N), p=pw)


def band_lines(k_band):
    from e5_build import canon_patterns
    npat = len(canon_patterns(3 if k_band < 21 else 1))
    return [f'pp{k_band}_{q}' for q in range(npat)] + [f'pn{k_band}_{q}' for q in range(npat)]


def peak_demand(W, k):
    worst = 0
    per_band = []
    for b in range(22):
        lines = band_lines(b)
        order = {L: j for j, L in enumerate(sorted(lines, key=lambda L: (int(L.split('_')[1]), L[1])))}
        sinks = {}
        for i in range(N):
            L = leaf_source('ubp3s', W, i, b, N)
            if L is not None:
                sinks.setdefault(L, []).append(i)
        iv = []
        for L, rows in sinks.items():
            t = order[L]
            T = len(lines)
            for s in range(k):
                seg = [(i + 0.5) / N for i in rows if int(i * k // N) == s]
                if not seg:
                    continue
                tap = (s + (t + 0.5) / T) / k
                iv.append((min(seg + [tap]), max(seg + [tap])))
        ev = sorted([(a, 1) for a, _ in iv] + [(c, -1) for _, c in iv], key=lambda e: (e[0], -e[1]))
        cur = best = 0
        for _, d in ev:
            cur += d
            best = max(best, cur)
        per_band.append(best)
        worst = max(worst, best)
    return worst, float(np.mean(per_band))


def tracks(U):
    side = (CELL_AREA / (U / 100)) ** 0.5
    return int((side / 22) // 0.92)


def main(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    res = {'tracks_per_band': {U: tracks(U) for U in (45, 52, 60)}, 'designs': {}}
    for name, k, lost in [('R2 (k=1, spread taps, 8-site taps)', 1, 6), ('R3 k=2', 2, 2), ('R3 k=4', 4, 2)]:
        rows = {}
        for tag, seed, p0, same in DEV:
            W = dev_matrix(seed, p0, same)
            rows[tag] = peak_demand(W, k)
        worst = max(v[0] for v in rows.values())
        util = {U: round(worst / (tracks(U) - lost), 2) for U in (45, 52, 60)}
        res['designs'][name] = {'k': k, 'tracks_lost_to_pad_columns': lost,
                                'peak_demand_per_dev_matrix': {t: v[0] for t, v in rows.items()},
                                'mean_band_demand_per_dev_matrix': {t: round(v[1], 1) for t, v in rows.items()},
                                'worst_peak': worst, 'peak_over_usable_tracks': util}
    (out / 'r3_design_model.json').write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main(Path(sys.argv[1]))
