#!/usr/bin/env bash
# Run TRACE inside the hardened sandbox. Usage: trace_run.sh <path relative to experiment root> <timeout_s> <trace args...>
# Prints a structured block; the verdict is parsed later from TRACE's text, never from exit codes.
set -u
HERE="$(cd "$(dirname "$0")/.." && pwd)"
DOCKER="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
REL="$1"; TMO="$2"; shift 2
ROOT_W="$(wslpath -w "$HERE")"
echo "### FILE $REL"
echo "### ARGS $*"
echo "### TIMEOUT $TMO"
echo "### START $(date -Is)"
t0=$(date +%s.%N)
"$DOCKER" run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges \
  --pids-limit 64 --memory "${MEM:-14g}" --memory-swap "${MEM:-14g}" --cpus "${CPUS:-1}" --user 65534:65534 \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m -v "$ROOT_W:/data:ro" --pull never \
  --entrypoint /bin/sh trace-sandbox:d57aa9a7 -c '
T="$1"; shift
timeout -s KILL "$T" /usr/bin/time -v /opt/trace/trace "$@" 2>&1
echo "### TRACE_EXIT $?"
echo "### CGROUP_MEMORY_PEAK_BYTES $(cat /sys/fs/cgroup/memory.peak 2>/dev/null || echo NA)"
' sh "$TMO" "/data/$REL" "$@"
echo "### DOCKER_EXIT $?"
t1=$(date +%s.%N)
echo "### WALL_SECONDS $(awk -v a="$t0" -v b="$t1" 'BEGIN{printf "%.2f", b-a}')"
echo "### END $(date -Is)"
