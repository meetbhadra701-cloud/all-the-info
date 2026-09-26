#!/usr/bin/env python3
"""Portfolio evaluation of TRACE (crash-safe, resumable).

TRACE's verdict depends strongly on traversal method (observed: one correct netlist is 'Correct' under -idx/-ipc,
'Buggy' under -igsm, and stalls under -dyn), so a capability claim needs a portfolio.
Per netlist (jobs CSV columns: job_id, rel_path, args (mode part, e.g. '-mul -s'), expected, note):
  * CONFIG_ORDER tried with a per-config timeout chosen by operand width W
  * expected CORRECT   -> stop at the first 'Correct'
  * expected INCORRECT -> run ALL configs (a 'Correct' anywhere would be a FALSE_PASS)
Rows are appended immediately per config run. A config whose log is already complete (has '### END') is
re-parsed instead of re-run, so interrupted runs resume without repeating work.
An optional jobs column 'configs' (';'-separated) restricts a netlist to a subset of CONFIG_ORDER (used to trim
W >= 24 runs of classes that timed out under all six configurations at W = 16; every trim is listed in
EXPERIMENTAL_MATRIX.md). Config indices k always refer to CONFIG_ORDER, so job ids stay comparable.
Usage: trace_portfolio.py <jobs.csv> <out.csv> [parallel_netlists]
"""
import csv
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trace_batch  # noqa: E402

CONFIG_ORDER = ['-dyn -p -c', '-idx -p -c', '-ipc -p -c', '-igs -p -c', '-ips -p -c', '-igsm -p -c']
TMO = {4: 60, 8: 60, 12: 90, 16: 120, 20: 180, 24: 240, 32: 300, 64: 900}
LOCK = threading.Lock()


def width(note):
    return int(note.split('W=')[1].split(';')[0])


def run_netlist(j, writer, fh):
    W = width(j['note'])
    allowed = [c.strip() for c in (j.get('configs') or '').split(';') if c.strip()] or CONFIG_ORDER
    for k, cfg in enumerate(CONFIG_ORDER):
        if cfg not in allowed:
            continue
        job = dict(j)
        job['job_id'] = f"{j['job_id']}__cfg{k}"
        job['args'] = f"{j['args']} {cfg} -no-steps"
        job['timeout_s'] = str(j.get('timeout_override') or TMO.get(W, 300))
        log = os.path.join(trace_batch.LOGDIR, job['job_id'] + '.log')
        if os.path.exists(log) and '### END' in open(log, 'rb').read().decode('utf-8', 'replace'):
            r = trace_batch.parse(job)
        else:
            r = trace_batch.run(job)
        with LOCK:
            writer.writerow(r)
            fh.flush()
        if j['expected'] == 'CORRECT' and r['trace_result'].lower().startswith('correct'):
            break


def main():
    jobs = list(csv.DictReader(open(sys.argv[1])))
    out = sys.argv[2]
    par = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    new = not os.path.exists(out)
    with open(out, 'a', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=trace_batch.FIELDS)
        if new:
            w.writeheader()
        with ThreadPoolExecutor(max_workers=par) as ex:
            list(ex.map(lambda j: run_netlist(j, w, fh), jobs))


if __name__ == '__main__':
    main()
