import re
import sys
import zlib

data = open(sys.argv[1], 'rb').read()
out = []
BS = b'\x5c'
for m in re.finditer(rb'stream\r?\n(.*?)\r?\nendstream', data, re.S):
    raw = m.group(1)
    try:
        dec = zlib.decompress(raw)
    except Exception:
        continue
    for tj in re.finditer(rb'\[(.*?)\]\s*TJ|\((.*?)\)\s*Tj', dec, re.S):
        seg = tj.group(1) if tj.group(1) is not None else tj.group(2)
        parts = re.findall(rb'\(((?:\x5c.|[^\x5c)])*)\)|(-?\d+\.?\d*)', seg)
        s = ''
        for txt, num in parts:
            if txt:
                t = txt.replace(BS + b'(', b'(').replace(BS + b')', b')').replace(BS + BS, BS)
                s += t.decode('latin-1', 'ignore')
            elif num:
                try:
                    if float(num) < -200:
                        s += ' '
                except ValueError:
                    pass
        out.append(s)
    out.append('\n')
txt = ' '.join(out)
txt = re.sub(r'[ \t]+', ' ', txt)
n = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
off = int(sys.argv[3]) if len(sys.argv) > 3 else 0
print(txt[off:off + n])
