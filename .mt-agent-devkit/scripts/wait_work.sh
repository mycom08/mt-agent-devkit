#!/usr/bin/env bash
set -euo pipefail
script_root=$(dirname -- "$0")
if [[ -n "${PYTHON_COMMAND:-}" ]]; then
  exec "$PYTHON_COMMAND" "$script_root/wait_work.py" "$@"
fi
for interpreter in python3 python; do
  if command -v "$interpreter" >/dev/null 2>&1; then
    exec "$interpreter" "$script_root/wait_work.py" "$@"
  fi
done
echo 'wait_work: Python 3 is required (python3 or python); set PYTHON_COMMAND.' >&2
exit 2
