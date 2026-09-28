"""Pre-registration support: prove from git history that a decision rule was committed before its results.

New in the harness (UBP did this by hand: 09_PREREGISTRATION.md, 21_WEEK2_TIMING_CLOSURE.md section 1 and
configs/suite_week2.json were committed before any Week-2 build; the check below makes that auditable).

    audit(repo, 'path/to/prereg.md', ['path/to/results.json', ...])
      -> the first commit of the pre-registration, the first commit of every result path, and whether the
         pre-registration commit is an ancestor of each; plus whether the pre-registration was edited afterwards
         (allowed -- e.g. results appended to the same document -- but then the rule of record is the FIRST version,
         which is returned by first_version()).
"""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(['git', '-C', str(repo), *args], capture_output=True, text=True)


def first_commit(repo: Path, path: str) -> dict | None:
    out = _git(repo, 'log', '--diff-filter=A', '--follow', '--format=%H %cI', '--', path).stdout.split('\n')
    lines = [x for x in out if x.strip()]
    if not lines:
        return None
    h, t = lines[-1].split()
    return {'commit': h, 'time': t}


def first_version(repo: Path, path: str) -> str:
    fc = first_commit(repo, path)
    return _git(repo, 'show', f'{fc["commit"]}:{path}').stdout if fc else ''


def audit(repo: Path, prereg: str, results: list[str]) -> dict:
    p = first_commit(repo, prereg)
    if p is None:
        return {'prereg': prereg, 'ok': False, 'error': 'pre-registration not committed'}
    rows = {}
    for r in results:
        fc = first_commit(repo, r)
        if fc is None:
            rows[r] = {'committed': False, 'after_prereg': None}
            continue
        anc = _git(repo, 'merge-base', '--is-ancestor', p['commit'], fc['commit']).returncode == 0
        rows[r] = {'committed': True, **fc, 'after_prereg': anc and fc['commit'] != p['commit']}
    now = (Path(repo) / prereg).read_text() if (Path(repo) / prereg).exists() else ''
    first = first_version(repo, prereg)
    sha = lambda s: hashlib.sha256(s.encode()).hexdigest()
    return {'prereg': prereg, **p, 'first_version_sha256': sha(first), 'current_sha256': sha(now),
            'edited_since': sha(first) != sha(now), 'results': rows,
            'ok': all(v['after_prereg'] for v in rows.values() if v['committed']) and any(v['committed'] for v in rows.values())}
