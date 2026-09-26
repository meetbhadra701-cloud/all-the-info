#!/usr/bin/env bash
# Records exact Yosys builds used in this experiment. Read-only; uses only local images/checkouts.
set -u
HERE="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$HERE/evidence/provenance.txt"
DOCKER="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
SUITE=/mnt/c/Users/meetb/Documents/Codex/2026-09-20/muxwise-experiment-1-zero-commitment-eda/outputs/muxwise-experiment-02/work/oss-cad-suite
SRC=/mnt/c/Users/meetb/Documents/Codex/2026-09-20/muxwise-experiment-1-zero-commitment-eda/outputs/yosys-fma-final-validation/current_upstream
{
echo "# Provenance recorded $(date -Is)"
echo "## Y_DIRTY (OSS CAD Suite, WSL)"; "$SUITE/bin/yosys" -V; cat "$SUITE/VERSION"; echo; sha256sum "$SUITE/libexec/yosys"
for img in muxwise-yosys-current:exp6 muxwise-yosys-patched:exp6; do
  echo "## docker image $img"
  "$DOCKER" image inspect --format '{{.Id}} created={{.Created}}' "$img"
  "$DOCKER" run --rm --network none "$img" /build/yosys -V
  "$DOCKER" run --rm --network none "$img" sha256sum /build/yosys
done
for d in source patched-source; do
  echo "## git checkout current_upstream/$d"
  git -C "$SRC/$d" log -1 --format='%H %an %ad %s' 2>&1
  git -C "$SRC/$d" rev-parse --abbrev-ref HEAD 2>&1
  echo "status (porcelain, first 20):"; git -C "$SRC/$d" status --porcelain 2>&1 | head -20
done
echo "## diff patched-source vs source (kernel/compressor_tree.cc)"
diff <(git -C "$SRC/source" show HEAD:kernel/compressor_tree.cc) <(git -C "$SRC/patched-source" show HEAD:kernel/compressor_tree.cc) | head -60
} > "$OUT" 2>&1
cat "$OUT"
