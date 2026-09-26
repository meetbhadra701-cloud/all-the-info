#!/usr/bin/env bash
# Wave 10: inventory of locally available tools (no network, read-only)
OSS=/mnt/c/Users/meetb/Documents/Codex/2026-09-20/muxwise-experiment-1-zero-commitment-eda/outputs/muxwise-experiment-02/work/oss-cad-suite
echo "== OSS CAD Suite bin"; ls "$OSS/bin" 2>/dev/null | tr '\n' ' '; echo
echo "== WSL basics"; for t in gcc g++ clang make cmake python3 pip3 git rustc cargo java node verilator iverilog; do printf "%s=%s " $t "$(command -v $t || echo -)"; done; echo
python3 -c "import sys; print('python', sys.version.split()[0])" 2>/dev/null
python3 -c "import numpy; print('numpy', numpy.__version__)" 2>&1 | tail -1
echo "== home"; ls ~ 2>/dev/null | tr '\n' ' '; echo
echo "== wave7d1"; ls ~/wave7d1 2>/dev/null | head -30 | tr '\n' ' '; echo
for d in ~/wave7d1/*/ ; do echo "  $d: $(ls "$d" 2>/dev/null | head -12 | tr '\n' ' ')"; done 2>/dev/null | head -20
echo "== dynamatic bin candidates"; find ~ -maxdepth 4 -type d -name "dynamatic*" 2>/dev/null | head; find ~ -maxdepth 6 -type f \( -name "mlir-opt" -o -name "circt-opt" -o -name "clang" -o -name "polygeist-opt" -o -name "cgeist" -o -name "dynamatic-opt" -o -name "vsim" \) 2>/dev/null | head -20
echo "== docker images"; "/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe" images --format '{{.Repository}}:{{.Tag}} {{.Size}}' 2>/dev/null | head -30
echo "== disk"; df -h ~ | tail -1; nproc; free -g | head -2
