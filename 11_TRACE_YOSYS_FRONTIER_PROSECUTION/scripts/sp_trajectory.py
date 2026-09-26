#!/usr/bin/env python3
"""Extract TRACE's specification-polynomial size trajectory from a log produced WITH progress steps.

TRACE prints one line per substitution step:  '║ [k/N] <#SP>, <#Cache>'
Outputs a compact summary: steps completed, N, max #SP and the step where it occurred, the size at
fixed fractions of the run, and the first step at which #SP exceeds 10x / 100x / 1000x the initial size.
Usage: sp_trajectory.py <log> [csv_out]
"""
import re
import sys
import json

ANSI = re.compile(r'\x1b\[[0-9;]*m')


def main():
    txt = ANSI.sub('', open(sys.argv[1], 'rb').read().decode('utf-8', 'replace'))
    pts = [(int(k), int(n), int(sp), int(c)) for k, n, sp, c in re.findall(r'\[(\d+)/(\d+)\]\s+(\d+),\s*(\d+)', txt)]
    if not pts:
        print(json.dumps({'status': 'NO_STEPS'}))
        return
    N = pts[0][1]
    sp0 = pts[0][2]
    kmax, _, spmax, _ = max(pts, key=lambda p: p[2])
    first = {}
    for mult in (10, 100, 1000):
        for k, _, sp, _ in pts:
            if sp > mult * sp0:
                first[f'x{mult}'] = k
                break
    frac = {}
    for f in (0.1, 0.25, 0.5, 0.75, 0.9):
        target = int(f * N)
        cand = [p for p in pts if p[0] <= target]
        if cand:
            frac[f'{int(f*100)}%'] = cand[-1][2]
    out = {'status': 'OK', 'steps_logged': len(pts), 'last_step': pts[-1][0], 'total_steps_N': N,
           'initial_sp': sp0, 'final_logged_sp': pts[-1][2], 'max_sp': spmax, 'max_sp_step': kmax,
           'first_step_exceeding': first, 'sp_at_fraction_of_N': frac}
    print(json.dumps(out))
    if len(sys.argv) > 2:
        with open(sys.argv[2], 'w') as f:
            f.write('step,N,sp,cache\n')
            for p in pts:
                f.write(','.join(map(str, p)) + '\n')


if __name__ == '__main__':
    main()
