#!/usr/bin/env bash
# Probe the ORFS image toolchain for building MappingEvolve (network disabled).
set -u
H="$(cd "$(dirname "$0")/../.." && pwd)"; HW="$(wslpath -w "$H")"
D="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
"$D" run --rm --network none -v "$HW:/w" --entrypoint /bin/bash openroad/orfs:latest -c '
  source /OpenROAD-flow-scripts/env.sh >/dev/null 2>&1
  echo "gcc: $(gcc --version | head -1)"; echo "g++: $(g++ --version | head -1)"; echo "cmake: $(cmake --version | head -1)"
  echo "make: $(make --version | head -1)"; echo "python3: $(python3 --version 2>&1)"
  for t in yosys yosys-abc abc openroad; do printf "%s: " $t; command -v $t || echo MISSING; done
  yosys-abc -q "version" 2>&1 | head -3
  yosys -V 2>&1 | head -1
  nproc; free -g | head -2; cat /etc/os-release | head -2
  python3 -c "import numpy; print(\"numpy\", numpy.__version__)" 2>&1
'
