#!/usr/bin/env bash
# Probe the local Dynamatic build: solver support, buffer algorithms, tools (read-only)
D=~/wave7d1/dynamatic-src
echo "== git"; git -C $D log -1 --format='%H %cd %s' 2>/dev/null
echo "== gurobi"; ls /opt 2>/dev/null; find / -maxdepth 3 -iname "*gurobi*" 2>/dev/null | head; echo "GUROBI_HOME=$GUROBI_HOME"
grep -i "gurobi\|DYNAMATIC_GUROBI\|ENABLE_LEQ\|HiGHS\|cbc\|or-tools\|ortools" $D/build/CMakeCache.txt 2>/dev/null | head -10
echo "== buffer algorithms in source"; grep -rho '"fpga20"\|"fpl22"\|"on-merges"\|"costaware"\|"mapbuf"\|"cost-aware"' $D/lib $D/include $D/tools 2>/dev/null | sort | uniq -c
echo "== bin"; ls $D/bin $D/build/bin 2>/dev/null | tr '\n' ' '; echo
echo "== integration tests"; ls $D/integration-test 2>/dev/null | head -60 | tr '\n' ' '; echo
echo "== docs"; ls $D/docs 2>/dev/null | tr '\n' ' '; echo
head -40 ~/wave7d1/WAVE_7_D1_DOSSIER.md 2>/dev/null
