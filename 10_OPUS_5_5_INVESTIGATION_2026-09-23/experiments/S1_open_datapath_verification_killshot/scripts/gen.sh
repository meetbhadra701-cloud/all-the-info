#!/usr/bin/env bash
# Kill-shot S1: do existing open engines already verify Yosys datapath passes at production widths?
# Generates RTL, synthesizes three architectures per design/width, writes AIGER + symbol maps.
# Uses the pre-existing OSS CAD Suite from MUXWISE Experiment 2 (no downloads).
set -u
S=/mnt/c/Users/meetb/Documents/Codex/2026-09-20/muxwise-experiment-1-zero-commitment-eda/outputs/muxwise-experiment-02/work/oss-cad-suite
Y="$S/bin/yosys"
W_LIST="${W_LIST:-8 16 24 32}"
OUT=/mnt/c/Users/meetb/AppData/Local/Temp/claude/C--Users-meetb-Desktop-CLAUDE-OPUS-5-5-RESEARCH-CONTEXT/03476a4d-4e8a-44cd-9bcd-493130f6d087/scratchpad/s1/work
mkdir -p "$OUT/rtl" "$OUT/aig" "$OUT/log"

gen_rtl() { # design W
  local d=$1 W=$2
  local f="$OUT/rtl/${d}_w${W}.v"
  case $d in
    mul_u)  printf 'module top(input [%d:0] a, input [%d:0] b, output [%d:0] y);\n  assign y = a * b;\nendmodule\n' $((W-1)) $((W-1)) $((2*W-1)) > "$f";;
    mul_s)  printf 'module top(input signed [%d:0] a, input signed [%d:0] b, output signed [%d:0] y);\n  assign y = a * b;\nendmodule\n' $((W-1)) $((W-1)) $((2*W-1)) > "$f";;
    mac_u)  printf 'module top(input [%d:0] a, input [%d:0] b, input [%d:0] c, output [%d:0] y);\n  assign y = a * b + c;\nendmodule\n' $((W-1)) $((W-1)) $((2*W-1)) $((2*W)) > "$f";;
    dot2_u) printf 'module top(input [%d:0] a0, input [%d:0] b0, input [%d:0] a1, input [%d:0] b1, output [%d:0] y);\n  assign y = a0 * b0 + a1 * b1;\nendmodule\n' $((W-1)) $((W-1)) $((W-1)) $((W-1)) $((2*W)) > "$f";;
    # negative control: injects a rare-input bug into bit 5 of the product (only when a[0]&b[W-1]).
    mulbug_u) printf 'module top(input [%d:0] a, input [%d:0] b, output [%d:0] y);\n  assign y = (a * b) ^ ({%d{1'"'"'b0}} | ((a[0] & b[%d]) << 5));\nendmodule\n' $((W-1)) $((W-1)) $((2*W-1)) $((2*W)) $((W-1)) > "$f";;
  esac
  echo "$f"
}

synth_one() { # design W arch
  local d=$1 W=$2 a=$3
  local rtl="$OUT/rtl/${d}_w${W}.v" base="$OUT/aig/${d}_w${W}_${a}"
  local flag=""
  case $a in norm) flag="";; booth) flag="-booth";; tree) flag="-arith_tree";; esac
  "$Y" -q -l "$OUT/log/synth_${d}_w${W}_${a}.log" -p "read_verilog $rtl; synth -top top $flag; aigmap; opt_clean; stat; write_aiger -symbols -map $base.map $base.aig" >/dev/null 2>&1
  local rc=$?
  if [ $rc -ne 0 ] || [ ! -s "$base.aig" ]; then echo "SYNTH_ERROR $d w$W $a rc=$rc"; return; fi
  local ands; ands=$(head -c 200 "$base.aig" | head -1)
  echo "SYNTH_OK $d w$W $a header=[$ands]"
}

for W in $W_LIST; do
  for d in mul_u mul_s mac_u dot2_u mulbug_u; do gen_rtl $d $W >/dev/null; done
done
export -f synth_one; export OUT Y
jobs=()
for W in $W_LIST; do
  for d in mul_u mul_s mac_u dot2_u; do for a in norm booth tree; do jobs+=("$d $W $a"); done; done
  jobs+=("mulbug_u $W booth")
done
printf '%s\n' "${jobs[@]}" | xargs -P 6 -L 1 bash -c 'synth_one $0 $1 $2'
# port-order audit: all architectures of the same design/width must have identical input/output maps
for W in $W_LIST; do for d in mul_u mul_s mac_u dot2_u; do
  ref="$OUT/aig/${d}_w${W}_norm.map"
  for a in booth tree; do
    m="$OUT/aig/${d}_w${W}_${a}.map"
    if [ -s "$ref" ] && [ -s "$m" ]; then
      if diff -q <(grep -E '^(input|output)' "$ref") <(grep -E '^(input|output)' "$m") >/dev/null; then echo "MAP_MATCH $d w$W norm~$a"; else echo "MAP_MISMATCH $d w$W norm~$a"; fi
    fi
  done
done; done
m="$OUT/aig/mulbug_u_w8_booth.map"; [ -s "$m" ] && diff -q <(grep -E '^(input|output)' "$OUT/aig/mul_u_w8_norm.map") <(grep -E '^(input|output)' "$m") >/dev/null && echo "MAP_MATCH mulbug_u w8 vs mul_u norm"
