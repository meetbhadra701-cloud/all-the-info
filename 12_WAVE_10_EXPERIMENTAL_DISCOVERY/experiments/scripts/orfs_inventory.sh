#!/usr/bin/env bash
# Inventory of the local openroad/orfs image (read-only, no network)
D="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
"$D" image inspect openroad/orfs:latest --format 'created={{.Created}} id={{.Id}}' 2>&1 | head -2
"$D" run --rm --network none --entrypoint /bin/bash openroad/orfs:latest -c '
  echo "== whoami: $(whoami)  pwd: $(pwd)"; ls / | tr "\n" " "; echo
  for p in /OpenROAD-flow-scripts /ORFS /flow /home; do [ -d $p ] && echo "dir $p: $(ls $p | head -30 | tr "\n" " ")"; done
  command -v openroad yosys klayout iverilog verilator python3 gcc g++ make cmake 2>/dev/null
  openroad -version 2>/dev/null | head -2; yosys -V 2>/dev/null
  F=$(dirname $(find / -maxdepth 4 -type d -name designs -path "*flow*" 2>/dev/null | head -1) 2>/dev/null); echo "flow dir: $F"
  [ -n "$F" ] && ls $F/designs 2>/dev/null | tr "\n" " " && echo && for pdk in $(ls $F/designs 2>/dev/null); do echo "  $pdk: $(ls $F/designs/$pdk 2>/dev/null | tr "\n" " ")"; done
  [ -n "$F" ] && ls $F/platforms 2>/dev/null | tr "\n" " "; echo
  git -C "$F/.." log -1 --format="ORFS commit %H %cd" 2>/dev/null
  python3 -c "import numpy, sys; print(\"numpy\", numpy.__version__)" 2>&1 | tail -1
' 2>&1 | head -80
