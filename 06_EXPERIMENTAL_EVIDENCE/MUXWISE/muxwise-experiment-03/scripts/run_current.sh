#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SUITE_DIR="${MUXWISE_OSS_CAD_SUITE:-$ROOT_DIR/../muxwise-experiment-02/work/oss-cad-suite}"

if [[ ! -x "$SUITE_DIR/bin/yosys" ]]; then
  echo "OSS CAD Suite not found at $SUITE_DIR" >&2
  exit 2
fi

export PATH="$SUITE_DIR/bin:$PATH"
exec "$SUITE_DIR/bin/$@"
