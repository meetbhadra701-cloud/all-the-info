#!/usr/bin/env bash
# Builds unmodified main.cpp against DeepSeek iteration states 5 (2efd616c), 12 (b5926427) and 15 (3d1644bd). Network off; sources read-only.
set -u
H="$(cd "$(dirname "$0")/../.." && pwd)"; HW="$(wslpath -w "$H")"
D="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
"$D" run --rm --network none --cpus ${CPUS:-3} --memory ${MEM:-8g} -v "$HW:/w" --entrypoint /bin/bash openroad/orfs:latest -c '
set -eu
source /OpenROAD-flow-scripts/env.sh >/dev/null 2>&1
ME=/w/third_party/MappingEvolve; RUN=$ME/output/proactive_evolve_openevolve_deepseek-v3-241226_20251116_014457
S=/tmp/c1ds; O=/w/experiments/outputs/c1/bin
mkdir -p $S/third-party $S/variants
cp -r $ME/third-party/mockturtle $S/third-party/mockturtle
cp $ME/third-party/CMakeLists.txt $S/third-party/CMakeLists.txt
cp /w/experiments/scripts/c1/CMakeLists_dsscan.txt $S/CMakeLists.txt
for k in 05 12 15; do v=ds_it$k; mkdir -p $S/variants/$v
  cp $ME/mapping/mapping.hpp $ME/mapping/main.cpp $S/variants/$v/
  cp $RUN/iter_$((10#$k))/evolved_mapping/*.cpp $S/variants/$v/
  ( cd $S/variants/$v && md5sum match_phase.cpp match_phase_exact.cpp match_drop_phase.cpp | sed "s|^|$v |" ) >> $O/MANIFEST_dsscan.txt
done
cmake -S $S -B $S/build -DCMAKE_BUILD_TYPE=Release > /w/experiments/logs/c1/build_dsscan_cmake.log 2>&1
cmake --build $S/build -j ${JOBS:-3} > /w/experiments/logs/c1/build_dsscan_make.log 2>&1 || { echo BUILD_FAILED; tail -20 /w/experiments/logs/c1/build_dsscan_make.log; exit 1; }
for b in orig_ds_it05 orig_ds_it12 orig_ds_it15; do f=$(find $S/build -type f -name $b -perm -u+x | head -1); cp $f $O/$b; md5sum $O/$b | sed "s|/w/experiments/outputs/c1/bin/||" >> $O/MANIFEST_dsscan.txt; done
echo BUILD_OK
'
