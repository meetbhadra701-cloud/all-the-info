"""LIN-CEC screen (04 Part 1; evidence for the proximity kill only). Parallel CRC-32 (poly 0x04C11DB7) over D data
bits in two forms -- flat GF(2) matrix vs bit-serial LFSR unrolled -- each through Yosys+ABC, then ABC `cec` and
`&cec` with a 60 s limit."""
import json
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
POLY = 0x04C11DB7


def step(crc, d):
    fb = ((crc >> 31) ^ d) & 1
    crc = (crc << 1) & 0xFFFFFFFF
    return crc ^ POLY if fb else crc


def matrix(D):
    """Each output bit as the set of input bits (crc_in[0..31], data[0..D-1]) it XORs."""
    def run(ci, data):
        c = ci
        for i in range(D):
            c = step(c, (data >> i) & 1)
        return c
    cols = []
    for j in range(32):
        cols.append(('c', j, run(1 << j, 0)))
    for i in range(D):
        cols.append(('d', i, run(0, 1 << i)))
    outs = []
    for k in range(32):
        terms = [f'{"crc_in" if t == "c" else "data"}[{j}]' for t, j, v in cols if (v >> k) & 1]
        outs.append(' ^ '.join(terms) if terms else "1'b0")
    return outs


def verilog(D):
    flat = '\n'.join(f'  assign crc_out[{k}] = {e};' for k, e in enumerate(matrix(D)))
    a = (f'module crc_flat(input [31:0] crc_in, input [{D-1}:0] data, output [31:0] crc_out);\n{flat}\nendmodule\n')
    b = (f'module crc_lfsr(input [31:0] crc_in, input [{D-1}:0] data, output reg [31:0] crc_out);\n'
         f'  integer i; reg fb;\n  always @* begin\n    crc_out = crc_in;\n'
         f'    for (i = 0; i < {D}; i = i + 1) begin\n      fb = crc_out[31] ^ data[i];\n'
         f'      crc_out = {{crc_out[30:0], 1\'b0}} ^ (fb ? 32\'h{POLY:08X} : 32\'h0);\n    end\n  end\nendmodule\n')
    return a, b


def dock(cmd, timeout=400):
    return subprocess.run(['docker', 'run', '--rm', '-v', f'{HERE}:/work', '-w', '/work', 'openroad/orfs:latest',
                           'bash', '-c', cmd], capture_output=True, text=True, timeout=timeout)


res = []
for D in (64, 256, 1024):
    a, b = verilog(D)
    (HERE / f'flat{D}.v').write_text(a)
    (HERE / f'lfsr{D}.v').write_text(b)
    for name, top in ((f'flat{D}', 'crc_flat'), (f'lfsr{D}', 'crc_lfsr')):
        p = dock(f"yosys -q -p 'read_verilog {name}.v; synth -flatten -top {top}; abc -g AND,NAND,OR,NOR,XOR,XNOR,MUX; "
                 f"opt_clean; rename {top} top; aigmap; write_aiger -zinit {name}.aig'")
        assert p.returncode == 0, p.stderr[-2000:]
    for cmd in (f'cec -T 60 flat{D}.aig lfsr{D}.aig', f'&r flat{D}.aig; &cec -T 60 lfsr{D}.aig'):
        t0 = time.time()
        p = dock(f"timeout 70 yosys-abc -c '{cmd}'; echo EXIT=$?")
        dt = time.time() - t0
        out = (p.stdout + p.stderr).strip().splitlines()
        verdict = next((l for l in out if 'equivalent' in l.lower() or 'undecided' in l.lower() or 'time' in l.lower()), '') or ('HARD TIMEOUT (70 s)' if 'EXIT=124' in (p.stdout + p.stderr) else (out[-1] if out else ''))
        res.append({'D': D, 'cmd': cmd, 'seconds': round(dt, 2), 'verdict': verdict.strip()})
        print(res[-1], flush=True)
(HERE / 'results.json').write_text(json.dumps(res, indent=1))
