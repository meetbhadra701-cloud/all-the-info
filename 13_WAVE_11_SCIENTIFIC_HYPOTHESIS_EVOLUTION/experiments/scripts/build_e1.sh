#!/usr/bin/env bash
# Wave 11 / E1: builds drv_dump (initial `map` operators + read-only dump patch) in openroad/orfs:latest, network off.
set -u
H="$(cd "$(dirname "$0")/../.." && pwd)"; R="$(cd "$H/.." && pwd)"; RW="$(wslpath -w "$R")"
D="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
"$D" run --rm --network none --cpus ${CPUS:-6} --memory ${MEM:-12g} -v "$RW:/r" --entrypoint /bin/bash openroad/orfs:latest -c '
set -eu
source /OpenROAD-flow-scripts/env.sh >/dev/null 2>&1
ME=/r/12_WAVE_10_EXPERIMENTAL_DISCOVERY/third_party/MappingEvolve; W=/r/13_WAVE_11_SCIENTIFIC_HYPOTHESIS_EVOLUTION; S=/tmp/e1
mkdir -p $S/third-party $S/variants/dump
cp -r $ME/third-party/mockturtle $S/third-party/mockturtle
cp $ME/third-party/CMakeLists.txt $S/third-party/CMakeLists.txt
cp $W/experiments/scripts/CMakeLists_e1.txt $S/CMakeLists.txt
cp $W/experiments/inputs/e1_dump_variant/*.hpp $W/experiments/inputs/e1_dump_variant/*.cpp $S/variants/dump/
cp /r/12_WAVE_10_EXPERIMENTAL_DISCOVERY/experiments/scripts/c1/c1_driver.cpp $S/variants/dump/
( cd $S/variants/dump && md5sum * ) > $W/experiments/bin/MANIFEST_e1.txt
cmake -S $S -B $S/build -DCMAKE_BUILD_TYPE=Release > $W/experiments/logs/build_e1_cmake.log 2>&1
cmake --build $S/build -j ${JOBS:-6} --target drv_dump > $W/experiments/logs/build_e1_make.log 2>&1 || { echo BUILD_FAILED; grep -n "error" $W/experiments/logs/build_e1_make.log | head -20; exit 1; }
f=$(find $S/build -type f -name drv_dump -perm -u+x | head -1); cp $f $W/experiments/bin/drv_dump; md5sum $W/experiments/bin/drv_dump | sed "s|$W/experiments/bin/||" >> $W/experiments/bin/MANIFEST_e1.txt
echo BUILD_OK
'
