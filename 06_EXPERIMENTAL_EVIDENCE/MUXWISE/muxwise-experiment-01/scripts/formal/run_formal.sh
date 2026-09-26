#!/usr/bin/env bash
set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root_dir="$(cd "$script_dir/../.." && pwd)"
mkdir -p "$root_dir/logs"

run_one() {
  local name="$1"
  local ys="$2"
  local log="$root_dir/logs/formal_${name}.log"
  set +e
  /usr/bin/time -f 'elapsed_seconds=%e\nmax_rss_kb=%M\nexit_status=%x' \
    "$root_dir/scripts/run_yosys.sh" yosys -s "$ys" >"$log" 2>&1
  local status=$?
  set -e
  printf 'status=%s\nlog=%s\n' "$status" "$log" > "$root_dir/logs/formal_${name}.status"
  return 0
}

run_one equivalent scripts/formal/equiv.ys
run_one incorrect scripts/formal/incorrect.ys

