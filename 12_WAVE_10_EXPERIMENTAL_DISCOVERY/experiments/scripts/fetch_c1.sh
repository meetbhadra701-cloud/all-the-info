#!/usr/bin/env bash
# Authorized download (user approval 2026-09-25): MappingEvolve (+mockturtle submodule) and lsils/benchmarks, shallow.
set -e
H="$(cd "$(dirname "$0")/../.." && pwd)"; T="$H/third_party"; mkdir -p "$T"; cd "$T"
[ -d MappingEvolve ] || git clone --depth 1 https://github.com/Flians/MappingEvolve.git
cd MappingEvolve && git submodule update --init --depth 1 third-party/mockturtle 2>&1 | tail -2; cd ..
[ -d benchmarks ] || git clone --depth 1 https://github.com/lsils/benchmarks.git
{
  echo "fetched_utc=$(date -u +%FT%TZ)"
  echo "MappingEvolve $(git -C MappingEvolve rev-parse HEAD)"
  echo "mockturtle $(git -C MappingEvolve/third-party/mockturtle rev-parse HEAD)"
  echo "benchmarks $(git -C benchmarks rev-parse HEAD)"
  du -sh MappingEvolve benchmarks
} | tee "$H/evidence/c1_provenance.txt"
