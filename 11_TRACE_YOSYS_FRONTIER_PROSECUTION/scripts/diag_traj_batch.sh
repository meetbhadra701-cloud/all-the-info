#!/usr/bin/env bash
# SP-size trajectories contrasting post-ABC Booth (fails at W=8,12) with pre-ABC Booth and post-ABC Booth at W=16 (pass).
H="$(cd "$(dirname "$0")/.." && pwd)"
bash "$H/scripts/diag_steps.sh" D3_mul_u_w8_boothpre_folded netlists/CONTROL/A_mul_u_w8__booth_pre_folded.aig 60 -mul -dyn -p -c
bash "$H/scripts/diag_steps.sh" D4_mul_u_w16_booth netlists/MAIN/A_mul_u_w16__booth.aig 60 -mul -dyn -p -c
bash "$H/scripts/diag_steps.sh" D5_mul_u_w12_booth netlists/MAIN/A_mul_u_w12__booth.aig 60 -mul -dyn -p -c
for t in D1_mul_s_w8_norm D2_mul_u_w8_booth D3_mul_u_w8_boothpre_folded D4_mul_u_w16_booth D5_mul_u_w12_booth; do
  echo "$t $(python3 "$H/scripts/sp_trajectory.py" "$H/logs/diag/$t.log")"; done
