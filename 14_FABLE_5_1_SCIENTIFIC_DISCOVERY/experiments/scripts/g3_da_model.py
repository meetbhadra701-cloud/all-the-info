"""Gate 3: the strongest via-ROM distributed-arithmetic (DA) competitor, formalized and costed.

Architecture DA(K), bit-plane, n = m = 64, ternary W, INT8 x (8 planes, MSB first), 14-bit y:
  * shared per block b (K inputs): the K current activation bits address a K->2^K one-hot word-line decoder;
    word lines run across all m rows (shared);
  * per (row i, block b): a via-ROM column group holding T_ib(u) + K (offset-coded, b_K = ceil(log2(2K+1)) bits)
    for all 2^K addresses u (OBC variant: 2^(K-1) entries + b_K XORs for conditional negation);
    each bitline has a precharge + sense latch, which is also the leaf pipeline register;
  * per row: compressor over ceil(n/K) b_K-bit leaves + the SAME accumulator/output stage as P (via-programmed
    constant absorbs the offsets); 8 cycles/word.
K = 1 degenerates to "table = sign selection", which in a via fabric needs no ROM: that is exactly design P.

Labels: MEASURED (our Yosys/ABC synthesis, same flow as E6/P), INFERRED (Ankhdjet's silicon-verified SKY130 ROM
cell, read from its package data, not re-verified), MODELED (sense/decoder periphery assumptions), DERIVED
(counts from the formulas).

python3 g3_da_model.py OUTDIR            -> OUTDIR/da_model.json and a markdown table on stdout
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from e5_build import XMAX, dont_use_cells, module_timing, width  # noqa: E402
from e6_build import synth_seq  # noqa: E402
from g3_build import prow_rtl  # noqa: E402

N = M = 64
CELL_ASBUILT = 2.21      # um^2 / cell, Ankhdjet sky130_v4 silicon-verified (INFERRED)
CELL_RAW = 0.65          # um^2 / cell, Ankhdjet v4 pre-rework raw cell (INFERRED, optimistic)
ARRAY_OVH = 0.20         # Ankhdjet array overhead (decoders/precharge/local routing) (INFERRED)
SENSE_CUSTOM = 5.0       # um^2 per bitline, custom precharge + sense (MODELED)
SENSE_STDCELL = 15.0144  # um^2 per bitline, sky130 dlxtp_1 latch (MEASURED cell area)
XOR2 = 8.7584            # sky130 xor2_1 (MEASURED cell area)
DEC_PER_WL = 12.0        # um^2 per word line: decoder gate + driver, shared by all rows (MODELED)


def main(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    du = dont_use_cells()
    ow = width(XMAX * N)
    rows = []
    for K in range(1, 9):
        L = math.ceil(N / K)
        b = math.ceil(math.log2(2 * K + 1))
        name = f'DAROW_K{K}'
        wd = out / name
        wd.mkdir(exist_ok=True)
        synth_seq(wd, name, prow_rtl(name, [b] * L, ow, 7), du)                     # MEASURED datapath
        dp = module_timing(wd, name)['area_um2']
        for obc in (False, True):
            if K == 1 and obc:
                continue
            entries = 2 ** (K - 1) if obc else 2 ** K
            cells = 0 if K == 1 else L * entries * b                                   # DERIVED (per row)
            sense = 0 if K == 1 else L * b                                              # bitlines per row
            xors = L * b if obc else 0
            dec = 0 if K == 1 else math.ceil(N / K) * entries * DEC_PER_WL / M         # shared, per row share
            for tag, cell, s_area in (('optimistic', CELL_RAW, SENSE_CUSTOM), ('as_built', CELL_ASBUILT, SENSE_CUSTOM),
                                      ('stdcell_sense', CELL_ASBUILT, SENSE_STDCELL)):
                rom = cells * cell * (1 + ARRAY_OVH)
                logic = dp + sense * s_area + xors * XOR2 + dec
                rows.append({'K': K, 'obc': obc, 'case': tag, 'leaves': L, 'leaf_bits': b, 'compressor_input_bits': L * b,
                             'rom_cells_per_row': cells, 'bitlines_per_row': sense,
                             'datapath_um2_MEASURED': round(dp, 1), 'rom_um2_INFERRED': round(rom, 1),
                             'periphery_um2_MODELED': round(sense * s_area + xors * XOR2 + dec, 1),
                             'row_logic_um2': round(logic, 1), 'row_total_synth_um2': round(logic + rom, 1)})
    (out / 'da_model.json').write_text(json.dumps(rows, indent=1))
    print('| K | OBC | case | leaves x bits | compressor bits | ROM cells/row | datapath (MEAS) | ROM (INF) | periphery (MOD) | row total |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    for r in rows:
        print(f"| {r['K']} | {r['obc']} | {r['case']} | {r['leaves']}x{r['leaf_bits']} | {r['compressor_input_bits']} | {r['rom_cells_per_row']} | "
              f"{r['datapath_um2_MEASURED']:.0f} | {r['rom_um2_INFERRED']:.0f} | {r['periphery_um2_MODELED']:.0f} | {r['row_total_synth_um2']:.0f} |")


if __name__ == '__main__':
    main(Path(sys.argv[1]))
