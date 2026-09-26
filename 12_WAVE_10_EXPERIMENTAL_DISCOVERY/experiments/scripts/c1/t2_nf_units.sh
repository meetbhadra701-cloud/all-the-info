#!/usr/bin/env bash
# T2: checks how ABC &nf interprets -D (delay target units) and -R (relaxation), using the adder.
G=/w/third_party/MappingEvolve/third-party/mockturtle/experiments/cell_libraries/asap7.genlib; C=/w/experiments/inputs/c1/c2
for o in "-p" "-p -D 2768" "-p -D 2768870" "-p -D 27688" "-p -D 276887" "-p -R 5" "-p -R 10" "-p -R 30" "-p -D 3417850" "-p -a" ; do
  printf "%-18s " "$o"; yosys-abc -q "read_genlib $G; read_aiger $C/adder.aig; &get -n; &nf $o; &put; print_stats" 2>&1 | grep -o "area *= *[0-9.]* *delay *= *[0-9.]*" | tr -s ' '
done
yosys-abc -q "read_genlib $G; read_aiger $C/adder.aig; &get -n; &nf -p -D 2768870 -v; &put" 2>&1 | head -30
