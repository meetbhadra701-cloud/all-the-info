#!/usr/bin/env bash
S=/mnt/c/Users/meetb/Documents/Codex/2026-09-20/muxwise-experiment-1-zero-commitment-eda/outputs/muxwise-experiment-02/work/oss-cad-suite
ABC="$S/bin/yosys-abc"
A=/mnt/c/Users/meetb/AppData/Local/Temp/claude/C--Users-meetb-Desktop-CLAUDE-OPUS-5-5-RESEARCH-CONTEXT/03476a4d-4e8a-44cd-9bcd-493130f6d087/scratchpad/s1/work/aig
cd "$A"
run() { echo "==== $1"; timeout 120 "$ABC" -c "$1" 2>&1 | tail -6; echo "[rc=$?]"; }
run "&r mul_u_w8_norm.aig; &cec mul_u_w8_booth.aig"
run "&r mul_u_w8_norm.aig; &cec mulbug_u_w8_booth.aig"
run "cec -T 60 mul_u_w8_norm.aig mul_u_w8_booth.aig"
run "cec -T 60 mul_u_w8_norm.aig mulbug_u_w8_booth.aig"
run "&acec -T 60 mul_u_w8_norm.aig mul_u_w8_booth.aig"
run "&acec -b -T 60 mul_u_w8_norm.aig mul_u_w8_booth.aig"
run "&acec -b -T 60 mul_u_w8_norm.aig mulbug_u_w8_booth.aig"
run "&acec -T 60 mac_u_w8_norm.aig mac_u_w8_tree.aig"
run "&r mul_u_w8_booth.aig; &polyn"
run "&r mul_u_w8_booth.aig; &polyn -v"
run "&r mulbug_u_w8_booth.aig; &polyn"
run "&r mul_s_w8_booth.aig; &polyn -s"
