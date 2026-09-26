#!/usr/bin/env bash
O=/mnt/c/Users/meetb/Documents/Codex/2026-09-20/muxwise-experiment-1-zero-commitment-eda/outputs
for d in yosys-fma-correctness-investigation yosys-fma-final-validation; do
  echo "== $d"; ls "$O/$d"; echo "  size: $(du -sh "$O/$d" 2>/dev/null | cut -f1)"
done
echo "== candidate binaries (ELF) anywhere under the two dirs"
find "$O/yosys-fma-correctness-investigation" "$O/yosys-fma-final-validation" -type f -size +5M 2>/dev/null | while read f; do head -c4 "$f" | grep -q ELF && echo "ELF $f $(stat -c%s "$f")"; done | head -20
echo "== git worktrees/checkouts"
find "$O/yosys-fma-correctness-investigation" "$O/yosys-fma-final-validation" -maxdepth 4 -name .git 2>/dev/null | head
echo "== passwitness patched pointers"
grep -rl -i "patched" /mnt/c/Users/meetb/Downloads/passwitness/out/fma-patched 2>/dev/null | head -5
ls /mnt/c/Users/meetb/Downloads/passwitness/out/fma-patched 2>/dev/null | head
