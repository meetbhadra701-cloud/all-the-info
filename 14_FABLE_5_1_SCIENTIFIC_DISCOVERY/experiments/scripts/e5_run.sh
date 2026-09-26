#!/usr/bin/env bash
# E5/E6 PnR job runner: ./e5_run.sh E_DIR job [job ...]   job = <design_dir>:<util>, e.g. g1_n32:60
# Runs the stock ORFS flow (SKY130 HD) on the pre-built netlist; 2 jobs in parallel, 2 cores each.
# NO_DCE=1 (Amendment A2): mount scripts/orfs_patch/synth_odb.tcl, identical to the image's except that
# eliminate_dead_logic is disabled (the regime-V fabric must not be pruned per W).
set -u
E5=$1; shift
PATCH=""
if [ "${NO_DCE:-0}" = "1" ]; then
  PATCH="-v $(cd "$(dirname "$0")" && pwd)/orfs_patch/synth_odb.tcl:/OpenROAD-flow-scripts/flow/scripts/synth_odb.tcl:ro"
fi
export PATCH
run_one() {
  E5=$1; job=$2; d=${job%%:*}; u=${job##*:}
  docker run --rm -v "$E5":/work $PATCH -w /OpenROAD-flow-scripts/flow openroad/orfs:latest bash -c \
    "make DESIGN_CONFIG=/work/$d/config_u$u.mk WORK_HOME=/work/orfs NUM_CORES=2 > /work/$d/orfs_u$u.log 2>&1; echo \$? > /work/$d/orfs_u$u.rc"
  echo "done $job rc=$(cat "$E5/$d/orfs_u$u.rc")"
}
export -f run_one
printf '%s\n' "$@" | xargs -P 2 -I{} bash -c 'run_one "$0" "{}"' "$E5"
