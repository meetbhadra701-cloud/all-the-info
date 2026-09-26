#!/usr/bin/env bash
# Wave 10 / C1: builds the MappingEvolve operator variants plus the study drivers.
# Runs inside openroad/orfs:latest with --network none. The source checkout is only read.
set -u
H="$(cd "$(dirname "$0")/../.." && pwd)"; HW="$(wslpath -w "$H")"
D="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
mkdir -p "$H/experiments/outputs/c1/bin" "$H/experiments/logs/c1"
"$D" run --rm --network none --cpus ${CPUS:-6} --memory ${MEM:-12g} -v "$HW:/w" --entrypoint /bin/bash openroad/orfs:latest -c '
set -eu
source /OpenROAD-flow-scripts/env.sh >/dev/null 2>&1
ME=/w/third_party/MappingEvolve; S=/tmp/c1src; O=/w/experiments/outputs/c1/bin
mkdir -p $S/third-party $S/variants
cp -r $ME/third-party/mockturtle $S/third-party/mockturtle
cp $ME/third-party/CMakeLists.txt $S/third-party/CMakeLists.txt
cp /w/experiments/scripts/c1/CMakeLists.txt /w/experiments/scripts/c1/c1_emap.cpp $S/
declare -A RUN=( [gpt5_it29]="proactive_evolve_openevolve_gpt-5-2025-08-07_20251116_134740/iter_29"
                 [deepseek_it24]="proactive_evolve_openevolve_deepseek-v3-241226_20251116_014457/iter_24"
                 [qwen_it20]="proactive_evolve_openevolve_qwen3-max_20251116_093335/iter_20" )
: > $O/MANIFEST.txt
for v in initial gpt5_it29 deepseek_it24 qwen_it20; do
  mkdir -p $S/variants/$v
  cp $ME/mapping/mapping.hpp $ME/mapping/main.cpp $ME/mapping/match_phase.cpp $ME/mapping/match_phase_exact.cpp $ME/mapping/match_drop_phase.cpp $S/variants/$v/
  cp /w/experiments/scripts/c1/c1_driver.cpp $S/variants/$v/
  if [ "$v" != initial ]; then cp $ME/output/${RUN[$v]}/evolved_mapping/*.cpp $S/variants/$v/; fi
  ( cd $S/variants/$v && md5sum mapping.hpp main.cpp match_phase.cpp match_phase_exact.cpp match_drop_phase.cpp c1_driver.cpp | sed "s|^|$v |" ) >> $O/MANIFEST.txt
done
cmake -S $S -B $S/build -DCMAKE_BUILD_TYPE=Release > /w/experiments/logs/c1/build_cmake.log 2>&1
cmake --build $S/build -j ${JOBS:-6} > /w/experiments/logs/c1/build_make.log 2>&1 || { echo BUILD_FAILED; tail -40 /w/experiments/logs/c1/build_make.log; exit 1; }
for b in orig_initial orig_gpt5_it29 orig_deepseek_it24 orig_qwen_it20 drv_initial drv_gpt5_it29 drv_deepseek_it24 drv_qwen_it20 drv_emap; do
  f=$(find $S/build -type f -name $b -perm -u+x | head -1); cp $f $O/$b; md5sum $O/$b | sed "s|/w/experiments/outputs/c1/bin/||" >> $O/MANIFEST.txt
done
echo "gcc=$(g++ --version | head -1)" >> $O/MANIFEST.txt; echo "cmake=$(cmake --version | head -1)" >> $O/MANIFEST.txt
echo BUILD_OK
'
