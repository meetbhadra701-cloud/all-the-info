#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ROOT_WIN="$(wslpath -w "$ROOT_DIR")"
mkdir -p "$ROOT_DIR/logs/sta" "$ROOT_DIR/work"
run_one() {
  local tag="$1" sdc="$2"
  local tcl="$ROOT_DIR/work/sta_${tag}.tcl" log="$ROOT_DIR/logs/sta/${tag}_${sdc}.log"
  local net="/workspace/netlists/${tag}.v" top
  case "$tag" in
    fir4_*) top=fir4;; mixed_*) top=mixed_left;; add_chain_*) top=add_chain;;
    *) echo "unknown tag $tag" >&2; exit 2;;
  esac
  cat > "$tcl" <<EOF
read_lef /OpenROAD-flow-scripts/flow/platforms/nangate45/lef/NangateOpenCellLibrary.tech.lef
read_lef /OpenROAD-flow-scripts/flow/platforms/nangate45/lef/NangateOpenCellLibrary.macro.mod.lef
read_liberty /OpenROAD-flow-scripts/flow/platforms/nangate45/lib/NangateOpenCellLibrary_typical.lib
read_verilog $net
link_design $top
source /workspace/constraints/$sdc
report_checks -path_delay max -format full_clock_expanded -digits 4
report_worst_slack -max -digits 4
report_tns -max -digits 4
exit
EOF
  echo "RUN $tag $sdc"
  docker.exe run --rm -v "$ROOT_WIN:/workspace" openroad/orfs:latest bash -lc "source ./env.sh; openroad -no_init -exit /workspace/work/sta_${tag}.tcl" > "$log" 2>&1 || true
}
for tag in fir4_w8_normal fir4_w8_arith_tree fir4_w16_normal fir4_w16_arith_tree mixed_w16_normal mixed_w16_arith_tree mixed_w32_normal mixed_w32_arith_tree add_chain_w16_normal add_chain_w16_arith_tree add_chain_w64_normal add_chain_w64_arith_tree; do
  for sdc in preliminary.sdc relaxed.sdc aggressive.sdc; do
    run_one "$tag" "$sdc"
  done
done
