#!/usr/bin/env bash
find / -xdev \( -name firtool -o -name circt-opt -o -name arcilator -o -name circt-verilog -o -name "mlir-opt" -o -name "calyx" \) -type f 2>/dev/null | head -20
for f in $(find / -xdev -name firtool -type f 2>/dev/null | head -2); do $f --version 2>&1 | head -3; done
ls ~/wave7d1/dynamatic-src/polygeist/llvm-project/build/bin 2>/dev/null | head -40 | tr '\n' ' '
