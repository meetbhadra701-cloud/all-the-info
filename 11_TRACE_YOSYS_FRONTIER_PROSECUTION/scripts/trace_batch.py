#!/usr/bin/env python3
"""Run TRACE jobs in the hardened sandbox (via WSL + docker.exe) and parse results.

jobs CSV columns: job_id, rel_path, args, timeout_s, expected, note
  expected = CORRECT | INCORRECT | UNKNOWN   (ground truth established independently of TRACE)
Output CSV columns (appended): job_id, rel_path, args, timeout_s, expected, tool_status, trace_result,
  max_polynomial, trace_elapsed_s, wall_s, max_rss_kb, and_gates, subst_steps, trace_exit, diag, note
tool_status: RESULT (a 'Result:' line was printed) | TIMEOUT | KILLED (non-timeout kill, e.g. memory) | NO_RESULT
The verdict is read ONLY from TRACE's 'Result:' line; exit codes are recorded but never interpreted as verdicts.
"""
import csv
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
WSL_RUN = '/mnt/c/Users/meetb/Desktop/CLAUDE_OPUS_5_5_RESEARCH_CONTEXT/11_TRACE_YOSYS_FRONTIER_PROSECUTION/scripts/trace_run.sh'
LOGDIR = os.path.join(ROOT, 'logs', 'trace')
os.makedirs(LOGDIR, exist_ok=True)
FIELDS = ['job_id', 'rel_path', 'args', 'timeout_s', 'expected', 'tool_status', 'trace_result', 'max_polynomial',
          'trace_elapsed_s', 'wall_s', 'cgroup_peak_mib', 'max_rss_kb', 'and_gates', 'subst_steps', 'trace_exit', 'diag', 'note']
MEM_LIMIT = 14 * 1024 ** 3   # --memory 14g in trace_run.sh (default); a job may lower it with an optional 'mem' column


def mem_limit(job):
    m = (job.get('mem') or '').strip().lower()
    return int(m[:-1]) * 1024 ** 3 if m.endswith('g') else MEM_LIMIT
# NOTE: busybox 'time -v' over-reports max RSS by ~4x (it treats ru_maxrss as pages); cgroup memory.peak is authoritative.


def grab(pat, txt, cast=str):
    m = re.search(pat, txt)
    return cast(m.group(1)) if m else ''


def run(job):
    log = os.path.join(LOGDIR, job['job_id'] + '.log')
    env = [f"MEM={job['mem']}"] if (job.get('mem') or '').strip() else []
    cmd = ['wsl.exe', '-d', 'Ubuntu-26.04', '--', 'env'] + env + ['bash', WSL_RUN, job['rel_path'], str(job['timeout_s'])] + job['args'].split()
    with open(log, 'wb') as f:
        subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)
    return parse(job)


def parse(job):
    log = os.path.join(LOGDIR, job['job_id'] + '.log')
    txt = open(log, 'rb').read().decode('utf-8', 'replace')
    res = grab(r'Result:\s*([^\r\n]+)', txt).strip()
    texit = grab(r'### TRACE_EXIT (\d+)', txt)
    wall = grab(r'### WALL_SECONDS ([\d.]+)', txt)
    peak = grab(r'### CGROUP_MEMORY_PEAK_BYTES (\d+)', txt)
    if res:
        st = 'RESULT'
    elif peak and peak.isdigit() and int(peak) >= 0.98 * mem_limit(job):
        st = 'MEMOUT'
    elif wall and float(wall) >= float(job['timeout_s']) - 2:
        st = 'TIMEOUT'
    elif texit in ('137', '9'):
        st = 'KILLED'
    else:
        st = 'NO_RESULT'
    diag_lines = [ln.strip() for ln in txt.splitlines()
                  if re.search(r'(?i)error|warning|unsupport|invalid|remainder|mismatch|abort|segment|exception|terminate', ln)
                  and 'page faults' not in ln and 'Exit status' not in ln][:6]
    row = {k: job.get(k, '') for k in ('job_id', 'rel_path', 'args', 'timeout_s', 'expected', 'note')}
    row.update({'tool_status': st, 'trace_result': res,
                'max_polynomial': grab(r'Maximum polynomial\s*:\s*(\d+)', txt),
                'trace_elapsed_s': grab(r'Elapsed time:\s*([\d.e+-]+)', txt),
                'wall_s': wall, 'cgroup_peak_mib': (f"{int(peak)/2**20:.1f}" if peak else ''), 'max_rss_kb': grab(r'Maximum resident set size \(kbytes\):\s*(\d+)', txt),
                'and_gates': grab(r'Number and-gates\s*:\s*(\d+)', txt),
                'subst_steps': grab(r'Substitution steps\s*:\s*(\d+)', txt),
                'trace_exit': texit, 'diag': ' | '.join(diag_lines)[:500]})
    print(f"{job['job_id']:<60} {st:<9} {res:<12} wall={wall} rss={row['max_rss_kb']} mp={row['max_polynomial']}", flush=True)
    return row


def main():
    if sys.argv[1] == '--reparse':
        jobs = list(csv.DictReader(open(sys.argv[2])))
        with open(sys.argv[3], 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            for j in jobs:
                w.writerow(parse(j))
        return
    jobs = list(csv.DictReader(open(sys.argv[1])))
    out = sys.argv[2]
    par = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    new = not os.path.exists(out)
    with open(out, 'a', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        with ThreadPoolExecutor(max_workers=par) as ex:
            for row in ex.map(run, jobs):
                w.writerow(row)
                f.flush()


if __name__ == '__main__':
    main()
