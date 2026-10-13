#!/usr/bin/env bash
set -euo pipefail
exec "${PYTHON_COMMAND:-python}" "$(dirname -- "$0")/wait_work.py" "$@"
