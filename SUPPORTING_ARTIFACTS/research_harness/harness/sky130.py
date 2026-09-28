"""Pinned SKY130 HD corner libraries for multi-corner sign-off.

Origin: ubpgen/pdk.py (identical source, hashes and extraction; the cache directory is a parameter here).

The ORFS image ships only the tt library. The slow and fast corners come from a volare sky130A build pinned by
sha256; its tt library is numerically identical to the ORFS tt (all 554,454 values, checked in UBP Week 2,
14_FABLE_5_1_SCIENTIFIC_DISCOVERY/21_WEEK2_TIMING_CLOSURE.md 1.6), so the three corners share one characterization.

    python3 -m harness.sky130 fetch [cache_dir]      # download once (~40 MB tarball, deleted after), verify hashes

Default cache: $RESEARCH_HARNESS_SKY130 or ~/.cache/research_harness/sky130. A UBP checkout can point it at
14_FABLE_5_1_SCIENTIFIC_DISCOVERY/ubpgen_cache/pdk (same files, same hashes).
"""
from __future__ import annotations

import os
import sys
import tarfile
import urllib.request
from pathlib import Path

from .records import sha256_file

VOLARE_TAG = 'sky130-fa87f8f4bbcc7255b6f0c0fb506960f531ae2392'
URL = f'https://github.com/efabless/volare/releases/download/{VOLARE_TAG}/sky130_fd_sc_hd.tar.zst'
TARBALL_SHA256 = 'd4081b3c0fbfa2afe31dba789c03157ad137ea08b11910e2c8b3ec81b2a61bf6'
MEMBER = 'sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__{}.lib'
CORNERS = {
    'ss': ('sky130_fd_sc_hd__ss_100C_1v60.lib', '1fb9eea47d4ec6177995d7f46e9c66f15b255c38ed1554f7d2856fa870b9a08b'),
    'ff': ('sky130_fd_sc_hd__ff_n40C_1v95.lib', '4d3bff41cd4ea64e2cafa391e86cb763b7a5f59ebbc56d0e9a53794073d3f97b'),
}
ORFS_TT = '/OpenROAD-flow-scripts/flow/platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib'
ORFS_TT_SHA256 = 'ec0e1067a35c8bf20b11e58d1e8ac53326067e4dac84a125cc1b917a3518d0d9'


def default_cache() -> Path:
    return Path(os.environ.get('RESEARCH_HARNESS_SKY130', Path.home() / '.cache' / 'research_harness' / 'sky130'))


def lib_path(corner: str, cache: Path | None = None) -> Path:
    return Path(cache or default_cache()) / CORNERS[corner][0]


def available(cache: Path | None = None) -> bool:
    return all(lib_path(c, cache).exists() and sha256_file(lib_path(c, cache)) == CORNERS[c][1] for c in CORNERS)


def require(cache: Path | None = None) -> None:
    if not available(cache):
        raise RuntimeError(f'SKY130 corner libraries missing or corrupted in {cache or default_cache()}: '
                           'run  python3 -m harness.sky130 fetch')


def fetch(cache: Path | None = None) -> Path:
    cache = Path(cache or default_cache())
    cache.mkdir(parents=True, exist_ok=True)
    if available(cache):
        return cache
    tb = cache / 'sky130_fd_sc_hd.tar.zst'
    if not tb.exists() or sha256_file(tb) != TARBALL_SHA256:
        urllib.request.urlretrieve(URL, tb)
    if sha256_file(tb) != TARBALL_SHA256:
        raise RuntimeError(f'tarball sha256 mismatch: {sha256_file(tb)}')
    import zstandard   # pip install zstandard (decompression only)
    want = {MEMBER.format(f[len('sky130_fd_sc_hd__'):-4]): c for c, (f, _) in CORNERS.items()}
    with open(tb, 'rb') as fh, tarfile.open(fileobj=zstandard.ZstdDecompressor().stream_reader(fh), mode='r|') as tf:
        for m in tf:
            if m.name in want:
                lib_path(want[m.name], cache).write_bytes(tf.extractfile(m).read())
    for c, (f, h) in CORNERS.items():
        if sha256_file(lib_path(c, cache)) != h:
            raise RuntimeError(f'{f}: sha256 mismatch')
    tb.unlink()
    return cache


def provenance() -> dict:
    return {'source': URL, 'tarball_sha256': TARBALL_SHA256, 'tt': {'file': ORFS_TT, 'sha256': ORFS_TT_SHA256},
            **{c: {'file': f, 'sha256': h} for c, (f, h) in CORNERS.items()}}


if __name__ == '__main__':
    if sys.argv[1:2] == ['fetch']:
        print('corner libraries verified:', fetch(Path(sys.argv[2]) if len(sys.argv) > 2 else None))
    else:
        print(__doc__)
