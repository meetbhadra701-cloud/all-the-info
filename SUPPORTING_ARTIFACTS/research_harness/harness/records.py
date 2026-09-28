"""Configuration hashing, provenance and append-only JSONL records.

Origin: ubpgen/config.py (Config.sha256), ubpgen/provenance.py, ubpgen/pipeline.py (_append), ubpgen/week2.py (_latest).
Decoupled: the repository root, the tracked paths and the tool probes are parameters, not UBP constants.

Contract (what made the UBP evidence auditable):
  * a configuration is a plain JSON object; its identity is the sha256 of its canonical JSON (sorted keys);
  * every event appends one record: time, command, git state (commit, branch, dirty flag for the tracked paths),
    tool versions, config hash, the config itself and the result;
  * records are never rewritten; readers take the latest record per key.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True)


def config_sha256(cfg: dict) -> str:
    """Identical to ubpgen's Config.sha256 for the same raw dictionary."""
    return hashlib.sha256(canonical_json(cfg).encode()).hexdigest()


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def git_state(repo: Path, tracked: tuple[str, ...] = ()) -> dict:
    """Commit, branch, and whether any tracked path has uncommitted changes (the 'generator_tree_dirty' flag)."""
    g = lambda *a: subprocess.run(['git', '-C', str(repo), *a], capture_output=True, text=True).stdout.strip()
    dirty = g('status', '--porcelain', '--', *tracked) if tracked else g('status', '--porcelain')
    return {'commit': g('rev-parse', 'HEAD'), 'branch': g('rev-parse', '--abbrev-ref', 'HEAD'), 'tree_dirty': bool(dirty)}


def tool_versions(image: str | None = None, probes: dict[str, list[str]] | None = None) -> dict:
    """Python / host, plus optionally a docker image id and commands run inside it (e.g. {'yosys': ['yosys', '-V']})."""
    out = {'python': sys.version.split()[0], 'host': platform.platform()}
    try:
        import numpy
        out['numpy'] = numpy.__version__
    except ImportError:
        pass
    if image:
        p = subprocess.run(['docker', 'image', 'inspect', image, '--format', '{{.Id}}'], capture_output=True, text=True)
        out.update({'image': image, 'image_id': p.stdout.strip()})
        for name, cmd in (probes or {}).items():
            q = subprocess.run(['docker', 'run', '--rm', image, *cmd], capture_output=True, text=True)
            out[name] = (q.stdout or q.stderr).strip().splitlines()[0] if (q.stdout or q.stderr) else ''
    return out


def record(cfg: dict, command: str, result: dict, repo: Path, tracked: tuple[str, ...] = (), tools: dict | None = None) -> dict:
    return {'time_utc': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'), 'command': command,
            'git': git_state(repo, tracked), 'tools': tools if tools is not None else tool_versions(),
            'config_sha256': config_sha256(cfg), 'config': cfg, 'result': result}


def append(path: Path, rec: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'a') as fh:
        fh.write(json.dumps(rec) + '\n')


def latest_by(path: Path, key: str) -> dict:
    """Latest record per result[key] (e.g. per program tag) of a JSONL record file."""
    out = {}
    if Path(path).exists():
        for line in Path(path).read_text().splitlines():
            r = json.loads(line)['result']
            out[r[key]] = r
    return out
