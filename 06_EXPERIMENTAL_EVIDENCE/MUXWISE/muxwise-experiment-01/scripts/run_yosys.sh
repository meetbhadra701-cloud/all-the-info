#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root_dir="$(cd "$script_dir/.." && pwd)"
image_name="muxwise-yosys:debian-bookworm"
mount_dir="$(wslpath -w "$root_dir" 2>/dev/null || printf '%s' "$root_dir")"

if ! docker.exe image inspect "$image_name" >/dev/null 2>&1; then
  docker.exe build -t "$image_name" -f "$root_dir/tooling/Dockerfile" "$root_dir/tooling"
fi

exec docker.exe run --rm \
  -v "$mount_dir:/work" \
  -w /work \
  "$image_name" "$@"
