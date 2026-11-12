#!/usr/bin/env bash

set -e

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

exec gdb -q \
    -ex "set debuginfod enabled off" \
    -x "$SCRIPT_DIR/main.py"

