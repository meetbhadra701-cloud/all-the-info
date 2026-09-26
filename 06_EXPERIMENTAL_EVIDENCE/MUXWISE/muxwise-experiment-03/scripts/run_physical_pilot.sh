#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ROOT_WIN="$(wslpath -w "$ROOT_DIR")"
mkdir -p "$ROOT_DIR/logs/physical" "$ROOT_DIR/work/physical"

run_one() {
  local tag="$1" sdc="$2"
  local tcl="$ROOT_DIR/work/physical/${tag}_${sdc}.tcl"
  local log="$ROOT_DIR/logs/physical/${tag}_${sdc}.log"
  local net="/workspace/netlists/${tag}.v" top
  case "$tag" in fir4_*) top=fir4;; mixed_*) top=mixed_left;; add_chain_*) top=add_chain;; esac
  cat > "$tcl" <<EOF
read_lef /OpenROAD-flow-scripts/flow/platforms/nangate45/lef/NangateOpenCellLibrary.tech.lef
read_lef /OpenROAD-flow-scripts/flow/platforms/nangate45/lef/NangateOpenCellLibrary.macro.mod.lef
read_liberty /OpenROAD-flow-scripts/flow/platforms/nangate45/lib/NangateOpenCellLibrary_typical.lib
read_verilog $net
link_design $top
read_sdc /workspace/constraints/$sdc.sdc
initialize_floorplan -utilization 20 -aspect_ratio 1.0 -core_space 10 -site FreePDK45_38x28_10R_NP_162NW_34O
make_tracks
source /OpenROAD-flow-scripts/flow/platforms/nangate45/setRC.tcl
set_global_routing_layer_adjustment metal2-metal3 0.5
set_global_routing_layer_adjustment metal4-metal10 0.25
set_routing_layers -signal metal2-metal10
place_pins -hor_layers metal5 -ver_layers metal6
global_placement -density 0.20 -timing_driven
estimate_parasitics -placement
report_design_area
report_checks -path_delay max -format full_clock_expanded -digits 4
report_worst_slack -max -digits 4
report_tns -max -digits 4
global_route -guide_file /workspace/work/physical/${tag}_${sdc}.route.guide -congestion_report_file /workspace/work/physical/${tag}_${sdc}.congestion.rpt
estimate_parasitics -global_routing
report_wire_length -global_route -summary
report_checks -path_delay max -format full_clock_expanded -digits 4
report_worst_slack -max -digits 4
report_tns -max -digits 4
write_def /workspace/work/physical/${tag}_${sdc}.def
exit
EOF
  echo "RUN $tag $sdc"
  /usr/bin/time -f 'MUXWISE_PHYSICAL_WALL_SECONDS=%e' docker.exe run --rm -v "$ROOT_WIN:/workspace" openroad/orfs:latest bash -lc "source ./env.sh; openroad -no_init -exit /workspace/work/physical/${tag}_${sdc}.tcl" > "$log" 2>&1 || true
}

# Bounded representative pilot: the largest FIR and mixed datapaths plus add-chain W64.
for tag in fir4_w16_normal fir4_w16_arith_tree mixed_w32_normal mixed_w32_arith_tree add_chain_w64_normal add_chain_w64_arith_tree; do
  run_one "$tag" aggressive
done
