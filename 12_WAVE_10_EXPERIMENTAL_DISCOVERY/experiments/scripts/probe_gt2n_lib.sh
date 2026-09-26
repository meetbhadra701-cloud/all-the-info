#!/usr/bin/env bash
# GT2N library structure: cell footprints across nanosheet widths / Vt flavors (read-only)
D="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
"$D" run --rm --network none --entrypoint /bin/bash openroad/orfs:latest -c '
cd /OpenROAD-flow-scripts/flow/platforms/gt2n
ls lef lef/* lib lib/* 2>/dev/null | head -40
sed -n 40,140p config.mk
python3 - <<PY
import re,glob
for f in sorted(glob.glob("lef/**/*.lef",recursive=True))[:12]:
    txt=open(f).read()
    macros=re.findall(r"MACRO\s+(\S+).*?SIZE\s+([\d.]+)\s+BY\s+([\d.]+)",txt,re.S)
    print(f,len(macros))
    for m in macros[:6]: print("   ",m)
PY
'
