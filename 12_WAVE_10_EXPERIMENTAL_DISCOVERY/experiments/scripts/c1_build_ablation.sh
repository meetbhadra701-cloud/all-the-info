#!/usr/bin/env bash
# Wave 10 / C1 / D2: builds the ablation drivers ab1 and ab2 (network off; the sources are only read).
set -u
H="$(cd "$(dirname "$0")/../.." && pwd)"; HW="$(wslpath -w "$H")"
D="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
"$D" run --rm --network none --cpus ${CPUS:-6} --memory ${MEM:-12g} -v "$HW:/w" --entrypoint /bin/bash openroad/orfs:latest -c '
set -eu
source /OpenROAD-flow-scripts/env.sh >/dev/null 2>&1
ME=/w/third_party/MappingEvolve; S=/tmp/c1ab; O=/w/experiments/outputs/c1/bin
mkdir -p $S/third-party $S/variants
cp -r $ME/third-party/mockturtle $S/third-party/mockturtle
cp $ME/third-party/CMakeLists.txt $S/third-party/CMakeLists.txt
cp /w/experiments/scripts/c1/CMakeLists_ablation.txt $S/CMakeLists.txt
for v in ab1 ab2; do
  mkdir -p $S/variants/$v
  cp $ME/mapping/mapping.hpp /w/experiments/scripts/c1/c1_driver.cpp $S/variants/$v/
  cp /w/experiments/inputs/c1/ablation/$v/*.cpp $S/variants/$v/
  ( cd $S/variants/$v && md5sum mapping.hpp match_phase.cpp match_phase_exact.cpp match_drop_phase.cpp c1_driver.cpp | sed "s|^|$v |" ) >> $O/MANIFEST_ablation.txt
done
cmake -S $S -B $S/build -DCMAKE_BUILD_TYPE=Release > /w/experiments/logs/c1/build_ablation_cmake.log 2>&1
cmake --build $S/build -j ${JOBS:-6} --target drv_ab1 drv_ab2 > /w/experiments/logs/c1/build_ablation_make.log 2>&1 || { echo BUILD_FAILED; tail -30 /w/experiments/logs/c1/build_ablation_make.log; exit 1; }
for b in drv_ab1 drv_ab2; do f=$(find $S/build -type f -name $b -perm -u+x | head -1); cp $f $O/$b; md5sum $O/$b | sed "s|/w/experiments/outputs/c1/bin/||" >> $O/MANIFEST_ablation.txt; done
echo BUILD_OK
'
