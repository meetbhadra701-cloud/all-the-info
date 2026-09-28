"""SKY130 HD corner libraries for sign-off (Week 2).

The ORFS image ships only the tt library (the one every base is implemented with). The slow and fast sign-off
corners come from the volare sky130A build below, pinned by sha256. Its tt library is numerically identical to the
ORFS tt (all 554,454 values; 21_WEEK2_TIMING_CLOSURE.md 1.6), so the three corners share one characterization.

python3 -m ubpgen.pdk fetch     # download once into ubpgen_cache/pdk (not committed), verify every hash
"""
from __future__ import annotations

import hashlib
import sys
import tarfile
import urllib.request
from pathlib import Path

from ._legacy import ROOT

CACHE = ROOT / 'ubpgen_cache' / 'pdk'
VOLARE_TAG = 'sky130-fa87f8f4bbcc7255b6f0c0fb506960f531ae2392'
URL = f'https://github.com/efabless/volare/releases/download/{VOLARE_TAG}/sky130_fd_sc_hd.tar.zst'
TARBALL_SHA256 = 'd4081b3c0fbfa2afe31dba789c03157ad137ea08b11910e2c8b3ec81b2a61bf6'
MEMBER = 'sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__{}.lib'
# corner name -> (library file, sha256); tt is the ORFS platform library (in the image), not downloaded
CORNERS = {
    'ss': ('sky130_fd_sc_hd__ss_100C_1v60.lib', '1fb9eea47d4ec6177995d7f46e9c66f15b255c38ed1554f7d2856fa870b9a08b'),
    'ff': ('sky130_fd_sc_hd__ff_n40C_1v95.lib', '4d3bff41cd4ea64e2cafa391e86cb763b7a5f59ebbc56d0e9a53794073d3f97b'),
}
ORFS_TT = '/OpenROAD-flow-scripts/flow/platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib'
ORFS_TT_SHA256 = 'ec0e1067a35c8bf20b11e58d1e8ac53326067e4dac84a125cc1b917a3518d0d9'


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def lib_path(corner: str) -> Path:
    return CACHE / CORNERS[corner][0]


def available() -> bool:
    return all(lib_path(c).exists() and sha256(lib_path(c)) == CORNERS[c][1] for c in CORNERS)


def require():
    if not available():
        raise RuntimeError('SKY130 corner libraries missing or corrupted: run  python3 -m ubpgen.pdk fetch')


def fetch():
    CACHE.mkdir(parents=True, exist_ok=True)
    if available():
        print('corner libraries present and verified:', CACHE)
        return
    tb = CACHE / 'sky130_fd_sc_hd.tar.zst'
    if not tb.exists() or sha256(tb) != TARBALL_SHA256:
        print('downloading', URL)
        urllib.request.urlretrieve(URL, tb)
    if sha256(tb) != TARBALL_SHA256:
        raise RuntimeError(f'tarball sha256 mismatch: {sha256(tb)}')
    import zstandard   # pip install zstandard (decompression only)
    want = {MEMBER.format(f[len('sky130_fd_sc_hd__'):-4]): c for c, (f, _) in CORNERS.items()}
    with open(tb, 'rb') as fh, tarfile.open(fileobj=zstandard.ZstdDecompressor().stream_reader(fh), mode='r|') as tf:
        for m in tf:
            if m.name in want:
                lib_path(want[m.name]).write_bytes(tf.extractfile(m).read())
    for c, (f, h) in CORNERS.items():
        if sha256(lib_path(c)) != h:
            raise RuntimeError(f'{f}: sha256 mismatch')
    tb.unlink()
    print('corner libraries verified:', CACHE)


def provenance() -> dict:
    return {'source': URL, 'tarball_sha256': TARBALL_SHA256, 'tt': {'file': ORFS_TT, 'sha256': ORFS_TT_SHA256},
            **{c: {'file': f, 'sha256': h} for c, (f, h) in CORNERS.items()}}


if __name__ == '__main__':
    if sys.argv[1:] == ['fetch']:
        fetch()
    else:
        print(__doc__)
