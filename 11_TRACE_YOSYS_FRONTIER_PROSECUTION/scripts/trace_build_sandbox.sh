#!/usr/bin/env bash
set -eu
HERE="$(cd "$(dirname "$0")/.." && pwd)"
DOCKER="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
CTX="$(wslpath -w "$HERE/third_party/trace_d57aa9a7")"
DF="$(wslpath -w "$HERE/scripts/trace_sandbox/Dockerfile")"
"$DOCKER" build --pull=false --network none -f "$DF" -t trace-sandbox:d57aa9a7 "$CTX"
"$DOCKER" image inspect --format '{{.Id}} {{.Created}}' trace-sandbox:d57aa9a7
