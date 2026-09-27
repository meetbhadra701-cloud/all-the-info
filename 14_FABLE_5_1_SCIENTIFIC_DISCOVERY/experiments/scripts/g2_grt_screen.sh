#!/usr/bin/env bash
# Gate 2 screening: global routing of one program on the met4-met5 layers only; prints wirelength and overflow.
# ./g2_grt_screen.sh G2_DIR DESIGN UTIL TAG     UTIL = 60 (generic G2 base g2_*) or 60s (R2 structured base g2s_*)
G2=$1; D=$2; U=$3; T=$4
if [[ $U == *r ]]; then NICK=g2r3_${D}_u${U%r}; KIND=r3
elif [[ $U == *s ]]; then NICK=g2s_${D}_u${U%s}; KIND=structured; else NICK=g2_${D}_u${U}; KIND=generic; fi
docker run --rm -v "$G2":/work -v "$(cd "$(dirname "$0")" && pwd)":/scripts -w /work \
  -e BASE_ODB=/work/orfs/results/sky130hd/$NICK/base/6_final.odb -e PROG_TCL=/work/$D/prog_$T.tcl \
  -e OUT=/work/$D/grt_${T}_u${U} -e MODE=grt -e DRT_ITERS=0 openroad/orfs:latest \
  /OpenROAD-flow-scripts/tools/install/OpenROAD/bin/openroad -no_init -threads 2 -exit /scripts/g2_program.tcl > "$G2/$D/grt_${T}_u${U}.log" 2>&1
L="$G2/$D/grt_${T}_u${U}.log"
wl=$(grep -oE 'Total wirelength: [0-9]+' "$L" | tail -1 | grep -oE '[0-9]+')
m4=$(grep -A9 'Final congestion report' "$L" | awk '$1=="met4"{print $4, $NF}')
m5=$(grep -A9 'Final congestion report' "$L" | awk '$1=="met5"{print $4, $NF}')
tot=$(grep -A9 'Final congestion report' "$L" | awk '$1=="Total"{print $NF}')
echo "{\"design\":\"$D\",\"util\":${U//[rs]/},\"base\":\"$KIND\",\"tag\":\"$T\",\"grt_wl_um\":${wl:-null},\"met4_usage_overflow\":\"$m4\",\"met5_usage_overflow\":\"$m5\",\"total_overflow\":${tot:-null}}" | tee -a "$G2/g2_grt_screen.jsonl"
