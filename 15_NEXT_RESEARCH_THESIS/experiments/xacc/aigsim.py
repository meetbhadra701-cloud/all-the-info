"""Bit-parallel, level-vectorised simulator of sequential ASCII AIGER models (independent of the RTL and of Yosys'
own simulator). 64 * L independent streams are simulated at once: every signal is an (L,) array of uint64 words.

Evaluation per cycle: inputs, latch outputs, AND gates level by level (one vectorised gather per level), outputs
sampled, latches updated. Latches start at their AIGER reset value (Yosys `setundef -zero -init` gives 0).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'SUPPORTING_ARTIFACTS' / 'research_harness'))
from harness.oracle import read_aag_seq  # noqa: E402

ONES = np.uint64(0xFFFFFFFFFFFFFFFF)


class AIGSim:
    def __init__(self, aag_path: Path):
        M, ins, lat, outs, ands, sym_in, sym_out = read_aag_seq(aag_path)
        self.M = M
        self.in_var = {sym_in[k]: lit >> 1 for k, lit in enumerate(ins)}
        self.out_lit = {sym_out[k]: lit for k, lit in enumerate(outs)}
        self.lat = [(cur >> 1, nxt, init) for cur, nxt, init in lat]
        level = np.zeros(M + 1, dtype=np.int64)
        for lhs, r0, r1 in ands:
            level[lhs >> 1] = 1 + max(level[r0 >> 1], level[r1 >> 1])
        by = {}
        for lhs, r0, r1 in ands:
            by.setdefault(int(level[lhs >> 1]), []).append((lhs >> 1, r0 >> 1, r0 & 1, r1 >> 1, r1 & 1))
        self.levels = []
        for lv in sorted(by):
            g = np.array(by[lv], dtype=np.int64)
            self.levels.append((g[:, 0], g[:, 1], (g[:, 2].astype(np.uint64) * ONES)[:, None],
                                g[:, 3], (g[:, 4].astype(np.uint64) * ONES)[:, None]))
        self.lat_cur = np.array([c for c, _, _ in self.lat], dtype=np.int64)
        self.lat_nxt = np.array([n >> 1 for _, n, _ in self.lat], dtype=np.int64)
        self.lat_neg = (np.array([n & 1 for _, n, _ in self.lat], dtype=np.uint64) * ONES)[:, None]
        self.lat_init = (np.array([1 if i == 1 else 0 for _, _, i in self.lat], dtype=np.uint64) * ONES)[:, None]

    def run(self, cycles: int, words: int, drive, sample):
        """drive(c) -> {input symbol: (words,) uint64}; sample(c, get) is called after evaluation, where
        get(output symbol) -> (words,) uint64."""
        val = np.zeros((self.M + 1, words), dtype=np.uint64)
        state = np.repeat(self.lat_init, words, axis=1) if len(self.lat) else None
        for c in range(cycles):
            for nm, w in drive(c).items():
                val[self.in_var[nm]] = w
            if state is not None:
                val[self.lat_cur] = state
            for lhs, a, na, b, nb in self.levels:
                val[lhs] = (val[a] ^ na) & (val[b] ^ nb)
            sample(c, lambda nm: val[self.out_lit[nm] >> 1] ^ (ONES if self.out_lit[nm] & 1 else np.uint64(0)))
            if state is not None:
                state = val[self.lat_nxt] ^ self.lat_neg


def pack_bits(bits: np.ndarray) -> np.ndarray:
    """bits: (lanes,) of 0/1 with lanes = 64 * words -> (words,) uint64, lane i = bit (i % 64) of word i // 64."""
    b = bits.astype(np.uint64).reshape(-1, 64)
    return (b << np.arange(64, dtype=np.uint64)).sum(axis=1).astype(np.uint64)


def unpack_bits(words: np.ndarray) -> np.ndarray:
    return ((words[:, None] >> np.arange(64, dtype=np.uint64)) & np.uint64(1)).reshape(-1).astype(np.uint8)
