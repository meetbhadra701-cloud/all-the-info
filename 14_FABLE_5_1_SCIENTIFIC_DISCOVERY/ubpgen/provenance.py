"""Provenance recorded with every generated design and every experiment record."""
from __future__ import annotations

import datetime as dt
import hashlib
import platform
import subprocess
import sys
from pathlib import Path

import numpy as np

from ._legacy import IMAGE, ROOT


def _git(*args) -> str:
    p = subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True, text=True)
    return p.stdout.strip()


def git_state() -> dict:
    dirty = _git('status', '--porcelain', '--', 'ubpgen', 'experiments/scripts')
    return {'commit': _git('rev-parse', 'HEAD'), 'branch': _git('rev-parse', '--abbrev-ref', 'HEAD'),
            'generator_tree_dirty': bool(dirty)}


_TOOLS = None


def tools() -> dict:
    global _TOOLS
    if _TOOLS is None:
        img = subprocess.run(['docker', 'image', 'inspect', IMAGE, '--format', '{{.Id}}'], capture_output=True, text=True)
        ys = subprocess.run(['docker', 'run', '--rm', IMAGE, 'yosys', '-V'], capture_output=True, text=True)
        _TOOLS = {'orfs_image': IMAGE, 'orfs_image_id': img.stdout.strip(), 'yosys': ys.stdout.strip(),
                  'python': sys.version.split()[0], 'numpy': np.__version__, 'host': platform.platform()}
    return _TOOLS


def sha256_file(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def record(cfg, command: str, extra: dict | None = None) -> dict:
    rec = {'time_utc': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'), 'command': command,
           'git': git_state(), 'tools': tools(), 'config_sha256': cfg.sha256(), 'config': cfg.raw}
    rec.update(extra or {})
    return rec
