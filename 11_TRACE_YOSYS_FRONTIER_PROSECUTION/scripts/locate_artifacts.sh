#!/usr/bin/env bash
# Read-only reconnaissance: locate Codex workspaces, PR #6231 worktree, and any built Yosys binaries.
C=/mnt/c/Users/meetb/Documents/Codex
echo "== Codex workspaces"; ls "$C"
for d in "$C"/*/; do echo "-- $d"; ls "$d" 2>/dev/null; done
echo "== dirs named like yosys-fma / exp6 / exp5"
find "$C" /mnt/c/Users/meetb/Downloads /mnt/c/Users/meetb/Desktop ~ -maxdepth 6 -type d \( -iname '*fma*' -o -iname '*exp6*' -o -iname '*exp5*' -o -iname '*6231*' \) 2>/dev/null | grep -v node_modules | head -40
echo "== yosys executables (ELF) under Codex/Downloads/home"
find "$C" /mnt/c/Users/meetb/Downloads ~ -maxdepth 8 -type f -name 'yosys' 2>/dev/null | head -20
