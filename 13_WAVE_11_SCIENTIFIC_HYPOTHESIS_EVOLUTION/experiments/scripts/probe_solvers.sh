#!/usr/bin/env bash
echo "== /opt"; ls /opt 2>&1 | head -30
echo "== which"; for b in cbc glpsol scip highs sat_runner solve fzn-cp-sat minizinc cplex gurobi_cl kissat cadical minisat glucose open-wbo rc2 lingeling picosat; do p=$(command -v $b 2>/dev/null); [ -n "$p" ] && echo "$b -> $p"; done
echo "== find ortools/cbc/scip/highs files"; find / -xdev \( -iname "*ortools*" -o -iname "*or-tools*" -o -iname "sat_runner*" -o -iname "libCbc*" -o -iname "libscip*" -o -iname "libhighs*" -o -iname "libglpk*" \) 2>/dev/null | grep -v proc | head -40
echo "== python pkgs"; python3 -c "import pkgutil; print(sorted(m.name for m in pkgutil.iter_modules() if m.name.lower() in ('ortools','pulp','pyscipopt','highspy','cvxpy','scipy','networkx','pysat','mip','swiglpk','z3')))"
echo "== /oss/bin solvers"; ls /oss/bin 2>/dev/null | grep -iE "z3|yices|boolector|bitwuzla|cvc|kissat|cadical|avy|pono|btor|abc|mini|glucose|lingeling|picosat|eqy|sby|smt" | tr '\n' ' '; echo
echo "== /oss/lib python"; ls /oss/lib/python3*/site-packages 2>/dev/null | head -50 | tr '\n' ' '; echo
