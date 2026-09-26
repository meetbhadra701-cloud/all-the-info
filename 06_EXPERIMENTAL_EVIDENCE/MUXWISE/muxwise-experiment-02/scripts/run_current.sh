#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root_dir="$(cd "$script_dir/.." && pwd)"
suite_dir="$root_dir/work/oss-cad-suite"
export PATH="$suite_dir/bin:$PATH"

exec "$suite_dir/bin/$@"

