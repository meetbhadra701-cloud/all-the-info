#!/usr/bin/env bash
# Gate 2 per-matrix run: ./g2_run_program.sh G2_DIR DESIGN UTIL TAG     UTIL = 60 (generic base) or 60s (R2 structured)
#   route pass (met4-met5 only) + sta/netlist pass on the frozen base, then functional verification vs numpy.
set -u
G2=$1; D=$2; U=$3; T=$4
if [[ $U == *s ]]; then NICK=g2s_${D}_u${U%s}; else NICK=g2_${D}_u${U}; fi
BASE=/work/orfs/results/sky130hd/$NICK/base
OUT=/work/$D/prog_${T}_u${U}
for MODE in ${MODES:-route sta}; do
  docker run --rm -v "$G2":/work -v "$(cd "$(dirname "$0")" && pwd)":/scripts -w /work \
    -e BASE_ODB=$BASE/6_final.odb -e BASE_SDC=$BASE/6_final.sdc -e PROG_TCL=/work/$D/prog_$T.tcl -e OUT=$OUT -e MODE=$MODE -e DRT_ITERS=${DRT_ITERS:-20} \
    openroad/orfs:latest /OpenROAD-flow-scripts/tools/install/OpenROAD/bin/openroad -no_init -threads 2 -exit \
    /scripts/g2_program.tcl > "$G2/$D/prog_${T}_u${U}_$MODE.log" 2>&1
done
if [[ " ${MODES:-route sta} " == *" sta "* ]]; then
  python3 "$(dirname "$0")/g2_verify.py" "$G2" "$D" "$T" "$G2/$D/prog_${T}_u${U}_programmed.v" | tail -1
fi
