#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
YOSYS_RUN="$SCRIPT_DIR/run_current.sh"
LIB="$ROOT_DIR/work/orfs/flow/platforms/nangate45/lib/NangateOpenCellLibrary_typical.lib"
SRC_DIR="$ROOT_DIR/reproducers"
YS_DIR="$ROOT_DIR/work/yosys"
mkdir -p "$YS_DIR" "$ROOT_DIR/netlists" "$ROOT_DIR/netlists/premap" "$ROOT_DIR/logs/mapping"

if [[ ! -f "$LIB" ]]; then
  echo "Missing Liberty file: $LIB" >&2
  exit 2
fi

run_one() {
  local design="$1" top="$2" width="$3" source="$4" config="$5"
  local suffix="normal"
  local tree_opt=""
  if [[ "$config" == "arith_tree" ]]; then
    suffix="arith_tree"
    tree_opt="-arith_tree"
  fi
  local tag="${design}_w${width}_${suffix}"
  local ys="$YS_DIR/${tag}.ys"
  local log="$ROOT_DIR/logs/mapping/${tag}.log"
  local netlist="$ROOT_DIR/netlists/${tag}.v"
  local premap="$ROOT_DIR/netlists/premap/${tag}.v"
  cat > "$ys" <<EOF
read_verilog -sv $SRC_DIR/$source
hierarchy -top $top
chparam -set W $width $top
synth -top $top -noabc $tree_opt
write_verilog -noattr -noexpr -simple-lhs $premap
abc -liberty $LIB -script $SCRIPT_DIR/abc_seeded.script
clean
stat -liberty $LIB
write_verilog -noattr -noexpr -simple-lhs $netlist
EOF
  echo "RUN $tag"
  /usr/bin/time -f 'MUXWISE_WALL_SECONDS=%e' "$YOSYS_RUN" yosys -s "$ys" > "$log" 2>&1
  # OpenROAD's Verilog reader does not need signedness after Liberty mapping;
  # remove only the redundant declaration keyword from the derived netlist.
  sed -E 's/\bsigned[[:space:]]+//' "$netlist" > "$netlist.tmp"
  mv "$netlist.tmp" "$netlist"
}

run_one fir4 fir4 8 fir4.v normal
run_one fir4 fir4 8 fir4.v arith_tree
run_one fir4 fir4 16 fir4.v normal
run_one fir4 fir4 16 fir4.v arith_tree
run_one mixed mixed_left 16 mixed_arith.v normal
run_one mixed mixed_left 16 mixed_arith.v arith_tree
run_one mixed mixed_left 32 mixed_arith.v normal
run_one mixed mixed_left 32 mixed_arith.v arith_tree
run_one add_chain add_chain 16 add_chain.v normal
run_one add_chain add_chain 16 add_chain.v arith_tree
run_one add_chain add_chain 64 add_chain.v normal
run_one add_chain add_chain 64 add_chain.v arith_tree
